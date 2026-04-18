"""Tests for ArticleView repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models.article_view import ArticleView
from knowledge_service.repositories.implementations.article_view import ArticleViewRepository


class TestArticleViewRepository:
    """Test ArticleView repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.add = MagicMock()
        session.flush = AsyncMock()
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

        repo = ArticleViewRepository(mock_session)

        # Mock the create method behavior - we need to verify the view object is created correctly
        result = await repo.record_view(article_id=1, user_id=1)

        # Verify the view object was created with correct values
        assert isinstance(result, ArticleView)
        assert result.article_id == 1
        assert result.user_id == 1

    async def test_record_view_without_user_id(self, mock_session):
        """Test recording a view without user_id (anonymous view)."""
        repo = ArticleViewRepository(mock_session)

        result = await repo.record_view(article_id=2, user_id=None)

        # Verify the view object was created with correct values
        assert isinstance(result, ArticleView)
        assert result.article_id == 2
        assert result.user_id is None
