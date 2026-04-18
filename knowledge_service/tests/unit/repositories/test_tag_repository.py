"""Tests for Tag repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import Tag
from knowledge_service.repositories.implementations.tag import TagRepository


class TestTagRepository:
    """Test Tag repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def sample_tag(self):
        """Create a sample tag."""
        return Tag(
            id=1,
            name="Test Tag",
            slug="test-tag",
            description="Test tag description",
            usage_count=5,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def test_get_by_slug(self, mock_session, sample_tag):
        """Test getting tag by slug."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_tag
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.get_by_slug("test-tag")

        assert result == sample_tag

    async def test_get_by_slug_not_found(self, mock_session):
        """Test getting tag by slug - not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.get_by_slug("nonexistent")

        assert result is None

    async def test_get_by_id_with_articles(self, mock_session, sample_tag):
        """Test getting tag by ID with articles."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_tag
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.get_by_id_with_articles(1)

        assert result == sample_tag

    async def test_find_by_name_or_slug(self, mock_session, sample_tag):
        """Test finding tag by name or slug."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_tag
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.find_by_name_or_slug("Test Tag", "test-tag")

        assert result == sample_tag

    async def test_find_by_name_or_slug_not_found(self, mock_session):
        """Test finding tag by name or slug - not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.find_by_name_or_slug("Nonexistent", "nonexistent")

        assert result is None

    async def test_find_by_name_or_slug_excluding(self, mock_session, sample_tag):
        """Test finding tag by name or slug excluding specific ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_tag
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.find_by_name_or_slug_excluding("Test Tag", "test-tag", exclude_id=2)

        assert result == sample_tag

    async def test_find_by_name_or_slug_excluding_same_id(self, mock_session):
        """Test excluding the same ID should allow the tag."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.find_by_name_or_slug_excluding("Test", "test", exclude_id=1)

        assert result is None

    async def test_find_tags_with_search(self, mock_session, sample_tag):
        """Test finding tags with search."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_tag]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result, total = await repo.find_tags(search="test")

        assert len(result) == 1
        assert total == 1

    async def test_find_tags_sort_by_name(self, mock_session, sample_tag):
        """Test finding tags sorted by name."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_tag]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result, _total = await repo.find_tags(sort_by="name", sort_desc=False)

        assert len(result) == 1

    async def test_find_tags_sort_by_name_desc(self, mock_session, sample_tag):
        """Test finding tags sorted by name descending."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_tag]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result, _total = await repo.find_tags(sort_by="name", sort_desc=True)

        assert len(result) == 1

    async def test_find_tags_sort_by_created_at(self, mock_session, sample_tag):
        """Test finding tags sorted by created_at."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_tag]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result, _total = await repo.find_tags(sort_by="created_at", sort_desc=False)

        assert len(result) == 1

    async def test_find_tags_sort_by_usage_count(self, mock_session, sample_tag):
        """Test finding tags sorted by usage_count (default)."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_tag]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result, _total = await repo.find_tags(sort_by="usage_count", sort_desc=True)

        assert len(result) == 1

    async def test_find_tags_sort_by_usage_count_asc(self, mock_session, sample_tag):
        """Test finding tags sorted by usage_count ascending."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_tag]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result, _total = await repo.find_tags(sort_by="usage_count", sort_desc=False)

        assert len(result) == 1

    async def test_get_popular(self, mock_session, sample_tag):
        """Test getting popular tags."""
        tag2 = Tag(
            id=2,
            name="Popular Tag",
            slug="popular-tag",
            usage_count=10,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [tag2, sample_tag]
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.get_popular(limit=20)

        assert len(result) == 2
        # Should be ordered by usage_count desc
        assert result[0].usage_count == 10
        assert result[1].usage_count == 5

    async def test_find_by_article(self, mock_session, sample_tag):
        """Test finding tags by article."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_tag]
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.find_by_article(1)

        assert len(result) == 1
        assert result[0] == sample_tag

    async def test_find_by_article_empty(self, mock_session):
        """Test finding tags by article - empty."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        repo = TagRepository(mock_session)
        result = await repo.find_by_article(999)

        assert result == []
