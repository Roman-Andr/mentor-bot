"""Tests for attachment API endpoints."""

import io
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from knowledge_service.api.deps import UserInfo
from knowledge_service.api.endpoints.attachments import (
    batch_upload_attachments,
    delete_attachment,
    get_attachment_file,
    list_article_attachments,
    upload_attachment,
)
from knowledge_service.core import ArticleStatus, NotFoundException, PermissionDenied, ValidationException
from knowledge_service.models import Article, Attachment

if TYPE_CHECKING:
    pass


class TestListArticleAttachments:
    """Test GET /attachments/article/{article_id} endpoint."""

    async def test_list_attachments_success(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test successful retrieval of article attachments."""
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await list_article_attachments(
                article_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
            )

        assert result.total == 1
        assert len(result.attachments) == 1
        mock_article_service.get_article_by_id.assert_called_once_with(1)
        mock_attachment_service.get_attachments_by_article.assert_called_once_with(1)

    async def test_list_attachments_published_article(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test anyone can view attachments for published articles."""
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.author_id = 999  # Different user
        mock_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await list_article_attachments(
                article_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
            )

        assert result.total == 1

    async def test_list_attachments_draft_denied(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test non-author cannot view attachments for draft articles."""
        mock_article.status = ArticleStatus.DRAFT
        mock_article.author_id = 999  # Different user
        mock_article_service.get_article_by_id.return_value = mock_article

        with pytest.raises(PermissionDenied):
            await list_article_attachments(
                article_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
            )

    async def test_list_attachments_other_department_denied(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test user cannot view attachments from other departments."""
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.author_id = 999
        mock_article.department_id = 999  # Different department
        mock_article_service.get_article_by_id.return_value = mock_article

        with pytest.raises(PermissionDenied):
            await list_article_attachments(
                article_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
            )


class TestUploadAttachment:
    """Test POST /attachments/upload endpoint."""

    async def test_upload_attachment_success(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test successful file upload."""
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        # Create a mock file
        file_content = b"Test file content"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_document.pdf"
        mock_file.size = len(file_content)
        mock_file.content_type = "application/pdf"
        mock_file.file = io.BytesIO(file_content)

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await upload_attachment(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
                article_id=1,
                file=mock_file,
            )

        assert result.name == "test_file.pdf"
        mock_attachment_service.create_attachment.assert_called_once()
        mock_storage_service.upload_file.assert_called_once()

    async def test_upload_attachment_as_admin(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_admin_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test admin can upload to any article."""
        mock_article.author_id = 999  # Different user
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "admin_upload.pdf"
        mock_file.size = 1024
        mock_file.content_type = "application/pdf"
        mock_file.file = io.BytesIO(b"admin content")

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await upload_attachment(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_admin_user,
                article_id=1,
                file=mock_file,
            )

        assert result is not None
        mock_storage_service.upload_file.assert_called_once()

    async def test_upload_to_other_user_article_denied(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test user cannot upload to others' articles."""
        mock_article.author_id = 999  # Different user
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "hack.pdf"

        with pytest.raises(PermissionDenied):
            await upload_attachment(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
                article_id=1,
                file=mock_file,
            )

    async def test_upload_attachment_invalid_size(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test upload with oversized file."""
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "huge.pdf"
        mock_file.size = 100 * 1024 * 1024  # 100MB
        mock_file.content_type = "application/pdf"
        # Mock the read() method to return content of the specified size
        mock_file.read = AsyncMock(return_value=b"x" * (100 * 1024 * 1024))

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            with pytest.raises(ValidationException) as exc_info:
                await upload_attachment(
                    article_service=mock_article_service,
                    attachment_service=mock_attachment_service,
                    current_user=mock_user,
                    article_id=1,
                    file=mock_file,
                )

        assert "File size exceeds" in str(exc_info.value.detail)

    async def test_upload_attachment_invalid_type(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test upload with invalid file type."""
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "virus.exe"
        mock_file.size = 1024

        with pytest.raises(ValidationException) as exc_info:
            await upload_attachment(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
                article_id=1,
                file=mock_file,
            )

        assert "File type not allowed" in str(exc_info.value.detail)


class TestBatchUploadAttachments:
    """Test POST /attachments/batch-upload endpoint."""

    async def test_batch_upload_success(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test successful batch upload."""
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_file1 = MagicMock(spec=UploadFile)
        mock_file1.filename = "file1.pdf"
        mock_file1.size = 1024
        mock_file1.content_type = "application/pdf"
        mock_file1.file = io.BytesIO(b"content1")

        mock_file2 = MagicMock(spec=UploadFile)
        mock_file2.filename = "file2.png"
        mock_file2.size = 2048
        mock_file2.content_type = "image/png"
        mock_file2.file = io.BytesIO(b"content2")

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await batch_upload_attachments(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
                article_id=1,
                files=[mock_file1, mock_file2],
            )

        assert result.total_uploaded == 2
        assert mock_storage_service.upload_file.call_count == 2

    async def test_batch_upload_skips_invalid_files(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test batch upload skips invalid files."""
        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        valid_file = MagicMock(spec=UploadFile)
        valid_file.filename = "valid.pdf"
        valid_file.size = 1024
        valid_file.content_type = "application/pdf"
        valid_file.file = io.BytesIO(b"valid content")

        invalid_file = MagicMock(spec=UploadFile)
        invalid_file.filename = "invalid.exe"
        invalid_file.size = 1024
        invalid_file.content_type = "application/x-msdownload"
        invalid_file.file = io.BytesIO(b"invalid content")

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await batch_upload_attachments(
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
                article_id=1,
                files=[valid_file, invalid_file],
            )

        # Only valid file should be processed
        assert result.total_uploaded == 1
        mock_storage_service.upload_file.assert_called_once()


class TestGetAttachmentFile:
    """Test GET /attachments/file/{article_id}/{filename} endpoint."""

    async def test_get_attachment_file_success(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test successful file download redirects to presigned URL."""
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_storage_service.get_presigned_url.return_value = (
            "http://localhost:9000/test-bucket/articles/1/test_file.pdf?signature=abc"
        )

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await get_attachment_file(
                article_id=1,
                filename="test_file.pdf",
                article_service=mock_article_service,
                current_user=mock_user,
            )

        assert isinstance(result, RedirectResponse)
        assert "test_file.pdf" in result.headers["location"]
        mock_storage_service.get_presigned_url.assert_called_once_with("articles/1/test_file.pdf", expires=3600)

    async def test_get_attachment_file_not_found(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test downloading non-existent file raises NotFoundException."""
        from knowledge_service.utils.storage import StorageError

        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_storage_service.get_presigned_url.side_effect = StorageError("File not found")

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            with pytest.raises(NotFoundException):
                await get_attachment_file(
                    article_id=1,
                    filename="nonexistent.pdf",
                    article_service=mock_article_service,
                    current_user=mock_user,
                )


class TestDeleteAttachment:
    """Test DELETE /attachments/{attachment_id} endpoint."""

    async def test_delete_attachment_success(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
        mock_attachment: Attachment,
    ) -> None:
        """Test successful attachment deletion by author."""
        mock_attachment.article_id = 1
        mock_attachment.name = "test_file.pdf"
        mock_attachment_service.get_attachment.return_value = mock_attachment

        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await delete_attachment(
                attachment_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
            )

        assert result.message == "Attachment deleted successfully"
        mock_attachment_service.delete_attachment.assert_called_once_with(1)
        mock_storage_service.delete_file.assert_called_once_with("articles/1/test_file.pdf")

    async def test_delete_attachment_as_admin(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_admin_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
        mock_attachment: Attachment,
    ) -> None:
        """Test admin can delete any attachment."""
        mock_attachment.article_id = 1
        mock_attachment.name = "admin_delete.pdf"
        mock_attachment_service.get_attachment.return_value = mock_attachment

        mock_article.author_id = 999  # Different user
        mock_article_service.get_article_by_id.return_value = mock_article

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await delete_attachment(
                attachment_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_admin_user,
            )

        assert result.message == "Attachment deleted successfully"
        mock_storage_service.delete_file.assert_called_once_with("articles/1/admin_delete.pdf")

    async def test_delete_other_user_attachment_denied(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
        mock_attachment: Attachment,
    ) -> None:
        """Test non-author cannot delete others' attachments."""
        mock_attachment.article_id = 1
        mock_attachment_service.get_attachment.return_value = mock_attachment

        mock_article.author_id = 999  # Different user
        mock_article_service.get_article_by_id.return_value = mock_article

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            with pytest.raises(PermissionDenied):
                await delete_attachment(
                    attachment_id=1,
                    article_service=mock_article_service,
                    attachment_service=mock_attachment_service,
                    current_user=mock_user,
                )

        # Storage delete should not be called when permission denied
        mock_storage_service.delete_file.assert_not_called()


class TestUploadAttachmentFileSaveError:
    """Test file save error handling in upload."""

    async def test_upload_attachment_s3_error(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test handling of S3 upload error during upload."""
        from knowledge_service.utils.storage import StorageError

        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.size = 1024
        mock_file.content_type = "application/pdf"
        mock_file.file = io.BytesIO(b"test content")

        mock_storage_service.upload_file.side_effect = StorageError("S3 upload failed")

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            with pytest.raises(HTTPException) as exc_info:
                await upload_attachment(
                    article_service=mock_article_service,
                    attachment_service=mock_attachment_service,
                    current_user=mock_user,
                    article_id=1,
                    file=mock_file,
                )

            assert exc_info.value.status_code == 500
            assert "File upload failed" in exc_info.value.detail


class TestGetAttachmentFileAccessControl:
    """Test access control for get_attachment_file endpoint."""

    async def test_get_attachment_file_draft_as_author(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test author can access draft article attachments."""
        mock_article.status = ArticleStatus.DRAFT
        mock_article.author_id = mock_user.id
        mock_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_storage_service.get_presigned_url.return_value = (
            "http://localhost:9000/test-bucket/articles/1/test_file.pdf?signature=abc"
        )

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await get_attachment_file(
                article_id=1,
                filename="test_file.pdf",
                article_service=mock_article_service,
                current_user=mock_user,
            )

            assert isinstance(result, RedirectResponse)

    async def test_get_attachment_file_draft_as_hr(
        self,
        mock_article_service: AsyncMock,
        mock_hr_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test HR can access draft article attachments."""
        mock_article.status = ArticleStatus.DRAFT
        mock_article.author_id = 999  # Different user
        mock_article.department_id = mock_hr_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_storage_service.get_presigned_url.return_value = (
            "http://localhost:9000/test-bucket/articles/1/hr_file.pdf?signature=abc"
        )

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await get_attachment_file(
                article_id=1,
                filename="hr_file.pdf",
                article_service=mock_article_service,
                current_user=mock_hr_user,
            )

            assert isinstance(result, RedirectResponse)

    async def test_get_attachment_file_other_department_denied(
        self,
        mock_article_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test user cannot access attachments from other departments."""
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.author_id = 999  # Different user
        mock_article.department_id = 888  # Different department
        mock_article_service.get_article_by_id.return_value = mock_article

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            with pytest.raises(PermissionDenied) as exc_info:
                await get_attachment_file(
                    article_id=1,
                    filename="test.pdf",
                    article_service=mock_article_service,
                    current_user=mock_user,
                )

            assert "other departments" in str(exc_info.value.detail)

    async def test_get_attachment_file_published_other_dept_as_admin(
        self,
        mock_article_service: AsyncMock,
        mock_admin_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test admin can access attachments from any department."""
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.author_id = 999
        mock_article.department_id = 888  # Different department
        mock_article_service.get_article_by_id.return_value = mock_article

        mock_storage_service.get_presigned_url.return_value = (
            "http://localhost:9000/test-bucket/articles/1/admin_access.pdf?signature=abc"
        )

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await get_attachment_file(
                article_id=1,
                filename="admin_access.pdf",
                article_service=mock_article_service,
                current_user=mock_admin_user,
            )

            assert isinstance(result, RedirectResponse)


class TestListAttachmentsStorageError:
    """Test StorageError handling for list_article_attachments - covers lines 65-67."""

    async def test_list_attachments_presigned_url_error_ignored(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: MagicMock,
        mock_article: Article,
        mock_attachment: Attachment,
    ) -> None:
        """
        Test that StorageError when generating presigned URL is ignored - covers lines 65-67.

        When get_presigned_url raises StorageError, the original URL should be kept.
        """
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.department_id = mock_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article
        mock_attachment_service.get_attachments_by_article.return_value = [mock_attachment]

        # Make get_presigned_url raise StorageError
        from knowledge_service.utils.storage import StorageError

        mock_storage_service.get_presigned_url.side_effect = StorageError("Failed to generate URL")

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await list_article_attachments(
                article_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
            )

        # Should still return the attachment with original URL
        assert result.total == 1
        assert len(result.attachments) == 1


class TestDeleteAttachmentStorageError:
    """Test StorageError handling for delete_attachment - covers lines 260-261."""

    async def test_delete_attachment_s3_error_continues(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_storage_service: MagicMock,
        mock_article: Article,
        mock_attachment: Attachment,
    ) -> None:
        """
        Test that StorageError when deleting from S3 is logged but continues - covers lines 260-261.

        When delete_file raises StorageError, DB deletion should still proceed.
        """
        from knowledge_service.utils.storage import StorageError

        mock_attachment.article_id = 1
        mock_attachment.name = "test_file.pdf"
        mock_attachment_service.get_attachment.return_value = mock_attachment

        mock_article.author_id = mock_user.id
        mock_article_service.get_article_by_id.return_value = mock_article

        # Make delete_file raise StorageError
        mock_storage_service.delete_file.side_effect = StorageError("S3 delete failed")

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await delete_attachment(
                attachment_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
            )

        # Should still return success message even if S3 delete failed
        assert result.message == "Attachment deleted successfully"
        # DB deletion should still be called
        mock_attachment_service.delete_attachment.assert_called_once_with(1)


class TestListAttachmentsAccessControl:
    """Test access control for list_article_attachments endpoint."""

    async def test_list_attachments_draft_as_hr_allowed(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_hr_user: UserInfo,
        mock_storage_service: AsyncMock,
        mock_article: Article,
    ) -> None:
        """Test HR can access draft article attachments."""
        mock_article.status = ArticleStatus.DRAFT
        mock_article.author_id = 999  # Different user
        mock_article.department_id = mock_hr_user.department_id
        mock_article_service.get_article_by_id.return_value = mock_article

        with patch(
            "knowledge_service.api.endpoints.attachments.get_storage_service", return_value=mock_storage_service
        ):
            result = await list_article_attachments(
                article_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_hr_user,
            )

        assert result.total == 1

    async def test_list_attachments_other_department_denied(
        self,
        mock_article_service: AsyncMock,
        mock_attachment_service: AsyncMock,
        mock_user: UserInfo,
        mock_article: Article,
    ) -> None:
        """Test user cannot list attachments from other departments."""
        mock_article.status = ArticleStatus.PUBLISHED
        mock_article.author_id = 999
        mock_article.department_id = 888  # Different department
        mock_article_service.get_article_by_id.return_value = mock_article

        with pytest.raises(PermissionDenied) as exc_info:
            await list_article_attachments(
                article_id=1,
                article_service=mock_article_service,
                attachment_service=mock_attachment_service,
                current_user=mock_user,
            )

        assert "other departments" in str(exc_info.value.detail)
