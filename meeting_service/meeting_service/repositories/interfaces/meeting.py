"""Meeting repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from meeting_service.core.enums import EmployeeLevel, MeetingType
from meeting_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    from meeting_service.models import Meeting


class IMeetingRepository(BaseRepository["Meeting", int]):
    """Meeting repository interface with meeting-specific queries."""

    @abstractmethod
    async def find_meetings(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        meeting_type: MeetingType | None = None,
        department: str | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
        is_mandatory: bool | None = None,
    ) -> tuple[Sequence["Meeting"], int]:
        """Find meetings with filtering and return results with total count."""
