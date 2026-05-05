"""Tests for search analytics API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from knowledge_service.api.endpoints.search_analytics import (
    cleanup_search_history,
    get_search_by_department,
    get_search_summary,
    get_search_timeseries,
    get_top_queries,
    get_zero_results_queries,
)


@pytest.fixture
def mock_search_history_repo():
    """Create a mock search history repository."""
    repo = MagicMock()
    repo.get_top_queries = AsyncMock()
    repo.get_zero_results_queries = AsyncMock()
    repo.get_by_department = AsyncMock()
    repo.get_search_timeseries = AsyncMock()
    repo.get_search_summary = AsyncMock()
    return repo


@pytest.fixture
def mock_hr_user():
    """Create a mock HR user."""
    user = MagicMock()
    user.has_role = MagicMock(side_effect=lambda roles: "HR" in roles)
    return user


@pytest.fixture
def mock_admin_user():
    """Create a mock Admin user."""
    user = MagicMock()
    user.has_role = MagicMock(side_effect=lambda roles: "ADMIN" in roles)
    return user


@pytest.fixture
def mock_regular_user():
    """Create a mock regular user."""
    user = MagicMock()
    user.has_role = MagicMock(return_value=False)
    return user


class TestGetTopQueries:
    """Test get top queries endpoint."""

    async def test_get_top_queries_success(self, mock_hr_user, mock_search_history_repo):
        """Test getting top queries successfully."""
        mock_search_history_repo.get_top_queries.return_value = [
            {"query": "test query", "count": 10, "avg_results_count": 5.0, "zero_results_count": 2}
        ]

        result = await get_top_queries(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=None,
            to_date=None,
            limit=20,
            department_id=None,
        )

        assert len(result) == 1
        assert result[0].query == "test query"
        assert result[0].count == 10

    async def test_get_top_queries_with_filters(self, mock_hr_user, mock_search_history_repo):
        """Test getting top queries with date and department filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_search_history_repo.get_top_queries.return_value = []

        result = await get_top_queries(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=from_date,
            to_date=to_date,
            limit=10,
            department_id=1,
        )

        mock_search_history_repo.get_top_queries.assert_called_once_with(
            from_date=from_date, to_date=to_date, limit=10, department_id=1
        )

    async def test_get_top_queries_non_hr_denied(self, mock_regular_user, mock_search_history_repo):
        """Test non-HR user is denied access."""
        with pytest.raises(HTTPException) as exc_info:
            await get_top_queries(
                current_user=mock_regular_user,
                search_history_repo=mock_search_history_repo,
                from_date=None,
                to_date=None,
                limit=20,
                department_id=None,
            )

        assert exc_info.value.status_code == 403
        assert "HR access required" in exc_info.value.detail


class TestGetZeroResultsQueries:
    """Test get zero results queries endpoint."""

    async def test_get_zero_results_queries_success(self, mock_hr_user, mock_search_history_repo):
        """Test getting zero results queries successfully."""
        mock_search_history_repo.get_zero_results_queries.return_value = [
            {"query": "no results", "count": 5, "last_searched_at": datetime.now(UTC)}
        ]

        result = await get_zero_results_queries(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=None,
            to_date=None,
            limit=20,
            department_id=None,
        )

        assert len(result) == 1
        assert result[0].query == "no results"

    async def test_get_zero_results_queries_with_filters(self, mock_hr_user, mock_search_history_repo):
        """Test getting zero results queries with filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        mock_search_history_repo.get_zero_results_queries.return_value = []

        result = await get_zero_results_queries(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=from_date,
            to_date=None,
            limit=10,
            department_id=1,
        )

        mock_search_history_repo.get_zero_results_queries.assert_called_once_with(
            from_date=from_date, to_date=None, limit=10, department_id=1
        )

    async def test_get_zero_results_queries_non_hr_denied(self, mock_regular_user, mock_search_history_repo):
        """Test non-HR user is denied access."""
        with pytest.raises(HTTPException) as exc_info:
            await get_zero_results_queries(
                current_user=mock_regular_user,
                search_history_repo=mock_search_history_repo,
                from_date=None,
                to_date=None,
                limit=20,
                department_id=None,
            )

        assert exc_info.value.status_code == 403


class TestGetSearchByDepartment:
    """Test get search by department endpoint."""

    async def test_get_search_by_department_success(self, mock_hr_user, mock_search_history_repo):
        """Test getting search stats by department successfully."""
        mock_search_history_repo.get_by_department.return_value = [
            {"department_id": 1, "department_name": "Engineering", "search_count": 100, "unique_users": 50}
        ]

        result = await get_search_by_department(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=None,
            to_date=None,
        )

        assert len(result) == 1
        assert result[0].department_name == "Engineering"

    async def test_get_search_by_department_with_date_filters(self, mock_hr_user, mock_search_history_repo):
        """Test getting search stats with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_search_history_repo.get_by_department.return_value = []
        mock_request = MagicMock()
        mock_request.headers.get.return_value = ""

        result = await get_search_by_department(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=from_date,
            to_date=to_date,
            request=mock_request,
        )

        mock_search_history_repo.get_by_department.assert_called_once_with(
            from_date=from_date, to_date=to_date, token=""
        )

    async def test_get_search_by_department_non_hr_denied(self, mock_regular_user, mock_search_history_repo):
        """Test non-HR user is denied access."""
        mock_request = MagicMock()
        with pytest.raises(HTTPException) as exc_info:
            await get_search_by_department(
                current_user=mock_regular_user,
                search_history_repo=mock_search_history_repo,
                from_date=None,
                to_date=None,
                request=mock_request,
            )

        assert exc_info.value.status_code == 403


class TestGetSearchTimeseries:
    """Test get search timeseries endpoint."""

    async def test_get_search_timeseries_success(self, mock_hr_user, mock_search_history_repo):
        """Test getting search timeseries successfully."""
        mock_search_history_repo.get_search_timeseries.return_value = [
            {"bucket": "2024-01-01", "search_count": 10, "unique_users": 5}
        ]

        result = await get_search_timeseries(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=None,
            to_date=None,
            granularity="day",
        )

        assert len(result) == 1
        assert result[0].search_count == 10

    async def test_get_search_timeseries_week_granularity(self, mock_hr_user, mock_search_history_repo):
        """Test getting search timeseries with week granularity."""
        mock_search_history_repo.get_search_timeseries.return_value = []

        result = await get_search_timeseries(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=None,
            to_date=None,
            granularity="week",
        )

        mock_search_history_repo.get_search_timeseries.assert_called_once_with(
            from_date=None, to_date=None, granularity="week"
        )

    async def test_get_search_timeseries_with_date_filters(self, mock_hr_user, mock_search_history_repo):
        """Test getting search timeseries with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        mock_search_history_repo.get_search_timeseries.return_value = []

        result = await get_search_timeseries(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=from_date,
            to_date=None,
            granularity="day",
        )

        mock_search_history_repo.get_search_timeseries.assert_called_once_with(
            from_date=from_date, to_date=None, granularity="day"
        )

    async def test_get_search_timeseries_non_hr_denied(self, mock_regular_user, mock_search_history_repo):
        """Test non-HR user is denied access."""
        with pytest.raises(HTTPException) as exc_info:
            await get_search_timeseries(
                current_user=mock_regular_user,
                search_history_repo=mock_search_history_repo,
                from_date=None,
                to_date=None,
                granularity="day",
            )

        assert exc_info.value.status_code == 403


class TestGetSearchSummary:
    """Test get search summary endpoint."""

    async def test_get_search_summary_success(self, mock_hr_user, mock_search_history_repo):
        """Test getting search summary successfully."""
        mock_search_history_repo.get_search_summary.return_value = {
            "total_searches": 1000,
            "unique_users": 100,
            "unique_queries": 500,
            "avg_results_per_search": 8.5,
            "zero_results_percentage": 5.0,
        }

        result = await get_search_summary(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=None,
            to_date=None,
        )

        assert result.total_searches == 1000
        assert result.unique_users == 100

    async def test_get_search_summary_with_date_filters(self, mock_hr_user, mock_search_history_repo):
        """Test getting search summary with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        mock_search_history_repo.get_search_summary.return_value = {
            "total_searches": 500,
            "unique_users": 50,
            "unique_queries": 250,
            "avg_results_per_search": 8.0,
            "zero_results_percentage": 4.0,
        }

        result = await get_search_summary(
            current_user=mock_hr_user,
            search_history_repo=mock_search_history_repo,
            from_date=from_date,
            to_date=None,
        )

        mock_search_history_repo.get_search_summary.assert_called_once_with(from_date=from_date, to_date=None)

    async def test_get_search_summary_non_hr_denied(self, mock_regular_user, mock_search_history_repo):
        """Test non-HR user is denied access."""
        with pytest.raises(HTTPException) as exc_info:
            await get_search_summary(
                current_user=mock_regular_user,
                search_history_repo=mock_search_history_repo,
                from_date=None,
                to_date=None,
            )

        assert exc_info.value.status_code == 403


class TestCleanupSearchHistory:
    """Test cleanup search history endpoint."""

    async def test_cleanup_search_history_admin_success(self, mock_admin_user):
        """Test admin can trigger cleanup successfully."""
        from unittest.mock import AsyncMock, patch

        with patch(
            "knowledge_service.api.endpoints.search_analytics.cleanup_old_search_history", new_callable=AsyncMock
        ) as mock_cleanup:
            mock_cleanup.return_value = 100

            result = await cleanup_search_history(current_user=mock_admin_user)

            assert "Cleaned up 100" in result["message"]

    async def test_cleanup_search_history_non_admin_denied(self, mock_regular_user):
        """Test non-admin user is denied access."""
        with pytest.raises(HTTPException) as exc_info:
            await cleanup_search_history(current_user=mock_regular_user)

        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail

    async def test_cleanup_search_history_hr_denied(self, mock_hr_user):
        """Test HR user is denied access (admin only)."""
        with pytest.raises(HTTPException) as exc_info:
            await cleanup_search_history(current_user=mock_hr_user)

        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail
