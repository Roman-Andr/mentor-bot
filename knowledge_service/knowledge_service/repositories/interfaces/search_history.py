"""SearchHistory repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Any

from knowledge_service.models import SearchHistory
from knowledge_service.repositories.interfaces.base import BaseRepository


class ISearchHistoryRepository(BaseRepository["SearchHistory", int]):
    """SearchHistory repository interface with specific queries."""

    @abstractmethod
    async def record_search(
        self,
        user_id: int,
        query: str,
        results_count: int,
        filters: dict,
        department_id: int | None = None,
    ) -> SearchHistory:
        """Record a search query in history."""

    @abstractmethod
    async def find_by_user(
        self, user_id: int, *, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[SearchHistory], int]:
        """Get user's search history with pagination."""

    @abstractmethod
    async def clear_user_history(self, user_id: int) -> int:
        """Clear all search history for a user, return count deleted."""

    @abstractmethod
    async def get_suggestions(self, query: str, department_id: int | None = None, limit: int = 10) -> Sequence[str]:
        """Get search suggestions from recent search history."""

    @abstractmethod
    async def get_popular_searches(self, department_id: int | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Get popular searches in the last 7 days."""

    @abstractmethod
    async def get_search_stats(self) -> dict[str, Any]:
        """Get comprehensive search statistics."""
