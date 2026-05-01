"""Certificate database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from checklists_service.database import Base


class Certificate(Base):
    """Certificate model for completed onboarding programs."""

    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cert_uid: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    checklist_id: Mapped[int] = mapped_column(ForeignKey("checklists.id"), nullable=False, unique=True)
    hr_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mentor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("cert_uid", name="uq_cert_uid"),)

    def __repr__(self) -> str:
        """Representation of Certificate."""
        return f"<Certificate(id={self.id}, cert_uid={self.cert_uid}, user_id={self.user_id})>"
