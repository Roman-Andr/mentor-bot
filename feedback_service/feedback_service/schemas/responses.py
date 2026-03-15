from typing import Any

from pydantic import BaseModel


class ServiceStatus(BaseModel):
    """Service status response schema."""

    service: str
    version: str
    status: str
    docs: str | None = None


class HealthCheck(BaseModel):
    """Health check response schema."""

    status: str
    service: str
    timestamp: str
    dependencies: dict[str, Any]
