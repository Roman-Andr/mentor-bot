"""FastAPI dependencies for authentication and authorization via HTTP."""

from collections.abc import AsyncGenerator
from typing import Annotated

import httpx
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from checklists_service.config import settings
from checklists_service.core import AuthException, PermissionDenied
from checklists_service.database import AsyncSessionLocal
from checklists_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from checklists_service.services import auth_service_circuit_breaker

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

            async def call_auth_service() -> httpx.Response:
                return await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {credentials.credentials}"},
                    timeout=settings.AUTH_SERVICE_TIMEOUT,
                )

            response = await auth_service_circuit_breaker.call(call_auth_service)

            if response.status_code != status.HTTP_200_OK:
                msg = "Invalid authentication credentials"
                raise AuthException(msg)

            user_data = response.json()
            return UserInfo(user_data)

        except Exception as e:
            if "Circuit breaker is OPEN" in str(e):
                msg = "Auth service temporarily unavailable"
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=msg,
                ) from e
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


async def require_mentor_or_above(
    current_user: Annotated[UserInfo, Depends(get_current_active_user)],
) -> UserInfo:
    """Dependency to require mentor or above role."""
    if not current_user.has_role(["MENTOR", "HR", "ADMIN"]):
        msg = "Mentor access required"
        raise PermissionDenied(msg)
    return current_user


async def get_auth_token(request: Request) -> str | None:
    """Dependency to get auth token from request state."""
    return getattr(request.state, "auth_token", None)


async def verify_service_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-Service-Api-Key")] = None,
) -> bool:
    """Verify service-to-service API key."""
    if not settings.SERVICE_API_KEY:
        return False
    if not x_api_key or x_api_key != settings.SERVICE_API_KEY:
        msg = "Invalid service API key"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    return True


ServiceAuth = Annotated[bool, Depends(verify_service_api_key)]


class ChecklistsServiceDep:
    """Simple marker for service-to-service calls."""



async def get_checklists_service_dep() -> ChecklistsServiceDep:
    """Dependency for service-to-service calls."""
    return ChecklistsServiceDep()


# Unit of Work dependency
async def get_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Get Unit of Work instance for current request."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise


# Type aliases for dependencies
UOWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
CurrentUser = Annotated[UserInfo, Depends(get_current_active_user)]
AdminUser = Annotated[UserInfo, Depends(require_admin)]
HRUser = Annotated[UserInfo, Depends(require_hr)]
MentorUser = Annotated[UserInfo, Depends(require_mentor_or_above)]
AuthToken = Annotated[str | None, Depends(get_auth_token)]
