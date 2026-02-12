"""Repository interfaces following Interface Segregation Principle."""

from notification_service.repositories.interfaces.base import BaseRepository
from notification_service.repositories.interfaces.notification import (
    INotificationRepository,
    IScheduledNotificationRepository,
)

__all__ = [
    "BaseRepository",
    "INotificationRepository",
    "IScheduledNotificationRepository",
]
