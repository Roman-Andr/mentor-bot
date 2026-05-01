"""Role change history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from auth_service.models import RoleChangeHistory
from auth_service.repositories.interfaces.base import BaseRepository


class IRoleChangeHistoryRepository(BaseRepository["RoleChangeHistory", int]):
    """Role change history repository interface."""

    @abstractmethod
    async def create(self, entity: RoleChangeHistory) -> RoleChangeHistory:
        """Create role change history entry."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[RoleChangeHistory]:
        """Get role change history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[RoleChangeHistory], int]:
        """Get all role change history with filtering and pagination."""
