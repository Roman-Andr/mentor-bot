"""FastAPI dependencies with repository pattern (minimal version)."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from loguru import logger

from auth_service.config import settings
from auth_service.core import AuthException, PermissionDenied, UserRole
from auth_service.database import AsyncSessionLocal
from auth_service.models import User
from auth_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from auth_service.services import AuthService, DepartmentService, InvitationService, UserService

# Security - supports both Authorization header and httpOnly cookies
security = HTTPBearer(auto_error=False)


def get_token_from_request(request: Request) -> str | None:
    """Extract token from Authorization header or httpOnly cookie."""
    # First, try Authorization header (Bearer token)
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:]  # Strip "Bearer " prefix

    # Fall back to httpOnly cookie
    return request.cookies.get("access_token")


# Unit of Work
async def get_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Get Unit of Work instance for current request."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        yield uow


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
    request: Request,
    auth_service: AuthServiceDep,
) -> User:
    """Get current authenticated user from header or cookie."""
    token = get_token_from_request(request)

    if not token:
        logger.debug("Authentication required but no token provided")
        msg = "Not authenticated"
        raise AuthException(msg)

    try:
        user = await auth_service.get_current_user(token)
        if not user.is_active:
            logger.warning("Authenticated user is inactive (user_id={})", user.id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
    except Exception as e:
        logger.warning("Authentication failed: {}", e)
        msg = "Invalid authentication credentials"
        raise AuthException(msg) from e
    else:
        return user


async def verify_service_api_key(request: Request) -> bool:
    """Verify SERVICE_API_KEY for inter-service communication."""
    service_key = request.headers.get("X-Service-API-Key")
    if not service_key:
        return False
    return service_key == settings.SERVICE_API_KEY


async def get_current_user_optional(
    request: Request,
    auth_service: AuthServiceDep,
) -> User | None:
    """Get current authenticated user from header or cookie, or None if not authenticated."""
    token = get_token_from_request(request)

    if not token:
        return None

    try:
        user = await auth_service.get_current_user(token)
        if not user.is_active:
            return None
    except Exception:
        return None
    else:
        return user


def require_role(allowed_roles: list[UserRole]) -> Callable[..., Awaitable[User]]:
    """Create factory for role-based dependencies."""

    async def dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(
                "Access denied for role={} (user_id={}, allowed={})",
                current_user.role,
                current_user.id,
                [r.value if hasattr(r, "value") else r for r in allowed_roles],
            )
            msg = "Access denied"
            raise PermissionDenied(msg)
        return current_user

    return dependency


# Type aliases
UOWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
UnitOfWorkDep = UOWDep  # Alias for consistency across services
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

InvitationServiceDep = Annotated[InvitationService, Depends(get_invitation_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_role([UserRole.ADMIN]))]
HRUser = Annotated[User, Depends(require_role([UserRole.HR, UserRole.ADMIN]))]
MentorUser = Annotated[User, Depends(require_role([UserRole.MENTOR, UserRole.HR, UserRole.ADMIN]))]
ServiceAuth = Annotated[bool, Depends(verify_service_api_key)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]
