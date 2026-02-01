"""Checklist and task database models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from checklists_service.core import ChecklistStatus, TaskStatus
from checklists_service.database import Base

if TYPE_CHECKING:
    from checklists_service.models import Template


class Checklist(Base):
    """Personal checklist model for individual users."""

    __tablename__ = "checklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Ownership
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Template reference
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"), nullable=False)

    # Progress tracking
    status: Mapped[ChecklistStatus] = mapped_column(
        Enum(ChecklistStatus), default=ChecklistStatus.IN_PROGRESS, nullable=False
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tasks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timeline
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Assignees
    mentor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hr_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Metadata
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    template: Mapped["Template"] = relationship("Template", back_populates="checklists")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="checklist", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Representation of Checklist."""
        return f"<Checklist(id={self.id}, user_id={self.user_id}, progress={self.progress_percentage}%)>"


class Task(Base):
    """Individual task model within a checklist."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    checklist_id: Mapped[int] = mapped_column(ForeignKey("checklists.id"), nullable=False)
    template_task_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Task details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Status and tracking
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Assignees
    assignee_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assignee_role: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Timeline
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Completion details
    completed_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)

    # Dependencies
    depends_on: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    blocks: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    checklist: Mapped["Checklist"] = relationship("Checklist", back_populates="tasks")

    def __repr__(self) -> str:
        """Representation of Task."""
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
