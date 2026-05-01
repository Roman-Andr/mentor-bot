"""Audit endpoints for notification service."""

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from notification_service.api.deps import CurrentUser, DatabaseSession
from notification_service.core import UserRole
from notification_service.repositories.unit_of_work import SqlAlchemyUnitOfWork

logger = logging.getLogger(__name__)

router = APIRouter()


# Schema for audit response
class NotificationAuditEntry(BaseModel):
    """Notification audit entry schema."""

    id: int
    user_id: int
    type: str
    channel: str
    status: str
    sent_at: datetime | None
    delivered_at: datetime | None
    read_at: datetime | None
    failure_reason: str | None
    metadata: dict | None
    created_at: datetime


class AuditResponse(BaseModel):
    """Generic audit response with pagination."""

    items: Sequence[BaseModel]
    total: int


def require_hr_or_admin(current_user: CurrentUser) -> None:
    """Require HR or Admin role for audit access."""
    if current_user.role not in (UserRole.HR, UserRole.ADMIN):
        raise PermissionError("Access denied: HR or Admin role required")


@router.get("/notifications-audit", response_model=AuditResponse)
async def get_notifications_audit(
    current_user: Annotated[CurrentUser, Depends()],
    db: DatabaseSession,
    user_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditResponse:
    """Get notifications audit history for audit purposes (HR/Admin only)."""
    require_hr_or_admin(current_user)

    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        stmt = uow.notifications._select()

        if user_id:
            stmt = stmt.where(uow.notifications._model.user_id == user_id)
        if from_date:
            stmt = stmt.where(uow.notifications._model.created_at >= from_date)
        if to_date:
            stmt = stmt.where(uow.notifications._model.created_at <= to_date)

        # Get total count
        count_stmt = uow.notifications._count()
        if user_id:
            count_stmt = count_stmt.where(uow.notifications._model.user_id == user_id)
        if from_date:
            count_stmt = count_stmt.where(uow.notifications._model.created_at >= from_date)
        if to_date:
            count_stmt = count_stmt.where(uow.notifications._model.created_at <= to_date)

        total_result = await uow._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Get items with pagination
        stmt = stmt.order_by(uow.notifications._model.created_at.desc()).offset(offset).limit(limit)
        result = await uow._session.execute(stmt)
        items = result.scalars().all()

        return AuditResponse(
            items=[NotificationAuditEntry.model_validate(item) for item in items],
            total=total,
        )
