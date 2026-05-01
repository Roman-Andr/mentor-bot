"""Task completion history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from checklists_service.models import TaskCompletionHistory
from checklists_service.repositories.interfaces.base import BaseRepository


class ITaskCompletionHistoryRepository(BaseRepository["TaskCompletionHistory", int]):
    """Task completion history repository interface."""

    @abstractmethod
    async def create(self, entity: TaskCompletionHistory) -> TaskCompletionHistory:
        """Create task completion history entry."""

    @abstractmethod
    async def get_by_task_id(
        self,
        task_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[TaskCompletionHistory]:
        """Get task completion history for a task with optional date filtering."""

    @abstractmethod
    async def get_by_checklist_id(
        self,
        checklist_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[TaskCompletionHistory]:
        """Get task completion history for a checklist with optional date filtering."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[TaskCompletionHistory]:
        """Get task completion history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[TaskCompletionHistory], int]:
        """Get all task completion history with filtering and pagination."""
