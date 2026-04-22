"""Checklist management endpoints."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from checklists_service.api.deps import AuthToken, CurrentUser, HRUser, ServiceAuth, UOWDep
from checklists_service.core import NotFoundException, PermissionDenied, ValidationException
from checklists_service.core.enums import ChecklistStatus
from checklists_service.schemas import (
    AutoCreateChecklistsRequest,
    ChecklistCreate,
    ChecklistListResponse,
    ChecklistResponse,
    ChecklistStats,
    ChecklistUpdate,
    CompletionTimeStats,
    MessageResponse,
    MonthlyStats,
)
from checklists_service.services import ChecklistService

router = APIRouter()


@router.get("/")
@router.get("")
async def get_checklists(
    uow: UOWDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    user_id: Annotated[int | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    department_id: Annotated[int | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    *,
    overdue_only: Annotated[bool, Query()] = False,
    sort_by: Annotated[str | None, Query()] = None,
    sort_order: Annotated[str, Query()] = "desc",
) -> ChecklistListResponse:
    """Get paginated list of checklists."""
    checklist_service = ChecklistService(uow)

    if user_id and user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
        msg = "Cannot view other users' checklists"
        raise PermissionDenied(msg)

    # HR/Admin can see all checklists; others only see their own
    effective_user_id = (
        user_id if user_id is not None else (None if current_user.role in ["HR", "ADMIN"] else current_user.id)
    )

    checklists, total = await checklist_service.get_checklists(
        skip=skip,
        limit=limit,
        user_id=effective_user_id,
        status=status,
        department_id=department_id,
        search=search,
        overdue_only=overdue_only,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    stats = await checklist_service.get_checklist_stats(user_id or current_user.id)

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ChecklistListResponse(
        total=total,
        checklists=[
            ChecklistResponse(
                **checklist.__dict__,
                is_overdue=checklist.due_date < datetime.now(UTC) and checklist.status != ChecklistStatus.COMPLETED,
                days_remaining=(
                    (checklist.due_date - datetime.now(UTC)).days
                    if checklist.due_date and checklist.status != ChecklistStatus.COMPLETED
                    else None
                ),
            )
            for checklist in checklists
        ],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
        stats=stats,
    )


@router.post("/")
@router.post("")
async def create_checklist(
    checklist_data: ChecklistCreate,
    uow: UOWDep,
    _current_user: HRUser,
    auth_token: AuthToken,
) -> ChecklistResponse:
    """Create new checklist (HR/admin only)."""
    checklist_service = ChecklistService(uow, auth_token)

    try:
        checklist = await checklist_service.create_checklist(checklist_data, auth_token)
        await uow.commit()
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
    uow: UOWDep,
    current_user: CurrentUser,
) -> ChecklistResponse:
    """Get checklist by ID."""
    checklist_service = ChecklistService(uow)

    try:
        checklist = await checklist_service.get_checklist(checklist_id)

        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot view other users' checklists"
            raise PermissionDenied(msg)

        return ChecklistResponse(
            **checklist.__dict__,
            is_overdue=checklist.due_date < datetime.now(UTC) and checklist.status != ChecklistStatus.COMPLETED,
            days_remaining=(
                (checklist.due_date - datetime.now(UTC)).days
                if checklist.due_date and checklist.status != ChecklistStatus.COMPLETED
                else None
            ),
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
    uow: UOWDep,
    current_user: CurrentUser,
) -> ChecklistResponse:
    """Update checklist."""
    checklist_service = ChecklistService(uow)

    try:
        checklist = await checklist_service.get_checklist(checklist_id)

        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot update other users' checklists"
            raise PermissionDenied(msg)

        updated_checklist = await checklist_service.update_checklist(checklist_id, checklist_data)
        await uow.commit()
        return ChecklistResponse(
            **updated_checklist.__dict__,
            is_overdue=updated_checklist.due_date < datetime.now(UTC)
            and updated_checklist.status != ChecklistStatus.COMPLETED,
            days_remaining=(
                (updated_checklist.due_date - datetime.now(UTC)).days
                if updated_checklist.due_date and updated_checklist.status != ChecklistStatus.COMPLETED
                else None
            ),
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.delete("/{checklist_id}")
async def delete_checklist(
    checklist_id: int,
    uow: UOWDep,
    _current_user: HRUser,
) -> MessageResponse:
    """Delete checklist (admin only)."""
    checklist_service = ChecklistService(uow)

    try:
        await checklist_service.delete_checklist(checklist_id)
        await uow.commit()
        return MessageResponse(message="Checklist deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{checklist_id}/complete")
async def complete_checklist(
    checklist_id: int,
    uow: UOWDep,
    current_user: CurrentUser,
) -> ChecklistResponse:
    """Mark checklist as completed."""
    checklist_service = ChecklistService(uow)

    try:
        checklist = await checklist_service.get_checklist(checklist_id)

        if checklist.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
            msg = "Cannot complete other users' checklists"
            raise PermissionDenied(msg)

        updated_checklist = await checklist_service.complete_checklist(checklist_id)
        await uow.commit()
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
    uow: UOWDep,
    current_user: CurrentUser,
) -> dict:
    """Get checklist progress details."""
    checklist_service = ChecklistService(uow)

    try:
        checklist = await checklist_service.get_checklist(checklist_id)

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
    uow: UOWDep,
    _current_user: HRUser,
    user_id: Annotated[int | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
) -> ChecklistStats:
    """Get checklist statistics (HR/admin only)."""
    checklist_service = ChecklistService(uow)

    return await checklist_service.get_checklist_stats(user_id, department)


@router.post("/auto-create")
async def auto_create_checklists(
    request: AutoCreateChecklistsRequest,
    uow: UOWDep,
    _service_auth: ServiceAuth,
) -> list[ChecklistResponse]:
    """
    Auto-create checklists for a user from matching templates.

    Service-to-service endpoint. Finds all ACTIVE templates matching the
    user's department and position, then creates a checklist from each template.
    """
    checklist_service = ChecklistService(uow)

    checklists = await checklist_service.auto_create_checklists(
        user_id=request.user_id,
        employee_id=request.employee_id,
        department_id=request.department_id,
        position=request.position,
        mentor_id=request.mentor_id,
    )

    await uow.commit()
    return [
        ChecklistResponse(
            **checklist.__dict__,
            is_overdue=False,
            days_remaining=(checklist.due_date - datetime.now(UTC)).days if checklist.due_date else None,
        )
        for checklist in checklists
    ]


@router.get("/stats/monthly")
async def get_monthly_stats(
    uow: UOWDep,
    _current_user: HRUser,
    months: Annotated[int, Query(ge=1, le=12)] = 6,
) -> list[MonthlyStats]:
    """Get monthly statistics (HR/admin only)."""
    checklist_service = ChecklistService(uow)
    stats = await checklist_service.get_monthly_stats(months)
    return [MonthlyStats(**s) for s in stats]


@router.get("/stats/completion-time")
async def get_completion_time_stats(
    uow: UOWDep,
    _current_user: HRUser,
) -> list[CompletionTimeStats]:
    """Get completion time distribution (HR/admin only)."""
    checklist_service = ChecklistService(uow)
    stats = await checklist_service.get_completion_time_distribution()
    return [CompletionTimeStats(**s) for s in stats]
