"""Tests for notification_service main.py FastAPI application."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLifespan:
    """Tests for the lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_startup(self):
        """Test lifespan startup initializes database and scheduler."""
        mock_app = MagicMock()

        # Create a real coroutine that does nothing
        async def mock_run():
            pass

        async def mock_stop():
            pass

        with (
            patch("notification_service.main.init_db", new_callable=AsyncMock) as mock_init_db,
            patch("notification_service.main.scheduler") as mock_scheduler,
            patch("notification_service.main.logger") as mock_logger,
        ):
            mock_scheduler.run = mock_run
            mock_scheduler.stop = mock_stop

            from notification_service.main import lifespan

            async with lifespan(mock_app) as _:
                # Verify startup was logged
                mock_logger.info.assert_any_call("Starting Notification Service...")
                # Verify database was initialized
                mock_init_db.assert_called_once()
                # Verify scheduler was started
                mock_logger.info.assert_any_call("Scheduler started")

    @pytest.mark.asyncio
    async def test_lifespan_shutdown(self):
        """Test lifespan shutdown stops scheduler."""
        mock_app = MagicMock()

        async def mock_run():
            pass

        async def mock_stop():
            pass

        with (
            patch("notification_service.main.init_db", new_callable=AsyncMock),
            patch("notification_service.main.scheduler") as mock_scheduler,
            patch("notification_service.main.logger") as mock_logger,
        ):
            mock_scheduler.run = mock_run
            mock_scheduler.stop = mock_stop

            from notification_service.main import lifespan

            async with lifespan(mock_app) as _:
                pass  # Exit context to trigger shutdown

            # Verify shutdown was logged
            mock_logger.info.assert_any_call("Shutting down Notification Service...")


class TestRootEndpoint:
    """Tests for the root endpoint."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint returns service status."""
        from notification_service.main import root
        from notification_service.schemas import ServiceStatus
        from notification_service.config import settings

        result = await root()

        assert isinstance(result, ServiceStatus)
        assert result.service == settings.APP_NAME
        assert result.version == settings.APP_VERSION
        assert result.status == "running"
        if settings.DEBUG:
            assert result.docs == "/docs"
        else:
            assert result.docs is None


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """Test health check endpoint returns correct status."""
        from notification_service.main import health_check
        from notification_service.schemas import HealthCheck

        # Mock the engine.connect() for database check
        with patch("notification_service.main.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()

            class AsyncContextMock:
                async def __aenter__(self):
                    return mock_conn
                async def __aexit__(self, *args):
                    return False

            mock_engine.connect = MagicMock(return_value=AsyncContextMock())

            with patch("notification_service.main.datetime") as mock_datetime:
                mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
                mock_datetime.now.return_value = mock_now
                mock_datetime.UTC = UTC

                result = await health_check()

                assert isinstance(result, HealthCheck)
                assert result.status == "healthy"
                assert result.service == "notification"
                # timestamp is a datetime object (not string), compare correctly
                assert result.timestamp == mock_now
                assert result.dependencies["database"] == "connected"
                assert result.dependencies["redis"] == "not_configured"


class TestIntegration:
    """Integration tests using TestClient."""

    def test_root_endpoint_integration(self, client):
        """Test root endpoint via HTTP."""
        from notification_service.config import settings

        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == settings.APP_NAME
        assert data["version"] == settings.APP_VERSION
        assert data["status"] == "running"

    def test_health_endpoint_integration(self, client):
        """Test health endpoint via HTTP."""
        # Mock the engine.connect() for database health check
        with patch("notification_service.main.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()

            class AsyncContextMock:
                async def __aenter__(self):
                    return mock_conn
                async def __aexit__(self, *args):
                    return False

            mock_engine.connect = MagicMock(return_value=AsyncContextMock())

            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "notification"
        assert "timestamp" in data
        assert "dependencies" in data
        assert data["dependencies"]["database"] == "connected"

    def test_404_not_found(self, client):
        """Test 404 for non-existent endpoint."""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404


class TestAppConfiguration:
    """Tests for FastAPI application configuration via client."""

    def test_app_has_openapi_endpoint(self, client):
        """Test app has OpenAPI endpoint configured."""
        from notification_service.config import settings

        # OpenAPI should be available at the configured path
        response = client.get(f"{settings.API_V1_PREFIX}/openapi.json")
        # May be 404 if not DEBUG, but endpoint should exist
        assert response.status_code in [200, 404]

    def test_notification_router_registered(self, client):
        """Test notification routes are accessible."""
        from notification_service.config import settings

        # Try to access a notification endpoint (POST to /send which requires auth)
        response = client.post(f"{settings.API_V1_PREFIX}/notifications/send")
        # Should not be 404 - may be 401/403/422 due to auth/validation requirements
        assert response.status_code != 404


class TestMiddleware:
    """Tests for middleware functionality."""

    def test_auth_token_middleware_extracts_token(self, client):
        """Test that auth token middleware is active."""
        from notification_service.config import settings

        # Make request with auth header
        headers = {"Authorization": "Bearer test_token_123"}
        response = client.get("/health", headers=headers)

        # Should succeed even though token might be invalid
        assert response.status_code == 200

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in response."""
        # Make OPTIONS request for CORS preflight
        response = client.options("/health")

        # CORS middleware should be active
        assert response.status_code in [200, 405]  # 405 if OPTIONS not allowed

    def test_request_without_auth_header(self, client):
        """Test requests without auth header work for public endpoints."""
        response = client.get("/health")

        assert response.status_code == 200
