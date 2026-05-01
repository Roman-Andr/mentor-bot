"""Tests for article service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import ArticleStatus, NotFoundException
from knowledge_service.models import Article, Tag
from knowledge_service.schemas import ArticleCreate, ArticleUpdate
from knowledge_service.services.article import ArticleService


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.articles = AsyncMock()
    uow.tags = AsyncMock()
    uow.article_views = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def sample_article():
    """Create a sample article for testing."""
    return Article(
        id=1,
        title="Test Article",
        slug="test-article",
        content="This is test content",
        excerpt="Test excerpt",
        category_id=1,
        author_id=1,
        author_name="Test Author",
        department_id=1,
        position="Developer",
        level="JUNIOR",
        status=ArticleStatus.DRAFT,
        is_pinned=False,
        is_featured=False,
        meta_title=None,
        meta_description=None,
        keywords=[],
        view_count=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        published_at=None,
    )


@pytest.fixture
def sample_published_article():
    """Create a sample published article for testing."""
    return Article(
        id=2,
        title="Published Article",
        slug="published-article",
        content="Published content",
        excerpt="Published excerpt",
        category_id=1,
        author_id=1,
        author_name="Test Author",
        department_id=1,
        position="Developer",
        level="JUNIOR",
        status=ArticleStatus.PUBLISHED,
        is_pinned=False,
        is_featured=True,
        meta_title=None,
        meta_description=None,
        keywords=[],
        view_count=10,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        published_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_tag():
    """Create a sample tag for testing."""
    tag = Tag(
        id=1,
        name="Python",
        slug="python",
        description="Python programming",
        usage_count=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    tag.articles = []
    return tag


class TestCreateArticle:
    """Tests for article creation."""

    async def test_create_article_basic(self, mock_uow, sample_article):
        """Test basic article creation."""
        mock_uow.articles.slug_exists.return_value = False
        mock_uow.articles.create.return_value = sample_article
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article

        service = ArticleService(mock_uow)
        article_data = ArticleCreate(
            title="Test Article",
            content="This is test content",
            excerpt="Test excerpt",
            category_id=1,
            department_id=1,
            position="Developer",
            level="JUNIOR",
            status=ArticleStatus.DRAFT,
        )

        result = await service.create_article(article_data, author_id=1, author_name="Test Author")

        assert result == sample_article
        mock_uow.articles.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_create_article_with_slug_collision(self, mock_uow, sample_article):
        """Test article creation handles slug collision."""
        mock_uow.articles.slug_exists.side_effect = [True, True, False]
        mock_uow.articles.create.return_value = sample_article
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article

        service = ArticleService(mock_uow)
        article_data = ArticleCreate(
            title="Test Article",
            content="This is test content",
            excerpt="Test excerpt",
            category_id=1,
            status=ArticleStatus.DRAFT,
        )

        result = await service.create_article(article_data, author_id=1, author_name="Test Author")

        assert mock_uow.articles.slug_exists.call_count == 3
        assert result == sample_article

    async def test_create_article_with_tags(self, mock_uow, sample_article, sample_tag):
        """Test article creation with tags."""
        mock_uow.articles.slug_exists.return_value = False
        mock_uow.articles.create.return_value = sample_article
        mock_uow.tags.get_all.return_value = [sample_tag]
        mock_uow.tags.update.return_value = sample_tag
        mock_uow.articles.update_search_vector.return_value = None
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article

        service = ArticleService(mock_uow)
        article_data = ArticleCreate(
            title="Test Article",
            content="This is test content",
            excerpt="Test excerpt",
            category_id=1,
            status=ArticleStatus.DRAFT,
            tag_ids=[1],
        )

        result = await service.create_article(article_data, author_id=1, author_name="Test Author")

        mock_uow.tags.get_all.assert_called_once()
        mock_uow.tags.update.assert_called_once()
        assert result == sample_article

    async def test_create_article_published(self, mock_uow, sample_published_article):
        """Test article creation with published status."""
        mock_uow.articles.slug_exists.return_value = False
        mock_uow.articles.create.return_value = sample_published_article
        mock_uow.articles.update_search_vector.return_value = None
        mock_uow.articles.get_by_id_with_relations.return_value = sample_published_article

        service = ArticleService(mock_uow)
        article_data = ArticleCreate(
            title="Published Article",
            content="Published content",
            excerpt="Published excerpt",
            category_id=1,
            status=ArticleStatus.PUBLISHED,
        )

        result = await service.create_article(article_data, author_id=1, author_name="Test Author")

        assert result.status == ArticleStatus.PUBLISHED
        assert result.published_at is not None


class TestGetArticle:
    """Tests for getting articles."""

    async def test_get_article_by_id_success(self, mock_uow, sample_article):
        """Test getting article by ID successfully."""
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article

        service = ArticleService(mock_uow)
        result = await service.get_article_by_id(1)

        assert result == sample_article
        mock_uow.articles.get_by_id_with_relations.assert_called_once_with(1)

    async def test_get_article_by_id_not_found(self, mock_uow):
        """Test getting non-existent article by ID."""
        mock_uow.articles.get_by_id_with_relations.return_value = None

        service = ArticleService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_article_by_id(999)

    async def test_get_article_by_slug_success(self, mock_uow, sample_article):
        """Test getting article by slug successfully."""
        mock_uow.articles.get_by_slug.return_value = sample_article

        service = ArticleService(mock_uow)
        result = await service.get_article_by_slug("test-article")

        assert result == sample_article
        mock_uow.articles.get_by_slug.assert_called_once_with("test-article")

    async def test_get_article_by_slug_not_found(self, mock_uow):
        """Test getting non-existent article by slug."""
        mock_uow.articles.get_by_slug.return_value = None

        service = ArticleService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_article_by_slug("non-existent")

    async def test_get_articles(self, mock_uow, sample_article, sample_published_article):
        """Test getting paginated articles."""
        mock_uow.articles.find_articles.return_value = ([sample_article, sample_published_article], 2)

        service = ArticleService(mock_uow)
        result, total = await service.get_articles(skip=0, limit=10)

        assert len(result) == 2
        assert total == 2
        mock_uow.articles.find_articles.assert_called_once()

    async def test_get_articles_with_filters(self, mock_uow, sample_article):
        """Test getting articles with filters."""
        mock_uow.articles.find_articles.return_value = ([sample_article], 1)

        service = ArticleService(mock_uow)
        result, total = await service.get_articles(
            skip=0,
            limit=10,
            category_id=1,
            tag_id=1,
            department_id=1,
            status="draft",
            search="test",
            featured_only=True,
            pinned_only=False,
            user_filters={"department_id": 1},
        )

        assert len(result) == 1
        assert total == 1

    async def test_get_articles_by_ids(self, mock_uow, sample_article, sample_published_article):
        """Test getting articles by IDs."""
        mock_uow.articles.get_by_ids.return_value = [sample_article, sample_published_article]

        service = ArticleService(mock_uow)
        result = await service.get_articles_by_ids([1, 2])

        assert len(result) == 2
        mock_uow.articles.get_by_ids.assert_called_once_with([1, 2])

    async def test_get_articles_by_ids_empty(self, mock_uow):
        """Test getting articles with empty IDs list."""
        service = ArticleService(mock_uow)
        result = await service.get_articles_by_ids([])

        assert result == []
        mock_uow.articles.get_by_ids.assert_not_called()


class TestUpdateArticle:
    """Tests for updating articles."""

    async def test_update_article_basic(self, mock_uow, sample_article):
        """Test basic article update."""
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article
        mock_uow.articles.update.return_value = sample_article
        mock_uow.articles.update_search_vector.return_value = None

        service = ArticleService(mock_uow)
        update_data = ArticleUpdate(content="Updated content")

        result = await service.update_article(1, update_data)

        assert result == sample_article
        mock_uow.articles.update.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_update_article_title_with_slug_change(self, mock_uow, sample_article):
        """Test article update with title change causing slug update."""
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article
        mock_uow.articles.slug_exists.return_value = False
        mock_uow.articles.update.return_value = sample_article
        mock_uow.articles.update_search_vector.return_value = None

        service = ArticleService(mock_uow)
        update_data = ArticleUpdate(title="New Title")

        await service.update_article(1, update_data)

        assert sample_article.title == "New Title"
        mock_uow.articles.slug_exists.assert_called_once_with("new-title", exclude_id=1)

    async def test_update_article_publish(self, mock_uow, sample_article):
        """Test publishing an article via update."""
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article
        mock_uow.articles.update.return_value = sample_article
        mock_uow.articles.update_search_vector.return_value = None

        service = ArticleService(mock_uow)
        update_data = ArticleUpdate(status=ArticleStatus.PUBLISHED)

        await service.update_article(1, update_data)

        assert sample_article.status == ArticleStatus.PUBLISHED
        assert sample_article.published_at is not None

    async def test_update_article_with_tag_changes(self, mock_uow, sample_article, sample_tag):
        """Test updating article with tag changes."""
        tag2 = Tag(
            id=2,
            name="JavaScript",
            slug="javascript",
            description="JS programming",
            usage_count=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        tag2.articles = []

        sample_tag.articles.append(sample_article)
        sample_article.tags = [sample_tag]

        mock_uow.articles.get_by_id_with_relations.return_value = sample_article
        mock_uow.tags.get_all.return_value = [sample_tag, tag2]
        mock_uow.tags.update.return_value = None
        mock_uow.articles.update.return_value = sample_article
        mock_uow.articles.update_search_vector.return_value = None

        service = ArticleService(mock_uow)
        update_data = ArticleUpdate(tag_ids=[2])

        await service.update_article(1, update_data)

        mock_uow.tags.update.assert_called()
        mock_uow.commit.assert_called_once()


class TestDeleteArticle:
    """Tests for deleting articles."""

    async def test_delete_article(self, mock_uow, sample_article, sample_tag):
        """Test article deletion."""
        sample_tag.articles.append(sample_article)
        sample_article.tags = [sample_tag]

        mock_uow.articles.get_by_id_with_relations.return_value = sample_article
        mock_uow.tags.update.return_value = None
        mock_uow.articles.delete.return_value = None

        service = ArticleService(mock_uow)
        await service.delete_article(1)

        mock_uow.tags.update.assert_called_once()
        mock_uow.articles.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()


class TestPublishArticle:
    """Tests for publishing articles."""

    async def test_publish_article(self, mock_uow, sample_article):
        """Test publishing an article."""
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article
        mock_uow.articles.update.return_value = sample_article
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article

        service = ArticleService(mock_uow)
        result = await service.publish_article(1)

        assert result.status == ArticleStatus.PUBLISHED
        assert result.published_at is not None
        mock_uow.commit.assert_called_once()


class TestRecordView:
    """Tests for recording article views."""

    async def test_record_view_with_user(self, mock_uow):
        """Test recording view with user ID."""
        mock_uow.articles.increment_view_count.return_value = None
        mock_uow.article_views.record_view.return_value = None

        service = ArticleService(mock_uow)
        await service.record_view(1, user_id=1)

        mock_uow.articles.increment_view_count.assert_called_once_with(1)
        mock_uow.article_views.record_view.assert_called_once_with(1, 1)
        mock_uow.commit.assert_called_once()

    async def test_record_view_without_user(self, mock_uow):
        """Test recording view without user ID."""
        mock_uow.articles.increment_view_count.return_value = None
        mock_uow.article_views.record_view.return_value = None

        service = ArticleService(mock_uow)
        await service.record_view(1, user_id=None)

        mock_uow.articles.increment_view_count.assert_called_once_with(1)
        mock_uow.article_views.record_view.assert_called_once_with(1, None)


class TestDepartmentArticles:
    """Tests for department-specific article operations."""

    async def test_get_department_articles(self, mock_uow, sample_article):
        """Test getting articles for a department."""
        mock_uow.articles.find_department_articles.return_value = ([sample_article], 1)

        service = ArticleService(mock_uow)
        result, total = await service.get_department_articles(1, skip=0, limit=10)

        assert len(result) == 1
        assert total == 1
        mock_uow.articles.find_department_articles.assert_called_once_with(1, skip=0, limit=10)


class TestArticleStats:
    """Tests for article statistics."""

    async def test_get_article_stats(self, mock_uow, sample_published_article, sample_tag):
        """Test getting article statistics."""
        # Only add the relationship in one direction to avoid duplication
        sample_published_article.tags = [sample_tag]

        mock_uow.articles.get_by_id_with_relations.return_value = sample_published_article
        mock_uow.articles.get_daily_views.return_value = {}
        mock_uow.articles.get_previous_week_views.return_value = 5

        service = ArticleService(mock_uow)
        result = await service.get_article_stats(1)

        assert result["article_id"] == sample_published_article.id
        assert result["title"] == sample_published_article.title
        assert result["view_count"] == sample_published_article.view_count
        assert "daily_views" in result
        assert "weekly_growth" in result
        assert "popular_tags" in result
        assert result["popular_tags"] == ["Python"]

    async def test_get_article_stats_with_growth(self, mock_uow, sample_published_article, sample_tag):
        """Test article stats with growth calculation."""
        sample_published_article.tags = [sample_tag]

        today = datetime.now(UTC).date()
        daily_views = {today: 10}

        mock_uow.articles.get_by_id_with_relations.return_value = sample_published_article
        mock_uow.articles.get_daily_views.return_value = daily_views
        mock_uow.articles.get_previous_week_views.return_value = 5

        service = ArticleService(mock_uow)
        result = await service.get_article_stats(1)

        expected_growth = ((10 - 5) / 5) * 100
        assert result["weekly_growth"] == round(expected_growth, 2)

    async def test_get_article_stats_zero_previous(self, mock_uow, sample_published_article, sample_tag):
        """Test article stats with zero previous week views."""
        sample_published_article.tags = [sample_tag]

        today = datetime.now(UTC).date()
        daily_views = {today: 10}

        mock_uow.articles.get_by_id_with_relations.return_value = sample_published_article
        mock_uow.articles.get_daily_views.return_value = daily_views
        mock_uow.articles.get_previous_week_views.return_value = 0

        service = ArticleService(mock_uow)
        result = await service.get_article_stats(1)

        assert result["weekly_growth"] == 0.0
