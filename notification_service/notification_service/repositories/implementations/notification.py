"""SQLAlchemy implementations of notification repositories."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import Column, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.core.enums import NotificationStatus, NotificationType
from notification_service.core.exceptions import NotFoundException
from notification_service.models import Notification, ScheduledNotification
from notification_service.repositories.implementations.base import SqlAlchemyBaseRepository
from notification_service.repositories.interfaces.notification import (
    INotificationRepository,
    IScheduledNotificationRepository,
)


class NotificationRepository(SqlAlchemyBaseRepository[Notification, int], INotificationRepository):
    """SQLAlchemy implementation of Notification repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize NotificationRepository with database session."""
        super().__init__(session, Notification)

    def _get_sort_column(self, sort_by: str | None) -> Column:
        """Get SQLAlchemy column for sorting."""
        column_map = {
            "type": Notification.type,
            "channel": Notification.channel,
            "status": Notification.status,
            "user": Notification.user_id,
            "createdAt": Notification.created_at,
            "scheduledFor": Notification.scheduled_for,
            "sentAt": Notification.sent_at,
        }
        return column_map.get(sort_by, Notification.created_at)

    async def find_notifications(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
        notification_type: NotificationType | None = None,
        status: NotificationStatus | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[Sequence[Notification], int]:
        """Find notifications with filtering and return results with total count."""
        count_stmt = select(func.count(Notification.id))
        stmt = select(Notification)

        if user_id:
            stmt = stmt.where(Notification.user_id == user_id)
            count_stmt = count_stmt.where(Notification.user_id == user_id)
        if notification_type:
            stmt = stmt.where(Notification.type == notification_type)
            count_stmt = count_stmt.where(Notification.type == notification_type)
        if status:
            stmt = stmt.where(Notification.status == status)
            count_stmt = count_stmt.where(Notification.status == status)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)
        stmt = stmt.order_by(sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        notifications = result.scalars().all()

        return notifications, total

    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Notification]:
        """Get notifications for a specific user."""
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()


class ScheduledNotificationRepository(
    SqlAlchemyBaseRepository[ScheduledNotification, int], IScheduledNotificationRepository
):
    """SQLAlchemy implementation of ScheduledNotification repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ScheduledNotificationRepository with database session."""
        super().__init__(session, ScheduledNotification)

    async def find_pending_before(self, before: datetime) -> Sequence[ScheduledNotification]:
        """Find all pending scheduled notifications with scheduled_time <= before."""
        stmt = (
            select(ScheduledNotification)
            .where(
                and_(
                    ScheduledNotification.scheduled_time <= before,
                    ScheduledNotification.processed == False,  # noqa: E712
                )
            )
            .order_by(ScheduledNotification.scheduled_time.asc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def mark_processed(self, notification_id: int) -> ScheduledNotification:
        """Mark a scheduled notification as processed."""
        notification = await self.get_by_id(notification_id)
        if not notification:
            not_found_msg = "ScheduledNotification"
            raise NotFoundException(not_found_msg)

        notification.processed = True
        notification.processed_at = datetime.now(UTC)
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def increment_retry(
        self, notification_id: int, next_scheduled_time: datetime
    ) -> ScheduledNotification:
        """Increment retry count and update scheduled time for next attempt."""
        notification = await self.get_by_id(notification_id)
        if not notification:
            not_found_msg = "ScheduledNotification"
            raise NotFoundException(not_found_msg)

        notification.retry_count += 1
        notification.failed_at = datetime.now(UTC)
        notification.scheduled_time = next_scheduled_time
        await self._session.flush()
        await self._session.refresh(notification)
        return notification
