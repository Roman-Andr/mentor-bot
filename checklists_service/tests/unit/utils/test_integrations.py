"""Unit tests for utils/integrations.py - AuthServiceClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from checklists_service.utils.integrations import (
    AuthServiceClient,
    NotificationServiceClient,
    auth_service_client,
    notification_service_client,
)


class TestAuthServiceClientValidateToken:
    """Test validate_token method."""

    async def test_validate_token_success(self) -> None:
        """Test successful token validation."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "email": "test@example.com", "role": "EMPLOYEE"}

        with patch.object(client.client, "get", new=AsyncMock(return_value=mock_response)):
            result = await client.validate_token("valid-token")

        assert result is not None
        assert result["id"] == 1
        assert result["email"] == "test@example.com"

    async def test_validate_token_unauthorized(self) -> None:
        """Test token validation returns None on 401."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch.object(client.client, "get", new=AsyncMock(return_value=mock_response)):
            result = await client.validate_token("invalid-token")

        assert result is None

    async def test_validate_token_not_found(self) -> None:
        """Test token validation returns None on 404."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(client.client, "get", new=AsyncMock(return_value=mock_response)):
            result = await client.validate_token("unknown-token")

        assert result is None

    async def test_validate_token_request_error(self) -> None:
        """Test token validation handles httpx.RequestError."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        with patch.object(client.client, "get", new=AsyncMock(side_effect=httpx.RequestError("Connection failed"))):
            result = await client.validate_token("token")

        assert result is None

    async def test_validate_token_generic_exception(self) -> None:
        """Test token validation handles generic exceptions."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        with patch.object(client.client, "get", new=AsyncMock(side_effect=Exception("Unexpected error"))):
            result = await client.validate_token("token")

        assert result is None


class TestAuthServiceClientGetUser:
    """Test get_user method."""

    async def test_get_user_success(self) -> None:
        """Test successful user retrieval."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "email": "user@example.com",
            "role": "MENTOR",
            "first_name": "John",
            "last_name": "Doe",
        }

        with patch.object(client.client, "get", new=AsyncMock(return_value=mock_response)):
            result = await client.get_user(1, "auth-token")

        assert result is not None
        assert result["id"] == 1
        assert result["role"] == "MENTOR"

    async def test_get_user_not_found(self) -> None:
        """Test get_user returns None when user not found."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(client.client, "get", new=AsyncMock(return_value=mock_response)):
            result = await client.get_user(999, "auth-token")

        assert result is None

    async def test_get_user_request_error(self) -> None:
        """Test get_user handles httpx.RequestError."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        with patch.object(client.client, "get", new=AsyncMock(side_effect=httpx.RequestError("Connection timeout"))):
            result = await client.get_user(1, "auth-token")

        assert result is None

    async def test_get_user_generic_exception(self) -> None:
        """Test get_user handles generic exceptions."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        with patch.object(client.client, "get", new=AsyncMock(side_effect=RuntimeError("Unexpected"))):
            result = await client.get_user(1, "auth-token")

        assert result is None


class TestAuthServiceClientInvalidateCache:
    """Test invalidate_user_cache method."""

    async def test_invalidate_user_cache(self) -> None:
        """Test cache invalidation for user."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        with patch("checklists_service.utils.integrations.cache") as mock_cache:
            mock_cache.delete_pattern = AsyncMock()

            await client.invalidate_user_cache(123)

            mock_cache.delete_pattern.assert_called_once_with("auth_user:*123*")

    async def test_invalidate_user_cache_different_user_ids(self) -> None:
        """Test cache invalidation with different user IDs."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        with patch("checklists_service.utils.integrations.cache") as mock_cache:
            mock_cache.delete_pattern = AsyncMock()

            await client.invalidate_user_cache(1)
            mock_cache.delete_pattern.assert_called_with("auth_user:*1*")

            await client.invalidate_user_cache(999999)
            mock_cache.delete_pattern.assert_called_with("auth_user:*999999*")


class TestAuthServiceClientInit:
    """Test AuthServiceClient initialization."""

    def test_init_with_default_url(self) -> None:
        """Test initialization uses default URL from settings."""
        with patch("checklists_service.utils.integrations.settings") as mock_settings:
            mock_settings.AUTH_SERVICE_URL = "http://auth-service:8001"
            mock_settings.AUTH_SERVICE_TIMEOUT = 30

            client = AuthServiceClient()

            assert client.base_url == "http://auth-service:8001"

    def test_init_with_custom_url(self) -> None:
        """Test initialization with custom URL."""
        client = AuthServiceClient(base_url="http://custom-auth:9000")

        assert client.base_url == "http://custom-auth:9000"


class TestAuthServiceClientSingleton:
    """Test the auth_service_client singleton."""

    def test_singleton_exists(self) -> None:
        """Test that auth_service_client singleton exists and is an AuthServiceClient."""
        assert auth_service_client is not None
        assert isinstance(auth_service_client, AuthServiceClient)

    def test_singleton_uses_default_settings(self) -> None:
        """Test that singleton uses settings from config."""
        # The singleton should have been initialized with settings
        assert auth_service_client.base_url is not None


class TestAuthServiceClientCachingDecorator:
    """Test that caching decorator is applied."""

    async def test_validate_token_uses_cache_decorator(self) -> None:
        """Test that validate_token method has @cached decorator."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        # Check that the method has the cache wrapper attributes
        assert hasattr(client.validate_token, "__wrapped__") or "cached" in str(type(client.validate_token))

    async def test_get_user_uses_cache_decorator(self) -> None:
        """Test that get_user method has @cached decorator."""
        client = AuthServiceClient(base_url="http://test-auth:8001")

        # Check that the method has the cache wrapper attributes
        assert hasattr(client.get_user, "__wrapped__") or "cached" in str(type(client.get_user))


class TestNotificationServiceClientSendNotification:
    """Test send_notification method."""

    async def test_send_notification_success(self) -> None:
        """Test successful notification sending."""
        client = NotificationServiceClient(base_url="http://test-notification:8002")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "status": "sent"}

        with patch.object(client.client, "post", new=AsyncMock(return_value=mock_response)):
            result = await client.send_notification(
                user_id=1,
                notification_type="task_assigned",
                channel="email",
                recipient_email="user@example.com",
                subject="Task Assigned",
                body="You have a new task",
            )

        assert result is not None
        assert result["id"] == 123
        assert result["status"] == "sent"

    async def test_send_notification_with_auth_token(self) -> None:
        """Test notification sending with auth token."""
        client = NotificationServiceClient(base_url="http://test-notification:8002")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 456, "status": "sent"}

        with patch.object(client.client, "post", new=AsyncMock(return_value=mock_response)) as mock_post:
            result = await client.send_notification(
                user_id=1,
                notification_type="task_completed",
                channel="telegram",
                recipient_telegram_id="123456789",
                subject="Task Completed",
                body="Task completed successfully",
                auth_token="service-token",
            )

            assert result is not None
            # Verify auth token was included in headers
            call_kwargs = mock_post.call_args[1]
            assert "headers" in call_kwargs
            assert call_kwargs["headers"]["Authorization"] == "Bearer service-token"

    async def test_send_notification_with_data(self) -> None:
        """Test notification sending with custom data."""
        client = NotificationServiceClient(base_url="http://test-notification:8002")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 789, "status": "sent"}

        with patch.object(client.client, "post", new=AsyncMock(return_value=mock_response)) as mock_post:
            result = await client.send_notification(
                user_id=1,
                notification_type="checklist_due",
                channel="email",
                recipient_email="user@example.com",
                subject="Checklist Due Soon",
                body="Your checklist is due soon",
                data={"checklist_id": 123, "due_date": "2026-05-01"},
            )

            assert result is not None
            # Verify data was included in payload
            call_kwargs = mock_post.call_args[1]
            assert "json" in call_kwargs
            assert call_kwargs["json"]["data"]["checklist_id"] == 123

    async def test_send_notification_error_response(self) -> None:
        """Test notification sending returns None on error response."""
        client = NotificationServiceClient(base_url="http://test-notification:8002")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch.object(client.client, "post", new=AsyncMock(return_value=mock_response)):
            result = await client.send_notification(
                user_id=1,
                notification_type="task_assigned",
                channel="email",
                recipient_email="user@example.com",
            )

        assert result is None

    async def test_send_notification_request_error(self) -> None:
        """Test notification sending handles httpx.RequestError."""
        client = NotificationServiceClient(base_url="http://test-notification:8002")

        with patch.object(client.client, "post", new=AsyncMock(side_effect=httpx.RequestError("Connection failed"))):
            result = await client.send_notification(
                user_id=1,
                notification_type="task_assigned",
                channel="email",
                recipient_email="user@example.com",
            )

        assert result is None

    async def test_send_notification_generic_exception(self) -> None:
        """Test notification sending handles generic exceptions."""
        client = NotificationServiceClient(base_url="http://test-notification:8002")

        with patch.object(client.client, "post", new=AsyncMock(side_effect=Exception("Unexpected error"))):
            result = await client.send_notification(
                user_id=1,
                notification_type="task_assigned",
                channel="email",
                recipient_email="user@example.com",
            )

        assert result is None


class TestNotificationServiceClientInit:
    """Test NotificationServiceClient initialization."""

    def test_init_with_default_url(self) -> None:
        """Test initialization uses default URL from settings."""
        with patch("checklists_service.utils.integrations.settings") as mock_settings:
            mock_settings.NOTIFICATION_SERVICE_URL = "http://notification-service:8002"
            mock_settings.SERVICE_TIMEOUT = 30

            client = NotificationServiceClient()

            assert client.base_url == "http://notification-service:8002"

    def test_init_with_custom_url(self) -> None:
        """Test initialization with custom URL."""
        client = NotificationServiceClient(base_url="http://custom-notification:9000")

        assert client.base_url == "http://custom-notification:9000"


class TestNotificationServiceClientSingleton:
    """Test the notification_service_client singleton."""

    def test_singleton_exists(self) -> None:
        """Test that notification_service_client singleton exists and is a NotificationServiceClient."""
        assert notification_service_client is not None
        assert isinstance(notification_service_client, NotificationServiceClient)

    def test_singleton_uses_default_settings(self) -> None:
        """Test that singleton uses settings from config."""
        # The singleton should have been initialized with settings
        assert notification_service_client.base_url is not None
