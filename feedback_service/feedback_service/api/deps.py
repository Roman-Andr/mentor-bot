"""FastAPI dependencies for authentication and authorization via HTTP."""

from typing import Annotated

import httpx
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from feedback_service.config import settings
from feedback_service.database import get_db

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
        self.department_id = self.department.get("id") if self.department else None
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Can only view your own {resource_name}",
            )
        return user_id
    elif not user_id and not current_user.has_role(allowed_roles):
        return current_user.id
    return user_id


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserInfo:
    """Dependency to get current authenticated user via auth service."""
    if not credentials:
        msg = "Not authenticated"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg,
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {credentials.credentials}"},
                timeout=settings.AUTH_SERVICE_TIMEOUT,
            )

            if response.status_code != status.HTTP_200_OK:
                msg = "Invalid authentication credentials"
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=msg,
                )

            user_data = response.json()
            return UserInfo(user_data)

        except httpx.RequestError as e:
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
        msg = "HR or Admin access required"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg,
        )
    return current_user


async def verify_service_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-Service-Api-Key")] = None,
) -> bool:
    """Verify service-to-service API key."""
    if not settings.SERVICE_API_KEY:
        msg = "Service API key not configured"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
    if not x_api_key or x_api_key != settings.SERVICE_API_KEY:
        msg = "Invalid service API key"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    return True


# Type aliases for dependencies
CurrentUser = Annotated[UserInfo, Depends(get_current_active_user)]
AdminUser = Annotated[UserInfo, Depends(require_admin)]
HRAdminUser = Annotated[UserInfo, Depends(require_hr_or_admin)]
DbDep = Annotated[AsyncSession, Depends(get_db)]
ServiceAuth = Annotated[bool, Depends(verify_service_api_key)]
