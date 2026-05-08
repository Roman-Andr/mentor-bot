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

    @abstractmethod
    async def delete_by_user_id(self, user_id: int) -> int:
        """Delete all password change history records for a user. Returns number of deleted records."""

    @abstractmethod
    async def nullify_changed_by(self, user_id: int) -> int:
        """Set changed_by to NULL for all records where a user is the changer. Returns number of updated records."""
