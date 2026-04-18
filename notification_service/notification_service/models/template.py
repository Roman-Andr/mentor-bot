"""Notification template database model for storing email/Telegram templates."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from notification_service.database import Base


class NotificationTemplate(Base):
    """Notification template model for storing reusable message templates."""

    __tablename__ = "notification_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Template identification
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)  # email, telegram
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Template content
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Template metadata
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    variables: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Unique constraint: only one active template per name/channel/language combination
    __table_args__ = (
        UniqueConstraint("name", "channel", "language", "is_active", name="uix_template_name_channel_lang_active"),
    )

    def __repr__(self) -> str:
        """Representation of NotificationTemplate."""
        return f"<NotificationTemplate(id={self.id}, name={self.name}, channel={self.channel}, lang={self.language})>"
