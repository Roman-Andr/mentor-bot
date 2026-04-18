"""Tests for model properties and methods."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from knowledge_service.core import ArticleStatus, AttachmentType, EmployeeLevel
from knowledge_service.models import Article, Attachment

if TYPE_CHECKING:
    pass


class TestArticleProperties:
    """Test Article model properties."""

    def test_article_is_published_when_published(self) -> None:
        """Test is_published property returns True for published articles."""
        article = Article(
            id=1,
            title="Published Article",
            slug="published-article",
            content="Content",
            author_id=1,
            author_name="Author",
            status=ArticleStatus.PUBLISHED,
            created_at=datetime.now(UTC),
        )

        assert article.is_published is True

    def test_article_is_published_when_draft(self) -> None:
        """Test is_published property returns False for draft articles."""
        article = Article(
            id=2,
            title="Draft Article",
            slug="draft-article",
            content="Content",
            author_id=1,
            author_name="Author",
            status=ArticleStatus.DRAFT,
            created_at=datetime.now(UTC),
        )

        assert article.is_published is False

    def test_article_is_published_when_archived(self) -> None:
        """Test is_published property returns False for archived articles."""
        article = Article(
            id=3,
            title="Archived Article",
            slug="archived-article",
            content="Content",
            author_id=1,
            author_name="Author",
            status=ArticleStatus.ARCHIVED,
            created_at=datetime.now(UTC),
        )

        assert article.is_published is False


    def test_article_repr(self) -> None:
        """Test Article __repr__ method."""
        article = Article(
            id=1,
            title="Test Article",
            slug="test-article",
            content="Content",
            author_id=1,
            author_name="Author",
            status=ArticleStatus.PUBLISHED,
            created_at=datetime.now(UTC),
        )

        repr_str = repr(article)

        assert "Article" in repr_str
        assert "id=1" in repr_str
        assert "title=Test Article" in repr_str
        assert "status" in repr_str


class TestAttachmentProperties:
    """Test Attachment model properties."""

    @patch("knowledge_service.models.attachment.settings")
    def test_attachment_file_url_property(self, mock_settings: Mock) -> None:
        """Test file_url property returns correct URL."""
        mock_settings.API_V1_PREFIX = "/api/v1"

        attachment = Attachment(
            id=1,
            article_id=1,
            name="document.pdf",
            type=AttachmentType.FILE,
            url="/storage/document.pdf",
            file_size=1024,
            mime_type="application/pdf",
            created_at=datetime.now(UTC),
        )

        expected_url = "/api/v1/attachments/1/download"
        assert attachment.file_url == expected_url

    @patch("knowledge_service.models.attachment.settings")
    def test_attachment_file_url_with_special_filename(self, mock_settings: Mock) -> None:
        """Test file_url property with special characters in filename."""
        mock_settings.API_V1_PREFIX = "/api/v1"

        attachment = Attachment(
            id=2,
            article_id=1,
            name="file with spaces & special.pdf",
            type=AttachmentType.FILE,
            url="/storage/file.pdf",
            file_size=2048,
            mime_type="application/pdf",
            created_at=datetime.now(UTC),
        )

        expected_url = "/api/v1/attachments/2/download"
        assert attachment.file_url == expected_url

    @patch("knowledge_service.models.attachment.settings")
    def test_attachment_file_url_for_link_type(self, mock_settings: Mock) -> None:
        """Test file_url property for LINK type attachment."""
        mock_settings.API_V1_PREFIX = "/api/v1"

        attachment = Attachment(
            id=3,
            article_id=1,
            name="External Link",
            type=AttachmentType.LINK,
            url="https://example.com/resource",
            file_size=None,
            mime_type=None,
            created_at=datetime.now(UTC),
        )

        # For links, file_url should return the external URL
        assert attachment.file_url == "https://example.com/resource"

    def test_attachment_repr(self) -> None:
        """Test Attachment __repr__ method."""
        attachment = Attachment(
            id=1,
            article_id=1,
            name="test.pdf",
            type=AttachmentType.FILE,
            url="/storage/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            created_at=datetime.now(UTC),
        )

        repr_str = repr(attachment)

        assert "Attachment" in repr_str
        assert "id=1" in repr_str
        assert "name=test.pdf" in repr_str
        assert "type" in repr_str
