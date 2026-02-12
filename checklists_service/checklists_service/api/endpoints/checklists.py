"""Checklist management endpoints."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from checklists_service.api import AdminUser, CurrentUser, DatabaseSession, HRUser
from checklists_service.api.deps import AuthToken
from checklists_service.core import NotFoundException, PermissionDenied, ValidationException
from checklists_service.core.enums import ChecklistStatus
from checklists_service.schemas import (
    ChecklistCreate,
    ChecklistListResponse,
    ChecklistResponse,
    ChecklistStats,
    ChecklistUpdate,
    MessageResponse,
)
from checklists_service.services import ChecklistService

router = APIRouter()


@router.get("/")
async def get_checklists(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    user_id: Annotated[int | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    *,
    overdue_only: Annotated[bool, Query()] = False,
) -> ChecklistListResponse:
    """Get paginated list of checklists."""
    checklist_service = ChecklistService(db)

    # Check permissions
    if user_id and user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
        msg = "Cannot view other users' checklists"
        raise PermissionDenied(msg)

    checklists, total = await checklist_service.get_checklists(
        skip=skip,
        limit=limit,
        user_id=user_id or current_user.id,
        status=status,
        department=department,
        overdue_only=overdue_only,
    )

    # Get stats
    stats = await checklist_service.get_checklist_stats(user_id or current_user.id)

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ChecklistListResponse(
        total=total,
        checklists=[
            ChecklistResponse(
                **checklist.__dict__,
                is_overdue=checklist.due_date < datetime.now(UTC) and checklist.status != ChecklistStatus.COMPLETED,
                days_remaining=(checklist.due_date - datetime.now(UTC)).days if checklist.due_date else None,
            )
            for checklist in checklists
        ],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
        stats=stats,
    )


@router.post("/")
async def create_checklist(
    checklist_data: ChecklistCreate,
    db: DatabaseSession,
    _current_user: HRUser,
    auth_token: AuthToken,
) -> ChecklistResponse:
    """Create new checklist (HR/admin only)."""
    checklist_service = ChecklistService(db)

    try:
        checklist = await checklist_service.create_checklist(checklist_data, auth_token)
        return ChecklistResponse(
            **checklist.__dict__,
            is_overdue=False,
            days_remaining=(checklist.due_date - datetime.now(UTC)).days if checklist.due_date else None,
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.get("/{checklist_id}")
async def get_checklist(
    checklist_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ChecklistResponse:
    """Get checklist by ID."""
    checklist_service = ChecklistService(db)

    try:
        checklist = await checklist_service.get_checklist(checklist_id)

        # Check permissions
        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot view other users' checklists"
            raise PermissionDenied(msg)

        return ChecklistResponse(
            **checklist.__dict__,
            is_overdue=checklist.due_date < datetime.now(UTC) and checklist.status != ChecklistStatus.COMPLETED,
            days_remaining=(checklist.due_date - datetime.now(UTC)).days if checklist.due_date else None,
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/{checklist_id}")
async def update_checklist(
    checklist_id: int,
    checklist_data: ChecklistUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ChecklistResponse:
    """Update checklist."""
    checklist_service = ChecklistService(db)

    try:
        checklist = await checklist_service.get_checklist(checklist_id)

        # Check permissions
        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot update other users' checklists"
            raise PermissionDenied(msg)

        updated_checklist = await checklist_service.update_checklist(checklist_id, checklist_data)
        return ChecklistResponse(
            **updated_checklist.__dict__,
            is_overdue=updated_checklist.due_date < datetime.now(UTC)
            and updated_checklist.status != ChecklistStatus.COMPLETED,
            days_remaining=(updated_checklist.due_date - datetime.now(UTC)).days
            if updated_checklist.due_date
            else None,
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.delete("/{checklist_id}")
async def delete_checklist(
    checklist_id: int,
    db: DatabaseSession,
    _current_user: AdminUser,
) -> MessageResponse:
    """Delete checklist (admin only)."""
    checklist_service = ChecklistService(db)

    try:
        await checklist_service.delete_checklist(checklist_id)
        return MessageResponse(message="Checklist deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{checklist_id}/complete")
async def complete_checklist(
    checklist_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ChecklistResponse:
    """Mark checklist as completed."""
    checklist_service = ChecklistService(db)

    try:
        checklist = await checklist_service.get_checklist(checklist_id)

        # Check permissions
        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot complete other users' checklists"
            raise PermissionDenied(msg)

        updated_checklist = await checklist_service.complete_checklist(checklist_id)
        return ChecklistResponse(
            **updated_checklist.__dict__,
            is_overdue=False,
            days_remaining=None,
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/{checklist_id}/progress")
async def get_checklist_progress(
    checklist_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict:
    """Get checklist progress details."""
    checklist_service = ChecklistService(db)

    try:
        checklist = await checklist_service.get_checklist(checklist_id)

        # Check permissions
        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot view other users' checklists"
            raise PermissionDenied(msg)

        return await checklist_service.get_checklist_progress(checklist_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/stats/summary")
async def get_checklist_stats(
    db: DatabaseSession,
    _current_user: HRUser,
    user_id: Annotated[int | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
) -> ChecklistStats:
    """Get checklist statistics (HR/admin only)."""
    checklist_service = ChecklistService(db)

    return await checklist_service.get_checklist_stats(user_id, department)
