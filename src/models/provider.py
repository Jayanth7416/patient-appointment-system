"""Provider Models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time
from enum import Enum


class Specialty(str, Enum):
    """Medical specialties"""
    PRIMARY_CARE = "primary_care"
    CARDIOLOGY = "cardiology"
    DERMATOLOGY = "dermatology"
    ORTHOPEDICS = "orthopedics"
    PEDIATRICS = "pediatrics"
    NEUROLOGY = "neurology"
    PSYCHIATRY = "psychiatry"
    ONCOLOGY = "oncology"
    GASTROENTEROLOGY = "gastroenterology"
    ENDOCRINOLOGY = "endocrinology"
    PULMONOLOGY = "pulmonology"
    RHEUMATOLOGY = "rheumatology"
    UROLOGY = "urology"
    OPHTHALMOLOGY = "ophthalmology"
    ENT = "ent"


class Location(BaseModel):
    """Clinic location"""
    id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    timezone: str = "America/New_York"


class WorkingHours(BaseModel):
    """Provider working hours for a day"""
    day: str  # monday, tuesday, etc.
    start_time: time
    end_time: time
    break_start: Optional[time] = None
    break_end: Optional[time] = None


class Provider(BaseModel):
    """Healthcare provider"""
    id: str
    first_name: str
    last_name: str
    title: str  # Dr., NP, PA, etc.
    specialty: Specialty
    credentials: List[str] = []  # MD, DO, NP, etc.
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    locations: List[Location] = []
    working_hours: List[WorkingHours] = []
    accepting_new_patients: bool = True
    languages: List[str] = ["English"]
    appointment_types: List[str] = ["new_patient", "follow_up", "consultation"]
    default_appointment_duration: int = 30  # minutes

    @property
    def full_name(self) -> str:
        return f"{self.title} {self.first_name} {self.last_name}"


class ProviderSearch(BaseModel):
    """Provider search parameters"""
    location_id: Optional[str] = None
    specialty: Optional[Specialty] = None
    name: Optional[str] = None
    accepting_new_patients: bool = True
    limit: int = 20
    offset: int = 0
