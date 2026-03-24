"""API endpoint routers for feedback service."""

from .feedback import router as feedback_router

__all__ = ["feedback_router"]
