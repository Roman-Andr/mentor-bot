"""FastAPI dependencies for authentication and authorization via HTTP."""

from collections.abc import AsyncGenerator
from secrets import compare_digest
from typing import Annotated

import httpx
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from feedback_service.config import settings
from feedback_service.database import AsyncSessionLocal, get_db
from feedback_service.repositories import SqlAlchemyUnitOfWork

security = HTTPBearer(auto_error=False)


class UserInfo:
    """User information from auth service."""

    def __init__(self, data: dict) -> None:
        """Initialize UserInfo with data from auth service."""
        self.id = data.get("id")
        self.email = data.get("email")
        self.employee_id = data.get("employee_id")
        self.role = data.get("role")
        self.is_active = data.get("is_active", True)
        self.is_verified = data.get("is_verified", False)
        self.department = data.get("department")
        # Try to get department_id from top-level field first, then from nested department object
        self.department_id = data.get("department_id") or (self.department.get("id") if self.department else None)
        self.position = data.get("position")
        self.level = data.get("level")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.telegram_id = data.get("telegram_id")

    def has_role(self, roles: list[str]) -> bool:
        """Check if user has any of the specified roles."""
        return self.role in roles if self.role else False


def check_user_access(
    current_user: UserInfo,
    user_id: int | None,
    allowed_roles: list[str],
    resource_name: str = "resource",
) -> int | None:
    """
    Check if user has access to view data for the specified user_id.

    - Users can always view their own data
    - Users with allowed_roles can view any user's data
    - If user_id is None and user has allowed_roles, returns None (view all)
    - If user_id is None and user lacks allowed_roles, returns current_user.id

    Args:
        current_user: The authenticated user
        user_id: The target user_id to view, or None for all
        allowed_roles: Roles that grant access to view other users' data
        resource_name: Name of the resource for error messages

    Returns:
        The effective user_id to filter by, or None if viewing all allowed

    Raises:
        HTTPException: 403 if user tries to view another user's data without permission

    """
    if user_id and user_id != current_user.id:
        if not current_user.has_role(allowed_roles):
            logger.warning(
                "Access denied to {} (current_user_id={}, requested_user_id={}, role={})",
                resource_name,
                current_user.id,
                user_id,
                current_user.role,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Can only view your own {resource_name}",
            )
        return user_id
    if not user_id and not current_user.has_role(allowed_roles):
        logger.debug(
            "Restricting {} query to current user (user_id={}, role={})",
            resource_name,
            current_user.id,
            current_user.role,
        )
        return current_user.id
    return user_id


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserInfo | None:
    """Dependency to get current authenticated user via auth service (optional)."""
    if not credentials:
        return None

    async with httpx.AsyncClient() as client:
        try:
            logger.debug("Validating bearer token via auth service")
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {credentials.credentials}"},
                timeout=settings.AUTH_SERVICE_TIMEOUT,
            )

            if response.status_code != status.HTTP_200_OK:
                logger.warning(
                    "Authentication failed: auth service returned status={}",
                    response.status_code,
                )
                return None

            user_data = response.json()
            logger.debug(
                "Authenticated user loaded (user_id={}, role={})",
                user_data.get("id"),
                user_data.get("role"),
            )
            return UserInfo(user_data)

        except httpx.RequestError as e:
            logger.error("Auth service unavailable during token validation: {}", e)
            return None


async def get_current_user_from_cookie(
    request: Request,
) -> UserInfo | None:
    """Dependency to get current authenticated user via cookie (for admin web)."""
    # Try to get session cookie and validate with auth service
    # For now, this is a placeholder - the admin web should use Bearer tokens
    # or we need to implement cookie-based auth validation
    return None


async def require_auth(
    service_auth: Annotated[bool, Depends(verify_service_api_key)],
    current_user: Annotated[UserInfo | None, Depends(get_current_user_optional)],
) -> UserInfo | None:
    """Require either service auth or user auth."""
    if not service_auth and not current_user:
        logger.warning("Authentication failed: neither service key nor user token provided")
        msg = "Not authenticated"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg,
        )
    return current_user


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserInfo:
    """Dependency to get current authenticated user via auth service."""
    if not credentials:
        logger.warning("Authentication failed: missing bearer token")
        msg = "Not authenticated"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg,
        )

    async with httpx.AsyncClient() as client:
        try:
            logger.debug("Validating bearer token via auth service")
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {credentials.credentials}"},
                timeout=settings.AUTH_SERVICE_TIMEOUT,
            )

            if response.status_code != status.HTTP_200_OK:
                logger.warning(
                    "Authentication failed: auth service returned status={}",
                    response.status_code,
                )
                msg = "Invalid authentication credentials"
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=msg,
                )

            user_data = response.json()
            logger.debug(
                "Authenticated user loaded (user_id={}, role={})",
                user_data.get("id"),
                user_data.get("role"),
            )
            return UserInfo(user_data)

        except httpx.RequestError as e:
            logger.error("Auth service unavailable during token validation: {}", e)
            msg = "Auth service unavailable"
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=msg,
            ) from e


async def get_current_active_user(
    current_user: Annotated[UserInfo, Depends(get_current_user)],
) -> UserInfo:
    """Dependency to get current active user."""
    if not current_user.is_active:
        logger.warning("Inactive user rejected (user_id={})", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def require_admin(
    current_user: Annotated[UserInfo, Depends(get_current_active_user)],
) -> UserInfo:
    """Dependency to require admin role."""
    if not current_user.has_role(["ADMIN"]):
        logger.warning("Admin access denied (user_id={}, role={})", current_user.id, current_user.role)
        msg = "Admin access required"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg,
        )
    return current_user


async def require_hr_or_admin(
    current_user: Annotated[UserInfo, Depends(get_current_active_user)],
) -> UserInfo:
    """Dependency to require HR or Admin role."""
    if not current_user.has_role(["HR", "ADMIN"]):
        logger.warning("HR/Admin access denied (user_id={}, role={})", current_user.id, current_user.role)
        msg = "HR or Admin access required"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg,
        )
    return current_user


async def verify_service_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-Service-Api-Key")] = None,
) -> bool:
    """Verify service-to-service API key. Returns True if valid, raises if invalid."""
    if not x_api_key:
        logger.warning("Service API key missing")
        msg = "Invalid service API key"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    if not settings.SERVICE_API_KEY:
        logger.error("Service API key is not configured")
        msg = "Service API key not configured"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
    if not compare_digest(x_api_key, settings.SERVICE_API_KEY):
        logger.warning("Invalid service API key rejected")
        msg = "Invalid service API key"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    logger.debug("Service API key accepted")
    return True


async def get_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Get Unit of Work instance for current request."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        yield uow


# Type aliases for dependencies
CurrentUser = Annotated[UserInfo, Depends(get_current_active_user)]
AdminUser = Annotated[UserInfo, Depends(require_admin)]
HRAdminUser = Annotated[UserInfo, Depends(require_hr_or_admin)]
DbDep = Annotated[AsyncSession, Depends(get_db)]
ServiceAuth = Annotated[bool, Depends(verify_service_api_key)]
UOWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
UnitOfWorkDep = UOWDep  # Alias for consistency
AuthUser = Annotated[UserInfo | None, Depends(require_auth)]
