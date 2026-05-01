"""Meeting status change history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from meeting_service.models import MeetingStatusChangeHistory
from meeting_service.repositories.interfaces.base import BaseRepository


class IMeetingStatusChangeHistoryRepository(BaseRepository["MeetingStatusChangeHistory", int]):
    """Meeting status change history repository interface."""

    @abstractmethod
    async def create(self, entity: MeetingStatusChangeHistory) -> MeetingStatusChangeHistory:
        """Create meeting status change history entry."""

    @abstractmethod
    async def get_by_meeting_id(
        self,
        meeting_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MeetingStatusChangeHistory]:
        """Get meeting status change history for a meeting with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[MeetingStatusChangeHistory], int]:
        """Get all meeting status change history with filtering and pagination."""
