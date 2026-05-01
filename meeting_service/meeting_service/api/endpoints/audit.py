"""Audit endpoints for meeting service."""

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from meeting_service.api.deps import CurrentUser, UnitOfWorkDep
from meeting_service.core import UserRole

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas for audit responses
class MeetingStatusChangeEntry(BaseModel):
    """Meeting status change history entry schema."""

    id: int
    meeting_id: int
    user_id: int
    action: str
    old_status: str | None
    new_status: str | None
    changed_at: datetime
    changed_by: int | None
    metadata: dict | None = None

    model_config = {"populate_by_name": True}

    @classmethod
    def from_model(cls, item):
        """Create schema from database model, handling field name mapping."""
        return cls(
            id=item.id,
            meeting_id=item.meeting_id,
            user_id=item.user_id,
            action=item.action,
            old_status=item.old_status,
            new_status=item.new_status,
            changed_at=item.changed_at,
            changed_by=item.changed_by,
            metadata=getattr(item, "meta_data", None),
        )


class MeetingParticipantEntry(BaseModel):
    """Meeting participant history entry schema."""

    id: int
    meeting_id: int
    user_id: int
    action: str
    joined_at: datetime
    left_at: datetime | None
    metadata: dict | None = None

    model_config = {"populate_by_name": True}

    @classmethod
    def from_model(cls, item):
        """Create schema from database model, handling field name mapping."""
        return cls(
            id=item.id,
            meeting_id=item.meeting_id,
            user_id=item.user_id,
            action=item.action,
            joined_at=item.joined_at,
            left_at=item.left_at,
            metadata=getattr(item, "meta_data", None),
        )


class AuditResponse(BaseModel):
    """Generic audit response with pagination."""

    items: Sequence[BaseModel]
    total: int


def require_hr_or_admin(current_user: CurrentUser) -> None:
    """Require HR or Admin role for audit access."""
    if current_user.role not in (UserRole.HR, UserRole.ADMIN):
        raise PermissionError("Access denied: HR or Admin role required")


@router.get("/meeting-status-change-history", response_model=AuditResponse)
async def get_meeting_status_change_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    meeting_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get meeting status change history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if meeting_id:
        items = await uow.meeting_status_change_history.get_by_meeting_id(
            meeting_id=meeting_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.meeting_status_change_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[MeetingStatusChangeEntry.from_model(item) for item in items],
        total=total,
    )


@router.get("/meeting-participant-history", response_model=AuditResponse)
async def get_meeting_participant_history(
    current_user: Annotated[CurrentUser, Depends()],
    uow: UnitOfWorkDep,
    meeting_id: Annotated[int | None, Query()] = None,
    user_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get meeting participant history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if meeting_id:
        items = await uow.meeting_participant_history.get_by_meeting_id(
            meeting_id=meeting_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    elif user_id:
        items = await uow.meeting_participant_history.get_by_user_id(
            user_id=user_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.meeting_participant_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[MeetingParticipantEntry.from_model(item) for item in items],
        total=total,
    )
