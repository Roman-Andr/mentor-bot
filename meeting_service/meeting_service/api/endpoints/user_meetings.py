"""User meeting assignment endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from meeting_service.api.deps import CurrentUser, HRUser, UOWDep
from meeting_service.core import (
    ConflictException,
    NotFoundException,
    PermissionDenied,
    ValidationException,
)
from meeting_service.core.enums import MeetingStatus
from meeting_service.models import UserMeeting
from meeting_service.schemas import (
    UserMeetingComplete,
    UserMeetingCreate,
    UserMeetingListResponse,
    UserMeetingResponse,
    UserMeetingUpdate,
)
from meeting_service.services import MeetingService

router = APIRouter()


def _to_response(um: UserMeeting) -> UserMeetingResponse:
    """Convert a UserMeeting ORM object to a response schema without triggering lazy loads."""
    data = {k: v for k, v in um.__dict__.items() if not k.startswith("_")}
    return UserMeetingResponse.model_validate(data)


@router.get("/my")
async def get_my_meetings(
    uow: UOWDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: MeetingStatus | None = None,
) -> UserMeetingListResponse:
    """Get current user's assigned meetings."""
    service = MeetingService(uow)
    items, total = await service.get_user_meetings(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
    )
    pages = (total + limit - 1) // limit if limit > 0 else 0
    return UserMeetingListResponse(
        total=total,
        items=[_to_response(item) for item in items],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/assign")
async def assign_meeting(
    assignment_data: UserMeetingCreate,
    uow: UOWDep,
    _current_user: HRUser,
) -> UserMeetingResponse:
    """Assign a meeting to a user (HR/Admin only)."""
    service = MeetingService(uow)
    try:
        assignment = await service.assign_meeting(assignment_data)
        return _to_response(assignment)
    except (NotFoundException, ConflictException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.get("/by-meeting/{meeting_id}")
async def get_meeting_assignments(
    meeting_id: int,
    uow: UOWDep,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    meeting_status: MeetingStatus | None = None,
) -> UserMeetingListResponse:
    """Get all user assignments for a specific meeting template (HR/Admin only)."""
    service = MeetingService(uow)
    try:
        items, total = await service.get_meeting_assignments(
            meeting_id=meeting_id,
            skip=skip,
            limit=limit,
            status=meeting_status,
        )
        pages = (total + limit - 1) // limit if limit > 0 else 0
        return UserMeetingListResponse(
            total=total,
            items=[_to_response(item) for item in items],
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            pages=pages,
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/{assignment_id}")
async def get_assignment(
    assignment_id: int,
    uow: UOWDep,
    current_user: CurrentUser,
) -> UserMeetingResponse:
    """Get a specific user meeting assignment."""
    service = MeetingService(uow)
    try:
        assignment = await service.get_assignment(assignment_id)
        if assignment.user_id != current_user.id and not current_user.has_role(["HR", "ADMIN"]):
            raise PermissionDenied
        return _to_response(assignment)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.patch("/{assignment_id}")
async def update_assignment(
    assignment_id: int,
    update_data: UserMeetingUpdate,
    uow: UOWDep,
    current_user: CurrentUser,
) -> UserMeetingResponse:
    """Update assignment (status, scheduled_at). Only HR or the assigned user can update."""
    service = MeetingService(uow)
    try:
        assignment = await service.get_assignment(assignment_id)
        if assignment.user_id != current_user.id and not current_user.has_role(["HR", "ADMIN"]):
            raise PermissionDenied
        updated = await service.update_assignment(assignment_id, update_data)
        return _to_response(updated)
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.post("/{assignment_id}/complete")
async def complete_meeting(
    assignment_id: int,
    completion: UserMeetingComplete,
    uow: UOWDep,
    current_user: CurrentUser,
) -> UserMeetingResponse:
    """Mark a meeting as completed (only the assigned user can complete)."""
    service = MeetingService(uow)
    try:
        assignment = await service.get_assignment(assignment_id)
        if assignment.user_id != current_user.id:
            raise PermissionDenied
        completed = await service.complete_meeting(assignment_id, completion)
        return _to_response(completed)
    except (NotFoundException, ValidationException, PermissionDenied) as e:
        if isinstance(e, PermissionDenied):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only complete your own meetings",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    uow: UOWDep,
    _current_user: HRUser,
) -> None:
    """Delete/cancel a user meeting assignment (HR/Admin only)."""
    service = MeetingService(uow)
    try:
        await service.delete_assignment(assignment_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/auto-assign/{user_id}")
async def auto_assign_for_user(
    user_id: int,
    uow: UOWDep,
    _current_user: HRUser,
    department_id: int | None = None,
    position: str | None = None,
    level: str | None = None,
) -> list[UserMeetingResponse]:
    """Automatically assign all matching mandatory meetings to a user (HR only)."""
    service = MeetingService(uow)
    assigned = await service.assign_meetings_for_user(
        user_id=user_id,
        department_id=department_id,
        position=position,
        level=level,
    )
    return [_to_response(a) for a in assigned]
