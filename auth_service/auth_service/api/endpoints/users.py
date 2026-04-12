"""User management endpoints with repository pattern."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from auth_service.api.deps import (
    AdminUser,
    CurrentUser,
    HRUser,
    UserServiceDep,
)
from auth_service.core import (
    ConflictException,
    NotFoundException,
    PermissionDenied,
    UserRole,
    ValidationException,
)
from auth_service.schemas import (
    MessageResponse,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


@router.get("/")
@router.get("")
async def get_users(
    user_service: UserServiceDep,
    _current_user: AdminUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    search: Annotated[str | None, Query()] = None,
    department_id: Annotated[int | None, Query()] = None,
    role: Annotated[UserRole | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
) -> UserListResponse:
    """Get paginated list of users (admin only)."""
    users, total = await user_service.get_users(
        skip=skip,
        limit=limit,
        search=search,
        department_id=department_id,
        role=role,
        is_active=is_active,
    )

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return UserListResponse(
        total=total,
        users=[UserResponse.model_validate(user) for user in users],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/")
@router.post("")
async def create_user(
    user_data: UserCreate,
    user_service: UserServiceDep,
    _current_user: AdminUser,
) -> UserResponse:
    """Create new user (admin only)."""
    try:
        user = await user_service.create_user(user_data)
        return UserResponse.model_validate(user)
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.detail),
        ) from e


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserServiceDep,
    current_user: CurrentUser,
) -> UserResponse:
    """Get user by ID (users can see themselves, mentors, admins/HR can see anyone)."""
    # Allow if: self, HR, Admin, or user is the current user's mentor
    is_self = current_user.id == user_id
    is_hr_or_admin = current_user.role in [UserRole.HR, UserRole.ADMIN]
    is_my_mentor = any(m.mentor_id == user_id and m.is_active for m in current_user.mentor_assignments)

    if not (is_self or is_hr_or_admin or is_my_mentor):
        raise PermissionDenied

    try:
        user = await user_service.get_user_by_id(user_id)
        return UserResponse.model_validate(user)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserServiceDep,
    current_user: CurrentUser,
) -> UserResponse:
    """Update user (users can update themselves, admins can update anyone)."""
    if current_user.id != user_id and current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise PermissionDenied

    try:
        user = await user_service.update_user(user_id, user_data)
        return UserResponse.model_validate(user)
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


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    user_service: UserServiceDep,
    _current_user: AdminUser,
) -> MessageResponse:
    """Delete (deactivate) user (admin only)."""
    try:
        await user_service.deactivate_user(user_id)
        return MessageResponse(message="User deactivated successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/by-telegram/{telegram_id}")
async def get_user_by_telegram_id(
    telegram_id: int,
    user_service: UserServiceDep,
    _current_user: HRUser,
) -> UserResponse:
    """Get user by Telegram ID (HR/admin only)."""
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.get("/by-email/{email}")
async def get_user_by_email(
    email: str,
    user_service: UserServiceDep,
    _current_user: HRUser,
) -> UserResponse:
    """Get user by email (HR/admin only)."""
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.post("/{user_id}/link-telegram")
async def link_telegram_account(
    user_id: int,
    telegram_id: int,
    user_service: UserServiceDep,
    current_user: CurrentUser,
    username: str | None = None,
) -> UserResponse:
    """Link Telegram account to user."""
    if current_user.id != user_id and current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise PermissionDenied

    try:
        user = await user_service.link_telegram_account(user_id, telegram_id, username)
        return UserResponse.model_validate(user)
    except (NotFoundException, ConflictException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.post("/{user_id}/change-role")
async def change_user_role(
    user_id: int,
    role: UserRole,
    user_service: UserServiceDep,
    _current_user: AdminUser,
) -> UserResponse:
    """Change user role (admin only)."""
    try:
        user = await user_service.update_user_role(user_id, role)
        return UserResponse.model_validate(user)
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.post("/{user_id}/change-password")
async def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
    user_service: UserServiceDep,
    current_user: CurrentUser,
) -> MessageResponse:
    """Change user password."""
    if current_user.id != user_id and current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise PermissionDenied

    try:
        await user_service.change_password(user_id, current_password, new_password)
        return MessageResponse(message="Password changed successfully")
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e
