"""Waitlist Service"""

import uuid
from datetime import date, datetime
from typing import Optional, List
import structlog

from src.models.waitlist import WaitlistEntry, WaitlistRequest, WaitlistStats

logger = structlog.get_logger()


class WaitlistService:
    """Waitlist management service"""

    def __init__(self):
        self.entries: dict = {}

    async def add_to_waitlist(self, request: WaitlistRequest) -> WaitlistEntry:
        """Add patient to waitlist"""
        entry_id = f"wl-{uuid.uuid4().hex[:12]}"

        # Calculate position
        existing = [
            e for e in self.entries.values()
            if e.provider_id == request.provider_id
            and e.status == "waiting"
        ]
        position = len(existing) + 1

        entry = WaitlistEntry(
            id=entry_id,
            patient_id=request.patient_id,
            provider_id=request.provider_id,
            location_id=request.location_id,
            preferred_dates=request.preferred_dates,
            preferred_time_of_day=request.preferred_time_of_day,
            appointment_type=request.appointment_type,
            urgency=request.urgency,
            position=position,
            created_at=datetime.utcnow()
        )

        self.entries[entry_id] = entry

        logger.info(
            "waitlist_entry_created",
            entry_id=entry_id,
            position=position
        )

        return entry

    async def get_entry(self, entry_id: str) -> Optional[WaitlistEntry]:
        """Get waitlist entry"""
        return self.entries.get(entry_id)

    async def remove_from_waitlist(self, entry_id: str):
        """Remove from waitlist"""
        entry = self.entries.get(entry_id)
        if not entry:
            raise ValueError("Waitlist entry not found")

        entry.status = "removed"

        logger.info("waitlist_entry_removed", entry_id=entry_id)

    async def get_patient_entries(self, patient_id: str) -> List[WaitlistEntry]:
        """Get all waitlist entries for a patient"""
        return [
            e for e in self.entries.values()
            if e.patient_id == patient_id
            and e.status == "waiting"
        ]

    async def get_provider_waitlist(
        self,
        provider_id: str,
        date: Optional[date] = None,
        limit: int = 50
    ) -> List[WaitlistEntry]:
        """Get waitlist for a provider"""
        results = [
            e for e in self.entries.values()
            if e.provider_id == provider_id
            and e.status == "waiting"
        ]

        results.sort(key=lambda e: e.position)

        return results[:limit]

    async def notify_patient(self, entry_id: str) -> dict:
        """Notify patient of available slot"""
        entry = self.entries.get(entry_id)
        if not entry:
            raise ValueError("Waitlist entry not found")

        entry.status = "notified"
        entry.notified_at = datetime.utcnow()

        logger.info("waitlist_patient_notified", entry_id=entry_id)

        return {
            "entry_id": entry_id,
            "status": "notified",
            "notified_at": entry.notified_at.isoformat()
        }

    async def get_stats(
        self,
        provider_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> WaitlistStats:
        """Get waitlist statistics"""
        entries = list(self.entries.values())

        if provider_id:
            entries = [e for e in entries if e.provider_id == provider_id]
        if location_id:
            entries = [e for e in entries if e.location_id == location_id]

        waiting = [e for e in entries if e.status == "waiting"]
        notified = [e for e in entries if e.status == "notified"]
        booked = [e for e in entries if e.status == "booked"]

        total = len(entries)
        converted = len(booked)

        return WaitlistStats(
            total_entries=total,
            waiting=len(waiting),
            notified=len(notified),
            converted=converted,
            average_wait_days=0,
            conversion_rate=converted / total if total > 0 else 0
        )
