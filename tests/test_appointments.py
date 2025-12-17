"""Tests for Appointment Service"""

import pytest
from datetime import date, time, timedelta
from src.services.appointment_service import AppointmentService
from src.models.appointment import AppointmentCreate, AppointmentType


@pytest.fixture
def appointment_service():
    return AppointmentService()


class TestAppointmentService:
    """Test appointment booking functionality"""

    @pytest.mark.asyncio
    async def test_create_appointment(self, appointment_service):
        """Test creating a new appointment"""
        request = AppointmentCreate(
            patient_id="pat-12345",
            provider_id="prov-001",
            location_id="loc-001",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time=time(10, 0),
            appointment_type=AppointmentType.NEW_PATIENT,
            duration_minutes=30,
            reason="Annual checkup"
        )

        appointment = await appointment_service.create_appointment(request)

        assert appointment.id is not None
        assert appointment.patient_id == "pat-12345"
        assert appointment.provider_id == "prov-001"
        assert appointment.status.value == "scheduled"

    @pytest.mark.asyncio
    async def test_cancel_appointment(self, appointment_service):
        """Test cancelling an appointment"""
        # Create first
        request = AppointmentCreate(
            patient_id="pat-12345",
            provider_id="prov-001",
            location_id="loc-001",
            scheduled_date=date.today() + timedelta(days=2),
            scheduled_time=time(11, 0),
            appointment_type=AppointmentType.FOLLOW_UP,
        )

        appointment = await appointment_service.create_appointment(request)

        # Cancel
        await appointment_service.cancel_appointment(
            appointment.id,
            reason="Patient request"
        )

        # Verify
        updated = await appointment_service.get_appointment(appointment.id)
        assert updated.status.value == "cancelled"
        assert updated.cancellation_reason == "Patient request"

    @pytest.mark.asyncio
    async def test_check_in(self, appointment_service):
        """Test patient check-in"""
        request = AppointmentCreate(
            patient_id="pat-12345",
            provider_id="prov-001",
            location_id="loc-001",
            scheduled_date=date.today() + timedelta(days=3),
            scheduled_time=time(14, 0),
            appointment_type=AppointmentType.FOLLOW_UP,
        )

        appointment = await appointment_service.create_appointment(request)

        await appointment_service.check_in(appointment.id)

        updated = await appointment_service.get_appointment(appointment.id)
        assert updated.status.value == "checked_in"
        assert updated.checked_in_at is not None
