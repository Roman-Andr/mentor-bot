"""Notification repository interfaces."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from notification_service.core.enums import NotificationStatus, NotificationType
from notification_service.models import Notification, ScheduledNotification
from notification_service.repositories.interfaces.base import BaseRepository


class INotificationRepository(BaseRepository["Notification", int]):
    """Notification repository interface."""

    @abstractmethod
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

    @abstractmethod
    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Notification]:
        """Get notifications for a specific user."""


class IScheduledNotificationRepository(BaseRepository["ScheduledNotification", int]):
    """Scheduled notification repository interface."""

    @abstractmethod
    async def find_pending_before(self, before: datetime) -> Sequence[ScheduledNotification]:
        """Find all pending scheduled notifications with scheduled_time <= before."""

    @abstractmethod
    async def mark_processed(self, notification_id: int) -> ScheduledNotification:
        """Mark a scheduled notification as processed."""

    @abstractmethod
    async def increment_retry(
        self, notification_id: int, next_scheduled_time: datetime
    ) -> ScheduledNotification:
        """Increment retry count and update scheduled time for next attempt."""
