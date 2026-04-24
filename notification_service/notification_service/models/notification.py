"""Notification database model for sent notifications."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.database import Base


class Notification(Base):
    """Notification model for tracking sent notifications."""

    __tablename__ = "notifications"

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
    data: Mapped[dict] = mapped_column(
        JSON, default=dict, nullable=False
    )  # Additional context (e.g., task_id, meeting_id)

    # Status
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, schema="notification", name="notificationstatus"),
        default=NotificationStatus.PENDING,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # If scheduled
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        """Representation of Notification."""
        return f"<Notification(id={self.id}, type={self.type}, status={self.status})>"
