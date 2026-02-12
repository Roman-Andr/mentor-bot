"""Notification schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType


class NotificationBase(BaseModel):
    """Base notification schema."""

    user_id: int
    recipient_telegram_id: int | None = None
    recipient_email: str | None = Field(None, max_length=255)
    type: NotificationType
    channel: NotificationChannel
    subject: str | None = Field(None, max_length=500)
    body: str = Field(..., min_length=1)
    data: dict = Field(default_factory=dict)


class NotificationCreate(NotificationBase):
    """Notification creation schema (immediate sending)."""


class NotificationResponse(NotificationBase):
    """Notification response schema."""

    id: int
    status: NotificationStatus
    error_message: str | None = None
    created_at: datetime
    scheduled_for: datetime | None = None
    sent_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ScheduledNotificationCreate(BaseModel):
    """Scheduled notification creation schema."""

    user_id: int
    recipient_telegram_id: int | None = None
    recipient_email: str | None = Field(None, max_length=255)
    type: NotificationType
    channel: NotificationChannel
    subject: str | None = Field(None, max_length=500)
    body: str = Field(..., min_length=1)
    data: dict = Field(default_factory=dict)
    scheduled_time: datetime  # When to send


class ScheduledNotificationResponse(ScheduledNotificationCreate):
    """Scheduled notification response schema."""

    id: int
    processed: bool
    processed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
