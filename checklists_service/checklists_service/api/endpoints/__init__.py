"""API endpoint routers for the Checklists Service."""

from checklists_service.api.endpoints.audit import router as audit_router
from checklists_service.api.endpoints.checklists import router as checklists_router
from checklists_service.api.endpoints.tasks import router as tasks_router
from checklists_service.api.endpoints.templates import router as templates_router

__all__ = [
    "audit_router",
    "checklists_router",
    "tasks_router",
    "templates_router",
]
