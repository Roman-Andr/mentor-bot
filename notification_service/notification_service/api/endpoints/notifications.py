"""Notification management endpoints."""

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status

from notification_service.api.deps import (
    CurrentUser,
    DatabaseSession,
    HRUser,
)
from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from notification_service.schemas import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
    ScheduledNotificationCreate,
    ScheduledNotificationResponse,
)
from notification_service.services import NotificationService
from notification_service.services.template import (
    MissingTemplateVariablesError,
    TemplateNotFoundError,
)

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
    sort_by: Annotated[str | None, Query()] = None,
    sort_order: Annotated[str, Query()] = "desc",
) -> list[NotificationResponse]:
    """Get notification history for the current user."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        notifications, _ = await service.find_notifications(
            skip=skip,
            limit=limit,
            user_id=current_user.id,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [NotificationResponse.model_validate(n) for n in notifications]


@router.get("/history/{user_id}")
async def get_user_notification_history(
    user_id: int,
    db: DatabaseSession,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    sort_by: Annotated[str | None, Query()] = None,
    sort_order: Annotated[str, Query()] = "desc",
) -> list[NotificationResponse]:
    """Get notification history for a specific user (HR/admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        notifications, _ = await service.find_notifications(
            skip=skip,
            limit=limit,
            user_id=user_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [NotificationResponse.model_validate(n) for n in notifications]


@router.get("/admin/list")
async def list_notifications(
    db: DatabaseSession,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user_id: Annotated[int | None, Query()] = None,
    notification_type: Annotated[NotificationType | None, Query(alias="type")] = None,
    status: Annotated[NotificationStatus | None, Query()] = None,
    sort_by: Annotated[str | None, Query()] = None,
    sort_order: Annotated[str, Query()] = "desc",
) -> NotificationListResponse:
    """Get paginated list of notifications with filtering and sorting (HR/admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)
        notifications, total = await service.find_notifications(
            skip=skip,
            limit=limit,
            user_id=user_id,
            notification_type=notification_type,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    pages = (total + limit - 1) // limit if limit > 0 else 0
    return NotificationListResponse(
        total=total,
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.post("/send-template")
async def send_template_notification(
    template_name: str,
    user_id: int,
    variables: dict[str, Any],
    channel: NotificationChannel,
    db: DatabaseSession,
    current_user: HRUser,
    recipient_telegram_id: int | None = None,
    recipient_email: str | None = None,
    notification_type: NotificationType = NotificationType.GENERAL,
    language: str = "en",
) -> NotificationResponse:
    """Send a notification using a template (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)

        try:
            notification = await service.send_template(
                template_name=template_name,
                user_id=user_id,
                recipient_telegram_id=recipient_telegram_id,
                recipient_email=recipient_email,
                variables=variables,
                channel=channel,
                notification_type=notification_type,
                language=language,
            )
        except TemplateNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from e
        except MissingTemplateVariablesError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

    return NotificationResponse.model_validate(notification)


@router.post("/schedule-template")
async def schedule_template_notification(
    template_name: str,
    user_id: int,
    variables: dict[str, Any],
    channel: NotificationChannel,
    scheduled_time: datetime,
    db: DatabaseSession,
    current_user: HRUser,
    recipient_telegram_id: int | None = None,
    recipient_email: str | None = None,
    notification_type: NotificationType = NotificationType.GENERAL,
    language: str = "en",
) -> ScheduledNotificationResponse:
    """Schedule a template-based notification (HR/Admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = NotificationService(uow)

        try:
            scheduled = await service.schedule_template(
                template_name=template_name,
                user_id=user_id,
                recipient_telegram_id=recipient_telegram_id,
                recipient_email=recipient_email,
                variables=variables,
                channel=channel,
                scheduled_time=scheduled_time,
                notification_type=notification_type,
                language=language,
            )
        except TemplateNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from e
        except MissingTemplateVariablesError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

    return ScheduledNotificationResponse.model_validate(scheduled)
