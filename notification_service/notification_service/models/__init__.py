"""Models package for the Notification Service."""

from notification_service.models.notification import Notification
from notification_service.models.scheduled import ScheduledNotification

__all__ = [
    "Notification",
    "ScheduledNotification",
]
