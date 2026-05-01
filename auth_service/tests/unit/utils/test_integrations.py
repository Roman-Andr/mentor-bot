"""Unit tests for integrations client (checklists service and notification service)."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from auth_service.utils.integrations import (
    ChecklistsServiceClient,
    NotificationServiceClient,
    checklists_service_client,
    notification_service_client,
)


class TestChecklistsServiceClientInit:
    """Tests for ChecklistsServiceClient initialization."""

    def test_init_with_default_url(self):
        """Test initialization with default URL from settings."""
        with patch("auth_service.utils.integrations.settings") as mock_settings:
            mock_settings.CHECKLISTS_SERVICE_URL = "http://checklists:8002"
            client = ChecklistsServiceClient()
            assert client.base_url == "http://checklists:8002"
            assert isinstance(client.client, httpx.AsyncClient)

    def test_init_with_custom_url(self):
        """Test initialization with custom URL."""
        client = ChecklistsServiceClient(base_url="http://custom:8000")
        assert client.base_url == "http://custom:8000"


class TestAutoCreateChecklists:
    """Tests for auto_create_checklists method."""

    @pytest.fixture
    def client(self):
        """Create a ChecklistsServiceClient with mocked httpx client."""
        with patch("auth_service.utils.integrations.settings") as mock_settings:
            mock_settings.CHECKLISTS_SERVICE_URL = "http://checklists:8002"
            mock_settings.SERVICE_API_KEY = "test-api-key"
            client = ChecklistsServiceClient()
            client.client = MagicMock(spec=httpx.AsyncClient)
            return client

    async def test_auto_create_success_200(self, client):
        """Test successful auto-create with 200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=[{"id": 1, "title": "Checklist 1"}])
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=2,
            position="Developer",
            mentor_id=3,
        )

        assert result == [{"id": 1, "title": "Checklist 1"}]
        client.client.post.assert_awaited_once_with(
            "/api/v1/checklists/auto-create",
            json={
                "user_id": 1,
                "employee_id": "EMP001",
                "department_id": 2,
                "position": "Developer",
                "mentor_id": 3,
            },
            headers={"X-Service-Api-Key": "test-service-api-key"},
        )

    async def test_auto_create_success_201(self, client):
        """Test successful auto-create with 201 response."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json = MagicMock(return_value=[{"id": 2, "title": "Checklist 2"}])
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=2,
            position="Developer",
            mentor_id=None,
        )

        assert result == [{"id": 2, "title": "Checklist 2"}]

    async def test_auto_create_none_mentor(self, client):
        """Test auto-create with mentor_id as None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=[])
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=2,
            position="Developer",
            mentor_id=None,
        )

        assert result == []
        # Verify the request JSON includes None for mentor_id
        call_args = client.client.post.call_args
        assert call_args.kwargs["json"]["mentor_id"] is None

    async def test_auto_create_failure_400(self, client):
        """Test auto-create with 400 response returns empty list."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=2,
            position="Developer",
            mentor_id=3,
        )

        assert result == []

    async def test_auto_create_failure_500(self, client):
        """Test auto-create with 500 response returns empty list."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=2,
            position="Developer",
            mentor_id=3,
        )

        assert result == []

    async def test_auto_create_request_error(self, client):
        """Test that RequestError is caught and returns empty list."""
        client.client.post = AsyncMock(side_effect=httpx.RequestError("Connection failed"))

        result = await client.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=2,
            position="Developer",
            mentor_id=3,
        )

        assert result == []

    async def test_auto_create_generic_exception(self, client):
        """Test that generic exceptions are caught and return empty list."""
        client.client.post = AsyncMock(side_effect=Exception("Unexpected error"))

        result = await client.auto_create_checklists(
            user_id=1,
            employee_id="EMP001",
            department_id=2,
            position="Developer",
            mentor_id=3,
        )

        assert result == []


class TestChecklistsServiceClientSingleton:
    """Tests for the checklists_service_client singleton."""

    def test_singleton_exists(self):
        """Test that the singleton instance exists."""
        assert isinstance(checklists_service_client, ChecklistsServiceClient)


class TestNotificationServiceClientInit:
    """Tests for NotificationServiceClient initialization."""

    def test_init_with_default_url(self):
        """Test initialization with default URL from settings."""
        with patch("auth_service.utils.integrations.settings") as mock_settings:
            mock_settings.NOTIFICATION_SERVICE_URL = "http://notification:8004"
            mock_settings.ADMIN_WEB_URL = "http://localhost:3000"
            client = NotificationServiceClient()
            assert client.base_url == "http://notification:8004"
            assert isinstance(client.client, httpx.AsyncClient)

    def test_init_with_custom_url(self):
        """Test initialization with custom URL."""
        with patch("auth_service.utils.integrations.settings") as mock_settings:
            mock_settings.ADMIN_WEB_URL = "http://localhost:3000"
            client = NotificationServiceClient(base_url="http://custom:8000")
            assert client.base_url == "http://custom:8000"

    def test_init_fallback_to_localhost(self):
        """Test initialization falls back to localhost when no URL configured."""
        with patch("auth_service.utils.integrations.settings") as mock_settings:
            mock_settings.NOTIFICATION_SERVICE_URL = None
            mock_settings.ADMIN_WEB_URL = "http://localhost:3000"
            client = NotificationServiceClient()
            assert client.base_url == "http://localhost:8004"


class TestSendPasswordResetEmail:
    """Tests for send_password_reset_email method."""

    @pytest.fixture
    def client(self):
        """Create a NotificationServiceClient with mocked httpx client."""
        with patch("auth_service.utils.integrations.settings") as mock_settings:
            mock_settings.NOTIFICATION_SERVICE_URL = "http://notification:8004"
            mock_settings.ADMIN_WEB_URL = "http://localhost:3000"
            mock_settings.SERVICE_API_KEY = "test-api-key"
            client = NotificationServiceClient()
            client.client = MagicMock(spec=httpx.AsyncClient)
            return client

    async def test_send_password_reset_email_success_200(self, client):
        """Test successful password reset email with 200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_email(
            to_email="user@example.com",
            user_name="Test User",
            reset_token="reset-token-123",
        )

        assert result is True
        client.client.post.assert_awaited_once()
        call_args = client.client.post.call_args
        assert call_args.kwargs["json"]["template"] == "password_reset"
        assert call_args.kwargs["json"]["to_email"] == "user@example.com"

    async def test_send_password_reset_email_success_201(self, client):
        """Test successful password reset email with 201 response."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_email(
            to_email="user@example.com",
            user_name="Test User",
            reset_token="reset-token-123",
        )

        assert result is True

    async def test_send_password_reset_email_success_202(self, client):
        """Test successful password reset email with 202 response."""
        mock_response = MagicMock()
        mock_response.status_code = 202
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_email(
            to_email="user@example.com",
            user_name="Test User",
            reset_token="reset-token-123",
        )

        assert result is True

    async def test_send_password_reset_email_failure_400(self, client):
        """Test password reset email with 400 response returns False."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_email(
            to_email="user@example.com",
            user_name="Test User",
            reset_token="reset-token-123",
        )

        assert result is False

    async def test_send_password_reset_email_failure_500(self, client):
        """Test password reset email with 500 response returns False."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_email(
            to_email="user@example.com",
            user_name="Test User",
            reset_token="reset-token-123",
        )

        assert result is False

    async def test_send_password_reset_email_request_error(self, client):
        """Test that RequestError is caught and returns False."""
        client.client.post = AsyncMock(side_effect=httpx.RequestError("Connection failed"))

        result = await client.send_password_reset_email(
            to_email="user@example.com",
            user_name="Test User",
            reset_token="reset-token-123",
        )

        assert result is False

    async def test_send_password_reset_email_generic_exception(self, client):
        """Test that generic exceptions are caught and return False."""
        client.client.post = AsyncMock(side_effect=Exception("Unexpected error"))

        result = await client.send_password_reset_email(
            to_email="user@example.com",
            user_name="Test User",
            reset_token="reset-token-123",
        )

        assert result is False


class TestSendPasswordResetConfirmationEmail:
    """Tests for send_password_reset_confirmation_email method."""

    @pytest.fixture
    def client(self):
        """Create a NotificationServiceClient with mocked httpx client."""
        with patch("auth_service.utils.integrations.settings") as mock_settings:
            mock_settings.NOTIFICATION_SERVICE_URL = "http://notification:8004"
            mock_settings.ADMIN_WEB_URL = "http://localhost:3000"
            mock_settings.SERVICE_API_KEY = "test-api-key"
            client = NotificationServiceClient()
            client.client = MagicMock(spec=httpx.AsyncClient)
            return client

    async def test_send_confirmation_email_success_200(self, client):
        """Test successful confirmation email with 200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_confirmation_email(
            to_email="user@example.com",
            user_name="Test User",
        )

        assert result is True
        client.client.post.assert_awaited_once()
        call_args = client.client.post.call_args
        assert call_args.kwargs["json"]["template"] == "password_reset_confirmation"
        assert call_args.kwargs["json"]["to_email"] == "user@example.com"

    async def test_send_confirmation_email_success_201(self, client):
        """Test successful confirmation email with 201 response."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_confirmation_email(
            to_email="user@example.com",
            user_name="Test User",
        )

        assert result is True

    async def test_send_confirmation_email_success_202(self, client):
        """Test successful confirmation email with 202 response."""
        mock_response = MagicMock()
        mock_response.status_code = 202
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_confirmation_email(
            to_email="user@example.com",
            user_name="Test User",
        )

        assert result is True

    async def test_send_confirmation_email_failure_400(self, client):
        """Test confirmation email with 400 response returns False."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_confirmation_email(
            to_email="user@example.com",
            user_name="Test User",
        )

        assert result is False

    async def test_send_confirmation_email_failure_500(self, client):
        """Test confirmation email with 500 response returns False."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.send_password_reset_confirmation_email(
            to_email="user@example.com",
            user_name="Test User",
        )

        assert result is False

    async def test_send_confirmation_email_request_error(self, client):
        """Test that RequestError is caught and returns False."""
        client.client.post = AsyncMock(side_effect=httpx.RequestError("Connection failed"))

        result = await client.send_password_reset_confirmation_email(
            to_email="user@example.com",
            user_name="Test User",
        )

        assert result is False

    async def test_send_confirmation_email_generic_exception(self, client):
        """Test that generic exceptions are caught and return False."""
        client.client.post = AsyncMock(side_effect=Exception("Unexpected error"))

        result = await client.send_password_reset_confirmation_email(
            to_email="user@example.com",
            user_name="Test User",
        )

        assert result is False


class TestNotificationServiceClientSingleton:
    """Tests for the notification_service_client singleton."""

    def test_singleton_exists(self):
        """Test that the singleton instance exists."""
        assert isinstance(notification_service_client, NotificationServiceClient)
