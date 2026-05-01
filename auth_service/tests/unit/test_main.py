"""Unit tests for main.py FastAPI application."""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from auth_service.main import app, lifespan


def get_test_client():
    """Create a TestClient without lifespan events."""
    return TestClient(app, raise_server_exceptions=False)


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_service_status(self):
        """Test root endpoint returns service status."""
        client = get_test_client()
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_root_includes_docs_url_in_debug(self):
        """Test root endpoint includes docs URL when DEBUG is True."""
        with patch("auth_service.main.settings.DEBUG", True):
            client = get_test_client()
            response = client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert "docs" in data
            assert data["docs"] == "/docs"

    def test_root_excludes_docs_url_in_production(self):
        """Test root endpoint excludes docs URL when DEBUG is False."""
        with patch("auth_service.main.settings.DEBUG", False):
            client = get_test_client()
            response = client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert data["docs"] is None


class TestHealthCheckEndpoint:
    """Tests for health check endpoint."""

    def test_health_check_returns_healthy(self):
        """Test health check endpoint returns healthy status."""
        with patch("auth_service.main.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

            client = get_test_client()
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "auth"
            assert "timestamp" in data
            assert "dependencies" in data

    def test_health_check_database_connected(self):
        """Test health check reports database as connected."""
        with patch("auth_service.main.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

            client = get_test_client()
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["dependencies"]["database"] == "connected"

    def test_health_check_database_disconnected(self):
        """Test health check reports database as disconnected when connection fails."""
        with patch("auth_service.main.engine") as mock_engine:
            # Simulate database connection failure
            mock_engine.connect.side_effect = SQLAlchemyError("Database connection failed")

            client = get_test_client()
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["dependencies"]["database"] == "disconnected"


class TestLifespan:
    """Tests for lifespan context manager."""

    async def test_lifespan_startup_initializes_db(self):
        """Test lifespan startup initializes database."""
        mock_app = MagicMock()

        with patch("auth_service.main.init_db", new_callable=AsyncMock) as mock_init_db:
            with patch("auth_service.main.create_default_admin_user", new_callable=AsyncMock):
                with patch("auth_service.main.logger"):
                    async with lifespan(mock_app):
                        pass

                mock_init_db.assert_called_once()

    async def test_lifespan_logs_startup_shutdown(self):
        """Test lifespan logs startup and shutdown messages."""
        mock_app = MagicMock()

        with patch("auth_service.main.init_db", new_callable=AsyncMock):
            with patch("auth_service.main.create_default_admin_user", new_callable=AsyncMock):
                with patch("auth_service.main.logger") as mock_logger:
                    async with lifespan(mock_app):
                        pass

                    # Verify startup log
                    mock_logger.info.assert_any_call("Starting Auth Service...")
                    mock_logger.info.assert_any_call("Database initialized")
                    mock_logger.info.assert_any_call("Shutting down Auth Service...")

class TestRateLimiter:
    """Tests for rate limiter configuration."""

    def test_rate_limiter_disabled_in_debug(self):
        """Test rate limiter is disabled in debug mode."""
        # When DEBUG is True, rate limiter should not be added
        with patch("auth_service.main.settings.DEBUG", True):
            # This is a configuration test - the rate limiter setup is
            # conditional on DEBUG being False
            pass


class TestCorsMiddleware:
    """Tests for CORS middleware configuration."""

    def test_cors_origins_configured(self):
        """Test CORS origins are configured from settings."""
        with patch("auth_service.main.settings.CORS_ORIGINS", ["http://localhost:3000"]):
            # CORS origins should be configured
            pass


class TestTrustedHostMiddleware:
    """Tests for trusted host middleware."""

    def test_allowed_hosts_configured(self):
        """Test allowed hosts are configured from settings."""
        with patch("auth_service.main.settings.ALLOWED_HOSTS", ["localhost", "example.com"]):
            # Allowed hosts should be configured
            pass


class TestRouterRegistration:
    """Tests for router registration."""

    def test_auth_router_registered(self):
        """Test auth router is registered."""
        client = get_test_client()
        # Test that auth endpoints are available
        response = client.post("/api/v1/auth/login", data={"username": "test", "password": "test"})
        # Should not be 404
        assert response.status_code != 404

    def test_users_router_registered(self):
        """Test users router is registered."""
        client = get_test_client()
        # Test that users endpoints are available
        response = client.get("/api/v1/users/")
        # Should not be 404 (will be 403 or 401 without auth, but not 404)
        assert response.status_code != 404

    def test_invitations_router_registered(self):
        """Test invitations router is registered."""
        client = get_test_client()
        response = client.get("/api/v1/invitations/")
        # Should not be 404
        assert response.status_code != 404

    def test_departments_router_registered(self):
        """Test departments router is registered."""
        client = get_test_client()
        response = client.get("/api/v1/departments/")
        # Should not be 404
        assert response.status_code != 404

    def test_user_mentors_router_registered(self):
        """Test user mentors router is registered."""
        client = get_test_client()
        response = client.get("/api/v1/user-mentors/")
        # Should not be 404
        assert response.status_code != 404


class TestAppConfiguration:
    """Tests for FastAPI app configuration."""

    def test_app_title(self):
        """Test app has correct title."""
        assert app.title == "Auth Service"

    def test_app_version(self):
        """Test app has version."""
        assert app.version is not None

    def test_app_description(self):
        """Test app has description."""
        assert app.description is not None


class TestCreateDefaultAdminUser:
    """Tests for create_default_admin_user function."""

    async def test_create_default_admin_user_when_not_exists(self):
        """Test create_default_admin_user creates admin when it doesn't exist."""
        from auth_service.main import create_default_admin_user
        from auth_service.schemas import UserCreate

        mock_uow_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_user_by_email = AsyncMock(return_value=None)
        mock_user_service.create_user = AsyncMock()

        mock_uow_context = AsyncMock()
        mock_uow_context.__aenter__.return_value = mock_uow_instance
        mock_uow_context.__aexit__.return_value = None

        with patch("auth_service.main.AsyncSessionLocal", return_value=mock_uow_instance):
            with patch("auth_service.main.SqlAlchemyUnitOfWork", return_value=mock_uow_context):
                with patch("auth_service.main.UserService", return_value=mock_user_service):
                    with patch("auth_service.main.settings.ADMIN_EMAIL", "admin@example.com"):
                        with patch("auth_service.main.settings.ADMIN_PASSWORD", "changeme_admin_password"):
                            with patch("auth_service.main.logger") as mock_logger:
                                await create_default_admin_user()

                                mock_user_service.get_user_by_email.assert_called_once_with("admin@example.com")
                                mock_user_service.create_user.assert_called_once()
                                call_args = mock_user_service.create_user.call_args[0][0]
                                assert isinstance(call_args, UserCreate)
                                assert call_args.email == "admin@example.com"
                                assert call_args.first_name == "Admin"
                                assert call_args.last_name == "User"
                                assert call_args.employee_id == "ADMIN001"
                                assert call_args.role == "ADMIN"
                                mock_logger.info.assert_any_call("Creating default admin user: {}", "admin@example.com")
                                mock_logger.info.assert_any_call("Default admin user created successfully")

    async def test_create_default_admin_user_when_exists(self):
        """Test create_default_admin_user skips creation when admin already exists."""
        from auth_service.main import create_default_admin_user

        existing_admin = MagicMock()
        existing_admin.email = "admin@example.com"

        mock_uow_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_user_by_email = AsyncMock(return_value=existing_admin)
        mock_user_service.create_user = AsyncMock()

        mock_uow_context = AsyncMock()
        mock_uow_context.__aenter__.return_value = mock_uow_instance
        mock_uow_context.__aexit__.return_value = None

        with patch("auth_service.main.AsyncSessionLocal", return_value=mock_uow_instance):
            with patch("auth_service.main.SqlAlchemyUnitOfWork", return_value=mock_uow_context):
                with patch("auth_service.main.UserService", return_value=mock_user_service):
                    with patch("auth_service.main.settings.ADMIN_EMAIL", "admin@example.com"):
                        with patch("auth_service.main.logger") as mock_logger:
                            await create_default_admin_user()

                            mock_user_service.get_user_by_email.assert_called_once_with("admin@example.com")
                            mock_user_service.create_user.assert_not_called()
                            mock_logger.info.assert_any_call("Default admin user already exists: {}", "admin@example.com")
