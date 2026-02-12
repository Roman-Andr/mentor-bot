"""Escalation request schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from escalation_service.core.enums import EscalationSource, EscalationStatus, EscalationType


class EscalationRequestBase(BaseModel):
    """Base escalation request schema."""

    user_id: int
    type: EscalationType
    source: EscalationSource
    reason: str | None = None
    context: dict = Field(default_factory=dict)
    assigned_to: int | None = None
    related_entity_type: str | None = None
    related_entity_id: int | None = None


class EscalationRequestCreate(EscalationRequestBase):
    """Escalation request creation schema."""


class EscalationRequestUpdate(BaseModel):
    """Escalation request update schema (for status changes)."""

    status: EscalationStatus | None = None
    assigned_to: int | None = None
    resolution_note: str | None = None  # optional note


class EscalationRequestResponse(EscalationRequestBase):
    """Escalation request response schema."""

    id: int
    status: EscalationStatus
    created_at: datetime
    updated_at: datetime | None = None
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class EscalationRequestListResponse(BaseModel):
    """Escalation request list response schema."""

    total: int
    requests: list[EscalationRequestResponse]
    page: int
    size: int
    pages: int
