"""Meeting template database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from meeting_service.core.enums import EmployeeLevel, MeetingType
from meeting_service.database import Base

if TYPE_CHECKING:
    from meeting_service.models.department import Department
    from meeting_service.models.material import MeetingMaterial
    from meeting_service.models.user_meeting import UserMeeting


class Meeting(Base):
    """Meeting template model."""

    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Core fields
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[MeetingType] = mapped_column(Enum(MeetingType), nullable=False, index=True)

    # Targeting (who this meeting is for)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    department: Mapped["Department | None"] = relationship("Department", back_populates="meetings")
    position: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    level: Mapped[EmployeeLevel | None] = mapped_column(Enum(EmployeeLevel, native=False), nullable=True, index=True)

    # Scheduling rules
    is_mandatory: Mapped[bool] = mapped_column(default=True, nullable=False)
    order: Mapped[int] = mapped_column(default=0, nullable=False)  # Display order
    deadline_days: Mapped[int] = mapped_column(default=7, nullable=False)  # Days from start of onboarding

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    materials: Mapped[list["MeetingMaterial"]] = relationship(
        "MeetingMaterial", back_populates="meeting", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["UserMeeting"]] = relationship(
        "UserMeeting", back_populates="meeting", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representation of Meeting."""
        return f"<Meeting(id={self.id}, title={self.title}, type={self.type})>"
