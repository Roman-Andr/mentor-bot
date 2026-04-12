"""Pydantic schemas for request/response validation."""

from checklists_service.schemas.checklist import (
    AutoCreateChecklistsRequest,
    ChecklistBase,
    ChecklistCreate,
    ChecklistListResponse,
    ChecklistResponse,
    ChecklistStats,
    ChecklistUpdate,
    CompletionTimeStats,
    MonthlyStats,
)
from checklists_service.schemas.department import DepartmentCreate, DepartmentResponse
from checklists_service.schemas.responses import (
    HealthCheck,
    MessageResponse,
    ServiceStatus,
)
from checklists_service.schemas.task import (
    TaskAttachmentResponse,
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
    "CompletionTimeStats",
    "DepartmentCreate",
    "DepartmentInfo",
    "DepartmentResponse",
    "HealthCheck",
    "MessageResponse",
    "MonthlyStats",
    "ServiceStatus",
    "TaskAttachmentResponse",
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
