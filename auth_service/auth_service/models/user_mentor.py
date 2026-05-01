"""User-Mentor relationship database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from auth_service.database import Base

if TYPE_CHECKING:
    from auth_service.models.user import User


class UserMentor(Base):
    """Relationship between a user and their mentor."""

    __tablename__ = "user_mentors"
    __table_args__ = (CheckConstraint("user_id != mentor_id", name="ck_user_mentor_no_self"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    mentor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    user: Mapped[User] = relationship("User", foreign_keys=[user_id], back_populates="mentor_assignments")
    mentor: Mapped[User] = relationship("User", foreign_keys=[mentor_id], back_populates="mentee_assignments")

    def __repr__(self) -> str:
        """Representation of UserMentor."""
        return f"<UserMentor(id={self.id}, user_id={self.user_id}, mentor_id={self.mentor_id})>"
