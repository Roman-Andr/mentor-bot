"""Mentor intervention history database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from escalation_service.database import Base

if TYPE_CHECKING:
    from escalation_service.models import Escalation, User


class MentorInterventionHistory(Base):
    """Mentor intervention history model for audit."""

    __tablename__ = "mentor_intervention_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    escalation_id: Mapped[int] = mapped_column(ForeignKey("escalations.id"), nullable=False, index=True)
    mentor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    intervention_type: Mapped[str] = mapped_column(String(50), nullable=False)
    intervention_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(50), nullable=True)
    escalation_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        """Representation of MentorInterventionHistory."""
        return f"<MentorInterventionHistory(id={self.id}, escalation_id={self.escalation_id}, mentor_id={self.mentor_id})>"
