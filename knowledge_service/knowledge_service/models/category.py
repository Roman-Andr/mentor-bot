"""Knowledge category database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from knowledge_service.core import EmployeeLevel
from knowledge_service.database import Base

if TYPE_CHECKING:
    from knowledge_service.models import Article, Category


class Category(Base):
    """Category model for organizing knowledge articles."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Hierarchy
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Target audience filtering
    department: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[EmployeeLevel | None] = mapped_column(String(50), nullable=True, index=True)

    # Metadata
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    parent: Mapped["Category | None"] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    articles: Mapped[list["Article"]] = relationship("Article", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Representation of Category."""
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"
