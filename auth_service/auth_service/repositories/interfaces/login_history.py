"""Login history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from auth_service.models import LoginHistory
from auth_service.repositories.interfaces.base import BaseRepository


class ILoginHistoryRepository(BaseRepository["LoginHistory", int]):
    """Login history repository interface."""

    @abstractmethod
    async def create(self, entity: LoginHistory) -> LoginHistory:
        """Create login history entry."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
    ) -> Sequence[LoginHistory]:
        """Get login history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[LoginHistory], int]:
        """Get all login history with filtering and pagination."""
