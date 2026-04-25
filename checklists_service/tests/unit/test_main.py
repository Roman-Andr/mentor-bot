"""Tests for main.py - FastAPI application entry point."""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import Request
from fastapi.exceptions import RequestValidationError

from checklists_service import main
from checklists_service.config import settings


class TestLifespan:
    """Test application lifespan handler."""

    async def test_lifespan_startup(self):
        """Test lifespan startup initializes database and cache."""
        mock_app = MagicMock()

        with patch("checklists_service.main.init_db") as mock_init_db, \
             patch("checklists_service.main.cache") as mock_cache:
            mock_init_db.return_value = AsyncMock()
            mock_cache.connect = AsyncMock()
            mock_cache.disconnect = AsyncMock()

            async with main.lifespan(mock_app):
                # During lifespan, init_db and cache.connect should be called
                mock_init_db.assert_awaited_once()
                mock_cache.connect.assert_awaited_once()

            # After exiting lifespan, cache.disconnect should be called
            mock_cache.disconnect.assert_awaited_once()


class TestRootEndpoint:
    """Test root endpoint."""

    async def test_root_debug_mode(self):
        """Test root endpoint in debug mode returns docs URL."""
        with patch.object(settings, "DEBUG", new=True):
            result = await main.root()

            assert result.service == settings.APP_NAME
            assert result.version == settings.APP_VERSION
            assert result.status == "running"
            assert result.docs == "/docs"

    async def test_root_production_mode(self):
        """Test root endpoint in production mode."""
        with patch.object(settings, "DEBUG", new=False):
            result = await main.root()

            assert result.service == settings.APP_NAME
            assert result.status == "running"
            assert result.docs is None


class TestHealthCheck:
    """Test health check endpoint."""

    async def test_health_check_connected(self):
        """Test health check when cache is connected."""
        with patch("checklists_service.main.cache") as mock_cache, \
             patch("checklists_service.main.engine") as mock_engine:
            mock_cache.is_connected = True
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()
            mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await main.health_check()

            assert result.status == "healthy"
            assert result.service == "checklists"
            assert result.dependencies["database"] == "connected"
            assert result.dependencies["redis"] == "connected"
            assert result.dependencies["auth_service"] == "connected"
            assert result.timestamp is not None

    async def test_health_check_disconnected(self):
        """Test health check when cache is disconnected."""
        with patch("checklists_service.main.cache") as mock_cache, \
             patch("checklists_service.main.engine") as mock_engine:
            mock_cache.is_connected = False
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()
            mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await main.health_check()

            assert result.status == "healthy"
            assert result.dependencies["redis"] == "disconnected"

    async def test_health_check_database_disconnected(self):
        """Test health check when database is disconnected (lines 119-120)."""
        with patch("checklists_service.main.cache") as mock_cache, \
             patch("checklists_service.main.engine") as mock_engine:
            mock_cache.is_connected = True
            # Simulate database connection failure
            mock_engine.connect.return_value.__aenter__ = AsyncMock(side_effect=Exception("DB connection failed"))
            mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await main.health_check()

            assert result.status == "unhealthy"
            assert result.dependencies["database"] == "disconnected"
            assert result.dependencies["redis"] == "connected"


class TestValidationExceptionHandler:
    """Test validation exception handler."""

    async def test_validation_exception_handler(self):
        """Test validation error handler returns proper JSON response."""
        mock_request = MagicMock(spec=Request)

        # Create a validation error
        errors = [
            {"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"}
        ]
        exc = RequestValidationError(errors=errors)

        with patch("checklists_service.main.logger") as mock_logger:
            response = await main.validation_exception_handler(mock_request, exc)

            assert response.status_code == 422
            assert "detail" in response.body.decode()
            mock_logger.error.assert_called_once()


class TestAppConfiguration:
    """Test FastAPI app configuration."""

    def test_app_title(self):
        """Test app has correct title."""
        assert main.app.title == settings.APP_NAME

    def test_app_version(self):
        """Test app has correct version."""
        assert main.app.version == settings.APP_VERSION

    def test_app_routers_registered(self):
        """Test all routers are registered."""
        routes = [route.path for route in main.app.routes]

        # Check that our API routes are registered
        assert any("/api/v1/templates" in route for route in routes)
        assert any("/api/v1/checklists" in route for route in routes)
        assert any("/api/v1/tasks" in route for route in routes)

    def test_app_has_lifespan(self):
        """Test app has lifespan handler."""
        # FastAPI merges lifespan contexts, so we check it's set (not identity)
        assert main.app.router.lifespan_context is not None


class TestMiddlewareConfiguration:
    """Test middleware is properly configured."""

    def test_rate_limiter_middleware_exists(self):
        """Test rate limiter is configured."""
        assert hasattr(main.app.state, "limiter") or any(
            "SlowAPIMiddleware" in str(middleware.cls) for middleware in main.app.user_middleware
        )

    def test_cors_middleware_exists(self):
        """Test CORS middleware is configured."""
        cors_middlewares = [
            middleware for middleware in main.app.user_middleware
            if "CORSMiddleware" in str(middleware.cls)
        ]
        assert len(cors_middlewares) > 0

    def test_trusted_host_middleware_exists(self):
        """Test TrustedHost middleware is configured."""
        host_middlewares = [
            middleware for middleware in main.app.user_middleware
            if "TrustedHostMiddleware" in str(middleware.cls)
        ]
        assert len(host_middlewares) > 0

    def test_auth_middleware_exists(self):
        """Test AuthToken middleware is configured."""
        auth_middlewares = [
            middleware for middleware in main.app.user_middleware
            if "AuthTokenMiddleware" in str(middleware.cls)
        ]
        assert len(auth_middlewares) > 0
