"""Knowledge article database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from knowledge_service.core import ArticleStatus, EmployeeLevel
from knowledge_service.database import Base
from knowledge_service.models.association import article_tags

if TYPE_CHECKING:
    from knowledge_service.models import Attachment, Category, Tag


class Article(Base):
    """Knowledge article model."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Category relationship
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    # Author information
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    author_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Target audience filtering
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[EmployeeLevel | None] = mapped_column(String(50), nullable=True, index=True)

    # Status and visibility
    status: Mapped[ArticleStatus] = mapped_column(String(50), default=ArticleStatus.DRAFT, nullable=False, index=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # SEO and metadata
    meta_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    keywords: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    # Full-text search
    search_vector: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        nullable=True,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    category: Mapped[Category | None] = relationship("Category", back_populates="articles")
    attachments: Mapped[list[Attachment]] = relationship(
        "Attachment", back_populates="article", cascade="all, delete-orphan"
    )
    tags: Mapped[list[Tag]] = relationship("Tag", secondary=article_tags, back_populates="articles")

    @property
    def is_published(self) -> bool:
        """Check if article is published."""
        return self.status == ArticleStatus.PUBLISHED

    def __repr__(self) -> str:
        """Representation of Article."""
        return f"<Article(id={self.id}, title={self.title}, status={self.status})>"
