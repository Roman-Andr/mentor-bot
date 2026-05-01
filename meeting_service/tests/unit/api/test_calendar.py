"""Unit tests for calendar API endpoints."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from meeting_service.api import deps
from meeting_service.api.endpoints.calendar import router as calendar_router
from meeting_service.config import settings


class TestConnectCalendar:
    """Tests for GET /api/v1/calendar/connect endpoint."""

    def test_connect_calendar_success(self):
        """Test initiating OAuth flow successfully."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        mock_user = MagicMock()
        mock_user.id = 100
        mock_user.role = "EMPLOYEE"
        mock_user.is_active = True

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        # Mock settings
        original_client_id = settings.GOOGLE_CLIENT_ID
        original_redirect_uri = settings.GOOGLE_REDIRECT_URI
        original_scopes = settings.GOOGLE_CALENDAR_SCOPES
        settings.GOOGLE_CLIENT_ID = "test-client-id"
        settings.GOOGLE_REDIRECT_URI = "http://localhost:8000/callback"
        settings.GOOGLE_CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]

        client = TestClient(app)

        with patch("meeting_service.api.endpoints.calendar.Flow") as mock_flow_class:
            mock_flow = MagicMock()
            mock_flow.authorization_url.return_value = (
                "https://accounts.google.com/o/oauth2/auth?redirect_uri=test",
                "test_state",
            )
            mock_flow_class.from_client_config.return_value = mock_flow

            # Act
            response = client.get("/api/v1/calendar/connect?state=100:csrf_token", follow_redirects=False)

        # Restore
        deps.get_db = original_db
        settings.GOOGLE_CLIENT_ID = original_client_id
        settings.GOOGLE_REDIRECT_URI = original_redirect_uri
        settings.GOOGLE_CALENDAR_SCOPES = original_scopes

        # Assert
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "accounts.google.com" in response.headers["location"]

    def test_connect_calendar_invalid_state_format(self):
        """Test with invalid state parameter format."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/connect?state=invalid", follow_redirects=False)

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid state" in response.json()["detail"]

    def test_connect_calendar_invalid_user_id(self):
        """Test with non-integer user_id in state."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/connect?state=abc:token", follow_redirects=False)

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid state" in response.json()["detail"]

    def test_connect_calendar_not_configured(self):
        """Test when Google Calendar is not configured."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        # Mock empty settings
        original_client_id = settings.GOOGLE_CLIENT_ID
        original_redirect_uri = settings.GOOGLE_REDIRECT_URI
        settings.GOOGLE_CLIENT_ID = ""
        settings.GOOGLE_REDIRECT_URI = ""

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/connect?state=100:token", follow_redirects=False)

        # Restore
        deps.get_db = original_db
        settings.GOOGLE_CLIENT_ID = original_client_id
        settings.GOOGLE_REDIRECT_URI = original_redirect_uri

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "not configured" in response.json()["detail"].lower()


class TestOAuthCallback:
    """Tests for GET /api/v1/calendar/callback endpoint."""

    @patch("meeting_service.api.endpoints.calendar.Flow")
    @patch("meeting_service.api.endpoints.calendar.SqlAlchemyUnitOfWork")
    @patch("meeting_service.api.endpoints.calendar.GoogleCalendarService")
    async def test_oauth_callback_success(self, mock_gc_service_class, mock_uow_class, mock_flow_class):
        """Test successful OAuth callback."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        mock_db = MagicMock()

        async def override_db() -> MagicMock:
            return mock_db

        original_db = deps.get_db
        deps.get_db = override_db

        # Mock Flow
        mock_flow = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.token = "test_access_token"
        mock_credentials.refresh_token = "test_refresh_token"
        mock_credentials.expiry = datetime.now(UTC) + timedelta(hours=1)
        mock_flow.credentials = mock_credentials
        mock_flow_class.from_client_config.return_value = mock_flow

        # Mock UOW
        mock_uow = MagicMock()
        mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow.__aexit__ = AsyncMock(return_value=None)
        mock_uow_class.return_value = mock_uow

        # Mock GoogleCalendarService
        mock_gc_service = MagicMock()
        mock_gc_service.save_credentials = AsyncMock()
        mock_gc_service_class.return_value = mock_gc_service

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/callback?code=auth_code&state=100:csrf_token")

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["user_id"] == "100"
        mock_flow.fetch_token.assert_called_once_with(code="auth_code")

    def test_oauth_callback_invalid_state(self):
        """Test callback with invalid state parameter."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/callback?code=auth_code&state=invalid")

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Failed to connect" in response.json()["detail"]

    @patch("meeting_service.api.endpoints.calendar.Flow")
    async def test_oauth_callback_fetch_token_error(self, mock_flow_class):
        """Test handling error during token fetch."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        # Mock Flow to raise exception
        mock_flow = MagicMock()
        mock_flow.fetch_token.side_effect = Exception("Invalid authorization code")
        mock_flow_class.from_client_config.return_value = mock_flow

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/callback?code=invalid&state=100:token")

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Failed to connect" in response.json()["detail"]


class TestGetCalendarStatus:
    """Tests for GET /api/v1/calendar/status/{user_id} endpoint."""

    @patch("meeting_service.api.endpoints.calendar.GoogleCalendarService")
    async def test_get_status_connected(self, mock_gc_service_class):
        """Test status when user has connected calendar."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        # Mock account
        mock_account = MagicMock()
        mock_account.sync_enabled = True

        # Mock GoogleCalendarService
        mock_gc_service = MagicMock()
        mock_gc_service.get_credentials = AsyncMock(return_value=mock_account)
        mock_gc_service_class.return_value = mock_gc_service

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/status/100")

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["connected"] is True
        assert data["sync_enabled"] is True

    @patch("meeting_service.api.endpoints.calendar.GoogleCalendarService")
    async def test_get_status_not_connected(self, mock_gc_service_class):
        """Test status when user has not connected calendar."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        # Mock GoogleCalendarService
        mock_gc_service = MagicMock()
        mock_gc_service.get_credentials = AsyncMock(return_value=None)
        mock_gc_service_class.return_value = mock_gc_service

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/status/100")

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["connected"] is False
        assert data["sync_enabled"] is False

    @patch("meeting_service.api.endpoints.calendar.GoogleCalendarService")
    async def test_get_status_connected_sync_disabled(self, mock_gc_service_class):
        """Test status when connected but sync is disabled."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        # Mock account with sync disabled
        mock_account = MagicMock()
        mock_account.sync_enabled = False

        # Mock GoogleCalendarService
        mock_gc_service = MagicMock()
        mock_gc_service.get_credentials = AsyncMock(return_value=mock_account)
        mock_gc_service_class.return_value = mock_gc_service

        client = TestClient(app)

        # Act
        response = client.get("/api/v1/calendar/status/100")

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["connected"] is True
        assert data["sync_enabled"] is False


class TestDisconnectCalendar:
    """Tests for DELETE /api/v1/calendar/{user_id} endpoint."""

    @patch("meeting_service.api.endpoints.calendar.SqlAlchemyUnitOfWork")
    async def test_disconnect_success(self, mock_uow_class):
        """Test disconnecting calendar successfully."""
        # Arrange
        app = FastAPI()
        app.include_router(calendar_router, prefix="/api/v1/calendar")

        async def override_db() -> MagicMock:
            return MagicMock()

        original_db = deps.get_db
        deps.get_db = override_db

        # Mock UOW
        mock_uow = MagicMock()
        mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow.__aexit__ = AsyncMock(return_value=None)
        mock_uow.google_calendar_accounts = MagicMock()
        mock_uow.google_calendar_accounts.delete = AsyncMock()
        mock_uow.commit = AsyncMock()
        mock_uow_class.return_value = mock_uow

        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/calendar/100")

        # Restore
        deps.get_db = original_db

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        mock_uow.google_calendar_accounts.delete.assert_called_once_with(100)
        mock_uow.commit.assert_called_once()
