"""Scheduled notification model for future notifications."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from notification_service.core.enums import NotificationChannel, NotificationType
from notification_service.database import Base


class ScheduledNotification(Base):
    """Model for notifications scheduled to be sent at a specific time."""

    __tablename__ = "scheduled_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Recipient
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    recipient_telegram_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recipient_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Content
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, schema="notification", name="notificationtype"), nullable=False, index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, schema="notification", name="notificationchannel"), nullable=False
    )
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Scheduling
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    processed: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Retry configuration
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(default=3, nullable=False)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        """Representation of ScheduledNotification."""
        return f"<ScheduledNotification(id={self.id}, scheduled_time={self.scheduled_time})>"
