"""Checklist repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from checklists_service.core.enums import ChecklistStatus
from checklists_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    from checklists_service.models import Checklist


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
        department: str | None = None,
        overdue_only: bool = False,
    ) -> tuple[Sequence["Checklist"], int]:
        """Find checklists with filtering and return results with total count."""

    @abstractmethod
    async def get_active_by_user(self, user_id: int) -> "Checklist | None":
        """Get active (non-completed) checklist for a user."""

    @abstractmethod
    async def get_progress(self, checklist_id: int) -> dict[str, Any]:
        """Get detailed progress information for checklist."""

    @abstractmethod
    async def get_statistics(
        self,
        user_id: int | None = None,
        department: str | None = None,
    ) -> dict[str, Any]:
        """Get checklist statistics."""

    @abstractmethod
    async def recalculate_progress(self, checklist_id: int) -> None:
        """Recalculate checklist progress based on task completion."""
