"""Password change history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from auth_service.models import PasswordChangeHistory
from auth_service.repositories.interfaces.base import BaseRepository


class IPasswordChangeHistoryRepository(BaseRepository["PasswordChangeHistory", int]):
    """Password change history repository interface."""

    @abstractmethod
    async def create(self, entity: PasswordChangeHistory) -> PasswordChangeHistory:
        """Create password change history entry."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[PasswordChangeHistory]:
        """Get password change history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[PasswordChangeHistory], int]:
        """Get all password change history with filtering and pagination."""
