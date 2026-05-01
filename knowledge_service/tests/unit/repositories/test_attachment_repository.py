"""Tests for Attachment repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import AttachmentType
from knowledge_service.models import Attachment
from knowledge_service.repositories.implementations.attachment import AttachmentRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestAttachmentRepository:
    """Test Attachment repository implementation."""

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
    def sample_attachment(self):
        """Create a sample attachment."""
        return Attachment(
            id=1,
            article_id=1,
            name="test_file.pdf",
            type=AttachmentType.FILE,
            url="http://localhost/api/v1/attachments/file/1/test_file.pdf",
            file_size=1024,
            mime_type="application/pdf",
            description="Test file",
            order=0,
            is_downloadable=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def test_get_by_article(self, mock_session, sample_attachment):
        """Test getting attachments by article ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_attachment]
        mock_session.execute.return_value = mock_result

        repo = AttachmentRepository(mock_session)
        result = await repo.get_by_article(1)

        assert len(result) == 1
        assert result[0] == sample_attachment

    async def test_get_by_article_empty(self, mock_session):
        """Test getting attachments by article ID - empty."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        repo = AttachmentRepository(mock_session)
        result = await repo.get_by_article(1)

        assert result == []

    async def test_get_by_article_multiple(self, mock_session, sample_attachment):
        """Test getting multiple attachments for an article."""
        attachment2 = Attachment(
            id=2,
            article_id=1,
            name="test_file2.pdf",
            type=AttachmentType.FILE,
            url="http://localhost/api/v1/attachments/file/1/test_file2.pdf",
            file_size=2048,
            mime_type="application/pdf",
            description="Test file 2",
            order=1,
            is_downloadable=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_attachment, attachment2]
        mock_session.execute.return_value = mock_result

        repo = AttachmentRepository(mock_session)
        result = await repo.get_by_article(1)

        assert len(result) == 2
        assert result[0].order == 0
        assert result[1].order == 1
