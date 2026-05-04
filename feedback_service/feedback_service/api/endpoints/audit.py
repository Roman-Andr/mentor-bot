"""Audit endpoints for feedback service."""

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, SerializeAsAny

from feedback_service.api.deps import CurrentUser, UnitOfWorkDep
from feedback_service.core import UserRole

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas for audit responses
class FeedbackStatusChangeEntry(BaseModel):
    """Feedback status change history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    feedback_id: int
    user_id: int
    action: str
    old_status: str | None = None
    new_status: str | None = None
    changed_at: datetime
    changed_by: int | None = None
    meta_data: dict | None = None


class AuditResponse(BaseModel):
    """Generic audit response with pagination."""

    items: Sequence[SerializeAsAny[BaseModel]]
    total: int


def require_hr_or_admin(current_user: CurrentUser) -> None:
    """Require HR or Admin role for audit access."""
    if current_user.role not in (UserRole.HR, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: HR or Admin role required",
        )


@router.get("/feedback-status-change-history", response_model=AuditResponse)
async def get_feedback_status_change_history(
    current_user: CurrentUser,
    uow: UnitOfWorkDep,
    feedback_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get feedback status change history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if feedback_id:
        items = await uow.feedback_status_change_history.get_by_feedback_id(
            feedback_id=feedback_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.feedback_status_change_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[FeedbackStatusChangeEntry.model_validate(item) for item in items],
        total=total,
    )
