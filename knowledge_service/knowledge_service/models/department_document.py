"""Department document database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from knowledge_service.database import Base

if TYPE_CHECKING:
    pass


class DepartmentDocument(Base):
    """Document attached to a department."""

    __tablename__ = "department_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Document metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "Регламенты", "Шаблоны", "Полезные ресурсы"

    # File information
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)  # S3 path
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Visibility
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)  # visible to all or only department

    # Author
    uploaded_by: Mapped[int] = mapped_column(Integer, nullable=False)  # user_id from auth_service

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        """Representation of DepartmentDocument."""
        return f"<DepartmentDocument(id={self.id}, title={self.title}, department_id={self.department_id})>"
