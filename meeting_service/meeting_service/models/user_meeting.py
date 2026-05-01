"""User meeting assignment database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from meeting_service.core.enums import MeetingStatus
from meeting_service.database import Base
from meeting_service.models.meeting import Meeting

if TYPE_CHECKING:
    pass


class UserMeeting(Base):
    """Meeting assigned to a specific user."""

    __tablename__ = "user_meetings"

    # Prevent duplicate assignments - database-level race condition protection
    __table_args__ = (UniqueConstraint("user_id", "meeting_id", name="uq_user_meeting_assignment"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # from auth service
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), nullable=False)

    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus, name="meetingstatus"), default=MeetingStatus.SCHEDULED, nullable=False
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5

    google_calendar_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    meeting: Mapped[Meeting] = relationship("Meeting", back_populates="assignments")

    def __repr__(self) -> str:
        """Representation of UserMeeting."""
        return f"<UserMeeting(id={self.id}, user_id={self.user_id}, status={self.status})>"
