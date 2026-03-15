"""Escalation request database model."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from escalation_service.core.enums import EscalationSource, EscalationStatus, EscalationType
from escalation_service.database import Base


class EscalationRequest(Base):
    """Model representing an escalation request."""

    __tablename__ = "escalation_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Who created the request
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Request details
    type: Mapped[EscalationType] = mapped_column(Enum(EscalationType), nullable=False, index=True)
    source: Mapped[EscalationSource] = mapped_column(Enum(EscalationSource), nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)  # free text explanation
    context: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)  # additional context

    # Assignment and status
    status: Mapped[EscalationStatus] = mapped_column(
        Enum(EscalationStatus), default=EscalationStatus.PENDING, nullable=False, index=True
    )
    assigned_to: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)  # user_id of assignee

    # Related entity (optional)
    related_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "task", "search_query"
    related_entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        """Representation of EscalationRequest."""
        return f"<EscalationRequest(id={self.id}, user_id={self.user_id}, type={self.type}, status={self.status})>"
