"""Category change history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from knowledge_service.models import CategoryChangeHistory
from knowledge_service.repositories.interfaces.base import BaseRepository


class ICategoryChangeHistoryRepository(BaseRepository["CategoryChangeHistory", int]):
    """Category change history repository interface."""

    @abstractmethod
    async def create(self, entity: CategoryChangeHistory) -> CategoryChangeHistory:
        """Create category change history entry."""

    @abstractmethod
    async def get_by_category_id(
        self,
        category_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[CategoryChangeHistory]:
        """Get category change history for a category with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[CategoryChangeHistory], int]:
        """Get all category change history with filtering and pagination."""
