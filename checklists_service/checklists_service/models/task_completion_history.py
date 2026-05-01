"""Task completion history database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from checklists_service.database import Base


class TaskCompletionHistory(Base):
    """Task completion history model for audit."""

    __tablename__ = "task_completion_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    checklist_id: Mapped[int] = mapped_column(ForeignKey("checklists.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[dict | None] = mapped_column(Text, nullable=True)
    completed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    def __repr__(self) -> str:
        """Representation of TaskCompletionHistory."""
        return f"<TaskCompletionHistory(id={self.id}, task_id={self.task_id}, user_id={self.user_id})>"
