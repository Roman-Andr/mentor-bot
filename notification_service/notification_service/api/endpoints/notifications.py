"""Notification management endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from notification_service.api.deps import (
    CurrentUser,
    DatabaseSession,
    HRUser,
)
from notification_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from notification_service.schemas import (
    NotificationCreate,
    NotificationResponse,
    ScheduledNotificationCreate,
    ScheduledNotificationResponse,
)
from notification_service.services import NotificationService

router = APIRouter()


@router.post("/send")
async def send_notification(
    notification_data: NotificationCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> NotificationResponse:
    """Send a notification immediately."""
    # Verify that the user sending is either the recipient or has HR/admin rights
    if notification_data.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot send notifications on behalf of another user",
        )

    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        notification = await service.send_immediate(notification_data)
        return NotificationResponse.model_validate(notification)


@router.post("/schedule")
async def schedule_notification(
    schedule_data: ScheduledNotificationCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ScheduledNotificationResponse:
    """Schedule a notification for future sending."""
    if schedule_data.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot schedule notifications on behalf of another user",
        )

    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        scheduled = await service.schedule(schedule_data)
        return ScheduledNotificationResponse.model_validate(scheduled)


@router.get("/history")
async def get_notification_history(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[NotificationResponse]:
    """Get notification history for the current user."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        notifications = await service.get_user_notifications(current_user.id, skip, limit)
        return [NotificationResponse.model_validate(n) for n in notifications]


@router.get("/history/{user_id}")
async def get_user_notification_history(
    user_id: int,
    db: DatabaseSession,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[NotificationResponse]:
    """Get notification history for a specific user (HR/admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        notifications = await service.get_user_notifications(user_id, skip, limit)
        return [NotificationResponse.model_validate(n) for n in notifications]
