"""Department document management endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import RedirectResponse

from knowledge_service.api import CurrentUser, HRUser, UOWDep
from knowledge_service.config import settings
from knowledge_service.core import NotFoundException, PermissionDenied, ValidationException
from knowledge_service.core.security import validate_file_size, validate_file_type, validate_filename
from knowledge_service.models import DepartmentDocument
from knowledge_service.schemas import (
    DepartmentDocumentListResponse,
    DepartmentDocumentResponse,
    DepartmentDocumentUpdate,
    MessageResponse,
)
from knowledge_service.utils.storage import StorageError, get_storage_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/department-documents", tags=["department-documents"])


def _get_object_name(department_id: int, filename: str) -> str:
    """Generate S3 object name from department ID and filename."""
    return f"department-documents/{department_id}/{filename}"


@router.get("")
async def list_department_documents(
    department_id: Annotated[int | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
    is_public: Annotated[bool | None, Query()] = None,
    uow: UOWDep = None,
    current_user: CurrentUser = None,
) -> DepartmentDocumentListResponse:
    """List department documents with optional filters."""
    # HR/Admin can see all documents, regular users only see their department + public
    if current_user.role not in ["HR", "ADMIN"]:
        # Regular users can only see documents from their department or public documents
        if department_id and department_id != current_user.department_id:
            msg = "Access to documents from other departments is not allowed"
            raise PermissionDenied(msg)
        # Force department_id to user's department if not specified
        if not department_id and current_user.department_id:
            department_id = current_user.department_id
        # If filtering by department, also include public docs
        if department_id:
            # Get both department and public documents
            documents = await uow.department_documents.get_by_department(department_id, category=category)
            public_docs = await uow.department_documents.get_all()
            # Filter public docs by category if specified
            if category:
                public_docs = [d for d in public_docs if d.is_public and d.category == category]
            else:
                public_docs = [d for d in public_docs if d.is_public]
            # Combine and deduplicate
            all_docs = {d.id: d for d in documents + public_docs}
            documents = list(all_docs.values())
        else:
            # No department specified, only show public docs
            documents = await uow.department_documents.get_all()
            if category:
                documents = [d for d in documents if d.is_public and d.category == category]
            else:
                documents = [d for d in documents if d.is_public]
    # HR/Admin can see all documents with filters
    elif department_id:
        documents = await uow.department_documents.get_by_department(
            department_id, category=category, is_public=is_public
        )
    elif category:
        documents = await uow.department_documents.get_by_category(category)
    else:
        documents = await uow.department_documents.get_all()

    return DepartmentDocumentListResponse(
        total=len(documents), documents=[DepartmentDocumentResponse.model_validate(d) for d in documents]
    )


@router.get("/{document_id}")
async def get_department_document(
    document_id: int,
    uow: UOWDep = None,
    current_user: CurrentUser = None,
) -> DepartmentDocumentResponse:
    """Get detailed information about a department document."""
    document = await uow.department_documents.get_by_id(document_id)
    if not document:
        msg = "Document"
        raise NotFoundException(msg)

    # Check access permissions
    if current_user.role not in ["HR", "ADMIN"]:
        if not document.is_public and document.department_id != current_user.department_id:
            msg = "Access to this document is not allowed"
            raise PermissionDenied(msg)

    return DepartmentDocumentResponse.model_validate(document)


@router.post("")
async def create_department_document(
    uow: UOWDep = None,
    current_user: HRUser = None,
    department_id: Annotated[int | None, Form()] = None,
    title: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    category: Annotated[str | None, Form()] = None,
    is_public: Annotated[bool, Form()] = False,
    file: Annotated[UploadFile, File()] = None,
) -> DepartmentDocumentResponse:
    """Upload a file as a department document."""
    if not file:
        msg = "File is required"
        raise ValidationException(msg)

    file_size = file.size if file.size is not None else 0
    if not validate_file_size(file_size):
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
    object_name = _get_object_name(department_id, safe_filename)

    try:
        await storage.upload_file(
            file_data=file_content,
            object_name=object_name,
            content_type=file.content_type,
            metadata={
                "department_id": str(department_id),
                "uploaded_by": str(current_user.id),
                "original_filename": file.filename or "unknown",
            },
        )
        file_path = object_name
    except StorageError as e:
        logger.exception("Failed to upload file to S3")
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}") from e

    document = await uow.department_documents.create(
        DepartmentDocument(
            department_id=department_id,
            title=title,
            description=description,
            category=category,
            file_name=safe_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            is_public=is_public,
            uploaded_by=current_user.id,
        )
    )
    await uow.commit()
    return DepartmentDocumentResponse.model_validate(document)


@router.put("/{document_id}")
async def update_department_document(
    document_id: int,
    update_data: DepartmentDocumentUpdate,
    uow: UOWDep = None,
    current_user: HRUser = None,
) -> DepartmentDocumentResponse:
    """Update department document metadata."""
    document = await uow.department_documents.get_by_id(document_id)
    if not document:
        msg = "Document"
        raise NotFoundException(msg)

    if update_data.title is not None:
        document.title = update_data.title
    if update_data.description is not None:
        document.description = update_data.description
    if update_data.category is not None:
        document.category = update_data.category
    if update_data.is_public is not None:
        document.is_public = update_data.is_public

    updated = await uow.department_documents.update(document)
    await uow.commit()
    return DepartmentDocumentResponse.model_validate(updated)


@router.delete("/{document_id}")
async def delete_department_document(
    document_id: int,
    uow: UOWDep = None,
    current_user: HRUser = None,
) -> MessageResponse:
    """Delete a department document."""
    document = await uow.department_documents.get_by_id(document_id)
    if not document:
        msg = "Document"
        raise NotFoundException(msg)

    # Delete from S3
    storage = get_storage_service()
    object_name = document.file_path
    try:
        await storage.delete_file(object_name)
    except StorageError as e:
        logger.warning("Failed to delete file from S3 (continuing with DB deletion): %s", e)

    await uow.department_documents.delete(document_id)
    await uow.commit()
    return MessageResponse(message="Document deleted successfully")


@router.get("/{document_id}/download")
async def download_department_document(
    document_id: int,
    uow: UOWDep = None,
    current_user: CurrentUser = None,
) -> RedirectResponse:
    """Generate presigned URL for downloading a department document."""
    document = await uow.department_documents.get_by_id(document_id)
    if not document:
        msg = "Document"
        raise NotFoundException(msg)

    # Check access permissions
    if current_user.role not in ["HR", "ADMIN"]:
        if not document.is_public and document.department_id != current_user.department_id:
            msg = "Access to this document is not allowed"
            raise PermissionDenied(msg)

    # Redirect to presigned URL for direct S3 access
    storage = get_storage_service()
    object_name = document.file_path
    try:
        presigned_url = storage.get_presigned_url(object_name, expires=settings.S3_PRESIGNED_URL_EXPIRY)
        return RedirectResponse(url=presigned_url)
    except StorageError as e:
        raise NotFoundException("File not found") from e
