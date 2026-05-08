"""Mentor assignment history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from auth_service.models import MentorAssignmentHistory
from auth_service.repositories.interfaces.base import BaseRepository


class IMentorAssignmentHistoryRepository(BaseRepository["MentorAssignmentHistory", int]):
    """Mentor assignment history repository interface."""

    @abstractmethod
    async def create(self, entity: MentorAssignmentHistory) -> MentorAssignmentHistory:
        """Create mentor assignment history entry."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MentorAssignmentHistory]:
        """Get mentor assignment history for a user with optional date filtering."""

    @abstractmethod
    async def get_by_mentor_id(
        self,
        mentor_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[MentorAssignmentHistory]:
        """Get mentor assignment history for a mentor with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[MentorAssignmentHistory], int]:
        """Get all mentor assignment history with filtering and pagination."""

    @abstractmethod
    async def delete_by_user_id(self, user_id: int) -> int:
        """Delete all mentor assignment history records for a user. Returns number of deleted records."""

    @abstractmethod
    async def delete_by_mentor_id(self, mentor_id: int) -> int:
        """Delete all mentor assignment history records for a mentor. Returns number of deleted records."""

    @abstractmethod
    async def nullify_changed_by(self, user_id: int) -> int:
        """Set changed_by to NULL for all records where a user is the changer. Returns number of updated records."""
