"""Unit tests for escalation_service/main.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from escalation_service.config import settings
from escalation_service.main import app, lifespan, logger

client = TestClient(app)


class TestLifespan:
    """Tests for lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_and_shutdown(self):
        """Test lifespan context manager handles startup and shutdown."""
        mock_app = MagicMock()

        with patch("escalation_service.main.init_db") as mock_init_db:
            async with lifespan(mock_app) as _:
                # During context, init_db should be called
                mock_init_db.assert_awaited_once()

        # No assertion needed for shutdown logging
        # The test verifies that the lifespan context manager runs without errors


class TestMainApp:
    """Tests for main app configuration."""

    def test_app_title_and_version(self):
        """Test app has correct title and version."""
        assert app.title == "Escalation Service"
        assert "Escalation" in app.description

    def test_app_has_middleware(self):
        """Test app has middleware configured."""
        # The app has middleware registered
        assert len(app.user_middleware) >= 2

    def test_app_has_routers(self):
        """Test app has routers configured."""
        # Verify routes are configured
        routes = [route.path for route in app.routes]
        assert "/" in routes
        assert "/health" in routes


class TestRateLimiting:
    """Tests for rate limiting configuration (lines 52-57)."""

    @pytest.mark.asyncio
    async def test_rate_limiting_disabled_when_debug_true(self):
        """Test rate limiting is skipped when DEBUG=True (covers line 53->60 branch)."""
        with patch.object(settings, "DEBUG", True):
            # Reload main module to trigger the if not settings.DEBUG: check
            import importlib
            import escalation_service.main as main_module

            importlib.reload(main_module)

            # When DEBUG=True, the limiter should not be set on app.state
            # (because the if block at lines 53-57 is skipped)
            assert not hasattr(main_module.app.state, "limiter") or main_module.app.state.limiter is None


class TestLogger:
    """Tests for logger configuration."""

    def test_logger_exists(self):
        """Test logger is properly configured."""
        assert logger is not None
        assert logger.name == "escalation_service.main"


class TestHealthCheck:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_db_disconnected(self):
        """Test health check when database is disconnected (lines 95-96)."""
        from escalation_service.main import health_check

        # Mock engine.connect as async context manager that raises exception
        with patch("escalation_service.main.engine") as mock_engine:
            mock_cm = AsyncMock()
            mock_cm.__aenter__ = AsyncMock(side_effect=Exception("DB connection failed"))
            mock_cm.__aexit__ = AsyncMock(return_value=False)
            mock_engine.connect = MagicMock(return_value=mock_cm)

            # Call the health check
            result = await health_check()

            # Assert unhealthy status when DB is disconnected
            assert result.status == "unhealthy"
            assert result.dependencies["database"] == "disconnected"
