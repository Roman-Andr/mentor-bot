"""Task schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from checklists_service.core import TaskStatus


class TaskBase(BaseModel):
    """Base task schema."""

    checklist_id: int
    template_task_id: int | None = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    category: str = Field(..., max_length=50)
    order: int = Field(0, ge=0)
    assignee_id: int | None = None
    assignee_role: str | None = Field(None, max_length=50)
    due_date: datetime
    depends_on: list[int] = Field(default_factory=list)


class TaskCreate(TaskBase):
    """Task creation schema."""


class TaskUpdate(BaseModel):
    """Task update schema."""

    status: TaskStatus | None = None
    assignee_id: int | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    completed_by: int | None = None
    completion_notes: str | None = None
    attachments: list[dict] | None = None


class TaskResponse(TaskBase):
    """Task response schema."""

    id: int
    status: TaskStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    completed_by: int | None = None
    completion_notes: str | None = None
    attachments: list[dict]
    blocks: list[int]
    created_at: datetime
    updated_at: datetime | None = None
    is_overdue: bool
    can_start: bool
    can_complete: bool

    model_config = ConfigDict(from_attributes=True)


class TaskProgress(BaseModel):
    """Task progress tracking schema."""

    task_id: int
    status: TaskStatus
    progress_percentage: int = Field(0, ge=0, le=100)
    notes: str | None = None
    attachments: list[dict] = Field(default_factory=list)


class TaskBulkUpdate(BaseModel):
    """Bulk task update schema."""

    task_ids: list[int]
    status: TaskStatus | None = None
    assignee_id: int | None = None
    due_date: datetime | None = None
