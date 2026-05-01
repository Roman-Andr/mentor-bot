"""Invitation database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from auth_service.core import EmployeeLevel, InvitationStatus, UserRole
from auth_service.database import Base

if TYPE_CHECKING:
    from auth_service.models.department import Department
    from auth_service.models.user import User


class Invitation(Base):
    """Invitation model for user registration."""

    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # User information
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    department: Mapped[Department | None] = relationship("Department", back_populates="invitations")
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[EmployeeLevel | None] = mapped_column(
        Enum(EmployeeLevel, name="employeelevel", native=False), nullable=True
    )
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="userrole"), default=UserRole.NEWBIE, nullable=False)

    # Mentor assignment
    mentor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    mentor: Mapped[User | None] = relationship("User", foreign_keys=[mentor_id])

    # Status
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus, name="invitationstatus"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[User | None] = relationship("User", foreign_keys=[user_id], back_populates="invitations")

    def __repr__(self) -> str:
        """Representation of Invitation."""
        return f"<Invitation(id={self.id}, email={self.email}, status={self.status})>"
