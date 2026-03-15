from datetime import datetime

from feedback_service.database import Base
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column


class ExperienceRating(Base):
    """Model for experience ratings."""

    __tablename__ = "experience_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
