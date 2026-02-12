"""Common response schemas."""

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str


class HealthCheck(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    timestamp: str | None = Field(None, description="Check timestamp")
    dependencies: dict | None = Field(default_factory=dict, description="Dependency health status")


class ServiceStatus(BaseModel):
    """Service status response schema."""

    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: str = Field(..., description="Service status")
    docs: str | None = Field(None, description="API documentation URL if debug mode is enabled")
