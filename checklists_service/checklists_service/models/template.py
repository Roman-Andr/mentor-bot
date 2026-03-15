"""Checklist template database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from checklists_service.core import EmployeeLevel, TaskCategory, TemplateStatus
from checklists_service.database import Base

if TYPE_CHECKING:
    from checklists_service.models import Checklist


class Template(Base):
    """Checklist template model for onboarding workflows."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Target audience
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[EmployeeLevel | None] = mapped_column(Enum(EmployeeLevel), nullable=True)

    # Configuration
    duration_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    task_categories: Mapped[list[TaskCategory]] = mapped_column(JSONB, default=list, nullable=False)
    default_assignee_role: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status
    status: Mapped[TemplateStatus] = mapped_column(Enum(TemplateStatus), default=TemplateStatus.ACTIVE, nullable=False)

    # Metadata
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    checklists: Mapped[list["Checklist"]] = relationship(
        "Checklist", back_populates="template", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["TaskTemplate"]] = relationship(
        "TaskTemplate", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representation of Template."""
        return f"<Template(id={self.id}, name={self.name}, department={self.department})>"


class TaskTemplate(Base):
    """Task template model for checklist items."""

    __tablename__ = "task_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Task configuration
    category: Mapped[TaskCategory] = mapped_column(
        Enum(TaskCategory), default=TaskCategory.DOCUMENTATION, nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    due_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Resources
    resources: Mapped[list[dict]] = mapped_column(JSONB, default=list, nullable=False)
    required_documents: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    # Assignee
    assignee_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    auto_assign: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Dependencies
    depends_on: Mapped[list[int]] = mapped_column(JSONB, default=list, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    template: Mapped["Template"] = relationship("Template", back_populates="tasks")

    def __repr__(self) -> str:
        """Representation of TaskTemplate."""
        return f"<TaskTemplate(id={self.id}, title={self.title}, template_id={self.template_id})>"
