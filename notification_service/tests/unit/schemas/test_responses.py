"""Unit tests for notification_service/schemas/responses.py."""

from datetime import UTC, datetime

import pytest
from notification_service.schemas.responses import HealthCheck, ServiceStatus


class TestServiceStatus:
    """Tests for ServiceStatus schema."""

    def test_minimal_service_status(self) -> None:
        """Creates ServiceStatus with minimal data."""
        data = {
            "service": "Notification Service",
            "version": "1.0.0",
            "status": "running",
        }
        result = ServiceStatus(**data)

        assert result.service == "Notification Service"
        assert result.version == "1.0.0"
        assert result.status == "running"
        assert result.docs is None

    def test_service_status_with_docs(self) -> None:
        """Creates ServiceStatus with docs URL."""
        data = {
            "service": "Notification Service",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
        }
        result = ServiceStatus(**data)

        assert result.docs == "/docs"

    def test_service_status_fields_required(self) -> None:
        """service, version, and status are required."""
        with pytest.raises(Exception):
            ServiceStatus(version="1.0.0", status="running")


class TestHealthCheck:
    """Tests for HealthCheck schema."""

    def test_minimal_health_check(self) -> None:
        """Creates HealthCheck with minimal data."""
        data = {
            "status": "healthy",
            "service": "notification",
        }
        result = HealthCheck(**data)

        assert result.status == "healthy"
        assert result.service == "notification"
        assert result.timestamp is None
        assert result.dependencies is None

    def test_full_health_check(self) -> None:
        """Creates HealthCheck with all fields."""
        now = datetime.now(UTC)
        data = {
            "status": "healthy",
            "service": "notification",
            "timestamp": now,
            "dependencies": {
                "database": "connected",
                "redis": "connected",
            },
        }
        result = HealthCheck(**data)

        assert result.status == "healthy"
        assert result.service == "notification"
        assert result.timestamp == now
        assert result.dependencies == {"database": "connected", "redis": "connected"}

    def test_health_check_with_unhealthy_status(self) -> None:
        """HealthCheck can represent unhealthy state."""
        data = {
            "status": "unhealthy",
            "service": "notification",
            "dependencies": {
                "database": "disconnected",
            },
        }
        result = HealthCheck(**data)

        assert result.status == "unhealthy"
        assert result.dependencies["database"] == "disconnected"
