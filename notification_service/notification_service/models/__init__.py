"""Models package for the Notification Service."""

from notification_service.models.notification import Notification
from notification_service.models.scheduled import ScheduledNotification
from notification_service.models.template import NotificationTemplate

__all__ = [
    "Notification",
    "NotificationTemplate",
    "ScheduledNotification",
]
