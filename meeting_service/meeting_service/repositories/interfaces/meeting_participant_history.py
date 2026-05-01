"""Meeting participant history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from meeting_service.models import MeetingParticipantHistory
from meeting_service.repositories.interfaces.base import BaseRepository


class IMeetingParticipantHistoryRepository(BaseRepository["MeetingParticipantHistory", int]):
    """Meeting participant history repository interface."""

    @abstractmethod
    async def create(self, entity: MeetingParticipantHistory) -> MeetingParticipantHistory:
        """Create meeting participant history entry."""

    @abstractmethod
    async def get_by_meeting_id(
        self,
        meeting_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MeetingParticipantHistory]:
        """Get meeting participant history for a meeting with optional date filtering."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MeetingParticipantHistory]:
        """Get meeting participant history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[MeetingParticipantHistory], int]:
        """Get all meeting participant history with filtering and pagination."""
