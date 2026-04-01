"""Dialogue scenario schemas for request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from knowledge_service.core import DialogueAnswerType, DialogueCategory


class DialogueStepBase(BaseModel):
    """Base dialogue step schema."""

    step_number: int = Field(..., ge=1)
    question: str = Field(..., min_length=1)
    answer_type: DialogueAnswerType = DialogueAnswerType.TEXT
    options: list[dict[str, Any]] | None = None
    answer_content: str | None = None
    next_step_id: int | None = None
    parent_step_id: int | None = None
    is_final: bool = False


class DialogueStepCreate(DialogueStepBase):
    """Dialogue step creation schema."""


class DialogueStepUpdate(BaseModel):
    """Dialogue step update schema."""

    step_number: int | None = Field(None, ge=1)
    question: str | None = Field(None, min_length=1)
    answer_type: DialogueAnswerType | None = None
    options: list[dict[str, Any]] | None = None
    answer_content: str | None = None
    next_step_id: int | None = None
    parent_step_id: int | None = None
    is_final: bool | None = None


class DialogueStepResponse(DialogueStepBase):
    """Dialogue step response schema."""

    id: int
    scenario_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DialogueScenarioBase(BaseModel):
    """Base dialogue scenario schema."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    keywords: list[str] = Field(default_factory=list)
    category: DialogueCategory
    is_active: bool = True
    display_order: int = Field(0, ge=0)


class DialogueScenarioCreate(DialogueScenarioBase):
    """Dialogue scenario creation schema."""

    steps: list[DialogueStepCreate] = Field(default_factory=list)


class DialogueScenarioUpdate(BaseModel):
    """Dialogue scenario update schema."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    keywords: list[str] | None = None
    category: DialogueCategory | None = None
    is_active: bool | None = None
    display_order: int | None = Field(None, ge=0)


class DialogueScenarioResponse(DialogueScenarioBase):
    """Dialogue scenario response schema."""

    id: int
    steps: list[DialogueStepResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DialogueScenarioListResponse(BaseModel):
    """Dialogue scenario list response schema."""

    total: int
    scenarios: list[DialogueScenarioResponse]
    page: int
    size: int
    pages: int


class DialogueStepReorderRequest(BaseModel):
    """Request schema for reordering steps."""

    step_ids: list[int] = Field(..., min_length=1)
