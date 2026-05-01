"""Mentor intervention history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from escalation_service.models import MentorInterventionHistory
from escalation_service.repositories.interfaces.base import BaseRepository


class IMentorInterventionHistoryRepository(BaseRepository["MentorInterventionHistory", int]):
    """Mentor intervention history repository interface."""

    @abstractmethod
    async def create(self, entity: MentorInterventionHistory) -> MentorInterventionHistory:
        """Create mentor intervention history entry."""

    @abstractmethod
    async def get_by_escalation_id(
        self,
        escalation_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MentorInterventionHistory]:
        """Get mentor intervention history for an escalation with optional date filtering."""

    @abstractmethod
    async def get_by_mentor_id(
        self,
        mentor_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MentorInterventionHistory]:
        """Get mentor intervention history for a mentor with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[MentorInterventionHistory], int]:
        """Get all mentor intervention history with filtering and pagination."""
