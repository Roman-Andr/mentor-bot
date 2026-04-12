"""Checklist repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Any

from checklists_service.core.enums import ChecklistStatus
from checklists_service.models import Checklist
from checklists_service.repositories.interfaces.base import BaseRepository


class IChecklistRepository(BaseRepository["Checklist", int]):
    """Checklist repository interface with checklist-specific queries."""

    @abstractmethod
    async def find_checklists(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
        status: ChecklistStatus | None = None,
        department_id: int | None = None,
        search: str | None = None,
        overdue_only: bool = False,
    ) -> tuple[Sequence[Checklist], int]:
        """Find checklists with filtering and return results with total count."""

    @abstractmethod
    async def get_active_by_user(self, user_id: int) -> Checklist | None:
        """Get active (non-completed) checklist for a user."""

    @abstractmethod
    async def get_progress(self, checklist_id: int) -> dict[str, Any]:
        """Get detailed progress information for checklist."""

    @abstractmethod
    async def get_statistics(
        self,
        user_id: int | None = None,
        department_id: int | None = None,
    ) -> dict[str, Any]:
        """Get checklist statistics."""

    @abstractmethod
    async def recalculate_progress(self, checklist_id: int) -> None:
        """Recalculate checklist progress based on task completion."""

    @abstractmethod
    async def get_by_user_and_template(self, user_id: int, template_id: int) -> Checklist | None:
        """Get checklist by user and template ID."""

    @abstractmethod
    async def get_monthly_stats(self, months: int = 6) -> list[dict[str, Any]]:
        """Get monthly statistics for the last N months."""

    @abstractmethod
    async def get_completion_time_distribution(self) -> list[dict[str, Any]]:
        """Get completion time distribution (in days)."""
