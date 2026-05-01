"""Template change history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from checklists_service.models import TemplateChangeHistory
from checklists_service.repositories.interfaces.base import BaseRepository


class ITemplateChangeHistoryRepository(BaseRepository["TemplateChangeHistory", int]):
    """Template change history repository interface."""

    @abstractmethod
    async def create(self, entity: TemplateChangeHistory) -> TemplateChangeHistory:
        """Create template change history entry."""

    @abstractmethod
    async def get_by_template_id(
        self,
        template_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[TemplateChangeHistory]:
        """Get template change history for a template with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[TemplateChangeHistory], int]:
        """Get all template change history with filtering and pagination."""
