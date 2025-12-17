"""Provider Management Endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
import structlog

from src.models.provider import Provider, ProviderSearch, Specialty
from src.services.provider_service import ProviderService

router = APIRouter()
logger = structlog.get_logger()

provider_service = ProviderService()


@router.get("", response_model=List[Provider])
async def list_providers(
    location_id: Optional[str] = None,
    specialty: Optional[Specialty] = None,
    name: Optional[str] = None,
    accepting_new: bool = True,
    limit: int = Query(default=20, le=100),
    offset: int = 0
):
    """
    List providers with filters

    - Filter by location, specialty, name
    - Only show providers accepting new patients
    """
    search = ProviderSearch(
        location_id=location_id,
        specialty=specialty,
        name=name,
        accepting_new_patients=accepting_new,
        limit=limit,
        offset=offset
    )

    providers = await provider_service.search_providers(search)
    return providers


@router.get("/{provider_id}", response_model=Provider)
async def get_provider(provider_id: str):
    """Get provider details"""
    provider = await provider_service.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.get("/{provider_id}/availability")
async def get_provider_availability(
    provider_id: str,
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    appointment_type: Optional[str] = None
):
    """
    Get provider's available appointment slots

    - Returns available time slots for booking
    - Cached for performance
    """
    from datetime import timedelta

    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=14)

    availability = await provider_service.get_availability(
        provider_id=provider_id,
        start_date=start_date,
        end_date=end_date,
        appointment_type=appointment_type
    )

    return availability


@router.get("/{provider_id}/schedule")
async def get_provider_schedule(
    provider_id: str,
    date: date = Query(default=None)
):
    """Get provider's schedule for a specific date"""
    if not date:
        date = date.today()

    schedule = await provider_service.get_schedule(provider_id, date)
    return schedule


@router.get("/locations")
async def list_locations(
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None
):
    """List clinic locations"""
    locations = await provider_service.list_locations(
        city=city,
        state=state,
        zip_code=zip_code
    )
    return {"locations": locations}


@router.get("/specialties")
async def list_specialties():
    """List available medical specialties"""
    return {
        "specialties": [s.value for s in Specialty]
    }
