"""Google Calendar account model for OAuth2 integration."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from meeting_service.database import Base


class GoogleCalendarAccount(Base):
    """Google Calendar account credentials for a user."""

    __tablename__ = "google_calendar_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)

    # OAuth2 tokens
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=True)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Calendar info
    calendar_id: Mapped[str] = mapped_column(String(255), nullable=False, default="primary")
    sync_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        return f"<GoogleCalendarAccount(user_id={self.user_id}, calendar_id={self.calendar_id})>"
