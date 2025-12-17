"""Waitlist Models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class WaitlistRequest(BaseModel):
    """Request to join waitlist"""
    patient_id: str
    provider_id: str
    location_id: Optional[str] = None
    preferred_dates: List[date] = []
    preferred_time_of_day: Optional[str] = None
    appointment_type: str
    urgency: str = "normal"  # normal, urgent, flexible
    notes: Optional[str] = None


class WaitlistEntry(BaseModel):
    """Waitlist entry"""
    id: str
    patient_id: str
    provider_id: str
    location_id: Optional[str]
    preferred_dates: List[date]
    preferred_time_of_day: Optional[str]
    appointment_type: str
    urgency: str
    status: str = "waiting"  # waiting, notified, booked, expired, removed
    position: int
    created_at: datetime
    notified_at: Optional[datetime] = None
    booked_appointment_id: Optional[str] = None


class WaitlistStats(BaseModel):
    """Waitlist statistics"""
    total_entries: int
    waiting: int
    notified: int
    converted: int
    average_wait_days: float
    conversion_rate: float
