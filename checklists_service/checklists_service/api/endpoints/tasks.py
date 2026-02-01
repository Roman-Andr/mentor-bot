"""Task management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from checklists_service.api import CurrentUser, DatabaseSession, HRUser
from checklists_service.core import NotFoundException, PermissionDenied, ValidationException
from checklists_service.schemas import (
    MessageResponse,
    TaskBulkUpdate,
    TaskProgress,
    TaskResponse,
    TaskUpdate,
)
from checklists_service.services import ChecklistService, TaskService

router = APIRouter()


@router.get("/checklist/{checklist_id}")
async def get_checklist_tasks(  # noqa: PLR0913
    checklist_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
    status: Annotated[str | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
    *,
    overdue_only: Annotated[bool, Query()] = False,
) -> list[TaskResponse]:
    """Get tasks for a specific checklist."""
    task_service = TaskService(db)

    try:
        tasks = await task_service.get_checklist_tasks(
            checklist_id=checklist_id,
            status=status,
            category=category,
            overdue_only=overdue_only,
        )

        # Check permissions via checklist
        checklist_service = ChecklistService(db)
        checklist = await checklist_service.get_checklist(checklist_id)

        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot view other users' tasks"
            raise PermissionDenied(msg)

        return [TaskResponse.model_validate(task) for task in tasks]
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/assigned-to-me")
async def get_my_assigned_tasks(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str | None, Query()] = None,
) -> list[TaskResponse]:
    """Get tasks assigned to current user."""
    task_service = TaskService(db)

    tasks, _ = await task_service.get_assigned_tasks(
        assignee_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
    )

    return [TaskResponse.model_validate(task) for task in tasks]


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Update task."""
    task_service = TaskService(db)

    try:
        task = await task_service.get_task(task_id)

        # Check permissions via checklist
        checklist_service = ChecklistService(db)
        checklist = await checklist_service.get_checklist(task.checklist_id)

        can_update = current_user.id in (checklist.user_id, task.assignee_id) or current_user.role in ["HR", "ADMIN"]

        if not can_update:
            msg = "Cannot update this task"
            raise PermissionDenied(msg)

        updated_task = await task_service.update_task(task_id, task_data)
        return TaskResponse.model_validate(updated_task)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{task_id}/progress")
async def update_task_progress(
    task_id: int,
    progress_data: TaskProgress,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Update task progress."""
    task_service = TaskService(db)

    try:
        task = await task_service.get_task(task_id)

        # Check permissions
        can_update = task.assignee_id == current_user.id or current_user.role in ["HR", "ADMIN"]

        if not can_update:
            msg = "Cannot update progress for this task"
            raise PermissionDenied(msg)

        updated_task = await task_service.update_task_progress(task_id, progress_data)
        return TaskResponse.model_validate(updated_task)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{task_id}/complete")
async def complete_task(
    task_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
    completion_notes: str | None = None,
) -> TaskResponse:
    """Mark task as completed."""
    task_service = TaskService(db)

    try:
        task = await task_service.get_task(task_id)

        # Check permissions
        can_complete = task.assignee_id == current_user.id or current_user.role in ["HR", "ADMIN"]

        if not can_complete:
            msg = "Cannot complete this task"
            raise PermissionDenied(msg)

        completed_task = await task_service.complete_task(task_id, current_user.id, completion_notes)
        return TaskResponse.model_validate(completed_task)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/bulk-update")
async def bulk_update_tasks(
    bulk_data: TaskBulkUpdate,
    db: DatabaseSession,
    _current_user: HRUser,
) -> MessageResponse:
    """Bulk update tasks (HR/admin only)."""
    task_service = TaskService(db)

    try:
        await task_service.bulk_update_tasks(bulk_data)
        return MessageResponse(message=f"Updated {len(bulk_data.task_ids)} tasks")
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.get("/{task_id}/dependencies")
async def get_task_dependencies(
    task_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict:
    """Get task dependencies and blockers."""
    task_service = TaskService(db)

    try:
        task = await task_service.get_task(task_id)

        # Check permissions via checklist
        checklist_service = ChecklistService(db)
        checklist = await checklist_service.get_checklist(task.checklist_id)

        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot view this task"
            raise PermissionDenied(msg)

        return await task_service.get_task_dependencies(task_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
