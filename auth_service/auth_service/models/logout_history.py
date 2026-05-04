"""Logout history database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from auth_service.database import Base


class LogoutHistory(Base):
    """Logout history model for security audit."""

    __tablename__ = "logout_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    logout_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    method: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        """Representation of LogoutHistory."""
        return f"<LogoutHistory(id={self.id}, user_id={self.user_id})>"
