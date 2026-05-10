"""API endpoint routers for feedback service."""

from .audit import router as audit_router
from .feedback import router as feedback_router
from .internal import router as internal_router

__all__ = ["audit_router", "feedback_router", "internal_router"]
