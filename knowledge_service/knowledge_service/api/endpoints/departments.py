"""Department management endpoints for knowledge service."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from knowledge_service.api.deps import KnowledgeServiceDep, ServiceAuth, get_knowledge_service_dep
from knowledge_service.database import AsyncSessionLocal
from knowledge_service.models.department import Department
from knowledge_service.schemas.department import DepartmentCreate, DepartmentResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    _service: Annotated[KnowledgeServiceDep, Depends(get_knowledge_service_dep)],
    _auth: ServiceAuth,
) -> DepartmentResponse:
    """Create new department in knowledge service (service-to-service only)."""
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
    _service: Annotated[KnowledgeServiceDep, Depends(get_knowledge_service_dep)],
    _auth: ServiceAuth,
) -> DepartmentResponse:
    """Get department by name (service-to-service only)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Department).where(Department.name == department_name))
        dept = result.scalar_one_or_none()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        return DepartmentResponse.model_validate(dept)


@router.put("/{department_name}")
async def update_department(
    department_name: str,
    department_data: DepartmentCreate,
    _service: Annotated[KnowledgeServiceDep, Depends(get_knowledge_service_dep)],
    _auth: ServiceAuth,
) -> DepartmentResponse:
    """Update department in knowledge service (service-to-service only)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Department).where(Department.name == department_name))
        dept = result.scalar_one_or_none()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

        if department_data.name != department_name:
            result = await session.execute(select(Department).where(Department.name == department_data.name))
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Department with this name already exists",
                )
            dept.name = department_data.name

        if department_data.description is not None:
            dept.description = department_data.description

        await session.commit()
        await session.refresh(dept)
        return DepartmentResponse.model_validate(dept)


@router.delete("/{department_name}")
async def delete_department(
    department_name: str,
    _service: Annotated[KnowledgeServiceDep, Depends(get_knowledge_service_dep)],
    _auth: ServiceAuth,
) -> dict[str, str]:
    """Delete department (service-to-service only)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Department).where(Department.name == department_name))
        dept = result.scalar_one_or_none()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

        await session.delete(dept)
        await session.commit()
        return {"message": "Department deleted successfully"}
