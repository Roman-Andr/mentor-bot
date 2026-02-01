"""Checklist schemas for request/response validation."""

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from checklists_service.core import ChecklistStatus


class ChecklistBase(BaseModel):
    """Base checklist schema."""

    user_id: int
    employee_id: str = Field(..., min_length=1, max_length=50)
    template_id: int
    start_date: datetime
    due_date: datetime | None = None
    mentor_id: int | None = None
    hr_id: int | None = None
    notes: str | None = None


class ChecklistCreate(ChecklistBase):
    """Checklist creation schema."""

    @field_validator("due_date")
    @classmethod
    def set_due_date(cls, v: datetime | None, info: Any) -> datetime | None:
        """Set due date if not provided."""
        if v is None and "start_date" in info.data:
            return info.data["start_date"] + timedelta(days=30)
        return v


class ChecklistUpdate(BaseModel):
    """Checklist update schema."""

    status: ChecklistStatus | None = None
    progress_percentage: int | None = Field(None, ge=0, le=100)
    mentor_id: int | None = None
    hr_id: int | None = None
    notes: str | None = None
    completed_at: datetime | None = None


class ChecklistResponse(ChecklistBase):
    """Checklist response schema."""

    id: int
    status: ChecklistStatus
    progress_percentage: int
    completed_tasks: int
    total_tasks: int
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    is_overdue: bool
    days_remaining: int | None

    model_config = ConfigDict(from_attributes=True)


class ChecklistStats(BaseModel):
    """Checklist statistics schema."""

    total: int = Field(..., description="Total number of checklists")
    completed: int = Field(..., description="Number of completed checklists")
    in_progress: int = Field(..., description="Number of in-progress checklists")
    overdue: int = Field(..., description="Number of overdue checklists")
    not_started: int = Field(..., description="Number of not started checklists")
    avg_completion_days: float = Field(..., description="Average completion time in days")
    completion_rate: float = Field(..., description="Completion rate percentage", ge=0.0, le=100.0)
    by_department: dict[str, int] = Field(..., description="Checklists count by department")
    recent_completions: list[dict[str, Any]] = Field(..., description="Recent checklist completions")


class ChecklistListResponse(BaseModel):
    """Checklist list response schema."""

    total: int
    checklists: list[ChecklistResponse]
    page: int
    size: int
    pages: int
    stats: ChecklistStats
