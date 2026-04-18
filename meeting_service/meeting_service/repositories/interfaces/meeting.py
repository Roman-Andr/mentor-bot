"""Meeting repository interface."""

from abc import abstractmethod
from collections.abc import Sequence

from meeting_service.core.enums import EmployeeLevel, MeetingType
from meeting_service.models import Meeting
from meeting_service.repositories.interfaces.base import BaseRepository


class IMeetingRepository(BaseRepository["Meeting", int]):
    """Meeting repository interface with meeting-specific queries."""

    @abstractmethod
    async def find_meetings(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        meeting_type: MeetingType | None = None,
        department_id: int | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
        is_mandatory: bool | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[Sequence[Meeting], int]:
        """Find meetings with filtering and return results with total count."""
