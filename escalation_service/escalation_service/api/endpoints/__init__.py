"""API endpoint routers."""

from escalation_service.api.endpoints.audit import router as audit_router
from escalation_service.api.endpoints.escalations import router as escalations_router

__all__ = [
    "audit_router",
    "escalations_router",
]
