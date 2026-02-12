"""User meeting assignment database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from meeting_service.core.enums import MeetingStatus
from meeting_service.database import Base

if TYPE_CHECKING:
    from meeting_service.models.meeting import Meeting


class UserMeeting(Base):
    """Meeting assigned to a specific user."""

    __tablename__ = "user_meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # from auth service
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), nullable=False)

    status: Mapped[MeetingStatus] = mapped_column(Enum(MeetingStatus), default=MeetingStatus.SCHEDULED, nullable=False)

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="assignments")

    def __repr__(self) -> str:
        """Representation of UserMeeting."""
        return f"<UserMeeting(id={self.id}, user_id={self.user_id}, status={self.status})>"
