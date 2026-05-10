"""Unit tests for utils/integrations.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from meeting_service.utils.integrations import AuthServiceClient, NotificationServiceClient


class TestAuthServiceClient:
    """Tests for AuthServiceClient."""

    @pytest.mark.asyncio
    async def test_get_user_success(self):
        """Test successful user fetch from auth service."""
        client = AuthServiceClient(base_url="http://auth:8000")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 42, "email": "user@example.com", "role": "EMPLOYEE"}

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch.object(client, "client", mock_http_client):
            result = await client.get_user(42, "test-token")

        assert result == {"id": 42, "email": "user@example.com", "role": "EMPLOYEE"}
        mock_http_client.get.assert_awaited_once_with(
            "/api/v1/users/42",
            headers={"Authorization": "Bearer test-token"},
        )

    @pytest.mark.asyncio
    async def test_get_user_not_found_returns_none(self):
        """Test that non-200 response returns None."""
        client = AuthServiceClient(base_url="http://auth:8000")

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch.object(client, "client", mock_http_client):
            result = await client.get_user(999, "test-token")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_request_error_returns_none(self):
        """Test that RequestError returns None."""
        client = AuthServiceClient(base_url="http://auth:8000")

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(side_effect=httpx.RequestError("Connection refused"))

        with patch.object(client, "client", mock_http_client):
            result = await client.get_user(1, "test-token")

        assert result is None


class TestNotificationServiceClient:
    """Tests for NotificationServiceClient."""

    @pytest.mark.asyncio
    async def test_schedule_template_notification_success(self):
        """Test successful template notification scheduling."""
        client = NotificationServiceClient(base_url="http://notification:8000")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "notif-123", "status": "scheduled"}

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        with patch.object(client, "client", mock_http_client):
            result = await client.schedule_template_notification(
                template_name="meeting_reminder",
                user_id=100,
                variables={"user_name": "Alice", "meeting_title": "HR Meeting"},
                channel="EMAIL",
                scheduled_time="2026-01-01T10:00:00+00:00",
                notification_type="MEETING_REMINDER",
                recipient_email="alice@example.com",
                language="en",
            )

        assert result == {"id": "notif-123", "status": "scheduled"}
        mock_http_client.post.assert_awaited_once()
        call_kwargs = mock_http_client.post.call_args
        assert call_kwargs[0][0] == "/api/v1/notifications/internal/schedule-template"

    @pytest.mark.asyncio
    async def test_schedule_template_notification_error_returns_none(self):
        """Test that non-200 response returns None."""
        client = NotificationServiceClient(base_url="http://notification:8000")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        with patch.object(client, "client", mock_http_client):
            result = await client.schedule_template_notification(
                template_name="meeting_reminder",
                user_id=100,
                variables={},
                channel="EMAIL",
                scheduled_time="2026-01-01T10:00:00+00:00",
                notification_type="MEETING_REMINDER",
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_schedule_template_notification_request_error_returns_none(self):
        """Test that RequestError returns None."""
        client = NotificationServiceClient(base_url="http://notification:8000")

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=httpx.RequestError("Connection refused"))

        with patch.object(client, "client", mock_http_client):
            result = await client.schedule_template_notification(
                template_name="meeting_reminder",
                user_id=100,
                variables={},
                channel="TELEGRAM",
                scheduled_time="2026-01-01T10:00:00+00:00",
                notification_type="MEETING_REMINDER",
                recipient_telegram_id=12345,
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_scheduled_notifications_success(self):
        """Test successful cancellation of scheduled notifications."""
        client = NotificationServiceClient(base_url="http://notification:8000")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cancelled": 3}

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        with patch.object(client, "client", mock_http_client):
            result = await client.cancel_scheduled_notifications(
                user_id=100,
                notification_type="MEETING_REMINDER",
                data_match={"source_service": "meeting_service", "assignment_id": 5},
            )

        assert result == 3
        mock_http_client.post.assert_awaited_once()
        call_kwargs = mock_http_client.post.call_args
        assert call_kwargs[0][0] == "/api/v1/notifications/internal/scheduled/cancel"

    @pytest.mark.asyncio
    async def test_cancel_scheduled_notifications_error_returns_zero(self):
        """Test that non-200 response returns 0."""
        client = NotificationServiceClient(base_url="http://notification:8000")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        with patch.object(client, "client", mock_http_client):
            result = await client.cancel_scheduled_notifications(
                user_id=100,
                notification_type="MEETING_REMINDER",
                data_match={"assignment_id": 5},
            )

        assert result == 0

    @pytest.mark.asyncio
    async def test_cancel_scheduled_notifications_request_error_returns_zero(self):
        """Test that RequestError returns 0."""
        client = NotificationServiceClient(base_url="http://notification:8000")

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=httpx.RequestError("Connection refused"))

        with patch.object(client, "client", mock_http_client):
            result = await client.cancel_scheduled_notifications(
                user_id=100,
                notification_type="MEETING_REMINDER",
                data_match={"assignment_id": 5},
            )

        assert result == 0

    @pytest.mark.asyncio
    async def test_schedule_notification_with_telegram_id(self):
        """Test scheduling with telegram recipient."""
        client = NotificationServiceClient(base_url="http://notification:8000")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "notif-456"}

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        with patch.object(client, "client", mock_http_client):
            result = await client.schedule_template_notification(
                template_name="meeting_reminder",
                user_id=100,
                variables={"minutes_until": 15},
                channel="TELEGRAM",
                scheduled_time="2026-01-01T09:45:00+00:00",
                notification_type="MEETING_REMINDER",
                recipient_telegram_id=99999,
                language="ru",
                data={"source_service": "meeting_service"},
            )

        assert result == {"id": "notif-456"}
        post_json = mock_http_client.post.call_args.kwargs["json"]
        assert post_json["recipient_telegram_id"] == 99999
        assert post_json["language"] == "ru"
        assert post_json["channel"] == "TELEGRAM"
