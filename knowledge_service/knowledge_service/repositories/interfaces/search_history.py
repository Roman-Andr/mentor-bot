"""SearchHistory repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime
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

    @abstractmethod
    async def get_top_queries(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 20,
        department_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get top search queries with statistics."""

    @abstractmethod
    async def get_zero_results_queries(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 20,
        department_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get queries that returned zero results."""

    @abstractmethod
    async def get_by_department(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Get search statistics grouped by department."""

    @abstractmethod
    async def get_search_timeseries(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        granularity: str = "day",
    ) -> list[dict[str, Any]]:
        """Get search timeseries data with specified granularity."""

    @abstractmethod
    async def get_search_summary(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Get overall search summary statistics."""

    @abstractmethod
    async def delete_old_search_history(self, retention_days: int) -> int:
        """Delete search history entries older than retention period."""
