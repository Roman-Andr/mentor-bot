"""Enum definitions for the Notification Service."""

from enum import Enum


class NotificationType(str, Enum):
    """Type of notification."""

    TASK_REMINDER = "TASK_REMINDER"
    MEETING_REMINDER = "MEETING_REMINDER"
    ONBOARDING_EVENT = "ONBOARDING_EVENT"
    GENERAL = "GENERAL"
    ESCALATION = "ESCALATION"


class NotificationChannel(str, Enum):
    """Channel through which notification is sent."""

    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"
    BOTH = "BOTH"  # For notifications that should go through both channels


class NotificationStatus(str, Enum):
    """Status of a notification."""

    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
