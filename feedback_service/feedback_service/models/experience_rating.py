"""Experience rating model for feedback service."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from feedback_service.database import Base


class ExperienceRating(Base):
    """Model for experience ratings."""

    __tablename__ = "experience_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Metadata for anonymous feedback analytics
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
