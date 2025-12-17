"""Availability Service"""

import uuid
from datetime import date, time, datetime, timedelta
from typing import Optional, List, Dict
import structlog

from src.models.availability import (
    TimeSlot,
    AvailabilitySearch,
    DayAvailability,
    CalendarDay,
    SlotHold
)
from src.services.cache_service import CacheService

logger = structlog.get_logger()


class AvailabilityService:
    """
    Availability management service

    Handles slot generation, caching, and hold management
    for high-concurrency booking scenarios.
    """

    def __init__(self):
        self.cache = CacheService()
        self.slots: Dict[str, TimeSlot] = {}
        self.holds: Dict[str, SlotHold] = {}
        self._generate_sample_slots()

    def _generate_sample_slots(self):
        """Generate sample availability for demo"""
        providers = [
            ("prov-001", "Dr. Sarah Johnson", "loc-001", "Downtown Clinic"),
            ("prov-002", "Dr. Michael Chen", "loc-002", "Eastside Medical"),
        ]

        for provider_id, provider_name, location_id, location_name in providers:
            for day_offset in range(14):
                slot_date = date.today() + timedelta(days=day_offset)
                if slot_date.weekday() < 5:  # Weekdays only
                    for hour in [9, 10, 11, 14, 15, 16]:
                        slot_id = f"slot-{uuid.uuid4().hex[:8]}"
                        self.slots[slot_id] = TimeSlot(
                            id=slot_id,
                            provider_id=provider_id,
                            provider_name=provider_name,
                            location_id=location_id,
                            location_name=location_name,
                            date=slot_date,
                            start_time=time(hour, 0),
                            end_time=time(hour, 30),
                            duration_minutes=30,
                            appointment_types=["new_patient", "follow_up"],
                            available=True
                        )

    async def search_slots(
        self,
        search: AvailabilitySearch
    ) -> List[TimeSlot]:
        """Search for available slots"""
        results = []

        for slot in self.slots.values():
            if not slot.available:
                continue
            if search.start_date and slot.date < search.start_date:
                continue
            if search.end_date and slot.date > search.end_date:
                continue
            if search.provider_id and slot.provider_id != search.provider_id:
                continue
            if search.location_id and slot.location_id != search.location_id:
                continue
            if search.appointment_type and search.appointment_type not in slot.appointment_types:
                continue
            if search.time_of_day:
                hour = slot.start_time.hour
                if search.time_of_day == "morning" and hour >= 12:
                    continue
                if search.time_of_day == "afternoon" and (hour < 12 or hour >= 17):
                    continue
                if search.time_of_day == "evening" and hour < 17:
                    continue

            results.append(slot)

        # Sort by date and time
        results.sort(key=lambda s: (s.date, s.start_time))

        return results[:search.limit]

    async def get_next_available(
        self,
        provider_id: Optional[str] = None,
        specialty: Optional[str] = None,
        location_id: Optional[str] = None,
        appointment_type: Optional[str] = None
    ) -> Optional[TimeSlot]:
        """Get next available slot"""
        search = AvailabilitySearch(
            provider_id=provider_id,
            location_id=location_id,
            appointment_type=appointment_type,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            limit=1
        )

        results = await self.search_slots(search)
        return results[0] if results else None

    async def get_calendar(
        self,
        provider_id: str,
        month: int,
        year: int
    ) -> List[CalendarDay]:
        """Get calendar view of availability"""
        import calendar as cal

        _, num_days = cal.monthrange(year, month)
        calendar_days = []

        for day in range(1, num_days + 1):
            day_date = date(year, month, day)
            day_slots = [
                s for s in self.slots.values()
                if s.provider_id == provider_id
                and s.date == day_date
                and s.available
            ]

            calendar_days.append(CalendarDay(
                date=day_date,
                available_slots=len(day_slots),
                has_availability=len(day_slots) > 0
            ))

        return calendar_days

    async def get_slot(self, slot_id: str) -> Optional[TimeSlot]:
        """Get slot by ID"""
        return self.slots.get(slot_id)

    async def is_slot_available(
        self,
        provider_id: str,
        date: date,
        time: time
    ) -> bool:
        """Check if a specific slot is available"""
        for slot in self.slots.values():
            if (slot.provider_id == provider_id
                and slot.date == date
                and slot.start_time == time):
                return slot.available
        return False

    async def mark_slot_booked(
        self,
        provider_id: str,
        date: date,
        time: time
    ):
        """Mark slot as booked"""
        for slot in self.slots.values():
            if (slot.provider_id == provider_id
                and slot.date == date
                and slot.start_time == time):
                slot.available = False
                break

    async def mark_slot_available(
        self,
        provider_id: str,
        date: date,
        time: time
    ):
        """Mark slot as available (after cancellation)"""
        for slot in self.slots.values():
            if (slot.provider_id == provider_id
                and slot.date == date
                and slot.start_time == time):
                slot.available = True
                break

    async def hold_slot(
        self,
        slot_id: str,
        patient_id: str,
        duration_minutes: int = 10
    ) -> SlotHold:
        """Temporarily hold a slot"""
        slot = self.slots.get(slot_id)
        if not slot or not slot.available:
            raise ValueError("Slot not available")

        hold_id = f"hold-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        hold = SlotHold(
            slot_id=slot_id,
            patient_id=patient_id,
            held_at=now,
            expires_at=now + timedelta(minutes=duration_minutes)
        )

        self.holds[hold_id] = hold
        slot.held_by = patient_id
        slot.held_until = hold.expires_at

        logger.info(
            "slot_held",
            slot_id=slot_id,
            patient_id=patient_id,
            expires_at=hold.expires_at
        )

        return hold

    async def release_hold(self, slot_id: str, patient_id: str):
        """Release a held slot"""
        slot = self.slots.get(slot_id)
        if slot and slot.held_by == patient_id:
            slot.held_by = None
            slot.held_until = None

            logger.info("slot_hold_released", slot_id=slot_id)
