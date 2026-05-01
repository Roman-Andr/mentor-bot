"""Tests for base repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import EmployeeLevel
from knowledge_service.models import Article, Category
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestSqlAlchemyBaseRepository:
    """Test base repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
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
            status="published",
            view_count=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def test_get_by_id_success(self, mock_session, sample_article):
        """Test getting entity by ID successfully."""
        # Mock the execute result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_article
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Article)
        result = await repo.get_by_id(1)

        assert result == sample_article
        mock_session.execute.assert_called_once()

    async def test_get_by_id_not_found(self, mock_session):
        """Test getting non-existent entity by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Article)
        result = await repo.get_by_id(999)

        assert result is None

    async def test_get_all(self, mock_session, sample_article):
        """Test getting all entities with pagination."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_article]
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Article)
        result = await repo.get_all(skip=0, limit=10)

        assert len(result) == 1
        assert result[0] == sample_article

    async def test_create(self, mock_session, sample_article):
        """Test creating an entity."""
        repo = SqlAlchemyBaseRepository(mock_session, Article)
        result = await repo.create(sample_article)

        assert result == sample_article
        mock_session.add.assert_called_once_with(sample_article)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_article)

    async def test_update(self, mock_session, sample_article):
        """Test updating an entity."""
        repo = SqlAlchemyBaseRepository(mock_session, Article)
        result = await repo.update(sample_article)

        assert result == sample_article
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_article)

    async def test_delete_success(self, mock_session, sample_article):
        """Test deleting an existing entity."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_article
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Article)
        result = await repo.delete(1)

        assert result is True
        mock_session.delete.assert_called_once_with(sample_article)
        mock_session.flush.assert_called_once()

    async def test_delete_not_found(self, mock_session):
        """Test deleting non-existent entity."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Article)
        result = await repo.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()

    async def test_get_by_id_with_string_id(self, mock_session):
        """Test getting entity with string ID type."""
        category = Category(
            id=1,
            name="Test",
            slug="test",
            description="Test desc",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = category
        mock_session.execute.return_value = mock_result

        repo = SqlAlchemyBaseRepository(mock_session, Category)
        result = await repo.get_by_id("test-slug")

        assert result == category
