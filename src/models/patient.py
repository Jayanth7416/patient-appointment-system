"""Patient Models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class PatientCreate(BaseModel):
    """Request to create patient"""
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class Patient(BaseModel):
    """Patient record"""
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    preferred_providers: List[str] = []
    preferred_locations: List[str] = []
    communication_preferences: dict = {
        "sms": True,
        "email": True,
        "phone": False
    }
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class PatientPreferences(BaseModel):
    """Patient scheduling preferences"""
    patient_id: str
    preferred_days: List[str] = []  # monday, tuesday, etc.
    preferred_time_of_day: Optional[str] = None  # morning, afternoon, evening
    preferred_providers: List[str] = []
    preferred_locations: List[str] = []
    reminder_hours_before: List[int] = [24, 2]
    communication_preferences: dict = {
        "sms": True,
        "email": True,
        "phone": False
    }
