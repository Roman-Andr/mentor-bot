"""Feedback status change history database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from feedback_service.database import Base


class FeedbackStatusChangeHistory(Base):
    """Feedback status change history model for audit."""

    __tablename__ = "feedback_status_change_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedback.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    meta_data: Mapped[dict | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Representation of FeedbackStatusChangeHistory."""
        return f"<FeedbackStatusChangeHistory(id={self.id}, feedback_id={self.feedback_id}, action={self.action})>"
