"""Audit endpoints for checklists service."""

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel, SerializeAsAny

from checklists_service.api.deps import CurrentUser, UnitOfWorkDep
from checklists_service.core import PermissionDenied

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas for audit responses
class ChecklistStatusEntry(BaseModel):
    """Checklist status history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    checklist_id: int
    user_id: int
    action: str
    old_status: str | None = None
    new_status: str | None = None
    changed_at: datetime
    changed_by: int | None = None
    meta_data: dict | None = None


class TaskCompletionEntry(BaseModel):
    """Task completion history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    task_id: int
    checklist_id: int
    user_id: int
    completed_at: datetime
    completion_notes: str | None = None
    attachments: dict | None = None
    completed_by: int | None = None


class TemplateChangeEntry(BaseModel):
    """Template change history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    template_id: int
    action: str
    old_name: str | None = None
    new_name: str | None = None
    changed_at: datetime
    changed_by: int | None = None
    change_summary: str | None = None


class AuditResponse(BaseModel):
    """Generic audit response with pagination."""

    items: Sequence[SerializeAsAny[BaseModel]]
    total: int


def require_hr_or_admin(current_user: CurrentUser) -> None:
    """Require HR or Admin role for audit access."""
    if current_user.role not in ("HR", "ADMIN"):
        raise PermissionDenied("Access denied: HR or Admin role required")


@router.get("/checklist-status-history", response_model=AuditResponse)
async def get_checklist_status_history(
    current_user: CurrentUser,
    uow: UnitOfWorkDep,
    checklist_id: Annotated[int | None, Query()] = None,
    user_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get checklist status history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if checklist_id:
        items = await uow.checklist_status_history.get_by_checklist_id(
            checklist_id=checklist_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    elif user_id:
        items = await uow.checklist_status_history.get_by_user_id(user_id=user_id, from_date=from_date, to_date=to_date)
        total = len(items)
    else:
        items, total = await uow.checklist_status_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[ChecklistStatusEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/task-completion-history", response_model=AuditResponse)
async def get_task_completion_history(
    current_user: CurrentUser,
    uow: UnitOfWorkDep,
    task_id: Annotated[int | None, Query()] = None,
    checklist_id: Annotated[int | None, Query()] = None,
    user_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get task completion history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if task_id:
        items = await uow.task_completion_history.get_by_task_id(task_id=task_id, from_date=from_date, to_date=to_date)
        total = len(items)
    elif checklist_id:
        items = await uow.task_completion_history.get_by_checklist_id(
            checklist_id=checklist_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    elif user_id:
        items = await uow.task_completion_history.get_by_user_id(user_id=user_id, from_date=from_date, to_date=to_date)
        total = len(items)
    else:
        items, total = await uow.task_completion_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[TaskCompletionEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/template-change-history", response_model=AuditResponse)
async def get_template_change_history(
    current_user: CurrentUser,
    uow: UnitOfWorkDep,
    template_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get template change history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if template_id:
        items = await uow.template_change_history.get_by_template_id(
            template_id=template_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.template_change_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[TemplateChangeEntry.model_validate(item) for item in items],
        total=total,
    )
