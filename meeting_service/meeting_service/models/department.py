"""Department database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from meeting_service.database import Base

if TYPE_CHECKING:
    from meeting_service.models import Meeting


class Department(Base):
    """Department model representing company departments."""

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="department")

    def __repr__(self) -> str:
        """Representation of Department."""
        return f"<Department(id={self.id}, name={self.name})>"
