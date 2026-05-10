"""Internal maintenance endpoints for notification data."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import delete, update

from notification_service.api.deps import DatabaseSession, ServiceAuth
from notification_service.core.enums import NotificationChannel, NotificationType
from notification_service.models import Notification, NotificationTemplate, ScheduledNotification
from notification_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from notification_service.services import NotificationService

router = APIRouter()


class InternalScheduleTemplateRequest(BaseModel):
    """Internal request for scheduling a template notification."""

    template_name: str
    user_id: int
    variables: dict[str, Any]
    channel: NotificationChannel
    scheduled_time: datetime
    recipient_telegram_id: int | None = None
    recipient_email: str | None = None
    notification_type: NotificationType = NotificationType.GENERAL
    language: str = "en"
    data: dict[str, Any] = Field(default_factory=dict)


class InternalCancelScheduledRequest(BaseModel):
    """Internal request for cancelling pending scheduled notifications."""

    user_id: int
    notification_type: NotificationType
    data_match: dict[str, Any]


@router.delete("/users/{user_id}")
async def cleanup_user_notification_data(
    user_id: int,
    db: DatabaseSession,
    _service_auth: ServiceAuth,
) -> dict[str, int]:
    """Remove notification-service data that belongs or points to a deleted user."""
    notifications = await db.execute(delete(Notification).where(Notification.user_id == user_id))
    scheduled = await db.execute(delete(ScheduledNotification).where(ScheduledNotification.user_id == user_id))
    templates = await db.execute(
        update(NotificationTemplate).where(NotificationTemplate.created_by == user_id).values(created_by=None)
    )
    await db.commit()
    return {
        "notifications": notifications.rowcount or 0,
        "scheduled_notifications": scheduled.rowcount or 0,
        "updated_templates": templates.rowcount or 0,
    }


@router.post("/schedule-template")
async def schedule_template_notification_internal(
    request: InternalScheduleTemplateRequest,
    db: DatabaseSession,
    _service_auth: ServiceAuth,
) -> dict[str, int]:
    """Schedule a template-based notification from another service."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        try:
            scheduled = await service.schedule_template(
                template_name=request.template_name,
                user_id=request.user_id,
                recipient_telegram_id=request.recipient_telegram_id,
                recipient_email=request.recipient_email,
                variables=request.variables,
                channel=request.channel,
                scheduled_time=request.scheduled_time,
                notification_type=request.notification_type,
                language=request.language,
                data=request.data,
            )
        finally:
            await service.cleanup()
    return {"id": scheduled.id}


@router.post("/scheduled/cancel")
async def cancel_scheduled_notifications_internal(
    request: InternalCancelScheduledRequest,
    db: DatabaseSession,
    _service_auth: ServiceAuth,
) -> dict[str, int]:
    """Cancel pending scheduled notifications from another service."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        try:
            cancelled = await service.cancel_scheduled(
                user_id=request.user_id,
                notification_type=request.notification_type,
                data_match=request.data_match,
            )
        finally:
            await service.cleanup()
    return {"cancelled": cancelled}
