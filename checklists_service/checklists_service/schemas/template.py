"""Template schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from checklists_service.core import EmployeeLevel, TaskCategory, TemplateStatus


class TemplateBase(BaseModel):
    """Base template schema."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    department_id: int | None = None
    position: str | None = Field(None, max_length=100)
    level: EmployeeLevel | None = Field(None, max_length=50)
    duration_days: int = Field(30, ge=1, le=365)
    task_categories: list[TaskCategory] = Field(default_factory=list)
    default_assignee_role: str | None = Field(None, max_length=50)


class TemplateCreate(TemplateBase):
    """Template creation schema."""

    status: TemplateStatus = TemplateStatus.DRAFT


class TemplateUpdate(BaseModel):
    """Template update schema."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    status: TemplateStatus | None = None
    is_default: bool | None = None


class TemplateResponse(TemplateBase):
    """Template response schema."""

    id: int
    status: TemplateStatus
    version: int
    is_default: bool
    created_at: datetime
    updated_at: datetime | None = None
    task_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class TaskTemplateBase(BaseModel):
    """Base task template schema."""

    template_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    instructions: str | None = None
    category: TaskCategory = TaskCategory.DOCUMENTATION
    order: int = Field(0, ge=0)
    due_days: int = Field(1, ge=0)
    estimated_minutes: int | None = Field(None, ge=1)
    resources: list[dict] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    assignee_role: str | None = Field(None, max_length=50)
    auto_assign: bool = True
    depends_on: list[int] = Field(default_factory=list)


class TaskTemplateCreate(TaskTemplateBase):
    """Task template creation schema."""


class TaskTemplateResponse(TaskTemplateBase):
    """Task template response schema."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TemplateWithTasks(TemplateResponse):
    """Template response with tasks."""

    tasks: list[TaskTemplateResponse]
