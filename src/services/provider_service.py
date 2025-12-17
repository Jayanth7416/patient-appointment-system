"""Provider Service"""

from datetime import date
from typing import Optional, List
import structlog

from src.models.provider import Provider, ProviderSearch, Specialty, Location, WorkingHours
from src.services.availability_service import AvailabilityService

logger = structlog.get_logger()


class ProviderService:
    """Provider management service"""

    def __init__(self):
        self.availability_service = AvailabilityService()
        self.providers = self._load_sample_providers()
        self.locations = self._load_sample_locations()

    def _load_sample_providers(self) -> dict:
        """Load sample provider data"""
        from datetime import time

        return {
            "prov-001": Provider(
                id="prov-001",
                first_name="Sarah",
                last_name="Johnson",
                title="Dr.",
                specialty=Specialty.PRIMARY_CARE,
                credentials=["MD", "FACP"],
                bio="Board-certified internist with 15 years of experience.",
                locations=[],
                working_hours=[
                    WorkingHours(day="monday", start_time=time(9, 0), end_time=time(17, 0)),
                    WorkingHours(day="tuesday", start_time=time(9, 0), end_time=time(17, 0)),
                    WorkingHours(day="wednesday", start_time=time(9, 0), end_time=time(17, 0)),
                    WorkingHours(day="thursday", start_time=time(9, 0), end_time=time(17, 0)),
                    WorkingHours(day="friday", start_time=time(9, 0), end_time=time(14, 0)),
                ],
                accepting_new_patients=True,
                languages=["English", "Spanish"]
            ),
            "prov-002": Provider(
                id="prov-002",
                first_name="Michael",
                last_name="Chen",
                title="Dr.",
                specialty=Specialty.CARDIOLOGY,
                credentials=["MD", "FACC"],
                bio="Specialist in cardiovascular disease and preventive cardiology.",
                locations=[],
                working_hours=[
                    WorkingHours(day="monday", start_time=time(8, 0), end_time=time(16, 0)),
                    WorkingHours(day="wednesday", start_time=time(8, 0), end_time=time(16, 0)),
                    WorkingHours(day="friday", start_time=time(8, 0), end_time=time(12, 0)),
                ],
                accepting_new_patients=True,
                languages=["English", "Mandarin"]
            ),
        }

    def _load_sample_locations(self) -> List[Location]:
        """Load sample locations"""
        return [
            Location(
                id="loc-001",
                name="Downtown Clinic",
                address="123 Main Street",
                city="New York",
                state="NY",
                zip_code="10001",
                phone="(212) 555-0100"
            ),
            Location(
                id="loc-002",
                name="Eastside Medical Center",
                address="456 East Avenue",
                city="New York",
                state="NY",
                zip_code="10022",
                phone="(212) 555-0200"
            ),
        ]

    async def search_providers(self, search: ProviderSearch) -> List[Provider]:
        """Search providers with filters"""
        results = list(self.providers.values())

        if search.specialty:
            results = [p for p in results if p.specialty == search.specialty]

        if search.name:
            name_lower = search.name.lower()
            results = [
                p for p in results
                if name_lower in p.first_name.lower()
                or name_lower in p.last_name.lower()
            ]

        if search.accepting_new_patients:
            results = [p for p in results if p.accepting_new_patients]

        return results[search.offset:search.offset + search.limit]

    async def get_provider(self, provider_id: str) -> Optional[Provider]:
        """Get provider by ID"""
        return self.providers.get(provider_id)

    async def get_availability(
        self,
        provider_id: str,
        start_date: date,
        end_date: date,
        appointment_type: Optional[str] = None
    ):
        """Get provider availability"""
        from src.models.availability import AvailabilitySearch

        search = AvailabilitySearch(
            provider_id=provider_id,
            start_date=start_date,
            end_date=end_date,
            appointment_type=appointment_type,
            limit=100
        )

        slots = await self.availability_service.search_slots(search)

        # Group by date
        by_date = {}
        for slot in slots:
            date_str = slot.date.isoformat()
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(slot)

        return {
            "provider_id": provider_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "availability": by_date
        }

    async def get_schedule(self, provider_id: str, date: date):
        """Get provider schedule for a date"""
        # Would return full schedule including booked and available slots
        return {
            "provider_id": provider_id,
            "date": date.isoformat(),
            "schedule": []
        }

    async def list_locations(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None
    ) -> List[Location]:
        """List locations with filters"""
        results = self.locations

        if city:
            results = [l for l in results if l.city.lower() == city.lower()]
        if state:
            results = [l for l in results if l.state.lower() == state.lower()]
        if zip_code:
            results = [l for l in results if l.zip_code == zip_code]

        return results
