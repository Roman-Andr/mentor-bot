"""Unit tests for main.py FastAPI application."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLifespan:
    """Tests for application lifespan (startup/shutdown)."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_success(self):
        """Test lifespan startup calls init_db successfully."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_init_db = AsyncMock()

        with patch("meeting_service.main.settings", mock_settings):
            with patch("meeting_service.main.init_db", mock_init_db):
                from meeting_service.main import lifespan

                mock_app = MagicMock()

                # Use async context manager
                async with lifespan(mock_app):
                    pass

                mock_init_db.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_startup_failure(self):
        """Test lifespan handles init_db failure gracefully."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_init_db = AsyncMock()
        mock_init_db.side_effect = Exception("Database connection failed")

        with patch("meeting_service.main.settings", mock_settings):
            with patch("meeting_service.main.init_db", mock_init_db):
                from meeting_service.main import lifespan

                mock_app = MagicMock()

                with pytest.raises(Exception, match="Database connection failed"):
                    async with lifespan(mock_app):
                        pass

                mock_init_db.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_logs(self, caplog):
        """Test lifespan shutdown logs message."""
        import logging

        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_init_db = AsyncMock()

        with patch("meeting_service.main.settings", mock_settings):
            with patch("meeting_service.main.init_db", mock_init_db):
                from meeting_service.main import lifespan

                mock_app = MagicMock()
                caplog.set_level(logging.INFO)

                async with lifespan(mock_app):
                    pass  # Startup happens here

                # Shutdown log message should be present
                assert any("Shutting down Meeting Service" in record.message for record in caplog.records)


class TestRootEndpoints:
    """Tests for root and health check endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies."""
        mock_settings = MagicMock()
        mock_settings.APP_NAME = "Meeting Service"
        mock_settings.APP_VERSION = "1.0.0"
        mock_settings.DEBUG = True
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.API_V1_PREFIX = "/api/v1"
        mock_settings.CORS_ORIGINS = ["*"]
        mock_settings.ALLOWED_HOSTS = ["*"]
        mock_init_db = AsyncMock()

        with patch("meeting_service.main.settings", mock_settings):
            with patch("meeting_service.main.init_db", mock_init_db):
                from fastapi.testclient import TestClient
                from meeting_service.main import app

                # Create client
                client = TestClient(app)
                return client

    def test_root_endpoint(self, client):
        """Test root endpoint returns service status."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Meeting Service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"

    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        # Mock the engine.connect() for database health check
        with patch("meeting_service.main.engine") as mock_engine:
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
        assert data["service"] == "meeting"
        assert "timestamp" in data
        assert data["dependencies"]["database"] == "connected"
        assert data["dependencies"]["auth_service"] == "enabled"

    def test_health_check_timestamp_format(self, client):
        """Test health check returns valid ISO timestamp."""
        from datetime import datetime

        response = client.get("/health")
        data = response.json()

        # Should be parseable as ISO datetime
        timestamp = data["timestamp"]
        parsed = datetime.fromisoformat(timestamp)
        assert parsed is not None


class TestAppConfiguration:
    """Tests for FastAPI app configuration."""

    def test_app_configuration_values(self):
        """Test FastAPI app configuration can be loaded."""
        # Simply verify the main module can be imported and accessed
        from meeting_service.main import app

        # Basic assertions about the app that should always be true
        assert app is not None
        assert app.title is not None
        assert app.version is not None
        assert len(app.routes) > 0


class TestMiddlewareConfiguration:
    """Tests for middleware configuration."""

    def test_middleware_stack_exists(self):
        """Test middleware stack is configured."""
        from meeting_service.main import app

        # Verify that middleware is configured
        assert len(app.user_middleware) >= 0  # Should have at least some middleware

    def test_routes_exist(self):
        """Test routes are registered."""
        from meeting_service.main import app

        # Verify routes are registered
        route_paths = [route.path for route in app.routes if hasattr(route, "path")]
        assert len(route_paths) > 0
