"""Meeting material database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from meeting_service.core.enums import MaterialType
from meeting_service.database import Base

if TYPE_CHECKING:
    from meeting_service.models.meeting import Meeting


class MeetingMaterial(Base):
    """Material attached to a meeting template."""

    __tablename__ = "meeting_materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)  # Link to file or external resource
    type: Mapped[MaterialType] = mapped_column(
        Enum(MaterialType, name="materialtype"), nullable=False
    )
    order: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    meeting: Mapped[Meeting] = relationship("Meeting", back_populates="materials")

    def __repr__(self) -> str:
        """Representation of MeetingMaterial."""
        return f"<MeetingMaterial(id={self.id}, title={self.title})>"
