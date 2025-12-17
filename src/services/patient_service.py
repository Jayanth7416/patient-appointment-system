"""Patient Service"""

import uuid
from datetime import date, datetime
from typing import Optional, List
import structlog

from src.models.patient import Patient, PatientCreate, PatientPreferences

logger = structlog.get_logger()


class PatientService:
    """Patient management service"""

    def __init__(self):
        self.patients: dict = {}
        self.preferences: dict = {}

    async def create_patient(self, request: PatientCreate) -> Patient:
        """Create a new patient record"""
        patient_id = f"pat-{uuid.uuid4().hex[:12]}"

        patient = Patient(
            id=patient_id,
            first_name=request.first_name,
            last_name=request.last_name,
            date_of_birth=request.date_of_birth,
            email=request.email,
            phone=request.phone,
            address=request.address,
            city=request.city,
            state=request.state,
            zip_code=request.zip_code,
            insurance_provider=request.insurance_provider,
            insurance_id=request.insurance_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.patients[patient_id] = patient

        logger.info("patient_created", patient_id=patient_id)

        return patient

    async def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID"""
        return self.patients.get(patient_id)

    async def get_appointments(
        self,
        patient_id: str,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 20
    ) -> List[dict]:
        """Get patient's appointments"""
        # Would query appointment service
        return []

    async def get_upcoming_appointments(self, patient_id: str) -> List[dict]:
        """Get patient's upcoming appointments"""
        return await self.get_appointments(
            patient_id=patient_id,
            status="scheduled",
            start_date=date.today()
        )

    async def get_history(self, patient_id: str, limit: int = 50) -> List[dict]:
        """Get patient's appointment history"""
        return await self.get_appointments(
            patient_id=patient_id,
            status="completed",
            limit=limit
        )

    async def get_preferences(self, patient_id: str) -> PatientPreferences:
        """Get patient's scheduling preferences"""
        if patient_id in self.preferences:
            return self.preferences[patient_id]

        return PatientPreferences(patient_id=patient_id)

    async def update_preferences(
        self,
        patient_id: str,
        preferences: dict
    ) -> PatientPreferences:
        """Update patient's preferences"""
        current = await self.get_preferences(patient_id)

        for key, value in preferences.items():
            if hasattr(current, key):
                setattr(current, key, value)

        self.preferences[patient_id] = current

        return current
