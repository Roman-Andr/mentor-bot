"""Department management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from auth_service.api.deps import AdminUser, DepartmentServiceDep
from auth_service.core import ConflictException, NotFoundException
from auth_service.schemas import (
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentResponse,
    DepartmentUpdate,
    MessageResponse,
)

router = APIRouter()


@router.get("/")
@router.get("")
async def get_departments(
    department_service: DepartmentServiceDep,
    _current_user: AdminUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    search: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str | None, Query()] = None,
    sort_order: Annotated[str, Query()] = "asc",
) -> DepartmentListResponse:
    """Get paginated list of departments (admin only)."""
    departments, total = await department_service.get_departments(
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return DepartmentListResponse(
        total=total,
        departments=[DepartmentResponse.model_validate(d) for d in departments],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/")
@router.post("")
async def create_department(
    department_data: DepartmentCreate,
    department_service: DepartmentServiceDep,
    _current_user: AdminUser,
) -> DepartmentResponse:
    """Create new department (admin only)."""
    logger.info(
        "Create department request (admin_id={}, name={})",
        _current_user.id,
        department_data.name,
    )
    try:
        department = await department_service.create_department(department_data)
        return DepartmentResponse.model_validate(department)
    except ConflictException as e:
        logger.warning("Create department conflict: {}", e.detail)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.detail),
        ) from e


@router.get("/{department_id}")
async def get_department(
    department_id: int,
    department_service: DepartmentServiceDep,
    _current_user: AdminUser,
) -> DepartmentResponse:
    """Get department by ID (admin only)."""
    try:
        department = await department_service.get_department_by_id(department_id)
        return DepartmentResponse.model_validate(department)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/{department_id}")
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    department_service: DepartmentServiceDep,
    _current_user: AdminUser,
) -> DepartmentResponse:
    """Update department (admin only)."""
    try:
        department = await department_service.update_department(department_id, department_data)
        return DepartmentResponse.model_validate(department)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.detail),
        ) from e


@router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    department_service: DepartmentServiceDep,
    _current_user: AdminUser,
) -> MessageResponse:
    """Delete department (admin only)."""
    logger.warning(
        "Delete department request (admin_id={}, department_id={})",
        _current_user.id,
        department_id,
    )
    try:
        await department_service.delete_department(department_id)
        return MessageResponse(message="Department deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.detail),
        ) from e
