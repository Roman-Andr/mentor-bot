"""Template management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from checklists_service.api.deps import AdminUser, HRUser, UOWDep
from checklists_service.core import ConflictException, NotFoundException
from checklists_service.schemas import (
    MessageResponse,
    TaskTemplateCreate,
    TaskTemplateResponse,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
    TemplateWithTasks,
)
from checklists_service.services import TemplateService

router = APIRouter()


@router.get("/")
@router.get("")
async def get_templates(
    uow: UOWDep,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    department_id: Annotated[int | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    is_default: Annotated[bool | None, Query()] = None,
) -> list[TemplateResponse]:
    """Get paginated list of templates (HR/admin only)."""
    template_service = TemplateService(uow)

    templates, _ = await template_service.get_templates(
        skip=skip,
        limit=limit,
        department_id=department_id,
        status=status,
        is_default=is_default,
    )

    return [TemplateResponse.model_validate(t) for t in templates]


@router.post("/")
@router.post("")
async def create_template(
    template_data: TemplateCreate,
    uow: UOWDep,
    _current_user: AdminUser,
) -> TemplateResponse:
    """Create new template (admin only)."""
    template_service = TemplateService(uow)

    try:
        template = await template_service.create_template(template_data)
        return TemplateResponse.model_validate(template)
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.detail),
        ) from e


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    uow: UOWDep,
    _current_user: HRUser,
) -> TemplateWithTasks:
    """Get template by ID with tasks (HR/admin only)."""
    template_service = TemplateService(uow)

    try:
        template = await template_service.get_template_with_tasks(template_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    else:
        return template


@router.put("/{template_id}")
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    uow: UOWDep,
    _current_user: AdminUser,
) -> TemplateResponse:
    """Update template (admin only)."""
    template_service = TemplateService(uow)

    try:
        template = await template_service.update_template(template_id, template_data)
        return TemplateResponse.model_validate(template)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    uow: UOWDep,
    _current_user: AdminUser,
) -> MessageResponse:
    """Delete template (admin only)."""
    template_service = TemplateService(uow)

    try:
        await template_service.delete_template(template_id)
        return MessageResponse(message="Template deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{template_id}/clone")
async def clone_template(
    template_id: int,
    uow: UOWDep,
    _current_user: AdminUser,
) -> TemplateResponse:
    """Clone template with new version (admin only)."""
    template_service = TemplateService(uow)

    try:
        template = await template_service.clone_template(template_id)
        return TemplateResponse.model_validate(template)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{template_id}/tasks")
async def add_task_to_template(
    template_id: int,
    task_data: TaskTemplateCreate,
    uow: UOWDep,
    _current_user: AdminUser,
) -> TaskTemplateResponse:
    """Add task to template (admin only)."""
    template_service = TemplateService(uow)

    try:
        task = await template_service.add_task_to_template(template_id, task_data)
        return TaskTemplateResponse.model_validate(task)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{template_id}/publish")
async def publish_template(
    template_id: int,
    uow: UOWDep,
    _current_user: AdminUser,
) -> TemplateResponse:
    """Publish template (set to active) (admin only)."""
    template_service = TemplateService(uow)

    try:
        template = await template_service.publish_template(template_id)
        return TemplateResponse.model_validate(template)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
