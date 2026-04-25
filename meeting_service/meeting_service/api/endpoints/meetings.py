"""Meeting template management endpoints (HR/Admin only)."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from meeting_service.api.deps import CurrentUser, UOWDep
from meeting_service.api.endpoints.user_meetings import _to_response
from meeting_service.core import NotFoundException
from meeting_service.core.enums import EmployeeLevel, MeetingStatus, MeetingType
from meeting_service.schemas import (
    MaterialCreate,
    MaterialResponse,
    MeetingCreate,
    MeetingListResponse,
    MeetingResponse,
    MeetingUpdate,
    UserMeetingUpdate,
)
from meeting_service.services import MeetingService

router = APIRouter()


@router.get("/")
@router.get("")
async def get_meetings(
    uow: UOWDep,
    _current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    meeting_type: MeetingType | None = None,
    department_id: int | None = None,
    position: str | None = None,
    level: EmployeeLevel | None = None,
    search: Annotated[str | None, Query()] = None,
    *,
    is_mandatory: bool | None = None,
    sort_by: Annotated[str | None, Query()] = None,
    sort_order: Annotated[str, Query()] = "asc",
) -> MeetingListResponse:
    """Get paginated list of meeting templates (HR/Admin only)."""
    logger.debug("GET /meetings request (skip={}, limit={})", skip, limit)
    service = MeetingService(uow)
    meetings, total = await service.get_meetings(
        skip=skip,
        limit=limit,
        meeting_type=meeting_type,
        department_id=department_id,
        position=position,
        level=level,
        is_mandatory=is_mandatory,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pages = (total + limit - 1) // limit if limit > 0 else 0
    return MeetingListResponse(
        total=total,
        meetings=[MeetingResponse.model_validate(m) for m in meetings],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> MeetingResponse:
    """Create a new meeting template (HR/Admin only)."""
    logger.info("POST /meetings request (title={})", meeting_data.title)
    service = MeetingService(uow)
    meeting = await service.create_meeting(meeting_data)
    logger.info("Meeting created via API (meeting_id={})", meeting.id)
    return MeetingResponse.model_validate(meeting)


@router.get("/user/{user_id}/upcoming")
async def get_user_upcoming_meetings(
    user_id: int,
    uow: UOWDep,
    _current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
) -> dict:
    """Get upcoming meetings for a user (HR/Admin only)."""
    service = MeetingService(uow)
    items, _ = await service.get_user_meetings(
        user_id=user_id,
        limit=limit,
        status=None,
    )

    return {"meetings": [_to_response(item).model_dump(mode="json") for item in items]}


@router.get("/user/{user_id}")
async def get_user_meetings(
    user_id: int,
    uow: UOWDep,
    _current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> dict:
    """Get all meetings for a user (HR/Admin only)."""
    service = MeetingService(uow)
    items, _ = await service.get_user_meetings(
        user_id=user_id,
        limit=limit,
        status=None,
    )

    return {"meetings": [_to_response(item).model_dump(mode="json") for item in items]}


@router.post("/{assignment_id}/confirm")
async def confirm_meeting(
    assignment_id: int,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> dict:
    """Confirm meeting attendance (HR/Admin only)."""
    service = MeetingService(uow)

    try:
        assignment = await service.get_assignment(assignment_id)
        updated = await service.update_assignment(assignment.id, UserMeetingUpdate(status=MeetingStatus.COMPLETED))
        return _to_response(updated).model_dump(mode="json")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{assignment_id}/cancel")
async def cancel_meeting(
    assignment_id: int,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> dict:
    """Cancel meeting assignment (HR/Admin only)."""
    service = MeetingService(uow)

    try:
        assignment = await service.get_assignment(assignment_id)
        updated = await service.update_assignment(assignment.id, UserMeetingUpdate(status=MeetingStatus.CANCELLED))
        return _to_response(updated).model_dump(mode="json")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> MeetingResponse:
    """Get meeting template by ID (HR/Admin only)."""
    logger.debug("GET /meetings/{} request", meeting_id)
    service = MeetingService(uow)
    try:
        meeting = await service.get_meeting(meeting_id)
        return MeetingResponse.model_validate(meeting)
    except NotFoundException as e:
        logger.warning("Get meeting failed via API: not found (meeting_id={})", meeting_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/{meeting_id}")
async def update_meeting(
    meeting_id: int,
    meeting_data: MeetingUpdate,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> MeetingResponse:
    """Update meeting template (HR/Admin only)."""
    logger.debug("PUT /meetings/{} request", meeting_id)
    service = MeetingService(uow)
    try:
        meeting = await service.update_meeting(meeting_id, meeting_data)
        logger.info("Meeting updated via API (meeting_id={})", meeting_id)
        return MeetingResponse.model_validate(meeting)
    except NotFoundException as e:
        logger.warning("Update meeting failed via API: not found (meeting_id={})", meeting_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> None:
    """Delete meeting template (HR/Admin only)."""
    logger.debug("DELETE /meetings/{} request", meeting_id)
    service = MeetingService(uow)
    try:
        await service.delete_meeting(meeting_id)
        logger.info("Meeting deleted via API (meeting_id={})", meeting_id)
    except NotFoundException as e:
        logger.warning("Delete meeting failed via API: not found (meeting_id={})", meeting_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


# Materials sub-resource
@router.get("/{meeting_id}/materials")
async def get_meeting_materials(
    meeting_id: int,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> list[MaterialResponse]:
    """Get all materials for a meeting (HR/Admin only)."""
    logger.debug("GET /meetings/{}/materials request", meeting_id)
    service = MeetingService(uow)
    try:
        await service.get_meeting(meeting_id)
        materials = await service.get_materials(meeting_id)
        return [MaterialResponse.model_validate(m) for m in materials]
    except NotFoundException as e:
        logger.warning("Get materials failed via API: not found (meeting_id={})", meeting_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{meeting_id}/materials", status_code=status.HTTP_201_CREATED)
async def add_meeting_material(
    meeting_id: int,
    material_data: MaterialCreate,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> MaterialResponse:
    """Add a material to a meeting (HR/Admin only)."""
    logger.info("POST /meetings/{}/materials request (title={})", meeting_id, material_data.title)
    service = MeetingService(uow)
    try:
        material = await service.add_material(meeting_id, material_data)
        logger.info("Material added via API (material_id={})", material.id)
        return MaterialResponse.model_validate(material)
    except NotFoundException as e:
        logger.warning("Add material failed via API: not found (meeting_id={})", meeting_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting_material(
    material_id: int,
    uow: UOWDep,
    _current_user: CurrentUser,
) -> None:
    """Delete a material (HR/Admin only)."""
    logger.debug("DELETE /materials/{} request", material_id)
    service = MeetingService(uow)
    try:
        await service.delete_material(material_id)
        logger.info("Material deleted via API (material_id={})", material_id)
    except NotFoundException as e:
        logger.warning("Delete material failed via API: not found (material_id={})", material_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
