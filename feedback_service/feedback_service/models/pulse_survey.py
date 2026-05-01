"""Pulse survey model for feedback service."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from feedback_service.database import Base


def _now() -> datetime:
    """Return a naive UTC datetime for PostgreSQL TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(UTC).replace(tzinfo=None)


class PulseSurvey(Base):
    """Model for daily pulse surveys."""

    __tablename__ = "pulse_surveys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)

    # Metadata for anonymous feedback analytics
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    position_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
