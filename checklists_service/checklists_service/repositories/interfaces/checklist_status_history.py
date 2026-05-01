"""Checklist status history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from checklists_service.models import ChecklistStatusHistory
from checklists_service.repositories.interfaces.base import BaseRepository


class IChecklistStatusHistoryRepository(BaseRepository["ChecklistStatusHistory", int]):
    """Checklist status history repository interface."""

    @abstractmethod
    async def create(self, entity: ChecklistStatusHistory) -> ChecklistStatusHistory:
        """Create checklist status history entry."""

    @abstractmethod
    async def get_by_checklist_id(
        self,
        checklist_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ChecklistStatusHistory]:
        """Get checklist status history for a checklist with optional date filtering."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[ChecklistStatusHistory]:
        """Get checklist status history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ChecklistStatusHistory], int]:
        """Get all checklist status history with filtering and pagination."""
