"""User meeting assignment endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

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
    logger.debug("GET /user-meetings/my request (user_id={}, status={})", current_user.id, status)
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
    logger.info("POST /user-meetings/assign request (user_id={}, meeting_id={})", assignment_data.user_id, assignment_data.meeting_id)
    service = MeetingService(uow)
    try:
        assignment = await service.assign_meeting(assignment_data)
        logger.info("Meeting assigned via API (assignment_id={})", assignment.id)
        return _to_response(assignment)
    except (NotFoundException, ConflictException) as e:
        logger.warning("Assign meeting failed via API: {} (user_id={}, meeting_id={})", e.detail, assignment_data.user_id, assignment_data.meeting_id)
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
    logger.debug("GET /user-meetings/by-meeting/{} request", meeting_id)
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
        logger.warning("Get meeting assignments failed via API: not found (meeting_id={})", meeting_id)
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
    logger.debug("GET /user-meetings/{} request", assignment_id)
    service = MeetingService(uow)
    try:
        assignment = await service.get_assignment(assignment_id)
        if assignment.user_id != current_user.id and not current_user.has_role(["HR", "ADMIN"]):
            logger.warning("Get assignment forbidden (current_user_id={}, assignment_id={})", current_user.id, assignment_id)
            raise PermissionDenied
        return _to_response(assignment)
    except NotFoundException as e:
        logger.warning("Get assignment failed via API: not found (assignment_id={})", assignment_id)
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
    logger.debug("PATCH /user-meetings/{} request", assignment_id)
    service = MeetingService(uow)
    try:
        assignment = await service.get_assignment(assignment_id)
        if assignment.user_id != current_user.id and not current_user.has_role(["HR", "ADMIN"]):
            logger.warning("Update assignment forbidden (current_user_id={}, assignment_id={})", current_user.id, assignment_id)
            raise PermissionDenied
        updated = await service.update_assignment(assignment_id, update_data)
        logger.info("Assignment updated via API (assignment_id={})", updated.id)
        return _to_response(updated)
    except (NotFoundException, ValidationException) as e:
        logger.warning("Update assignment failed via API: {} (assignment_id={})", e.detail, assignment_id)
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
    logger.info("POST /user-meetings/{}/complete request", assignment_id)
    service = MeetingService(uow)
    try:
        assignment = await service.get_assignment(assignment_id)
        if assignment.user_id != current_user.id:
            logger.warning("Complete meeting forbidden (current_user_id={}, assignment_id={})", current_user.id, assignment_id)
            raise PermissionDenied
        completed = await service.complete_meeting(assignment_id, completion)
        logger.info("Meeting completed via API (assignment_id={})", completed.id)
        return _to_response(completed)
    except (NotFoundException, ValidationException, PermissionDenied) as e:
        if isinstance(e, PermissionDenied):
            logger.warning("Complete meeting forbidden (current_user_id={}, assignment_id={})", current_user.id, assignment_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only complete your own meetings",
            ) from e
        logger.warning("Complete meeting failed via API: {} (assignment_id={})", e.detail, assignment_id)
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
    logger.debug("DELETE /user-meetings/{} request", assignment_id)
    service = MeetingService(uow)
    try:
        await service.delete_assignment(assignment_id)
        logger.info("Assignment deleted via API (assignment_id={})", assignment_id)
    except NotFoundException as e:
        logger.warning("Delete assignment failed via API: not found (assignment_id={})", assignment_id)
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
    logger.info("POST /user-meetings/auto-assign/{} request", user_id)
    service = MeetingService(uow)
    assigned = await service.assign_meetings_for_user(
        user_id=user_id,
        department_id=department_id,
        position=position,
        level=level,
    )
    logger.info("Auto-assign completed via API (user_id={}, assigned_count={})", user_id, len(assigned))
    return [_to_response(a) for a in assigned]
