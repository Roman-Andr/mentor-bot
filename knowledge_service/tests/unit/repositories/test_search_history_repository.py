"""Tests for SearchHistory repository implementation."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import SearchHistory
from knowledge_service.repositories.implementations.search_history import SearchHistoryRepository


class TestSearchHistoryRepository:
    """Test SearchHistory repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.delete = AsyncMock()
        return session

    @pytest.fixture
    def sample_search_history(self):
        """Create a sample search history entry."""
        return SearchHistory(
            id=1,
            user_id=1,
            query="test query",
            filters={"category": "test"},
            results_count=5,
            department_id=1,
            created_at=datetime.now(UTC),
        )

    @pytest.fixture
    def sample_search_histories(self):
        """Create sample search history entries."""
        return [
            SearchHistory(
                id=1,
                user_id=1,
                query="query 1",
                filters={},
                results_count=3,
                department_id=1,
                created_at=datetime.now(UTC) - timedelta(hours=1),
            ),
            SearchHistory(
                id=2,
                user_id=1,
                query="query 2",
                filters={},
                results_count=5,
                department_id=1,
                created_at=datetime.now(UTC),
            ),
        ]

    async def test_record_search(self, mock_session, sample_search_history):
        """Test recording a search query."""
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        repo = SearchHistoryRepository(mock_session)

        # Create a new search history entry
        new_entry = SearchHistory(
            id=2,
            user_id=1,
            query="new search",
            filters={"tag": "test"},
            results_count=10,
            department_id=1,
            created_at=datetime.now(UTC),
        )

        # Mock the base repository create method behavior
        with MagicMock() as mock_create:
            mock_create.return_value = new_entry
            mock_session.add(new_entry)

        result = await repo.record_search(
            user_id=1,
            query="new search",
            results_count=10,
            filters={"tag": "test"},
            department_id=1,
        )

        assert result is not None
        assert result.user_id == 1
        assert result.query == "new search"

    async def test_record_search_without_department(self, mock_session):
        """Test recording a search without department."""
        repo = SearchHistoryRepository(mock_session)

        result = await repo.record_search(
            user_id=1,
            query="search query",
            results_count=5,
            filters={},
            department_id=None,
        )

        assert result is not None
        assert result.department_id is None

    async def test_find_by_user(self, mock_session, sample_search_histories):
        """Test finding search history by user."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_search_histories
        mock_result.scalar_one.return_value = 2
        mock_session.execute.return_value = mock_result

        repo = SearchHistoryRepository(mock_session)
        result, total = await repo.find_by_user(1)

        assert len(result) == 2
        assert total == 2

    async def test_find_by_user_pagination(self, mock_session, sample_search_histories):
        """Test finding search history with pagination."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_search_histories[0]]
        mock_result.scalar_one.return_value = 2
        mock_session.execute.return_value = mock_result

        repo = SearchHistoryRepository(mock_session)
        result, total = await repo.find_by_user(1, skip=0, limit=1)

        assert len(result) == 1
        assert total == 2

    async def test_clear_user_history(self, mock_session, sample_search_histories):
        """Test clearing user search history."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_search_histories
        mock_session.execute.return_value = mock_result

        repo = SearchHistoryRepository(mock_session)
        result = await repo.clear_user_history(1)

        assert result == 2
        assert mock_session.delete.call_count == 2
        mock_session.flush.assert_called_once()

    async def test_clear_user_history_empty(self, mock_session):
        """Test clearing empty search history."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        repo = SearchHistoryRepository(mock_session)
        result = await repo.clear_user_history(1)

        assert result == 0
        mock_session.delete.assert_not_called()

    async def test_get_suggestions(self, mock_session):
        """Test getting search suggestions."""
        mock_row1 = MagicMock()
        mock_row1.__getitem__ = MagicMock(return_value="test query")
        mock_row2 = MagicMock()
        mock_row2.__getitem__ = MagicMock(return_value="testing")

        mock_result = MagicMock()
        mock_result.all.return_value = [("test query", 10), ("testing", 5)]
        mock_session.execute.return_value = mock_result

        repo = SearchHistoryRepository(mock_session)
        result = await repo.get_suggestions("test")

        assert len(result) == 2
        assert "test query" in result
        assert "testing" in result

    async def test_get_suggestions_with_department(self, mock_session):
        """Test getting search suggestions with department filter."""
        mock_result = MagicMock()
        mock_result.all.return_value = [("department search", 3)]
        mock_session.execute.return_value = mock_result

        repo = SearchHistoryRepository(mock_session)
        result = await repo.get_suggestions("search", department_id=1)

        assert len(result) == 1

    async def test_get_popular_searches(self, mock_session):
        """Test getting popular searches."""
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("popular query", 15, 8.5),
            ("another query", 10, 5.0),
        ]
        mock_session.execute.return_value = mock_result

        repo = SearchHistoryRepository(mock_session)
        result = await repo.get_popular_searches()

        assert len(result) == 2
        assert result[0]["query"] == "popular query"
        assert result[0]["search_count"] == 15
        assert result[0]["avg_results"] == 8.5

    async def test_get_popular_searches_with_department(self, mock_session):
        """Test getting popular searches with department filter."""
        mock_result = MagicMock()
        mock_result.all.return_value = [("dept query", 5, 3.0)]
        mock_session.execute.return_value = mock_result

        repo = SearchHistoryRepository(mock_session)
        result = await repo.get_popular_searches(department_id=1)

        assert len(result) == 1

    async def test_get_search_stats(self, mock_session):
        """Test getting search statistics."""
        # Total searches
        total_result = MagicMock()
        total_result.scalar_one.return_value = 100

        # Popular queries
        popular_result = MagicMock()
        popular_result.all.return_value = [("query1", 50), ("query2", 30)]

        # No results queries
        no_results_result = MagicMock()
        no_results_result.all.return_value = [("no result query", 5)]

        # Department searches
        dept_result = MagicMock()
        dept_result.all.return_value = [(1, 40), (2, 30)]

        # Avg results
        avg_result = MagicMock()
        avg_result.scalar_one.return_value = 8.5

        # Last 30 days
        days_result = MagicMock()
        days_result.all.return_value = [(datetime.now(UTC).date(), 10)]

        mock_session.execute = AsyncMock(
            side_effect=[
                total_result,
                popular_result,
                no_results_result,
                dept_result,
                avg_result,
                days_result,
            ]
        )

        repo = SearchHistoryRepository(mock_session)
        result = await repo.get_search_stats()

        assert result["total_searches"] == 100
        assert len(result["popular_queries"]) == 2
        assert len(result["no_results_queries"]) == 1
        assert result["searches_by_department"] == {1: 40, 2: 30}
        assert result["avg_results_per_search"] == 8.5
        assert len(result["searches_last_30_days"]) == 1

    async def test_get_search_stats_none_values(self, mock_session):
        """Test getting search stats when values are None."""
        total_result = MagicMock()
        total_result.scalar_one.return_value = None

        popular_result = MagicMock()
        popular_result.all.return_value = []

        no_results_result = MagicMock()
        no_results_result.all.return_value = []

        dept_result = MagicMock()
        dept_result.all.return_value = []

        avg_result = MagicMock()
        avg_result.scalar_one.return_value = None

        days_result = MagicMock()
        days_result.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[
                total_result,
                popular_result,
                no_results_result,
                dept_result,
                avg_result,
                days_result,
            ]
        )

        repo = SearchHistoryRepository(mock_session)
        result = await repo.get_search_stats()

        assert result["total_searches"] == 0
        assert result["avg_results_per_search"] == 0.0
