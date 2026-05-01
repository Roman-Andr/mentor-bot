"""Tests for knowledge analytics API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from knowledge_service.api.deps import UserInfo
from knowledge_service.api.endpoints.analytics import (
    get_knowledge_summary,
    get_top_articles,
    get_views_by_category,
    get_views_by_tag,
    get_views_timeseries,
)
from knowledge_service.schemas import (
    CategoryStats,
    KnowledgeSummary,
    TagStats,
    TimeseriesPoint,
    TopArticleStats,
)


@pytest.fixture
def mock_uow() -> AsyncMock:
    """Create a mock Unit of Work."""
    from knowledge_service.repositories import SqlAlchemyUnitOfWork

    uow = AsyncMock(spec=SqlAlchemyUnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.article_views = AsyncMock()
    return uow


@pytest.fixture
def mock_hr_user() -> UserInfo:
    """Create a mock HR user."""
    return UserInfo(
        {
            "id": 3,
            "email": "hr@example.com",
            "employee_id": "HR001",
            "role": "HR",
            "is_active": True,
            "is_verified": True,
            "department": {"id": 2, "name": "HR"},
            "position": "HR Manager",
            "level": "SENIOR",
            "first_name": "HR",
            "last_name": "Manager",
            "telegram_id": None,
        }
    )


class TestGetTopArticles:
    """Test GET /analytics/top-articles endpoint."""

    async def test_get_top_articles_success(
        self,
        mock_uow: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful retrieval of top articles."""
        mock_uow.article_views.get_top_articles.return_value = [
            {
                "article_id": 1,
                "title": "Test Article",
                "view_count": 100,
                "unique_viewers": 50,
            }
        ]

        result = await get_top_articles(
            uow=mock_uow,
            _current_user=mock_hr_user,
            from_date=None,
            to_date=None,
            limit=10,
            department_id=None,
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TopArticleStats)
        assert result[0].article_id == 1
        assert result[0].title == "Test Article"
        assert result[0].view_count == 100
        assert result[0].unique_viewers == 50
        mock_uow.article_views.get_top_articles.assert_called_once()

    async def test_get_top_articles_with_date_range(
        self,
        mock_uow: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test retrieval of top articles with date range filter."""
        from_date = datetime(2026, 1, 1, tzinfo=UTC)
        to_date = datetime(2026, 1, 31, tzinfo=UTC)

        await get_top_articles(
            uow=mock_uow,
            _current_user=mock_hr_user,
            from_date=from_date,
            to_date=to_date,
            limit=5,
            department_id=1,
        )

        mock_uow.article_views.get_top_articles.assert_called_once_with(
            from_date=from_date,
            to_date=to_date,
            limit=5,
            department_id=1,
        )


class TestGetViewsTimeseries:
    """Test GET /analytics/views-timeseries endpoint."""

    async def test_get_views_timeseries_success(
        self,
        mock_uow: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful retrieval of views timeseries."""
        mock_uow.article_views.get_timeseries.return_value = [
            {
                "bucket": "2026-01-01T00:00:00",
                "views": 42,
                "unique_viewers": 17,
            }
        ]

        result = await get_views_timeseries(
            uow=mock_uow,
            _current_user=mock_hr_user,
            from_date=None,
            to_date=None,
            granularity="day",
            article_id=None,
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TimeseriesPoint)
        assert result[0].bucket == "2026-01-01T00:00:00"
        assert result[0].views == 42
        assert result[0].unique_viewers == 17
        mock_uow.article_views.get_timeseries.assert_called_once()

    async def test_get_views_timeseries_week_granularity(
        self,
        mock_uow: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test retrieval of views timeseries with weekly granularity."""
        await get_views_timeseries(
            uow=mock_uow,
            _current_user=mock_hr_user,
            from_date=None,
            to_date=None,
            granularity="week",
            article_id=1,
        )

        mock_uow.article_views.get_timeseries.assert_called_once_with(
            from_date=None,
            to_date=None,
            granularity="week",
            article_id=1,
        )


class TestGetViewsByCategory:
    """Test GET /analytics/views-by-category endpoint."""

    async def test_get_views_by_category_success(
        self,
        mock_uow: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful retrieval of views by category."""
        mock_uow.article_views.get_by_category.return_value = [
            {
                "category_id": 1,
                "category_name": "Onboarding",
                "view_count": 200,
            }
        ]

        result = await get_views_by_category(
            uow=mock_uow,
            _current_user=mock_hr_user,
            from_date=None,
            to_date=None,
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], CategoryStats)
        assert result[0].category_id == 1
        assert result[0].category_name == "Onboarding"
        assert result[0].view_count == 200
        mock_uow.article_views.get_by_category.assert_called_once()


class TestGetViewsByTag:
    """Test GET /analytics/views-by-tag endpoint."""

    async def test_get_views_by_tag_success(
        self,
        mock_uow: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful retrieval of views by tag."""
        mock_uow.article_views.get_by_tag.return_value = [
            {
                "tag_id": 1,
                "tag_name": "hr",
                "view_count": 150,
            }
        ]

        result = await get_views_by_tag(
            uow=mock_uow,
            _current_user=mock_hr_user,
            from_date=None,
            to_date=None,
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TagStats)
        assert result[0].tag_id == 1
        assert result[0].tag_name == "hr"
        assert result[0].view_count == 150
        mock_uow.article_views.get_by_tag.assert_called_once()


class TestGetKnowledgeSummary:
    """Test GET /analytics/summary endpoint."""

    async def test_get_knowledge_summary_success(
        self,
        mock_uow: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful retrieval of knowledge summary."""
        mock_uow.article_views.get_summary_stats.return_value = {
            "total_views": 1000,
            "unique_viewers": 500,
            "total_articles": 50,
            "avg_views_per_article": 20.0,
        }

        result = await get_knowledge_summary(
            uow=mock_uow,
            _current_user=mock_hr_user,
            from_date=None,
            to_date=None,
        )

        assert isinstance(result, KnowledgeSummary)
        assert result.total_views == 1000
        assert result.unique_viewers == 500
        assert result.total_articles == 50
        assert result.avg_views_per_article == 20.0
        mock_uow.article_views.get_summary_stats.assert_called_once()

    async def test_get_knowledge_summary_with_date_range(
        self,
        mock_uow: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test retrieval of knowledge summary with date range filter."""
        from_date = datetime(2026, 1, 1, tzinfo=UTC)
        to_date = datetime(2026, 1, 31, tzinfo=UTC)

        mock_uow.article_views.get_summary_stats.return_value = {
            "total_views": 1000,
            "unique_viewers": 500,
            "total_articles": 50,
            "avg_views_per_article": 20.0,
        }

        result = await get_knowledge_summary(
            uow=mock_uow,
            _current_user=mock_hr_user,
            from_date=from_date,
            to_date=to_date,
        )

        mock_uow.article_views.get_summary_stats.assert_called_once_with(
            from_date=from_date,
            to_date=to_date,
        )
