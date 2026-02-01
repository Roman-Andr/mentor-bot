"""Tag database model for article categorization."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from knowledge_service.database import Base
from knowledge_service.models.association import article_tags

if TYPE_CHECKING:
    from knowledge_service.models import Article


class Tag(Base):
    """Tag model for categorizing articles."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Usage statistics
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    articles: Mapped[list["Article"]] = relationship("Article", secondary=article_tags, back_populates="tags")

    def __repr__(self) -> str:
        """Representation of Tag."""
        return f"<Tag(id={self.id}, name={self.name}, usage_count={self.usage_count})>"
