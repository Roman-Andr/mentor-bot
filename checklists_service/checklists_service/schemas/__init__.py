"""Pydantic schemas for request/response validation."""

from checklists_service.schemas.checklist import (
    AutoCreateChecklistsRequest,
    ChecklistBase,
    ChecklistCreate,
    ChecklistListResponse,
    ChecklistResponse,
    ChecklistStats,
    ChecklistUpdate,
)
from checklists_service.schemas.responses import (
    HealthCheck,
    MessageResponse,
    ServiceStatus,
)
from checklists_service.schemas.task import (
    TaskBase,
    TaskBulkUpdate,
    TaskCreate,
    TaskProgress,
    TaskResponse,
    TaskUpdate,
)
from checklists_service.schemas.template import (
    DepartmentInfo,
    TaskTemplateCreate,
    TaskTemplateResponse,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
    TemplateWithTasks,
)

__all__ = [
    "AutoCreateChecklistsRequest",
    "ChecklistBase",
    "ChecklistCreate",
    "ChecklistListResponse",
    "ChecklistResponse",
    "ChecklistStats",
    "ChecklistUpdate",
    "DepartmentInfo",
    "HealthCheck",
    "MessageResponse",
    "ServiceStatus",
    "TaskBase",
    "TaskBulkUpdate",
    "TaskCreate",
    "TaskProgress",
    "TaskResponse",
    "TaskTemplateCreate",
    "TaskTemplateResponse",
    "TaskUpdate",
    "TemplateCreate",
    "TemplateResponse",
    "TemplateUpdate",
    "TemplateWithTasks",
]
