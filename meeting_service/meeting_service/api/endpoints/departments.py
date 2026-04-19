"""Department management endpoints for meeting service."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from meeting_service.api.deps import MeetingServiceDep, ServiceAuth, UOWDep, get_meeting_service_dep
from meeting_service.models.department import Department
from meeting_service.schemas.department import DepartmentCreate, DepartmentResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    uow: UOWDep,
    _service: Annotated[MeetingServiceDep, Depends(get_meeting_service_dep)],
    _auth: ServiceAuth,
) -> DepartmentResponse:
    """Create new department in meeting service (service-to-service only)."""
    existing = await uow.departments.get_by_name(department_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department with this name already exists",
        )

    dept = Department(name=department_data.name, description=department_data.description)
    await uow.departments.create(dept)
    await uow.commit()
    return DepartmentResponse.model_validate(dept)


@router.get("/{department_name}")
async def get_department(
    department_name: str,
    uow: UOWDep,
    _service: Annotated[MeetingServiceDep, Depends(get_meeting_service_dep)],
    _auth: ServiceAuth,
) -> DepartmentResponse:
    """Get department by name (service-to-service only)."""
    dept = await uow.departments.get_by_name(department_name)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return DepartmentResponse.model_validate(dept)


@router.put("/{department_name}")
async def update_department(
    department_name: str,
    department_data: DepartmentCreate,
    uow: UOWDep,
    _service: Annotated[MeetingServiceDep, Depends(get_meeting_service_dep)],
    _auth: ServiceAuth,
) -> DepartmentResponse:
    """Update department in meeting service (service-to-service only)."""
    dept = await uow.departments.get_by_name(department_name)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    if department_data.name != department_name:
        existing = await uow.departments.get_by_name(department_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department with this name already exists",
            )
        dept.name = department_data.name

    if department_data.description is not None:
        dept.description = department_data.description

    await uow.departments.update(dept)
    return DepartmentResponse.model_validate(dept)


@router.delete("/{department_name}")
async def delete_department(
    department_name: str,
    uow: UOWDep,
    _service: Annotated[MeetingServiceDep, Depends(get_meeting_service_dep)],
    _auth: ServiceAuth,
) -> dict[str, str]:
    """Delete department (service-to-service only)."""
    dept = await uow.departments.get_by_name(department_name)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    await uow.departments.delete(dept.id)
    return {"message": "Department deleted successfully"}
