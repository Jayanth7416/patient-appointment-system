"""Appointment Management Endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from datetime import date, datetime
import structlog

from src.models.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentStatus
)
from src.services.appointment_service import AppointmentService
from src.services.notification_service import NotificationService

router = APIRouter()
logger = structlog.get_logger()

appointment_service = AppointmentService()
notification_service = NotificationService()


@router.post("", response_model=Appointment, status_code=201)
async def create_appointment(
    appointment: AppointmentCreate,
    background_tasks: BackgroundTasks
):
    """
    Book a new appointment

    Flow:
    1. Acquire distributed lock on slot
    2. Verify slot availability
    3. Create appointment record
    4. Update availability cache
    5. Send confirmation notification
    """
    try:
        created = await appointment_service.create_appointment(appointment)

        # Send confirmation async
        background_tasks.add_task(
            notification_service.send_confirmation,
            created.id,
            created.patient_id
        )

        logger.info(
            "appointment_created",
            appointment_id=created.id,
            provider_id=created.provider_id
        )

        return created

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("appointment_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to book appointment")


@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    """Get appointment details"""
    appointment = await appointment_service.get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.patch("/{appointment_id}", response_model=Appointment)
async def update_appointment(
    appointment_id: str,
    update: AppointmentUpdate,
    background_tasks: BackgroundTasks
):
    """
    Reschedule or modify appointment

    - Can change date/time if new slot is available
    - Triggers notification to patient
    """
    try:
        updated = await appointment_service.update_appointment(
            appointment_id,
            update
        )

        if update.scheduled_time:
            background_tasks.add_task(
                notification_service.send_reschedule_confirmation,
                updated.id,
                updated.patient_id
            )

        return updated

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    reason: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Cancel an appointment

    - Releases the slot for others
    - Notifies waitlist if applicable
    - Sends cancellation confirmation
    """
    try:
        await appointment_service.cancel_appointment(appointment_id, reason)

        # Notify waitlist
        background_tasks.add_task(
            appointment_service.process_waitlist,
            appointment_id
        )

        return {"status": "cancelled", "appointment_id": appointment_id}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_appointments(
    provider_id: Optional[str] = None,
    location_id: Optional[str] = None,
    date: Optional[date] = None,
    status: Optional[AppointmentStatus] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0
):
    """List appointments with filters (for admin/staff)"""
    appointments = await appointment_service.list_appointments(
        provider_id=provider_id,
        location_id=location_id,
        date=date,
        status=status,
        limit=limit,
        offset=offset
    )
    return {"appointments": appointments, "total": len(appointments)}


@router.post("/{appointment_id}/check-in")
async def check_in(appointment_id: str):
    """Mark patient as checked in"""
    try:
        await appointment_service.check_in(appointment_id)
        return {"status": "checked_in", "appointment_id": appointment_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{appointment_id}/complete")
async def complete_appointment(
    appointment_id: str,
    notes: Optional[str] = None
):
    """Mark appointment as completed"""
    try:
        await appointment_service.complete(appointment_id, notes)
        return {"status": "completed", "appointment_id": appointment_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
