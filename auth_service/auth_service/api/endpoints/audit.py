"""Audit endpoints for auth service."""

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from auth_service.api.deps import CurrentUser, UnitOfWorkDep
from auth_service.core import UserRole

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas for audit responses
class LoginHistoryEntry(BaseModel):
    """Login history entry schema."""

    id: int
    user_id: int
    login_at: datetime
    ip_address: str | None
    user_agent: str | None
    success: bool
    failure_reason: str | None
    method: str | None


class RoleChangeEntry(BaseModel):
    """Role change history entry schema."""

    id: int
    user_id: int
    old_role: str | None
    new_role: str
    changed_at: datetime
    changed_by: int | None
    reason: str | None


class InvitationHistoryEntry(BaseModel):
    """Invitation status history entry schema."""

    id: int
    invitation_id: int
    old_status: str | None
    new_status: str
    changed_at: datetime
    changed_by: int | None
    metadata: dict | None


class MentorAssignmentEntry(BaseModel):
    """Mentor assignment history entry schema."""

    id: int
    user_id: int
    mentor_id: int | None
    action: str
    changed_at: datetime
    changed_by: int | None
    reason: str | None


class AuditResponse(BaseModel):
    """Generic audit response with pagination."""

    items: Sequence[BaseModel]
    total: int


def require_hr_or_admin(current_user: CurrentUser) -> None:
    """Require HR or Admin role for audit access."""
    if current_user.role not in (UserRole.HR, UserRole.ADMIN):
        raise PermissionError("Access denied: HR or Admin role required")


@router.get("/login-history", response_model=AuditResponse)
async def get_login_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    user_id: int | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> AuditResponse:
    """Get login history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if user_id:
        items = await uow.login_history.get_by_user_id(
            user_id=user_id, from_date=from_date, to_date=to_date, limit=limit
        )
        total = len(items)
    else:
        items, total = await uow.login_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[LoginHistoryEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/role-change-history", response_model=AuditResponse)
async def get_role_change_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    user_id: int | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> AuditResponse:
    """Get role change history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if user_id:
        items = await uow.role_change_history.get_by_user_id(
            user_id=user_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.role_change_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[RoleChangeEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/invitation-history", response_model=AuditResponse)
async def get_invitation_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    invitation_id: int | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> AuditResponse:
    """Get invitation status history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if invitation_id:
        items = await uow.invitation_status_history.get_by_invitation_id(
            invitation_id=invitation_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.invitation_status_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[InvitationHistoryEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/mentor-assignment-history", response_model=AuditResponse)
async def get_mentor_assignment_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    user_id: int | None = Query(None),
    mentor_id: int | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> AuditResponse:
    """Get mentor assignment history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if user_id:
        items = await uow.mentor_assignment_history.get_by_user_id(
            user_id=user_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    elif mentor_id:
        items = await uow.mentor_assignment_history.get_by_mentor_id(
            mentor_id=mentor_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.mentor_assignment_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[MentorAssignmentEntry.model_validate(item) for item in items],
        total=total,
    )
