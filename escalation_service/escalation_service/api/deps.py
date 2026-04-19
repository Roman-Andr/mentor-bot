"""FastAPI dependencies for authentication and authorization via HTTP."""

from collections.abc import AsyncGenerator
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from escalation_service.config import settings
from escalation_service.core.exceptions import AuthException, NotFoundException, PermissionDenied
from escalation_service.database import AsyncSessionLocal, get_db
from escalation_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from escalation_service.services import EscalationService

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
    if not current_user.has_role(["ADMIN"]):
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


# UoW dependency
async def get_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Get Unit of Work instance for current request."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        yield uow


async def require_any_assignee_or_hr(
    current_user: Annotated[UserInfo, Depends(get_current_active_user)],
    escalation_id: int,
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)],
) -> tuple[UserInfo, SqlAlchemyUnitOfWork]:
    """Check if user is the assignee or has HR/ADMIN role."""
    request = await uow.escalations.get_by_id(escalation_id)
    if not request:
        msg = "Escalation request"
        raise NotFoundException(msg)

    if current_user.id != request.assigned_to and not current_user.has_role(["HR", "ADMIN"]):
        msg = "Access denied"
        raise PermissionDenied(msg)

    return current_user, uow


# Service dependency
async def get_escalation_service(uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]) -> EscalationService:
    """Get EscalationService instance."""
    return EscalationService(uow)


# Type aliases
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
UOWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
EscalationServiceDep = Annotated[EscalationService, Depends(get_escalation_service)]
CurrentUser = Annotated[UserInfo, Depends(get_current_active_user)]
AdminUser = Annotated[UserInfo, Depends(require_admin)]
HRUser = Annotated[UserInfo, Depends(require_hr)]
