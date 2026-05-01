"""FastAPI dependencies for authentication and authorization via HTTP."""

from collections.abc import AsyncGenerator
from secrets import compare_digest
from typing import Annotated

import httpx
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.config import settings
from meeting_service.core.exceptions import AuthException, PermissionDenied
from meeting_service.database import AsyncSessionLocal, get_db
from meeting_service.repositories.unit_of_work import SqlAlchemyUnitOfWork

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
        self.position = data.get("position")
        self.level = data.get("level")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.telegram_id = data.get("telegram_id")

    def has_role(self, roles: list[str]) -> bool:
        """Check if user has any of the specified roles."""
        return self.role in roles if self.role else False


async def get_current_user(
    _request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserInfo:
    """Dependency to get current authenticated user via auth service."""
    if not credentials:
        msg = "Not authenticated"
        raise AuthException(msg)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {credentials.credentials}"},
                timeout=settings.AUTH_SERVICE_TIMEOUT,
            )
            if response.status_code != status.HTTP_200_OK:
                msg = "Invalid authentication credentials"
                raise AuthException(msg)

            user_data = response.json()
            return UserInfo(user_data)

        except Exception as e:
            msg = "Invalid authentication credentials"
            raise AuthException(msg) from e


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
    if not current_user.has_role(["HR", "ADMIN"]):
        msg = "Admin access required"
        raise PermissionDenied(msg)
    return current_user


async def require_hr(
    current_user: Annotated[UserInfo, Depends(get_current_active_user)],
) -> UserInfo:
    """Dependency to require HR role."""
    if not current_user.has_role(["HR", "ADMIN"]):
        msg = "HR access required"
        raise PermissionDenied(msg)
    return current_user


# Type aliases for dependencies
CurrentUser = Annotated[UserInfo, Depends(get_current_active_user)]
AdminUser = Annotated[UserInfo, Depends(require_admin)]
HRUser = Annotated[UserInfo, Depends(require_hr)]
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


# Unit of Work dependency
async def get_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Get Unit of Work instance for current request."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        yield uow


UOWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
UnitOfWorkDep = UOWDep  # Alias for consistency


async def verify_service_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-Service-Api-Key")] = None,
) -> bool:
    """Verify service-to-service API key."""
    if not settings.SERVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service API key not configured",
        )
    if not x_api_key or not compare_digest(x_api_key, settings.SERVICE_API_KEY):
        msg = "Invalid service API key"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    return True


ServiceAuth = Annotated[bool, Depends(verify_service_api_key)]


class MeetingServiceDep:
    """Simple marker for service-to-service calls."""



async def get_meeting_service_dep() -> MeetingServiceDep:
    """Dependency for service-to-service calls."""
    return MeetingServiceDep()
