"""Audit endpoints for escalation service."""

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel, SerializeAsAny

from escalation_service.api.deps import CurrentUser, UnitOfWorkDep
from escalation_service.core import PermissionDenied, UserRole

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas for audit responses
class EscalationStatusEntry(BaseModel):
    """Escalation status history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    escalation_id: int
    user_id: int
    action: str
    old_status: str | None = None
    new_status: str | None = None
    changed_at: datetime
    changed_by: int | None = None
    meta_data: dict | None = None


class MentorInterventionEntry(BaseModel):
    """Mentor intervention history entry schema."""

    model_config = {"from_attributes": True}

    id: int
    escalation_id: int
    mentor_id: int
    intervention_type: str
    intervention_at: datetime
    notes: str | None = None
    outcome: str | None = None
    escalation_resolved: bool


class AuditResponse(BaseModel):
    """Generic audit response with pagination."""

    items: Sequence[SerializeAsAny[BaseModel]]
    total: int


def require_hr_or_admin(current_user: CurrentUser) -> None:
    """Require HR or Admin role for audit access."""
    if current_user.role not in (UserRole.HR.value, UserRole.ADMIN.value):
        raise PermissionDenied("Access denied: HR or Admin role required")


@router.get("/escalation-status-history", response_model=AuditResponse)
async def get_escalation_status_history(
    current_user: CurrentUser,
    uow: UnitOfWorkDep,
    escalation_id: Annotated[int | None, Query()] = None,
    user_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get escalation status history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if escalation_id:
        items = await uow.escalation_status_history.get_by_escalation_id(
            escalation_id=escalation_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    elif user_id:
        items = await uow.escalation_status_history.get_by_user_id(
            user_id=user_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.escalation_status_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[EscalationStatusEntry.model_validate(item) for item in items],
        total=total,
    )


@router.get("/mentor-intervention-history", response_model=AuditResponse)
async def get_mentor_intervention_history(
    current_user: CurrentUser,
    uow: UnitOfWorkDep,
    escalation_id: Annotated[int | None, Query()] = None,
    mentor_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get mentor intervention history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    if escalation_id:
        items = await uow.mentor_intervention_history.get_by_escalation_id(
            escalation_id=escalation_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    elif mentor_id:
        items = await uow.mentor_intervention_history.get_by_mentor_id(
            mentor_id=mentor_id, from_date=from_date, to_date=to_date
        )
        total = len(items)
    else:
        items, total = await uow.mentor_intervention_history.get_all(
            from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )

    return AuditResponse(
        items=[MentorInterventionEntry.model_validate(item) for item in items],
        total=total,
    )
