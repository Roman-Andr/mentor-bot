"""Tests for Article repository implementation."""

from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import ArticleStatus, EmployeeLevel
from knowledge_service.models import Article
from knowledge_service.repositories.implementations.article import ArticleRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestArticleRepository:
    """Test Article repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def sample_article(self):
        """Create a sample article."""
        return Article(
            id=1,
            title="Test Article",
            slug="test-article",
            content="Test content",
            excerpt="Test excerpt",
            category_id=1,
            author_id=1,
            author_name="Test Author",
            department_id=1,
            position="Developer",
            level=EmployeeLevel.JUNIOR,
            status=ArticleStatus.PUBLISHED,
            view_count=10,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            published_at=datetime.now(UTC),
        )

    async def test_create_with_relations(self, mock_session, sample_article):
        """Test creating article with eager-loaded relations."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_article
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.create(sample_article)

        assert result == sample_article
        mock_session.add.assert_called_once_with(sample_article)
        mock_session.flush.assert_called_once()

    async def test_update_with_relations(self, mock_session, sample_article):
        """Test updating article with eager-loaded relations."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_article
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.update(sample_article)

        assert result == sample_article
        mock_session.flush.assert_called_once()

    async def test_get_by_slug(self, mock_session, sample_article):
        """Test getting article by slug."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_article
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.get_by_slug("test-article")

        assert result == sample_article

    async def test_get_by_slug_not_found(self, mock_session):
        """Test getting article by slug - not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.get_by_slug("nonexistent")

        assert result is None

    async def test_get_by_id_with_relations(self, mock_session, sample_article):
        """Test getting article by ID with relations."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_article
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.get_by_id_with_relations(1)

        assert result == sample_article

    async def test_find_articles_with_category_filter(self, mock_session, sample_article):
        """Test finding articles with category filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1  # for count
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(category_id=1)

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_with_tag_filter(self, mock_session, sample_article):
        """Test finding articles with tag filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1  # for count
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(tag_id=1)

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_with_department_filter(self, mock_session, sample_article):
        """Test finding articles with department filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1  # for count
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(department_id=1)

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_with_status_filter(self, mock_session, sample_article):
        """Test finding articles with status filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1  # for count
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(status="published")

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_with_search(self, mock_session, sample_article):
        """Test finding articles with search query."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1  # for count
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(search="test")

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_with_featured_only(self, mock_session, sample_article):
        """Test finding featured articles only."""
        sample_article.is_featured = True
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, _total = await repo.find_articles(featured_only=True)

        assert len(result) == 1
        assert result[0].is_featured is True

    async def test_find_articles_with_pinned_only(self, mock_session, sample_article):
        """Test finding pinned articles only."""
        sample_article.is_pinned = True
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, _total = await repo.find_articles(pinned_only=True)

        assert len(result) == 1
        assert result[0].is_pinned is True

    async def test_find_articles_with_user_filters(self, mock_session, sample_article):
        """Test finding articles with user filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        user_filters = {
            "department_id": 1,
            "position": "Developer",
            "level": "JUNIOR",
        }
        result, _total = await repo.find_articles(user_filters=user_filters)

        assert len(result) == 1

    async def test_find_department_articles(self, mock_session, sample_article):
        """Test finding published articles for a department."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_department_articles(department_id=1)

        assert len(result) == 1
        assert total == 1

    async def test_slug_exists_true(self, mock_session, sample_article):
        """Test checking if slug exists - exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_article
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.slug_exists("test-article")

        assert result is True

    async def test_slug_exists_false(self, mock_session):
        """Test checking if slug exists - not exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.slug_exists("nonexistent")

        assert result is False

    async def test_slug_exists_with_exclude_id(self, mock_session, sample_article):
        """Test checking slug existence excluding specific ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.slug_exists("test-article", exclude_id=1)

        assert result is False

    async def test_increment_view_count(self, mock_session):
        """Test incrementing view count."""
        repo = ArticleRepository(mock_session)
        await repo.increment_view_count(1)

        mock_session.execute.assert_called_once()

    async def test_update_search_vector(self, mock_session):
        """Test updating search vector."""
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        await repo.update_search_vector(1)

        mock_session.execute.assert_called_once()

    async def test_get_daily_views(self, mock_session):
        """Test getting daily views."""
        today = date.today()
        mock_row = MagicMock()
        mock_row.view_date = today
        mock_row.count = 5

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.get_daily_views(1, today - timedelta(days=7))

        assert today in result
        assert result[today] == 5

    async def test_get_previous_week_views(self, mock_session):
        """Test getting previous week views."""
        today = date.today()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.get_previous_week_views(1, today)

        assert result == 10

    async def test_get_previous_week_views_none(self, mock_session):
        """Test getting previous week views when none."""
        today = date.today()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = None
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.get_previous_week_views(1, today)

        assert result == 0

    async def test_get_by_ids(self, mock_session, sample_article):
        """Test getting articles by IDs."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = [sample_article]
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result = await repo.get_by_ids([1, 2, 3])

        assert len(result) == 1
        assert result[0] == sample_article

    async def test_get_by_ids_empty(self, mock_session):
        """Test getting articles by IDs with empty list."""
        repo = ArticleRepository(mock_session)
        result = await repo.get_by_ids([])

        assert result == []
        mock_session.execute.assert_not_called()

    async def test_find_articles_desc_sort_order(self, mock_session, sample_article):
        """Test finding articles with descending sort order."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(sort_by="viewCount", sort_order="desc")

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_pinned_desc_sort(self, mock_session, sample_article):
        """Test finding articles with pinned sorting and descending order."""
        sample_article.is_pinned = True
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(sort_by="createdAt", sort_order="desc")

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_pinned_asc_sort(self, mock_session, sample_article):
        """Test finding articles with pinned sorting and ascending order."""
        sample_article.is_pinned = True
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(sort_by="publishedAt", sort_order="asc")

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_view_count_desc(self, mock_session, sample_article):
        """Test finding articles sorted by viewCount desc (non-pinned sort)."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(sort_by="viewCount", sort_order="DESC")

        assert len(result) == 1
        assert total == 1

    async def test_find_articles_title_asc(self, mock_session, sample_article):
        """Test finding articles sorted by title asc (non-pinned sort asc branch)."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleRepository(mock_session)
        result, total = await repo.find_articles(sort_by="title", sort_order="asc")

        assert len(result) == 1
        assert total == 1
