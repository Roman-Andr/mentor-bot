"""Comment model for feedback service."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from feedback_service.database import Base


class Comment(Base):
    """Model for comments and suggestions."""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Metadata for anonymous feedback analytics
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Reply fields (for HR/Admin responses)
    reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    replied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    replied_by: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Optional contact info for follow-up on anonymous comments
    allow_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
