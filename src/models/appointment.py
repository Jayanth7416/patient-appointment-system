"""Appointment Models"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(str, Enum):
    """Types of appointments"""
    NEW_PATIENT = "new_patient"
    FOLLOW_UP = "follow_up"
    CONSULTATION = "consultation"
    URGENT = "urgent"
    TELEHEALTH = "telehealth"
    ANNUAL_CHECKUP = "annual_checkup"


class AppointmentCreate(BaseModel):
    """Request to create appointment"""
    patient_id: str
    provider_id: str
    location_id: str
    scheduled_date: date
    scheduled_time: time
    appointment_type: AppointmentType
    duration_minutes: int = 30
    reason: Optional[str] = None
    notes: Optional[str] = None
    telehealth: bool = False


class AppointmentUpdate(BaseModel):
    """Request to update appointment"""
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class Appointment(BaseModel):
    """Appointment record"""
    id: str
    patient_id: str
    provider_id: str
    location_id: str
    scheduled_time: datetime
    end_time: datetime
    appointment_type: AppointmentType
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reason: Optional[str] = None
    notes: Optional[str] = None
    telehealth: bool = False
    telehealth_link: Optional[str] = None
    checked_in_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "apt-12345",
                "patient_id": "pat-67890",
                "provider_id": "prov-11111",
                "location_id": "loc-22222",
                "scheduled_time": "2024-01-20T10:30:00",
                "end_time": "2024-01-20T11:00:00",
                "appointment_type": "follow_up",
                "status": "scheduled"
            }
        }
