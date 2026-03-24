"""Database models for Telegram Bot."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all database models."""


class UserSession(Base):
    """User session and preferences."""

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, index=True, nullable=True
    )  # Reference to auth service

    # User preferences
    language: Mapped[str] = mapped_column(String(10), default="en")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_time: Mapped[str] = mapped_column(String(5), default="09:00")

    # Session data
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    session_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    def __repr__(self) -> str:
        """Representation of UserSession."""
        return f"<UserSession(telegram_id={self.telegram_id}, user_id={self.user_id})>"


class BotLog(Base):
    """Bot interaction logs."""

    __tablename__ = "bot_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=True)

    # Interaction details
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., "command", "callback", "message"
    command: Mapped[str] = mapped_column(String(100), nullable=True)
    data: Mapped[str] = mapped_column(Text, nullable=True)

    # Response details
    response_time: Mapped[float] = mapped_column(nullable=True)  # in seconds
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    # Metadata
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        """Representation of BotLog."""
        return f"<BotLog(telegram_id={self.telegram_id}, action={self.action})>"


class Notification(Base):
    """Scheduled notifications."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=True)

    # Notification details
    notification_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., "task_reminder", "meeting"
    message: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, sent, failed, cancelled
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    metadata_obj: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    def __repr__(self) -> str:
        """Representation of Notification."""
        return f"<Notification(telegram_id={self.telegram_id}, type={self.notification_type})>"
