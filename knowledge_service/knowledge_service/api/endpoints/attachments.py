"""Attachment management endpoints."""

import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from knowledge_service.api import ArticleServiceDep, AttachmentServiceDep, CurrentUser
from knowledge_service.config import settings
from knowledge_service.core import NotFoundException, PermissionDenied, ValidationException
from knowledge_service.core.enums import ArticleStatus, AttachmentType
from knowledge_service.core.security import validate_file_size, validate_file_type, validate_filename
from knowledge_service.schemas import AttachmentResponse, MessageResponse

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.post("/upload")
async def upload_attachment(
    article_service: ArticleServiceDep,
    attachment_service: AttachmentServiceDep,
    current_user: CurrentUser,
    article_id: Annotated[int, Form()],
    file: Annotated[UploadFile, File()],
    description: Annotated[str | None, Form()] = None,
    order: Annotated[int, Form()] = 0,
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
    storage_path = Path(settings.STORAGE_PATH) / str(article_id)
    storage_path.mkdir(parents=True, exist_ok=True)

    file_path = storage_path / safe_filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {e}") from e

    attachment = await attachment_service.create_attachment(
        article_id=article_id,
        name=safe_filename,
        attachment_type=AttachmentType.FILE,
        url=f"/api/v1/attachments/file/{article_id}/{safe_filename}",
        file_size=file.size,
        mime_type=file.content_type,
        description=description,
        order=order,
        is_downloadable=is_downloadable,
    )
    return AttachmentResponse.model_validate(attachment)


@router.get("/file/{article_id}/{filename}")
async def get_attachment_file(
    article_id: int,
    filename: str,
    article_service: ArticleServiceDep,
    current_user: CurrentUser,
) -> FileResponse:
    """Serve attachment file."""
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
        and article.department
        and article.department != current_user.department
    ):
        msg = "Access to attachments from other departments is not allowed"
        raise PermissionDenied(msg)

    file_path = Path(settings.STORAGE_PATH) / str(article_id) / filename
    if not file_path.exists():
        msg = "File not found"
        raise NotFoundException(msg)

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


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

    file_path = Path(settings.STORAGE_PATH) / str(attachment.article_id) / attachment.name
    if file_path.exists():
        file_path.unlink()

    await attachment_service.delete_attachment(attachment_id)
    return MessageResponse(message="Attachment deleted successfully")
