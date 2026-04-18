"""Tests for attachment service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_service.core import AttachmentType, NotFoundException
from knowledge_service.models import Attachment
from knowledge_service.services.attachment import AttachmentService


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.attachments = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def sample_attachment():
    """Create a sample attachment for testing."""
    return Attachment(
        id=1,
        article_id=1,
        name="test_file.pdf",
        type=AttachmentType.FILE,
        url="/api/v1/attachments/file/1/test_file.pdf",
        file_size=1024,
        mime_type="application/pdf",
        description="Test file description",
        order=0,
        is_downloadable=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_link_attachment():
    """Create a sample link attachment for testing."""
    return Attachment(
        id=2,
        article_id=1,
        name="External Link",
        type=AttachmentType.LINK,
        url="https://example.com/resource",
        file_size=0,
        mime_type=None,
        description="External resource link",
        order=1,
        is_downloadable=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


class TestCreateAttachment:
    """Tests for attachment creation."""

    async def test_create_attachment_basic(self, mock_uow, sample_attachment):
        """Test basic attachment creation."""
        mock_uow.attachments.create.return_value = sample_attachment

        service = AttachmentService(mock_uow)
        result = await service.create_attachment(
            article_id=1,
            name="test_file.pdf",
            attachment_type=AttachmentType.FILE,
            url="/api/v1/attachments/file/1/test_file.pdf",
            file_size=1024,
            mime_type="application/pdf",
            description="Test file description",
            order=0,
            is_downloadable=True,
        )

        assert result == sample_attachment
        mock_uow.attachments.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_create_link_attachment(self, mock_uow, sample_link_attachment):
        """Test link attachment creation."""
        mock_uow.attachments.create.return_value = sample_link_attachment

        service = AttachmentService(mock_uow)
        result = await service.create_attachment(
            article_id=1,
            name="External Link",
            attachment_type=AttachmentType.LINK,
            url="https://example.com/resource",
            file_size=0,
            mime_type=None,
            description="External resource link",
            order=1,
            is_downloadable=False,
        )

        assert result == sample_link_attachment
        assert result.type == AttachmentType.LINK
        assert result.is_downloadable is False

    async def test_create_attachment_minimal(self, mock_uow, sample_attachment):
        """Test attachment creation with minimal parameters."""
        mock_uow.attachments.create.return_value = sample_attachment

        service = AttachmentService(mock_uow)
        result = await service.create_attachment(
            article_id=1,
            name="test_file.pdf",
            attachment_type=AttachmentType.FILE,
            url="/api/v1/attachments/file/1/test_file.pdf",
        )

        assert result == sample_attachment
        # Verify default values
        call_args = mock_uow.attachments.create.call_args[0][0]
        assert call_args.order == 0
        assert call_args.is_downloadable is True
        assert call_args.file_size is None
        assert call_args.mime_type is None
        assert call_args.description is None


class TestGetAttachment:
    """Tests for getting attachments."""

    async def test_get_attachment_success(self, mock_uow, sample_attachment):
        """Test getting attachment by ID successfully."""
        mock_uow.attachments.get_by_id.return_value = sample_attachment

        service = AttachmentService(mock_uow)
        result = await service.get_attachment(1)

        assert result == sample_attachment
        mock_uow.attachments.get_by_id.assert_called_once_with(1)

    async def test_get_attachment_not_found(self, mock_uow):
        """Test getting non-existent attachment."""
        mock_uow.attachments.get_by_id.return_value = None

        service = AttachmentService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_attachment(999)

    async def test_get_attachments_by_article(self, mock_uow, sample_attachment, sample_link_attachment):
        """Test getting all attachments for an article."""
        mock_uow.attachments.get_by_article.return_value = [sample_attachment, sample_link_attachment]

        service = AttachmentService(mock_uow)
        result = await service.get_attachments_by_article(1)

        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        mock_uow.attachments.get_by_article.assert_called_once_with(1)

    async def test_get_attachments_by_article_empty(self, mock_uow):
        """Test getting attachments for article with no attachments."""
        mock_uow.attachments.get_by_article.return_value = []

        service = AttachmentService(mock_uow)
        result = await service.get_attachments_by_article(999)

        assert result == []


class TestDeleteAttachment:
    """Tests for deleting attachments."""

    async def test_delete_attachment(self, mock_uow, sample_attachment):
        """Test attachment deletion."""
        mock_uow.attachments.get_by_id.return_value = sample_attachment
        mock_uow.attachments.delete.return_value = None

        service = AttachmentService(mock_uow)
        await service.delete_attachment(1)

        mock_uow.attachments.get_by_id.assert_called_once_with(1)
        mock_uow.attachments.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    async def test_delete_attachment_not_found(self, mock_uow):
        """Test deleting non-existent attachment."""
        mock_uow.attachments.get_by_id.return_value = None

        service = AttachmentService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.delete_attachment(999)

        mock_uow.attachments.delete.assert_not_called()
        mock_uow.commit.assert_not_called()

    async def test_delete_link_attachment(self, mock_uow, sample_link_attachment):
        """Test deleting link attachment."""
        mock_uow.attachments.get_by_id.return_value = sample_link_attachment
        mock_uow.attachments.delete.return_value = None

        service = AttachmentService(mock_uow)
        await service.delete_attachment(2)

        mock_uow.attachments.delete.assert_called_once_with(2)
        mock_uow.commit.assert_called_once()
