"""Availability Management Endpoints"""

from fastapi import APIRouter, Query
from typing import Optional, List
from datetime import date, time
import structlog

from src.models.availability import TimeSlot, AvailabilitySearch
from src.services.availability_service import AvailabilityService

router = APIRouter()
logger = structlog.get_logger()

availability_service = AvailabilityService()


@router.get("/search")
async def search_availability(
    specialty: Optional[str] = None,
    location_id: Optional[str] = None,
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    time_of_day: Optional[str] = Query(
        default=None,
        enum=["morning", "afternoon", "evening"]
    ),
    appointment_type: Optional[str] = None,
    limit: int = Query(default=20, le=100)
):
    """
    Search for available appointment slots

    - Find slots across multiple providers
    - Filter by specialty, location, time preference
    - Returns aggregated availability
    """
    from datetime import timedelta

    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=14)

    search = AvailabilitySearch(
        specialty=specialty,
        location_id=location_id,
        start_date=start_date,
        end_date=end_date,
        time_of_day=time_of_day,
        appointment_type=appointment_type,
        limit=limit
    )

    results = await availability_service.search_slots(search)

    return {
        "slots": results,
        "total": len(results),
        "search_criteria": search.model_dump()
    }


@router.get("/next-available")
async def get_next_available(
    provider_id: Optional[str] = None,
    specialty: Optional[str] = None,
    location_id: Optional[str] = None,
    appointment_type: Optional[str] = None
):
    """
    Get next available slot

    - Returns the soonest available appointment
    - Useful for urgent scheduling
    """
    slot = await availability_service.get_next_available(
        provider_id=provider_id,
        specialty=specialty,
        location_id=location_id,
        appointment_type=appointment_type
    )

    if not slot:
        return {"message": "No availability found", "slot": None}

    return {"slot": slot}


@router.get("/calendar")
async def get_availability_calendar(
    provider_id: str,
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2024, le=2030)
):
    """
    Get calendar view of provider availability

    - Returns day-by-day availability for a month
    - Shows number of open slots per day
    """
    calendar = await availability_service.get_calendar(
        provider_id=provider_id,
        month=month,
        year=year
    )

    return {"calendar": calendar, "provider_id": provider_id}


@router.get("/slots/{slot_id}")
async def get_slot_details(slot_id: str):
    """Get details for a specific slot"""
    slot = await availability_service.get_slot(slot_id)
    if not slot:
        return {"error": "Slot not found"}
    return slot


@router.post("/slots/{slot_id}/hold")
async def hold_slot(
    slot_id: str,
    patient_id: str,
    duration_minutes: int = 10
):
    """
    Temporarily hold a slot

    - Prevents double-booking during checkout
    - Released automatically after duration
    """
    hold = await availability_service.hold_slot(
        slot_id=slot_id,
        patient_id=patient_id,
        duration_minutes=duration_minutes
    )

    return hold


@router.delete("/slots/{slot_id}/hold")
async def release_slot_hold(slot_id: str, patient_id: str):
    """Release a held slot"""
    await availability_service.release_hold(slot_id, patient_id)
    return {"status": "released", "slot_id": slot_id}
