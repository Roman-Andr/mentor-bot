"""Invitation status history database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from auth_service.database import Base


class InvitationStatusHistory(Base):
    """Invitation status history model for audit."""

    __tablename__ = "invitation_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invitation_id: Mapped[int] = mapped_column(ForeignKey("invitations.id"), nullable=False, index=True)
    old_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    meta_data: Mapped[dict | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Representation of InvitationStatusHistory."""
        return f"<InvitationStatusHistory(id={self.id}, invitation_id={self.invitation_id}, old_status={self.old_status}, new_status={self.new_status})>"
