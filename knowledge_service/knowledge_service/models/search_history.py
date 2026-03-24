"""Search history database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from knowledge_service.database import Base

if TYPE_CHECKING:
    from knowledge_service.models import Department


class SearchHistory(Base):
    """Search history model for tracking user searches."""

    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    query: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    # Search context
    filters: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    department: Mapped["Department | None"] = relationship("Department", back_populates="search_histories")
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        """Representation of SearchHistory."""
        return f"<SearchHistory(id={self.id}, query={self.query}, user_id={self.user_id})>"
