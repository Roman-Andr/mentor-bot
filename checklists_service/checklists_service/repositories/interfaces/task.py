"""Task repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Any

from checklists_service.models import Task
from checklists_service.repositories.interfaces.base import BaseRepository


class ITaskRepository(BaseRepository["Task", int]):
    """Task repository interface with task-specific queries."""

    @abstractmethod
    async def find_by_checklist(
        self,
        checklist_id: int,
        *,
        status: str | None = None,
        category: str | None = None,
        overdue_only: bool = False,
    ) -> Sequence[Task]:
        """Find tasks for a specific checklist with optional filters."""

    @abstractmethod
    async def find_assigned(
        self,
        assignee_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> tuple[Sequence[Task], int]:
        """Find tasks assigned to a specific user."""

    @abstractmethod
    async def get_dependencies(self, task_id: int) -> dict[str, Any]:
        """Get task dependencies and blockers."""

    @abstractmethod
    async def get_incomplete_dependencies(self, task_id: int) -> Sequence[Task]:
        """Get incomplete tasks that this task depends on."""

    @abstractmethod
    async def get_blocked_by(self, task_id: int) -> Sequence[Task]:
        """Get tasks that are blocked by this task."""

    @abstractmethod
    async def count_by_status(self, checklist_id: int) -> dict[str, int]:
        """Count tasks by status for a checklist."""

    @abstractmethod
    async def count_by_category(self, checklist_id: int) -> dict[str, int]:
        """Count tasks by category for a checklist."""

    @abstractmethod
    async def count_overdue(self, checklist_id: int) -> int:
        """Count overdue tasks for a checklist."""

    @abstractmethod
    async def get_blocked_tasks(self, checklist_id: int) -> Sequence[Task]:
        """Get blocked tasks for a checklist."""

    @abstractmethod
    async def find_by_ids(self, task_ids: list[int]) -> Sequence[Task]:
        """Find tasks by a list of IDs."""
