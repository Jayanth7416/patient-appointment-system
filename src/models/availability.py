"""Availability Models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime


class TimeSlot(BaseModel):
    """Available appointment slot"""
    id: str
    provider_id: str
    provider_name: str
    location_id: str
    location_name: str
    date: date
    start_time: time
    end_time: time
    duration_minutes: int
    appointment_types: List[str]
    available: bool = True
    held_by: Optional[str] = None  # patient_id if held
    held_until: Optional[datetime] = None


class AvailabilitySearch(BaseModel):
    """Availability search parameters"""
    specialty: Optional[str] = None
    location_id: Optional[str] = None
    provider_id: Optional[str] = None
    start_date: date
    end_date: date
    time_of_day: Optional[str] = None  # morning, afternoon, evening
    appointment_type: Optional[str] = None
    limit: int = 20


class DayAvailability(BaseModel):
    """Availability for a single day"""
    date: date
    total_slots: int
    available_slots: int
    slots: List[TimeSlot] = []


class CalendarDay(BaseModel):
    """Calendar view for a day"""
    date: date
    available_slots: int
    has_availability: bool


class SlotHold(BaseModel):
    """Temporary hold on a slot"""
    slot_id: str
    patient_id: str
    held_at: datetime
    expires_at: datetime
    status: str = "active"  # active, released, expired, converted
