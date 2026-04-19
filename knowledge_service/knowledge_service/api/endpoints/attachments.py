"""Attachment management endpoints."""

import logging
from contextlib import suppress
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

from knowledge_service.api import ArticleServiceDep, AttachmentServiceDep, CurrentUser
from knowledge_service.config import settings
from knowledge_service.core import NotFoundException, PermissionDenied, ValidationException
from knowledge_service.core.enums import ArticleStatus, AttachmentType
from knowledge_service.core.security import validate_file_size, validate_file_type, validate_filename
from knowledge_service.schemas import (
    AttachmentListResponse,
    AttachmentResponse,
    BatchUploadResponse,
    FileUploadError,
    MessageResponse,
)
from knowledge_service.utils import StorageError, get_storage_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/attachments", tags=["attachments"])


def _get_object_name(article_id: int, filename: str) -> str:
    """Generate S3 object name from article ID and filename."""
    return f"articles/{article_id}/{filename}"


@router.get("/article/{article_id}")
async def list_article_attachments(
    article_id: int,
    article_service: ArticleServiceDep,
    attachment_service: AttachmentServiceDep,
    current_user: CurrentUser,
) -> AttachmentListResponse:
    """List all attachments for an article."""
    article = await article_service.get_article_by_id(article_id)

    if (
        article.status != ArticleStatus.PUBLISHED
        and article.author_id != current_user.id
        and current_user.role not in ["HR", "ADMIN"]
    ):
        msg = "Access denied"
        raise PermissionDenied(msg)

    if (
        current_user.role not in ["HR", "ADMIN"]
        and article.author_id != current_user.id
        and article.department_id
        and article.department_id != current_user.department_id
    ):
        msg = "Access to attachments from other departments is not allowed"
        raise PermissionDenied(msg)

    attachments = await attachment_service.get_attachments_by_article(article_id)

    # Generate presigned URLs for each attachment
    storage = get_storage_service()
    for attachment in attachments:
        if attachment.type == AttachmentType.FILE:
            object_name = _get_object_name(attachment.article_id, attachment.name)
            with suppress(StorageError):
                attachment.url = storage.get_presigned_url(
                    object_name,
                    expires=settings.S3_PRESIGNED_URL_EXPIRY,
                )

    return AttachmentListResponse(
        total=len(attachments),
        attachments=[AttachmentResponse.model_validate(a) for a in attachments],
    )


@router.post("/upload")
async def upload_attachment(
    article_service: ArticleServiceDep,
    attachment_service: AttachmentServiceDep,
    current_user: CurrentUser,
    article_id: Annotated[int, Form()],
    file: Annotated[UploadFile, File()],
    description: Annotated[str | None, Form()] = None,
    order: Annotated[int, Form()] = 0,
    *,
    is_downloadable: Annotated[bool, Form()] = True,
) -> AttachmentResponse:
    """Upload a file as attachment to an article."""
    article = await article_service.get_article_by_id(article_id)
    if article.author_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
        msg = "Cannot attach files to other users' articles"
        raise PermissionDenied(msg)

    if not validate_file_size(file.size or 0):
        msg = f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
        raise ValidationException(msg)
    if not validate_file_type(file.filename or ""):
        msg = f"File type not allowed. Allowed: {settings.ALLOWED_FILE_TYPES}"
        raise ValidationException(msg)

    safe_filename = validate_filename(file.filename or "unknown")

    # Read file content
    file_content = await file.read()

    # Upload to S3
    storage = get_storage_service()
    object_name = _get_object_name(article_id, safe_filename)

    try:
        await storage.upload_file(
            file_data=file_content,
            object_name=object_name,
            content_type=file.content_type,
            metadata={
                "article_id": str(article_id),
                "uploaded_by": str(current_user.id),
                "original_filename": file.filename or "unknown",
            },
        )
        # Use presigned URL for immediate access
        file_url = storage.get_presigned_url(object_name, expires=settings.S3_PRESIGNED_URL_EXPIRY)
    except StorageError as e:
        logger.error("Failed to upload file to S3: %s", e)
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}") from e

    attachment = await attachment_service.create_attachment(
        article_id=article_id,
        name=safe_filename,
        attachment_type=AttachmentType.FILE,
        url=file_url,
        file_size=file.size,
        mime_type=file.content_type,
        description=description,
        order=order,
        is_downloadable=is_downloadable,
    )
    return AttachmentResponse.model_validate(attachment)


@router.post("/batch-upload")
async def batch_upload_attachments(
    article_service: ArticleServiceDep,
    attachment_service: AttachmentServiceDep,
    current_user: CurrentUser,
    article_id: Annotated[int, Form()],
    files: Annotated[list[UploadFile], File()],
) -> BatchUploadResponse:
    """
    Upload multiple files as attachments to an article.

    Returns detailed information about successful uploads and failures.
    """
    article = await article_service.get_article_by_id(article_id)
    if article.author_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
        msg = "Cannot attach files to other users' articles"
        raise PermissionDenied(msg)

    created_attachments = []
    upload_errors = []
    storage = get_storage_service()

    for file in files:
        filename = file.filename or "unknown"

        if not validate_file_size(file.size or 0):
            upload_errors.append(
                FileUploadError(
                    filename=filename,
                    error=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB} MB",
                )
            )
            continue

        if not validate_file_type(filename):
            upload_errors.append(
                FileUploadError(
                    filename=filename,
                    error="File type not allowed",
                )
            )
            continue

        safe_filename = validate_filename(filename)
        file_content = await file.read()

        object_name = _get_object_name(article_id, safe_filename)
        try:
            await storage.upload_file(
                file_data=file_content,
                object_name=object_name,
                content_type=file.content_type,
                metadata={
                    "article_id": str(article_id),
                    "uploaded_by": str(current_user.id),
                    "original_filename": filename,
                },
            )
            file_url = storage.get_presigned_url(object_name, expires=settings.S3_PRESIGNED_URL_EXPIRY)
        except StorageError as e:
            upload_errors.append(
                FileUploadError(
                    filename=filename,
                    error=f"Storage upload failed: {e!s}",
                )
            )
            continue

        attachment = await attachment_service.create_attachment(
            article_id=article_id,
            name=safe_filename,
            attachment_type=AttachmentType.FILE,
            url=file_url,
            file_size=file.size,
            mime_type=file.content_type,
            description=None,
            order=0,
            is_downloadable=True,
        )
        created_attachments.append(AttachmentResponse.model_validate(attachment))

    return BatchUploadResponse(
        total_uploaded=len(created_attachments),
        total_failed=len(upload_errors),
        attachments=created_attachments,
        errors=upload_errors,
    )


@router.get("/file/{article_id}/{filename}")
async def get_attachment_file(
    article_id: int,
    filename: str,
    article_service: ArticleServiceDep,
    current_user: CurrentUser,
) -> RedirectResponse:
    """Serve attachment file via S3 presigned URL."""
    article = await article_service.get_article_by_id(article_id)
    if (
        article.status != ArticleStatus.PUBLISHED
        and article.author_id != current_user.id
        and current_user.role not in ["HR", "ADMIN"]
    ):
        msg = "Access denied"
        raise PermissionDenied(msg)

    if (
        current_user.role not in ["HR", "ADMIN"]
        and article.author_id != current_user.id
        and article.department_id
        and article.department_id != current_user.department_id
    ):
        msg = "Access to attachments from other departments is not allowed"
        raise PermissionDenied(msg)

    # Redirect to presigned URL for direct S3 access
    storage = get_storage_service()
    object_name = _get_object_name(article_id, filename)
    try:
        presigned_url = storage.get_presigned_url(
            object_name,
            expires=settings.S3_PRESIGNED_URL_EXPIRY,
        )
        return RedirectResponse(url=presigned_url)
    except StorageError as e:
        raise NotFoundException("File not found") from e


@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    article_service: ArticleServiceDep,
    attachment_service: AttachmentServiceDep,
    current_user: CurrentUser,
) -> MessageResponse:
    """Delete an attachment."""
    attachment = await attachment_service.get_attachment(attachment_id)

    article = await article_service.get_article_by_id(attachment.article_id)
    if article.author_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
        msg = "Cannot delete other users' attachments"
        raise PermissionDenied(msg)

    # Delete from S3
    storage = get_storage_service()
    object_name = _get_object_name(attachment.article_id, attachment.name)
    try:
        await storage.delete_file(object_name)
    except StorageError as e:
        logger.warning("Failed to delete file from S3 (continuing with DB deletion): %s", e)

    await attachment_service.delete_attachment(attachment_id)
    return MessageResponse(message="Attachment deleted successfully")
