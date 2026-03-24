"""FastAPI dependencies with repository pattern (minimal version)."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth_service.core import AuthException, PermissionDenied, UserRole
from auth_service.database import AsyncSessionLocal
from auth_service.models import User
from auth_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from auth_service.services import AuthService, DepartmentService, InvitationService, UserService

# Security
security = HTTPBearer(auto_error=False)


# Unit of Work
async def get_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Get Unit of Work instance for current request."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise


# Service dependencies
async def get_auth_service(uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]) -> AuthService:
    """Get AuthService instance with dependency injection."""
    return AuthService(uow)


async def get_user_service(uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]) -> UserService:
    """Get UserService instance with dependency injection."""
    return UserService(uow)


async def get_invitation_service(uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]) -> InvitationService:
    """Get InvitationService instance with dependency injection."""
    return InvitationService(uow)


async def get_department_service(uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]) -> DepartmentService:
    """Get DepartmentService instance with dependency injection."""
    return DepartmentService(uow)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
DepartmentServiceDep = Annotated[DepartmentService, Depends(get_department_service)]


# User authentication
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: AuthServiceDep,
) -> User:
    """Get current authenticated user."""
    if not credentials:
        msg = "Not authenticated"
        raise AuthException(msg)

    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
    except Exception as e:
        msg = "Invalid authentication credentials"
        raise AuthException(msg) from e
    else:
        return user


def require_role(allowed_roles: list[UserRole]) -> Callable[..., Awaitable[User]]:
    """Create factory for role-based dependencies."""

    async def dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            msg = "Access denied"
            raise PermissionDenied(msg)
        return current_user

    return dependency


# Type aliases
UOWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

InvitationServiceDep = Annotated[InvitationService, Depends(get_invitation_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_role([UserRole.ADMIN]))]
HRUser = Annotated[User, Depends(require_role([UserRole.HR, UserRole.ADMIN]))]
MentorUser = Annotated[User, Depends(require_role([UserRole.MENTOR, UserRole.HR, UserRole.ADMIN]))]
