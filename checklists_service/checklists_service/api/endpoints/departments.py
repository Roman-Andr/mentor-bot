"""Department management endpoints for checklists service."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from checklists_service.api.deps import ChecklistsServiceDep, ServiceAuth, get_checklists_service_dep
from checklists_service.schemas import DepartmentCreate, DepartmentResponse, MessageResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    _service: Annotated[ChecklistsServiceDep, Depends(get_checklists_service_dep)],
    _auth: ServiceAuth,
) -> DepartmentResponse:
    """Create new department in checklists service (service-to-service only)."""
    from sqlalchemy import select

    from checklists_service.database import AsyncSessionLocal
    from checklists_service.models.department import Department

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Department).where(Department.name == department_data.name))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department with this name already exists",
            )

        dept = Department(name=department_data.name, description=department_data.description)
        session.add(dept)
        await session.commit()
        await session.refresh(dept)
        return DepartmentResponse.model_validate(dept)


@router.get("/{department_name}")
async def get_department(
    department_name: str,
    _service: Annotated[ChecklistsServiceDep, Depends(get_checklists_service_dep)],
    _auth: ServiceAuth,
) -> DepartmentResponse:
    """Get department by name (service-to-service only)."""
    from sqlalchemy import select

    from checklists_service.database import AsyncSessionLocal
    from checklists_service.models.department import Department

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Department).where(Department.name == department_name))
        dept = result.scalar_one_or_none()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        return DepartmentResponse.model_validate(dept)


@router.delete("/{department_name}")
async def delete_department(
    department_name: str,
    _service: Annotated[ChecklistsServiceDep, Depends(get_checklists_service_dep)],
    _auth: ServiceAuth,
) -> MessageResponse:
    """Delete department (service-to-service only)."""
    from sqlalchemy import select

    from checklists_service.database import AsyncSessionLocal
    from checklists_service.models.department import Department

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Department).where(Department.name == department_name))
        dept = result.scalar_one_or_none()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

        await session.delete(dept)
        await session.commit()
        return MessageResponse(message="Department deleted successfully")
