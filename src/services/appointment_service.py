"""Appointment Service"""

import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List
import structlog

from src.models.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentStatus
)
from src.services.availability_service import AvailabilityService
from src.services.cache_service import CacheService

logger = structlog.get_logger()


class AppointmentService:
    """
    Appointment management service

    Handles booking, rescheduling, and cancellation
    with distributed locking for concurrent access.
    """

    def __init__(self):
        self.availability_service = AvailabilityService()
        self.cache = CacheService()
        self.appointments: dict = {}  # In-memory store for demo

    async def create_appointment(
        self,
        request: AppointmentCreate
    ) -> Appointment:
        """
        Create a new appointment

        Uses distributed lock to prevent double-booking
        """
        slot_id = f"{request.provider_id}:{request.scheduled_date}:{request.scheduled_time}"

        # Acquire lock
        lock_key = f"lock:slot:{slot_id}"
        lock_acquired = await self.cache.acquire_lock(lock_key, ttl=30)

        if not lock_acquired:
            raise ValueError("Slot is currently being booked by another user")

        try:
            # Verify availability
            is_available = await self.availability_service.is_slot_available(
                provider_id=request.provider_id,
                date=request.scheduled_date,
                time=request.scheduled_time
            )

            if not is_available:
                raise ValueError("Selected slot is no longer available")

            # Create appointment
            appointment_id = f"apt-{uuid.uuid4().hex[:12]}"
            scheduled_datetime = datetime.combine(
                request.scheduled_date,
                request.scheduled_time
            )

            appointment = Appointment(
                id=appointment_id,
                patient_id=request.patient_id,
                provider_id=request.provider_id,
                location_id=request.location_id,
                scheduled_time=scheduled_datetime,
                end_time=scheduled_datetime + timedelta(minutes=request.duration_minutes),
                appointment_type=request.appointment_type,
                status=AppointmentStatus.SCHEDULED,
                reason=request.reason,
                notes=request.notes,
                telehealth=request.telehealth,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Save appointment
            self.appointments[appointment_id] = appointment

            # Update availability cache
            await self.availability_service.mark_slot_booked(
                provider_id=request.provider_id,
                date=request.scheduled_date,
                time=request.scheduled_time
            )

            logger.info(
                "appointment_created",
                appointment_id=appointment_id,
                provider_id=request.provider_id
            )

            return appointment

        finally:
            # Release lock
            await self.cache.release_lock(lock_key)

    async def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID"""
        return self.appointments.get(appointment_id)

    async def update_appointment(
        self,
        appointment_id: str,
        update: AppointmentUpdate
    ) -> Appointment:
        """Update/reschedule appointment"""
        appointment = self.appointments.get(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        if appointment.status == AppointmentStatus.CANCELLED:
            raise ValueError("Cannot update cancelled appointment")

        if update.scheduled_date or update.scheduled_time:
            # Rescheduling - need to check availability
            new_date = update.scheduled_date or appointment.scheduled_time.date()
            new_time = update.scheduled_time or appointment.scheduled_time.time()

            is_available = await self.availability_service.is_slot_available(
                provider_id=appointment.provider_id,
                date=new_date,
                time=new_time
            )

            if not is_available:
                raise ValueError("New slot is not available")

            # Release old slot
            await self.availability_service.mark_slot_available(
                provider_id=appointment.provider_id,
                date=appointment.scheduled_time.date(),
                time=appointment.scheduled_time.time()
            )

            # Update time
            appointment.scheduled_time = datetime.combine(new_date, new_time)

            # Book new slot
            await self.availability_service.mark_slot_booked(
                provider_id=appointment.provider_id,
                date=new_date,
                time=new_time
            )

        if update.reason:
            appointment.reason = update.reason
        if update.notes:
            appointment.notes = update.notes

        appointment.updated_at = datetime.utcnow()

        logger.info("appointment_updated", appointment_id=appointment_id)

        return appointment

    async def cancel_appointment(
        self,
        appointment_id: str,
        reason: Optional[str] = None
    ):
        """Cancel an appointment"""
        appointment = self.appointments.get(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        if appointment.status == AppointmentStatus.CANCELLED:
            raise ValueError("Appointment already cancelled")

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = reason
        appointment.cancelled_at = datetime.utcnow()
        appointment.updated_at = datetime.utcnow()

        # Release slot
        await self.availability_service.mark_slot_available(
            provider_id=appointment.provider_id,
            date=appointment.scheduled_time.date(),
            time=appointment.scheduled_time.time()
        )

        logger.info("appointment_cancelled", appointment_id=appointment_id)

    async def list_appointments(
        self,
        provider_id: Optional[str] = None,
        location_id: Optional[str] = None,
        date: Optional[date] = None,
        status: Optional[AppointmentStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Appointment]:
        """List appointments with filters"""
        results = list(self.appointments.values())

        if provider_id:
            results = [a for a in results if a.provider_id == provider_id]
        if location_id:
            results = [a for a in results if a.location_id == location_id]
        if date:
            results = [a for a in results if a.scheduled_time.date() == date]
        if status:
            results = [a for a in results if a.status == status]

        return results[offset:offset + limit]

    async def check_in(self, appointment_id: str):
        """Mark patient as checked in"""
        appointment = self.appointments.get(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        appointment.status = AppointmentStatus.CHECKED_IN
        appointment.checked_in_at = datetime.utcnow()
        appointment.updated_at = datetime.utcnow()

    async def complete(self, appointment_id: str, notes: Optional[str] = None):
        """Mark appointment as completed"""
        appointment = self.appointments.get(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        appointment.status = AppointmentStatus.COMPLETED
        appointment.completed_at = datetime.utcnow()
        if notes:
            appointment.notes = notes
        appointment.updated_at = datetime.utcnow()

    async def process_waitlist(self, appointment_id: str):
        """Process waitlist when slot becomes available"""
        # Would notify waitlisted patients
        logger.info("processing_waitlist", appointment_id=appointment_id)
