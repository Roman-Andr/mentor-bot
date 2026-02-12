"""Meeting template management endpoints (HR/Admin only)."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from meeting_service.api.deps import (
    DatabaseSession,
    HRUser,
)
from meeting_service.core import (
    NotFoundException,
)
from meeting_service.core.enums import EmployeeLevel, MeetingType
from meeting_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from meeting_service.schemas import (
    MaterialCreate,
    MaterialResponse,
    MeetingCreate,
    MeetingListResponse,
    MeetingResponse,
    MeetingUpdate,
)
from meeting_service.services import MeetingService

router = APIRouter()


@router.get("/")
async def get_meetings(
    db: DatabaseSession,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    meeting_type: MeetingType | None = None,
    department: str | None = None,
    position: str | None = None,
    level: EmployeeLevel | None = None,
    *,
    is_mandatory: bool | None = None,
) -> MeetingListResponse:
    """Get paginated list of meeting templates (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = MeetingService(uow)
        meetings, total = await service.get_meetings(
            skip=skip,
            limit=limit,
            meeting_type=meeting_type,
            department=department,
            position=position,
            level=level,
            is_mandatory=is_mandatory,
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
async def create_meeting(
    meeting_data: MeetingCreate,
    db: DatabaseSession,
    _current_user: HRUser,
) -> MeetingResponse:
    """Create a new meeting template (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = MeetingService(uow)
        meeting = await service.create_meeting(meeting_data)
        return MeetingResponse.model_validate(meeting)


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    db: DatabaseSession,
    _current_user: HRUser,
) -> MeetingResponse:
    """Get meeting template by ID (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = MeetingService(uow)
        try:
            meeting = await service.get_meeting(meeting_id)
            return MeetingResponse.model_validate(meeting)
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e.detail),
            ) from e


@router.put("/{meeting_id}")
async def update_meeting(
    meeting_id: int,
    meeting_data: MeetingUpdate,
    db: DatabaseSession,
    _current_user: HRUser,
) -> MeetingResponse:
    """Update meeting template (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = MeetingService(uow)
        try:
            meeting = await service.update_meeting(meeting_id, meeting_data)
            return MeetingResponse.model_validate(meeting)
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e.detail),
            ) from e


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    db: DatabaseSession,
    _current_user: HRUser,
) -> None:
    """Delete meeting template (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = MeetingService(uow)
        try:
            await service.delete_meeting(meeting_id)
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e.detail),
            ) from e


# Materials sub-resource
@router.get("/{meeting_id}/materials")
async def get_meeting_materials(
    meeting_id: int,
    db: DatabaseSession,
    _current_user: HRUser,
) -> list[MaterialResponse]:
    """Get all materials for a meeting (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = MeetingService(uow)
        try:
            # Ensure meeting exists
            await service.get_meeting(meeting_id)
            materials = await service.get_materials(meeting_id)
            return [MaterialResponse.model_validate(m) for m in materials]
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e.detail),
            ) from e


@router.post("/{meeting_id}/materials", status_code=status.HTTP_201_CREATED)
async def add_meeting_material(
    meeting_id: int,
    material_data: MaterialCreate,
    db: DatabaseSession,
    _current_user: HRUser,
) -> MaterialResponse:
    """Add a material to a meeting (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = MeetingService(uow)
        try:
            material = await service.add_material(meeting_id, material_data)
            return MaterialResponse.model_validate(material)
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e.detail),
            ) from e


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting_material(
    material_id: int,
    db: DatabaseSession,
    _current_user: HRUser,
) -> None:
    """Delete a material (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = MeetingService(uow)
        try:
            await service.delete_material(material_id)
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e.detail),
            ) from e
