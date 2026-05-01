"""Attachment database model for article files."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from knowledge_service.config import settings
from knowledge_service.core import AttachmentType
from knowledge_service.database import Base
from knowledge_service.models import Article

if TYPE_CHECKING:
    pass


class Attachment(Base):
    """Attachment model for article files and links."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Attachment details
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[AttachmentType] = mapped_column(
        Enum(AttachmentType, name="attachmenttype"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in bytes
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Metadata
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_downloadable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    article: Mapped[Article] = relationship("Article", back_populates="attachments")

    @property
    def file_url(self) -> str:
        """Get download URL for the attachment."""
        if self.type == AttachmentType.LINK:
            return self.url
        return f"{settings.API_V1_PREFIX}/attachments/{self.id}/download"

    def __repr__(self) -> str:
        """Representation of Attachment."""
        return f"<Attachment(id={self.id}, name={self.name}, type={self.type})>"
