"""Repository interfaces following Interface Segregation Principle."""

from notification_service.repositories.interfaces.base import BaseRepository
from notification_service.repositories.interfaces.notification import (
    INotificationRepository,
    IScheduledNotificationRepository,
)
from notification_service.repositories.interfaces.template import INotificationTemplateRepository

__all__ = [
    "BaseRepository",
    "INotificationRepository",
    "INotificationTemplateRepository",
    "IScheduledNotificationRepository",
]
