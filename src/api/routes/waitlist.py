"""Waitlist Management Endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
import structlog

from src.models.waitlist import WaitlistEntry, WaitlistRequest
from src.services.waitlist_service import WaitlistService

router = APIRouter()
logger = structlog.get_logger()

waitlist_service = WaitlistService()


@router.post("", response_model=WaitlistEntry, status_code=201)
async def join_waitlist(request: WaitlistRequest):
    """
    Join waitlist for an appointment slot

    - Patient will be notified when slot becomes available
    - Priority based on join time and urgency
    """
    try:
        entry = await waitlist_service.add_to_waitlist(request)

        logger.info(
            "waitlist_entry_created",
            entry_id=entry.id,
            patient_id=request.patient_id
        )

        return entry

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{entry_id}", response_model=WaitlistEntry)
async def get_waitlist_entry(entry_id: str):
    """Get waitlist entry details"""
    entry = await waitlist_service.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    return entry


@router.delete("/{entry_id}")
async def leave_waitlist(entry_id: str):
    """Remove from waitlist"""
    try:
        await waitlist_service.remove_from_waitlist(entry_id)
        return {"status": "removed", "entry_id": entry_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/patient/{patient_id}")
async def get_patient_waitlist(patient_id: str):
    """Get all waitlist entries for a patient"""
    entries = await waitlist_service.get_patient_entries(patient_id)
    return {"entries": entries, "total": len(entries)}


@router.get("/provider/{provider_id}")
async def get_provider_waitlist(
    provider_id: str,
    date: Optional[date] = None,
    limit: int = Query(default=50, le=200)
):
    """Get waitlist for a provider (staff view)"""
    entries = await waitlist_service.get_provider_waitlist(
        provider_id=provider_id,
        date=date,
        limit=limit
    )
    return {"entries": entries, "total": len(entries)}


@router.post("/{entry_id}/notify")
async def notify_waitlist_patient(entry_id: str):
    """Manually notify patient of available slot"""
    try:
        result = await waitlist_service.notify_patient(entry_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_waitlist_stats(
    provider_id: Optional[str] = None,
    location_id: Optional[str] = None
):
    """Get waitlist statistics"""
    stats = await waitlist_service.get_stats(
        provider_id=provider_id,
        location_id=location_id
    )
    return stats
