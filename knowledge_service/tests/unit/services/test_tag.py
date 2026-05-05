"""Tests for tag service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import ConflictException, NotFoundException, ValidationException
from knowledge_service.models import Article, Tag
from knowledge_service.schemas import TagCreate, TagUpdate
from knowledge_service.services.tag import TagService


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.tags = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def sample_tag():
    """Create a sample tag for testing."""
    tag = Tag(
        id=1,
        name="Python",
        slug="python",
        description="Python programming",
        usage_count=5,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    tag.articles = []
    return tag


@pytest.fixture
def sample_tag_with_article(sample_tag):
    """Create a sample tag with an article attached."""
    article = Article(
        id=1,
        title="Test Article",
        slug="test-article",
        content="Test content",
        excerpt="Test excerpt",
        category_id=1,
        author_id=1,
        author_name="Author",
        status="published",
        view_count=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    sample_tag.articles = [article]
    return sample_tag


@pytest.fixture
def another_tag():
    """Create another sample tag for testing."""
    tag = Tag(
        id=2,
        name="JavaScript",
        slug="javascript",
        description="JavaScript programming",
        usage_count=3,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    tag.articles = []
    return tag


class TestCreateTag:
    """Tests for tag creation."""

    async def test_create_tag_basic(self, mock_uow, sample_tag):
        """Test basic tag creation."""
        mock_uow.tags.find_by_name_or_slug.return_value = None
        mock_uow.tags.create.return_value = sample_tag

        service = TagService(mock_uow)
        tag_data = TagCreate(
            name="Python",
            slug="python",
            description="Python programming",
        )

        result = await service.create_tag(tag_data)

        assert result == sample_tag
        mock_uow.tags.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_create_tag_duplicate_name(self, mock_uow, sample_tag):
        """Test tag creation with duplicate name."""
        mock_uow.tags.find_by_name_or_slug.return_value = sample_tag

        service = TagService(mock_uow)
        tag_data = TagCreate(
            name="Python",
            slug="different-slug",
            description="Description",
        )

        with pytest.raises(ConflictException, match="already exists"):
            await service.create_tag(tag_data)

    async def test_create_tag_duplicate_slug(self, mock_uow, sample_tag):
        """Test tag creation with duplicate slug."""
        mock_uow.tags.find_by_name_or_slug.return_value = sample_tag

        service = TagService(mock_uow)
        tag_data = TagCreate(
            name="Different Name",
            slug="python",
            description="Description",
        )

        with pytest.raises(ConflictException, match="already exists"):
            await service.create_tag(tag_data)


class TestGetTag:
    """Tests for getting tags."""

    async def test_get_tag_by_id_success(self, mock_uow, sample_tag):
        """Test getting tag by ID successfully."""
        mock_uow.tags.get_by_id_with_articles.return_value = sample_tag

        service = TagService(mock_uow)
        result = await service.get_tag_by_id(1)

        assert result == sample_tag
        mock_uow.tags.get_by_id_with_articles.assert_called_once_with(1)

    async def test_get_tag_by_id_not_found(self, mock_uow):
        """Test getting non-existent tag by ID."""
        mock_uow.tags.get_by_id_with_articles.return_value = None

        service = TagService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_tag_by_id(999)

    async def test_get_tag_by_slug_success(self, mock_uow, sample_tag):
        """Test getting tag by slug successfully."""
        mock_uow.tags.get_by_slug.return_value = sample_tag

        service = TagService(mock_uow)
        result = await service.get_tag_by_slug("python")

        assert result == sample_tag
        mock_uow.tags.get_by_slug.assert_called_once_with("python")

    async def test_get_tag_by_slug_not_found(self, mock_uow):
        """Test getting non-existent tag by slug."""
        mock_uow.tags.get_by_slug.return_value = None

        service = TagService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_tag_by_slug("non-existent")

    async def test_get_tags(self, mock_uow, sample_tag, another_tag):
        """Test getting paginated tags."""
        mock_uow.tags.find_tags.return_value = ([sample_tag, another_tag], 2)

        service = TagService(mock_uow)
        result, total = await service.get_tags(skip=0, limit=10)

        assert len(result) == 2
        assert total == 2

    async def test_get_tags_with_search(self, mock_uow, sample_tag):
        """Test getting tags with search."""
        mock_uow.tags.find_tags.return_value = ([sample_tag], 1)

        service = TagService(mock_uow)
        result, _total = await service.get_tags(skip=0, limit=10, search="python")

        assert len(result) == 1
        mock_uow.tags.find_tags.assert_called_once_with(
            skip=0,
            limit=10,
            search="python",
            sort_by="usage_count",
            sort_desc=True,
        )

    async def test_get_tags_with_custom_sort(self, mock_uow, sample_tag):
        """Test getting tags with custom sort."""
        mock_uow.tags.find_tags.return_value = ([sample_tag], 1)

        service = TagService(mock_uow)
        _result, _total = await service.get_tags(skip=0, limit=10, sort_by="name", sort_desc=False)

        mock_uow.tags.find_tags.assert_called_once_with(
            skip=0,
            limit=10,
            search=None,
            sort_by="name",
            sort_desc=False,
        )

    async def test_get_popular_tags(self, mock_uow, sample_tag, another_tag):
        """Test getting popular tags."""
        mock_uow.tags.get_popular.return_value = [sample_tag, another_tag]

        service = TagService(mock_uow)
        result = await service.get_popular_tags(limit=20)

        assert len(result) == 2
        mock_uow.tags.get_popular.assert_called_once_with(20)

    async def test_get_tags_by_article(self, mock_uow, sample_tag):
        """Test getting tags by article."""
        mock_uow.tags.find_by_article.return_value = [sample_tag]

        service = TagService(mock_uow)
        result = await service.get_tags_by_article(1)

        assert len(result) == 1
        mock_uow.tags.find_by_article.assert_called_once_with(1)


class TestUpdateTag:
    """Tests for updating tags."""

    async def test_update_tag_basic(self, mock_uow, sample_tag):
        """Test basic tag update."""
        mock_uow.tags.get_by_id_with_articles.return_value = sample_tag
        mock_uow.tags.find_by_name_or_slug_excluding.return_value = None
        mock_uow.tags.update.return_value = sample_tag

        service = TagService(mock_uow)
        update_data = TagUpdate(description="Updated description")

        result = await service.update_tag(1, update_data)

        assert result.description == "Updated description"
        mock_uow.commit.assert_called_once()

    async def test_update_tag_name_conflict(self, mock_uow, sample_tag, another_tag):
        """Test tag update with name conflict."""
        mock_uow.tags.get_by_id_with_articles.return_value = sample_tag
        mock_uow.tags.find_by_name_or_slug_excluding.return_value = another_tag

        service = TagService(mock_uow)
        update_data = TagUpdate(name="JavaScript")

        with pytest.raises(ValidationException, match="already exists"):
            await service.update_tag(1, update_data)

    async def test_update_tag_description_only(self, mock_uow, sample_tag):
        """Test tag update with only description (no name change)."""
        mock_uow.tags.get_by_id_with_articles.return_value = sample_tag

        # No conflict check needed when only updating description
        async def mock_update(tag: Tag) -> Tag:
            return tag

        mock_uow.tags.update.side_effect = mock_update

        service = TagService(mock_uow)
        update_data = TagUpdate(description="Updated description only")

        result = await service.update_tag(1, update_data)

        assert result.description == "Updated description only"
        # find_by_name_or_slug_excluding should not be called when only description is updated
        mock_uow.tags.find_by_name_or_slug_excluding.assert_not_called()

    async def test_update_tag_name_success(self, mock_uow, sample_tag):
        """Test successful tag name update."""
        mock_uow.tags.get_by_id_with_articles.return_value = sample_tag
        mock_uow.tags.find_by_name_or_slug_excluding.return_value = None

        # Mock update to return the tag that was passed to it
        async def mock_update(tag: Tag) -> Tag:
            return tag

        mock_uow.tags.update.side_effect = mock_update

        service = TagService(mock_uow)
        update_data = TagUpdate(name="Python 3")

        result = await service.update_tag(1, update_data)

        assert result.name == "Python 3"


class TestDeleteTag:
    """Tests for deleting tags."""

    async def test_delete_tag(self, mock_uow, sample_tag):
        """Test tag deletion."""
        mock_uow.tags.get_by_id_with_articles.return_value = sample_tag
        mock_uow.tags.delete.return_value = None

        service = TagService(mock_uow)
        await service.delete_tag(1)

        mock_uow.tags.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    async def test_delete_tag_in_use(self, mock_uow, sample_tag_with_article):
        """Test deleting tag that is in use."""
        mock_uow.tags.get_by_id_with_articles.return_value = sample_tag_with_article

        service = TagService(mock_uow)

        with pytest.raises(ValidationException, match="in use"):
            await service.delete_tag(1)


class TestMergeTags:
    """Tests for merging tags."""

    async def test_merge_tags_success(self, mock_uow, sample_tag, another_tag):
        """Test successful tag merge."""
        mock_uow.tags.get_by_id_with_articles.side_effect = [sample_tag, another_tag]
        mock_uow.tags.update.return_value = None
        mock_uow.tags.delete.return_value = None

        service = TagService(mock_uow)
        await service.merge_tags(source_tag_id=1, target_tag_id=2)

        mock_uow.tags.update.assert_called_once()
        mock_uow.tags.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    async def test_merge_tags_same_id(self, mock_uow):
        """Test merging tag with itself."""
        service = TagService(mock_uow)

        with pytest.raises(ValidationException, match="itself"):
            await service.merge_tags(source_tag_id=1, target_tag_id=1)

    async def test_merge_tags_with_article_transfer(self, mock_uow, sample_tag, another_tag):
        """Test tag merge with article transfer."""
        article = Article(
            id=1,
            title="Test Article",
            slug="test-article",
            content="Content",
            excerpt="Excerpt",
            category_id=1,
            author_id=1,
            author_name="Author",
            status="published",
            view_count=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        article.tags = [sample_tag]
        sample_tag.articles = [article]
        another_tag.articles = []

        mock_uow.tags.get_by_id_with_articles.side_effect = [sample_tag, another_tag]
        mock_uow.tags.update.return_value = None
        mock_uow.tags.delete.return_value = None

        service = TagService(mock_uow)
        result = await service.merge_tags(source_tag_id=1, target_tag_id=2)

        assert result.id == 2
        assert another_tag.usage_count == 4  # 3 + 1
