"""Tests for search API endpoints."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
from fastapi import HTTPException, status

from knowledge_service.api.endpoints.search import (
    clear_search_history,
    get_search_stats,
    popular_searches,
    search_articles,
    search_history,
    search_suggestions,
)
from knowledge_service.core import SearchSortBy
from knowledge_service.schemas import SearchQuery, SearchResponse

if TYPE_CHECKING:
    from knowledge_service.api.deps import UserInfo

from unittest.mock import AsyncMock


class TestSearchArticles:
    """Test POST /search endpoint."""

    async def test_search_articles_success(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful article search."""
        search_query = SearchQuery(
            query="test search",
            page=1,
            size=10,
        )

        result = await search_articles(
            search_query=search_query,
            search_service=mock_search_service,
            current_user=mock_user,
        )

        assert isinstance(result, SearchResponse)
        assert result.total == 1
        assert result.query == "test search"
        assert result.page == 1
        assert result.size == 10

    async def test_search_articles_with_filters(
        self,
        mock_search_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test search with various filters (admin can specify department_id)."""
        search_query = SearchQuery(
            query="python",
            category_id=1,
            tag_ids=[1, 2],
            department_id=2,  # Admin can search other departments
            position="Developer",
            level="JUNIOR",
            only_published=True,
            sort_by=SearchSortBy.RELEVANCE,
            page=2,
            size=10,
        )

        await search_articles(
            search_query=search_query,
            search_service=mock_search_service,
            current_user=mock_admin_user,
        )

        call_kwargs = mock_search_service.search_articles.call_args[1]
        assert call_kwargs["query"] == "python"
        assert call_kwargs["filters"]["category_id"] == 1
        assert call_kwargs["filters"]["tag_ids"] == [1, 2]
        assert call_kwargs["filters"]["department_id"] == 2  # Admin's requested department
        assert call_kwargs["filters"]["position"] == "Developer"
        assert call_kwargs["filters"]["level"] == "JUNIOR"

    async def test_search_articles_regular_user_cannot_search_other_departments(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test that regular users cannot search other departments."""
        search_query = SearchQuery(
            query="python",
            department_id=999,  # Trying to search another department
            page=1,
            size=10,
        )

        with pytest.raises(HTTPException) as exc_info:
            await search_articles(
                search_query=search_query,
                search_service=mock_search_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    async def test_search_articles_regular_user_department_forced(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test that regular users are forced to their own department."""
        search_query = SearchQuery(
            query="python",
            page=1,
            size=10,
        )

        await search_articles(
            search_query=search_query,
            search_service=mock_search_service,
            current_user=mock_user,
        )

        call_kwargs = mock_search_service.search_articles.call_args[1]
        # Regular user's department_id should be forced, not query's
        assert call_kwargs["filters"]["department_id"] == mock_user.department_id

    async def test_search_articles_user_filters_applied(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test that user filters are automatically applied."""
        search_query = SearchQuery(
            query="test",
            page=1,
            size=10,
        )

        await search_articles(
            search_query=search_query,
            search_service=mock_search_service,
            current_user=mock_user,
        )

        call_kwargs = mock_search_service.search_articles.call_args[1]
        user_filters = call_kwargs["user_filters"]
        assert user_filters["department_id"] == mock_user.department_id
        assert user_filters["position"] == mock_user.position
        assert user_filters["level"] == mock_user.level

    async def test_search_articles_pagination_calculation(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test pagination calculation."""
        mock_search_service.search_articles.return_value = (
            [{"id": 1, "score": 1.0}],
            100,
            [],
        )

        search_query = SearchQuery(
            query="test",
            page=1,
            size=10,
        )

        result = await search_articles(
            search_query=search_query,
            search_service=mock_search_service,
            current_user=mock_user,
        )

        assert result.pages == 10  # 100 results / 10 per page
        assert result.total == 100


class TestSearchSuggestions:
    """Test GET /search/suggest endpoint."""

    async def test_search_suggestions_success(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful search suggestions."""
        mock_search_service.get_search_suggestions.return_value = [
            "python tutorial",
            "python basics",
            "python advanced",
        ]

        result = await search_suggestions(
            query="python",
            search_service=mock_search_service,
            current_user=mock_user,
        )

        assert len(result) == 3
        assert "python tutorial" in result
        mock_search_service.get_search_suggestions.assert_called_once_with(
            query="python",
            department_id=mock_user.department_id,
            limit=10,
        )

    async def test_search_suggestions_with_limit(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test search suggestions with custom limit."""
        await search_suggestions(
            query="test",
            search_service=mock_search_service,
            current_user=mock_user,
            limit=5,
        )

        call_kwargs = mock_search_service.get_search_suggestions.call_args[1]
        assert call_kwargs["limit"] == 5


class TestPopularSearches:
    """Test GET /search/popular endpoint."""

    async def test_popular_searches_success(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful popular searches retrieval."""
        mock_search_service.get_popular_searches.return_value = [
            {"query": "python", "count": 50},
            {"query": "django", "count": 30},
        ]

        result = await popular_searches(
            search_service=mock_search_service,
            current_user=mock_user,
        )

        assert len(result) == 2
        assert result[0]["query"] == "python"
        mock_search_service.get_popular_searches.assert_called_once_with(
            department_id=mock_user.department_id,
            limit=10,
        )


class TestSearchHistory:
    """Test GET /search/history endpoint."""

    async def test_search_history_success(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful search history retrieval."""
        mock_history_item = AsyncMock()
        mock_history_item.id = 1
        mock_history_item.query = "python tutorial"
        mock_history_item.results_count = 10
        mock_history_item.created_at = datetime.now(UTC)
        mock_history_item.filters = {"category_id": 1}

        mock_search_service.get_user_search_history.return_value = ([mock_history_item], 1)

        result = await search_history(
            search_service=mock_search_service,
            current_user=mock_user,
        )

        assert len(result) == 1
        assert result[0]["query"] == "python tutorial"
        mock_search_service.get_user_search_history.assert_called_once_with(
            user_id=mock_user.id,
            skip=0,
            limit=50,
        )

    async def test_search_history_with_pagination(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test search history with pagination."""
        await search_history(
            search_service=mock_search_service,
            current_user=mock_user,
            skip=20,
            limit=10,
        )

        call_kwargs = mock_search_service.get_user_search_history.call_args[1]
        assert call_kwargs["skip"] == 20
        assert call_kwargs["limit"] == 10


class TestClearSearchHistory:
    """Test DELETE /search/history endpoint."""

    async def test_clear_search_history_success(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test successful search history clearing."""
        result = await clear_search_history(
            search_service=mock_search_service,
            current_user=mock_user,
        )

        assert result["message"] == "Search history cleared"
        mock_search_service.clear_user_search_history.assert_called_once_with(mock_user.id)


class TestGetSearchStats:
    """Test GET /search/stats endpoint."""

    async def test_get_search_stats_as_admin(
        self,
        mock_search_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test admin can access search stats."""
        mock_search_service.get_search_stats.return_value = {
            "total_searches": 1000,
            "popular_queries": [{"query": "python", "count": 50}],
            "no_results_queries": [],
            "searches_by_department": {"1": 100},
            "avg_results_per_search": 8.5,
            "searches_last_30_days": [{"date": "2024-01-01", "count": 30}],
        }

        result = await get_search_stats(
            search_service=mock_search_service,
            current_user=mock_admin_user,
        )

        assert result.total_searches == 1000

    async def test_get_search_stats_as_hr(
        self,
        mock_search_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test HR can access search stats."""
        mock_search_service.get_search_stats.return_value = {
            "total_searches": 500,
            "popular_queries": [{"query": "hr", "count": 20}],
            "no_results_queries": [],
            "searches_by_department": {"1": 50},
            "avg_results_per_search": 7.5,
            "searches_last_30_days": [{"date": "2024-01-01", "count": 15}],
        }

        result = await get_search_stats(
            search_service=mock_search_service,
            current_user=mock_hr_user,
        )

        assert result.total_searches == 500

    async def test_get_search_stats_as_regular_user_denied(
        self,
        mock_search_service: AsyncMock,
        mock_user: UserInfo,
    ) -> None:
        """Test regular user cannot access search stats."""
        with pytest.raises(HTTPException) as exc_info:
            await get_search_stats(
                search_service=mock_search_service,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
