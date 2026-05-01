"""Meeting participant history database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from meeting_service.database import Base

if TYPE_CHECKING:
    from meeting_service.models import Meeting, User


class MeetingParticipantHistory(Base):
    """Meeting participant history model for audit."""

    __tablename__ = "meeting_participant_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta_data: Mapped[dict | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Representation of MeetingParticipantHistory."""
        return f"<MeetingParticipantHistory(id={self.id}, meeting_id={self.meeting_id}, user_id={self.user_id})>"
