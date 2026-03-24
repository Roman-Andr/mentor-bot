"""Task management endpoints."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from checklists_service.api.deps import CurrentUser, HRUser, UOWDep
from checklists_service.core import NotFoundException, PermissionDenied, ValidationException
from checklists_service.core.enums import TaskStatus
from checklists_service.models import Task
from checklists_service.schemas import (
    MessageResponse,
    TaskBulkUpdate,
    TaskProgress,
    TaskResponse,
    TaskUpdate,
)
from checklists_service.services import ChecklistService, TaskService

router = APIRouter()


async def _build_task_response(task: Task, uow: UOWDep) -> TaskResponse:
    """Build a TaskResponse with computed fields from a Task ORM object."""
    now = datetime.now(UTC)

    is_overdue = task.due_date < now and task.status != TaskStatus.COMPLETED

    deps_completed = True
    if task.depends_on:
        deps = await uow.tasks.find_by_ids(task.depends_on)
        dep_status = {t.id: t.status for t in deps}
        deps_completed = all(s == TaskStatus.COMPLETED for s in dep_status.values())

    can_start = task.status == TaskStatus.PENDING and deps_completed
    can_complete = task.status != TaskStatus.COMPLETED and deps_completed

    return TaskResponse(
        id=task.id,
        checklist_id=task.checklist_id,
        template_task_id=task.template_task_id,
        title=task.title,
        description=task.description,
        category=task.category,
        order=task.order,
        assignee_id=task.assignee_id,
        assignee_role=task.assignee_role,
        due_date=task.due_date,
        depends_on=task.depends_on,
        status=task.status,
        started_at=task.started_at,
        completed_at=task.completed_at,
        completed_by=task.completed_by,
        completion_notes=task.completion_notes,
        attachments=task.attachments,
        blocks=task.blocks,
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_overdue=is_overdue,
        can_start=can_start,
        can_complete=can_complete,
    )


@router.get("/checklist/{checklist_id}")
async def get_checklist_tasks(
    checklist_id: int,
    uow: UOWDep,
    current_user: CurrentUser,
    status: Annotated[str | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
    *,
    overdue_only: Annotated[bool, Query()] = False,
) -> list[TaskResponse]:
    """Get tasks for a specific checklist."""
    task_service = TaskService(uow)
    checklist_service = ChecklistService(uow)

    try:
        tasks = await task_service.get_checklist_tasks(
            checklist_id=checklist_id,
            status=status,
            category=category,
            overdue_only=overdue_only,
        )

        checklist = await checklist_service.get_checklist(checklist_id)

        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot view other users' tasks"
            raise PermissionDenied(msg)

        responses = []
        for task in tasks:
            response = await _build_task_response(task, uow)
            responses.append(response)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    else:
        return responses


@router.get("/assigned-to-me")
async def get_my_assigned_tasks(
    uow: UOWDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[str | None, Query()] = None,
) -> list[TaskResponse]:
    """Get tasks assigned to current user."""
    task_service = TaskService(uow)

    tasks, _ = await task_service.get_assigned_tasks(
        assignee_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
    )

    now = datetime.now(UTC)
    responses = []
    for task in tasks:
        is_overdue = task.due_date < now and task.status != TaskStatus.COMPLETED
        can_start = False
        can_complete = False

        response = TaskResponse(
            id=task.id,
            checklist_id=task.checklist_id,
            template_task_id=task.template_task_id,
            title=task.title,
            description=task.description,
            category=task.category,
            order=task.order,
            assignee_id=task.assignee_id,
            assignee_role=task.assignee_role,
            due_date=task.due_date,
            depends_on=task.depends_on,
            status=task.status,
            started_at=task.started_at,
            completed_at=task.completed_at,
            completed_by=task.completed_by,
            completion_notes=task.completion_notes,
            attachments=task.attachments,
            blocks=task.blocks,
            created_at=task.created_at,
            updated_at=task.updated_at,
            is_overdue=is_overdue,
            can_start=can_start,
            can_complete=can_complete,
        )
        responses.append(response)

    return responses


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    uow: UOWDep,
    current_user: CurrentUser,
) -> TaskResponse:
    """Update task."""
    task_service = TaskService(uow)
    checklist_service = ChecklistService(uow)

    try:
        task = await task_service.get_task(task_id)

        checklist = await checklist_service.get_checklist(task.checklist_id)
        can_update = current_user.id in (checklist.user_id, task.assignee_id) or current_user.role in ["HR", "ADMIN"]
        if not can_update:
            msg = "Cannot update this task"
            raise PermissionDenied(msg)

        updated_task = await task_service.update_task(task_id, task_data)

        response = await _build_task_response(updated_task, uow)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    else:
        return response


@router.post("/{task_id}/progress")
async def update_task_progress(
    task_id: int,
    progress_data: TaskProgress,
    uow: UOWDep,
    current_user: CurrentUser,
) -> TaskResponse:
    """Update task progress."""
    task_service = TaskService(uow)

    try:
        task = await task_service.get_task(task_id)

        can_update = task.assignee_id == current_user.id or current_user.role in ["HR", "ADMIN"]
        if not can_update:
            msg = "Cannot update progress for this task"
            raise PermissionDenied(msg)

        updated_task = await task_service.update_task_progress(task_id, progress_data)

        response = await _build_task_response(updated_task, uow)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    else:
        return response


@router.post("/{task_id}/complete")
async def complete_task(
    task_id: int,
    uow: UOWDep,
    current_user: CurrentUser,
    completion_notes: str | None = None,
) -> TaskResponse:
    """Mark task as completed."""
    task_service = TaskService(uow)

    try:
        completed_task = await task_service.complete_task(task_id, current_user.id, completion_notes)

        response = await _build_task_response(completed_task, uow)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    else:
        return response


@router.post("/bulk-update")
async def bulk_update_tasks(
    bulk_data: TaskBulkUpdate,
    uow: UOWDep,
    _current_user: HRUser,
) -> MessageResponse:
    """Bulk update tasks (HR/admin only)."""
    task_service = TaskService(uow)

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
    uow: UOWDep,
    current_user: CurrentUser,
) -> dict:
    """Get task dependencies and blockers."""
    task_service = TaskService(uow)
    checklist_service = ChecklistService(uow)

    try:
        task = await task_service.get_task(task_id)

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
