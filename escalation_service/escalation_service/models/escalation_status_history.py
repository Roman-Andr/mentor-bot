"""Escalation status history database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from escalation_service.database import Base

if TYPE_CHECKING:
    from escalation_service.models import Escalation, User


class EscalationStatusHistory(Base):
    """Escalation status history model for audit."""

    __tablename__ = "escalation_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    escalation_id: Mapped[int] = mapped_column(ForeignKey("escalations.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    metadata: Mapped[dict | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Representation of EscalationStatusHistory."""
        return f"<EscalationStatusHistory(id={self.id}, escalation_id={self.escalation_id}, action={self.action})>"
