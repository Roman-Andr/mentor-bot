"""Logout history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from auth_service.models import LogoutHistory
from auth_service.repositories.interfaces.base import BaseRepository


class ILogoutHistoryRepository(BaseRepository["LogoutHistory", int]):
    """Logout history repository interface."""

    @abstractmethod
    async def create(self, entity: LogoutHistory) -> LogoutHistory:
        """Create logout history entry."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
    ) -> Sequence[LogoutHistory]:
        """Get logout history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[LogoutHistory], int]:
        """Get all logout history with filtering and pagination."""
