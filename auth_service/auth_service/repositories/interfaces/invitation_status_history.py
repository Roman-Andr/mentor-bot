"""Invitation status history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from auth_service.models import InvitationStatusHistory
from auth_service.repositories.interfaces.base import BaseRepository


class IInvitationStatusHistoryRepository(BaseRepository["InvitationStatusHistory", int]):
    """Invitation status history repository interface."""

    @abstractmethod
    async def create(self, entity: InvitationStatusHistory) -> InvitationStatusHistory:
        """Create invitation status history entry."""

    @abstractmethod
    async def get_by_invitation_id(
        self,
        invitation_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[InvitationStatusHistory]:
        """Get invitation status history for an invitation with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[InvitationStatusHistory], int]:
        """Get all invitation status history with filtering and pagination."""
