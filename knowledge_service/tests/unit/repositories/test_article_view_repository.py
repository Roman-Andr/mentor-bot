"""Tests for ArticleView repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.models.article_view import ArticleView
from knowledge_service.repositories.implementations.article_view import ArticleViewRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestArticleViewRepository:
    """Test ArticleView repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def sample_article_view(self):
        """Create a sample article view."""
        return ArticleView(
            id=1,
            article_id=1,
            user_id=1,
            viewed_at=datetime.now(UTC),
        )

    async def test_record_view_with_user_id(self, mock_session, sample_article_view):
        """Test recording a view with user_id."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        repo = ArticleViewRepository(mock_session)
        result = await repo.record_view(article_id=1, user_id=1)

        # Verify the view object was created with correct values
        assert isinstance(result, ArticleView)
        assert result.article_id == 1
        assert result.user_id == 1

    async def test_record_view_without_user_id(self, mock_session):
        """Test recording a view without user_id (anonymous view)."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        repo = ArticleViewRepository(mock_session)
        result = await repo.record_view(article_id=2, user_id=None)

        # Verify the view object was created with correct values
        assert isinstance(result, ArticleView)
        assert result.article_id == 2
        assert result.user_id is None

    async def test_get_top_articles_basic(self, mock_session):
        """Test getting top articles by view count."""
        mock_result = MagicMock()
        mock_result.article_id = 1
        mock_result.title = "Test Article"
        mock_result.view_count = 10
        mock_result.unique_viewers = 5

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_top_articles(limit=10)

        assert len(result) == 1
        assert result[0]["article_id"] == 1
        assert result[0]["title"] == "Test Article"
        assert result[0]["view_count"] == 10
        assert result[0]["unique_viewers"] == 5

    async def test_get_top_articles_with_date_filters(self, mock_session):
        """Test getting top articles with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        mock_result = MagicMock()
        mock_result.article_id = 1
        mock_result.title = "Test Article"
        mock_result.view_count = 10
        mock_result.unique_viewers = 5

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_top_articles(from_date=from_date, to_date=to_date, limit=10)

        assert len(result) == 1
        assert result[0]["article_id"] == 1
        assert result[0]["view_count"] == 10
        assert result[0]["unique_viewers"] == 5
        mock_session.execute.assert_called_once()

    async def test_get_top_articles_with_department_filter(self, mock_session):
        """Test getting top articles filtered by department."""
        mock_result = MagicMock()
        mock_result.article_id = 1
        mock_result.title = "Test Article"
        mock_result.view_count = 10
        mock_result.unique_viewers = 5

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_top_articles(department_id=1, limit=10)

        assert len(result) == 1
        assert result[0]["article_id"] == 1
        assert result[0]["title"] == "Test Article"
        assert result[0]["view_count"] == 10
        assert result[0]["unique_viewers"] == 5
        mock_session.execute.assert_called_once()

    async def test_get_timeseries_day_granularity(self, mock_session):
        """Test getting timeseries data with day granularity."""
        mock_result = MagicMock()
        mock_result.bucket = datetime(2024, 1, 1, tzinfo=UTC)
        mock_result.views = 10
        mock_result.unique_viewers = 5

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_timeseries(granularity="day")

        assert len(result) == 1
        assert result[0]["bucket"] == "2024-01-01T00:00:00+00:00"
        assert result[0]["views"] == 10
        assert result[0]["unique_viewers"] == 5

    async def test_get_timeseries_week_granularity(self, mock_session):
        """Test getting timeseries data with week granularity."""
        mock_result = MagicMock()
        mock_result.bucket = datetime(2024, 1, 1, tzinfo=UTC)
        mock_result.views = 10
        mock_result.unique_viewers = 5

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_timeseries(granularity="week")

        assert len(result) == 1
        assert result[0]["bucket"] == "2024-01-01T00:00:00+00:00"
        assert result[0]["views"] == 10
        assert result[0]["unique_viewers"] == 5

    async def test_get_timeseries_with_article_filter(self, mock_session):
        """Test getting timeseries data filtered by article."""
        mock_result = MagicMock()
        mock_result.bucket = datetime(2024, 1, 1, tzinfo=UTC)
        mock_result.views = 10
        mock_result.unique_viewers = 5

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_timeseries(article_id=1, granularity="day")

        assert len(result) == 1
        assert result[0]["bucket"] == "2024-01-01T00:00:00+00:00"
        assert result[0]["views"] == 10
        assert result[0]["unique_viewers"] == 5
        mock_session.execute.assert_called_once()

    async def test_get_timeseries_with_date_filters(self, mock_session):
        """Test getting timeseries data with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        mock_result = MagicMock()
        mock_result.bucket = datetime(2024, 1, 1, tzinfo=UTC)
        mock_result.views = 10
        mock_result.unique_viewers = 5

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_timeseries(from_date=from_date, to_date=to_date, granularity="day")

        assert len(result) == 1
        assert result[0]["bucket"] == "2024-01-01T00:00:00+00:00"
        assert result[0]["views"] == 10
        assert result[0]["unique_viewers"] == 5

    async def test_get_by_category(self, mock_session):
        """Test getting view statistics by category."""
        mock_result = MagicMock()
        mock_result.category_id = 1
        mock_result.category_name = "Test Category"
        mock_result.view_count = 10

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_by_category()

        assert len(result) == 1
        assert result[0]["category_id"] == 1
        assert result[0]["category_name"] == "Test Category"
        assert result[0]["view_count"] == 10

    async def test_get_by_category_with_date_filters(self, mock_session):
        """Test getting category statistics with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        mock_result = MagicMock()
        mock_result.category_id = 1
        mock_result.category_name = "Test Category"
        mock_result.view_count = 10

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_by_category(from_date=from_date, to_date=to_date)

        assert len(result) == 1
        assert result[0]["category_id"] == 1
        assert result[0]["category_name"] == "Test Category"
        assert result[0]["view_count"] == 10

    async def test_get_by_tag(self, mock_session):
        """Test getting view statistics by tag."""
        mock_result = MagicMock()
        mock_result.tag_id = 1
        mock_result.tag_name = "Test Tag"
        mock_result.view_count = 10

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_by_tag()

        assert len(result) == 1
        assert result[0]["tag_id"] == 1
        assert result[0]["tag_name"] == "Test Tag"
        assert result[0]["view_count"] == 10

    async def test_get_by_tag_with_date_filters(self, mock_session):
        """Test getting tag statistics with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        mock_result = MagicMock()
        mock_result.tag_id = 1
        mock_result.tag_name = "Test Tag"
        mock_result.view_count = 10

        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute_result

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_by_tag(from_date=from_date, to_date=to_date)

        assert len(result) == 1
        assert result[0]["tag_id"] == 1
        assert result[0]["tag_name"] == "Test Tag"
        assert result[0]["view_count"] == 10

    async def test_get_summary_stats(self, mock_session):
        """Test getting summary statistics."""
        # Mock total views
        mock_views_result = MagicMock()
        mock_views_result.scalar.return_value = 100

        # Mock unique viewers
        mock_viewers_result = MagicMock()
        mock_viewers_result.scalar.return_value = 50

        # Mock total articles
        mock_articles_result = MagicMock()
        mock_articles_result.scalar.return_value = 20

        # Setup execute to return different results based on call count
        mock_session.execute.side_effect = [mock_views_result, mock_viewers_result, mock_articles_result]

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_summary_stats()

        assert result["total_views"] == 100
        assert result["unique_viewers"] == 50
        assert result["total_articles"] == 20
        assert result["avg_views_per_article"] == 5.0

    async def test_get_summary_stats_with_date_filters(self, mock_session):
        """Test getting summary statistics with date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)

        mock_views_result = MagicMock()
        mock_views_result.scalar.return_value = 100

        mock_viewers_result = MagicMock()
        mock_viewers_result.scalar.return_value = 50

        mock_articles_result = MagicMock()
        mock_articles_result.scalar.return_value = 20

        mock_session.execute.side_effect = [mock_views_result, mock_viewers_result, mock_articles_result]

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_summary_stats(from_date=from_date, to_date=to_date)

        assert result["total_views"] == 100
        assert result["unique_viewers"] == 50
        assert result["total_articles"] == 20
        assert result["avg_views_per_article"] == 5.0

    async def test_get_summary_stats_no_articles(self, mock_session):
        """Test getting summary statistics when no articles exist."""
        mock_views_result = MagicMock()
        mock_views_result.scalar.return_value = 0

        mock_viewers_result = MagicMock()
        mock_viewers_result.scalar.return_value = 0

        mock_articles_result = MagicMock()
        mock_articles_result.scalar.return_value = 0

        mock_session.execute.side_effect = [mock_views_result, mock_viewers_result, mock_articles_result]

        repo = ArticleViewRepository(mock_session)
        result = await repo.get_summary_stats()

        assert result["total_views"] == 0
        assert result["unique_viewers"] == 0
        assert result["total_articles"] == 0
        assert result["avg_views_per_article"] == 0.0
