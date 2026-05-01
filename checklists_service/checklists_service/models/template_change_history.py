"""Template change history database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from checklists_service.database import Base


class TemplateChangeHistory(Base):
    """Template change history model for audit."""

    __tablename__ = "template_change_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Representation of TemplateChangeHistory."""
        return f"<TemplateChangeHistory(id={self.id}, template_id={self.template_id}, action={self.action})>"
