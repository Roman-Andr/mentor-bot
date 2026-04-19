"""
Tests for Article Service edge cases.

Covers lines 95-96 in services/article.py:
- The while loop incrementing counter when generating slugs
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_service.core import ArticleStatus
from knowledge_service.models import Article
from knowledge_service.schemas import ArticleUpdate
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


class TestUpdateArticleSlugCollisionLoop:
    """Test the while loop during slug generation on update - covers lines 95-96."""

    async def test_update_article_title_with_multiple_slug_collisions(
        self, mock_uow, sample_article
    ):
        """
        Test update_article with multiple slug collisions - covers lines 95-96.

        This tests the while loop incrementing the counter multiple times:
        - Line 94: First check returns True (exists)
        - Line 95: counter becomes 1
        - Line 96: slug becomes "new-title-1"
        - Loop continues...
        - Finally a unique slug is found
        """
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article
        # Multiple slug exists checks - first 2 return True, third returns False
        mock_uow.articles.slug_exists.side_effect = [
            True,   # "new-title" exists
            True,   # "new-title-1" exists
            False,  # "new-title-2" is available
        ]
        mock_uow.articles.update.return_value = sample_article
        mock_uow.articles.update_search_vector.return_value = None

        service = ArticleService(mock_uow)
        update_data = ArticleUpdate(title="New Title")

        await service.update_article(1, update_data)

        # Verify the while loop ran multiple times
        assert mock_uow.articles.slug_exists.call_count == 3
        # Verify the final slug was set correctly
        assert sample_article.slug == "new-title-2"
        assert sample_article.title == "New Title"

    async def test_update_article_title_with_single_slug_collision(
        self, mock_uow, sample_article
    ):
        """
        Test update_article with single slug collision.

        This covers line 95-96 being executed once.
        """
        mock_uow.articles.get_by_id_with_relations.return_value = sample_article
        # Single collision then success
        mock_uow.articles.slug_exists.side_effect = [
            True,   # "new-title" exists
            False,  # "new-title-1" is available
        ]
        mock_uow.articles.update.return_value = sample_article
        mock_uow.articles.update_search_vector.return_value = None

        service = ArticleService(mock_uow)
        update_data = ArticleUpdate(title="New Title")

        await service.update_article(1, update_data)

        # Verify slug_exists was called twice
        assert mock_uow.articles.slug_exists.call_count == 2
        # Verify the final slug
        assert sample_article.slug == "new-title-1"
