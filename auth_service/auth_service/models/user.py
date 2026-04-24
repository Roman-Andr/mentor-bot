"""User database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from auth_service.core import EmployeeLevel, UserRole
from auth_service.database import Base

if TYPE_CHECKING:
    from auth_service.models import Department, Invitation
    from auth_service.models.password_reset import PasswordResetToken
    from auth_service.models.user_mentor import UserMentor


class User(Base):
    """User model representing system users."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Company information
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    department: Mapped[Department | None] = relationship("Department", back_populates="users")
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[EmployeeLevel | None] = mapped_column(
        Enum(EmployeeLevel, schema="auth", name="employeelevel", native=False), nullable=True
    )
    hire_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Authentication and authorization
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, schema="auth", name="userrole"), default=UserRole.NEWBIE, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    invitations: Mapped[list[Invitation]] = relationship(
        "Invitation", foreign_keys="Invitation.user_id", back_populates="user", cascade="all, delete-orphan"
    )
    mentor_assignments: Mapped[list[UserMentor]] = relationship(
        "UserMentor", foreign_keys="UserMentor.user_id", back_populates="user", cascade="all, delete-orphan"
    )
    mentee_assignments: Mapped[list[UserMentor]] = relationship(
        "UserMentor", foreign_keys="UserMentor.mentor_id", back_populates="mentor", cascade="all, delete-orphan"
    )
    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def mentor_id(self) -> int | None:
        """Get active mentor ID from mentor assignments."""
        for assignment in self.mentor_assignments:
            if assignment.is_active:
                return assignment.mentor_id
        return None

    @property
    def full_name(self) -> str:
        """Get full name combining first and last name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def __repr__(self) -> str:
        """Representation of User."""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


@event.listens_for(User, "before_insert")
@event.listens_for(User, "before_update")
def normalize_email_case(_mapper: object, _connection: object, target: "User") -> None:
    """Normalize email to lowercase before saving."""
    if target.email:
        target.email = target.email.lower()
