"""API endpoint routers."""

from escalation_service.api.endpoints.escalations import router as escalations_router

__all__ = [
    "escalations_router",
]
