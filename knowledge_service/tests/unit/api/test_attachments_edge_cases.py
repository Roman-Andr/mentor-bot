"""
Tests for attachment endpoint edge cases.

Covers:
- Lines 149-150: batch_upload permission denied
- Line 158: batch_upload skip oversized file
- Lines 179: batch_upload skip S3 upload error
- Lines 210-220: get_attachment_file permission denied for draft
"""

import io
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile

from knowledge_service.api.endpoints.attachments import (
    batch_upload_attachments,
    get_attachment_file,
)
from knowledge_service.core import ArticleStatus, PermissionDenied
from knowledge_service.utils.storage import StorageError

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from knowledge_service.api.deps import UserInfo
    from knowledge_service.models import Article


class TestBatchUploadPermissionDenied:
    """Test batch upload permission denied - covers lines 149-150."""

    async def test_batch_upload_to_other_user_article_denied(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test batch upload denied when user doesn't own article - covers lines 149-150."""
        mock_article.author_id = 999  # Different user
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"

        with patch("knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service):
            with pytest.raises(PermissionDenied) as exc_info:
                await batch_upload_attachments(
                    article_service=mock_article_service,
                    attachment_service=mock_attachment_service,
                    current_user=mock_user,
                    article_id=1,
                    files=[mock_file],
                )

        assert "Cannot attach files to other users' articles" in str(exc_info.value.detail)
        mock_storage_service.upload_file.assert_not_called()


class TestBatchUploadSkipOversizedFile:
    """Test batch upload skipping oversized files - covers line 158."""

    async def test_batch_upload_skips_oversized_file(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """
        Test batch upload skips oversized files - covers line 158.

        When a file exceeds MAX_FILE_SIZE_MB, it should be skipped via 'continue'.
        """
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        # Create an oversized file (> 10MB default limit)
        oversized_file = MagicMock(spec=UploadFile)
        oversized_file.filename = "oversized.pdf"
        oversized_file.size = 20 * 1024 * 1024  # 20MB
        oversized_file.content_type = "application/pdf"
        oversized_file.file = io.BytesIO(b"x" * (20 * 1024 * 1024))

        # Create a valid file
        valid_file = MagicMock(spec=UploadFile)
        valid_file.filename = "valid.pdf"
        valid_file.size = 1024
        valid_file.content_type = "application/pdf"
        valid_file.file = io.BytesIO(b"valid content")

        with patch("knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service):
            result = await batch_upload_attachments(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
                article_id=1,
                files=[oversized_file, valid_file],
            )

        # Only the valid file should be processed
        assert result.total_uploaded == 1
        mock_attachment_service.create_attachment.assert_called_once()
        # Storage upload should only be called once for the valid file
        mock_storage_service.upload_file.assert_called_once()


class TestBatchUploadSkipInvalidFileType:
    """Test batch upload skipping invalid file types."""

    async def test_batch_upload_skips_invalid_file_type(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test batch upload skips files with invalid types (line 160)."""
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        # Create an invalid file type
        invalid_file = MagicMock(spec=UploadFile)
        invalid_file.filename = "virus.exe"
        invalid_file.size = 1024
        invalid_file.content_type = "application/x-msdownload"
        invalid_file.file = io.BytesIO(b"malicious content")

        # Create a valid file
        valid_file = MagicMock(spec=UploadFile)
        valid_file.filename = "valid.pdf"
        valid_file.size = 1024
        valid_file.content_type = "application/pdf"
        valid_file.file = io.BytesIO(b"valid content")

        with patch("knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service):
            result = await batch_upload_attachments(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
                article_id=1,
                files=[invalid_file, valid_file],
            )

        # Only the valid file should be processed
        assert result.total_uploaded == 1
        mock_attachment_service.create_attachment.assert_called_once()
        # Storage upload should only be called once for the valid file
        mock_storage_service.upload_file.assert_called_once()


class TestBatchUploadS3Error:
    """Test batch upload S3 upload error - covers line 179."""

    async def test_batch_upload_skips_file_on_s3_error(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """
        Test batch upload skips files that fail S3 upload - covers line 179.

        When an S3 upload raises an exception, it should be skipped via 'continue'.
        """
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        # Create a file that will cause an error during S3 upload
        error_file = MagicMock(spec=UploadFile)
        error_file.filename = "error.pdf"
        error_file.size = 1024
        error_file.content_type = "application/pdf"
        error_file.file = io.BytesIO(b"error content")

        # Create a valid file
        valid_file = MagicMock(spec=UploadFile)
        valid_file.filename = "valid.pdf"
        valid_file.size = 1024
        valid_file.content_type = "application/pdf"
        valid_file.file = io.BytesIO(b"valid content")

        # Make storage upload fail for first call
        call_count = [0]
        async def mock_upload(*, file_data, object_name, content_type=None, metadata=None):
            call_count[0] += 1
            if call_count[0] == 1:
                raise StorageError("S3 upload failed")
            return object_name

        mock_storage_service.upload_file = mock_upload

        with patch("knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service):
            result = await batch_upload_attachments(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
                article_id=1,
                files=[error_file, valid_file],
            )

        # Only the valid file should be processed (error file skipped via continue)
        assert result.total_uploaded == 1
        mock_attachment_service.create_attachment.assert_called_once()


class TestGetAttachmentFileDraftPermissionDenied:
    """Test get_attachment_file permission denied for draft - covers lines 210-220."""

    async def test_get_attachment_file_draft_denied(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """
        Test getting attachment file for draft article denied for non-author - covers lines 210-220.

        This covers the specific case where:
        - Article status is DRAFT
        - User is not the author
        - User is not HR/ADMIN
        - PermissionDenied is raised
        """
        mock_article.status = ArticleStatus.DRAFT
        mock_article.author_id = 999  # Different user
        mock_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article

        with patch("knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service):
            with pytest.raises(PermissionDenied) as exc_info:
                await get_attachment_file(
                    article_id=1,
                    filename="test.pdf",
                    article_service=mock_article_service,
                    current_user=mock_user,
                )

            assert "Access denied" in str(exc_info.value.detail)
        # Storage should not be called when permission is denied
        mock_storage_service.get_presigned_url.assert_not_called()
