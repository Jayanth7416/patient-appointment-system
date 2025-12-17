"""Patient Endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
import structlog

from src.models.patient import Patient, PatientCreate
from src.models.appointment import Appointment
from src.services.patient_service import PatientService

router = APIRouter()
logger = structlog.get_logger()

patient_service = PatientService()


@router.get("/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """Get patient details"""
    patient = await patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/{patient_id}/appointments")
async def get_patient_appointments(
    patient_id: str,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=20, le=100)
):
    """
    Get patient's appointments

    - Filter by status (upcoming, past, cancelled)
    - Filter by date range
    """
    appointments = await patient_service.get_appointments(
        patient_id=patient_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    return {
        "patient_id": patient_id,
        "appointments": appointments,
        "total": len(appointments)
    }


@router.get("/{patient_id}/upcoming")
async def get_upcoming_appointments(patient_id: str):
    """Get patient's upcoming appointments"""
    appointments = await patient_service.get_upcoming_appointments(patient_id)
    return {"appointments": appointments}


@router.get("/{patient_id}/history")
async def get_appointment_history(
    patient_id: str,
    limit: int = Query(default=50, le=200)
):
    """Get patient's appointment history"""
    history = await patient_service.get_history(patient_id, limit)
    return {"history": history}


@router.post("", response_model=Patient, status_code=201)
async def create_patient(patient: PatientCreate):
    """Register a new patient"""
    try:
        created = await patient_service.create_patient(patient)
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{patient_id}/preferences")
async def get_patient_preferences(patient_id: str):
    """Get patient's scheduling preferences"""
    preferences = await patient_service.get_preferences(patient_id)
    return preferences


@router.put("/{patient_id}/preferences")
async def update_patient_preferences(
    patient_id: str,
    preferences: dict
):
    """Update patient's scheduling preferences"""
    try:
        updated = await patient_service.update_preferences(patient_id, preferences)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
