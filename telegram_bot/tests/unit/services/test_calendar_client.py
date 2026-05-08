"""Unit tests for telegram_bot/services/calendar_client.py."""

from unittest.mock import MagicMock, patch

import pytest
from telegram_bot.services.calendar_client import CalendarClient


class TestCalendarClient:
    """Test cases for CalendarClient."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client."""
        self.client = CalendarClient(base_url="http://test-meeting:8006")
        self.auth_token = "test_token_123"
        self.user_id = 123

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.get")
    async def test_check_connection_status_connected(self, mock_get):
        """Test checking connection status - connected."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"connected": True, "email": "user@example.com"}
        mock_get.return_value = mock_response

        result = await self.client.check_connection_status(self.user_id, self.auth_token)

        assert result["connected"] is True
        assert result["email"] == "user@example.com"

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.get")
    async def test_check_connection_status_not_connected(self, mock_get):
        """Test checking connection status - not connected."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"connected": False}
        mock_get.return_value = mock_response

        result = await self.client.check_connection_status(self.user_id, self.auth_token)

        assert result["connected"] is False

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.get")
    async def test_check_connection_status_http_error(self, mock_get):
        """Test checking connection status - HTTP error."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.side_effect = httpx.HTTPStatusError("Server error", request=MagicMock(), response=mock_response)

        result = await self.client.check_connection_status(self.user_id, self.auth_token)

        assert result["connected"] is False
        assert "error" in result

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.get")
    async def test_check_connection_status_request_error(self, mock_get):
        """Test checking connection status - request error."""
        import httpx

        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.check_connection_status(self.user_id, self.auth_token)

        assert result["connected"] is False
        assert "error" in result

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.get")
    async def test_get_connect_url(self, mock_get):
        """Test getting connect URL by calling Meeting Service."""
        mock_response = MagicMock()
        mock_response.status_code = 307
        mock_response.headers = {"location": "https://accounts.google.com/o/oauth2/auth?code=test"}
        mock_get.return_value = mock_response

        result = await self.client.get_connect_url(self.user_id, "test_state")

        assert result == "https://accounts.google.com/o/oauth2/auth?code=test"
        mock_get.assert_called_once()
        # Verify it calls the Meeting Service /connect endpoint with the state parameter
        call_args = mock_get.call_args
        assert "calendar/connect" in call_args[0][0]
        assert call_args[1]["params"]["state"] == f"{self.user_id}:test_state"

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.get")
    async def test_get_connect_url_no_location_header(self, mock_get):
        """Test getting connect URL when response has no location header."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 307
        mock_response.headers = {}
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Failed to get authorization URL"):
            await self.client.get_connect_url(self.user_id, "test_state")

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.get")
    async def test_get_connect_url_http_error(self, mock_get):
        """Test getting connect URL with HTTP error."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.request = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await self.client.get_connect_url(self.user_id, "test_state")

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.get")
    async def test_get_connect_url_request_error(self, mock_get):
        """Test getting connect URL with request error."""
        import httpx

        mock_get.side_effect = httpx.RequestError("Connection failed")

        with pytest.raises(httpx.RequestError):
            await self.client.get_connect_url(self.user_id, "test_state")

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.delete")
    async def test_disconnect_calendar_success(self, mock_delete):
        """Test disconnecting calendar - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_delete.return_value = mock_response

        result = await self.client.disconnect_calendar(self.user_id, self.auth_token)

        assert "success" in result or "error" not in result

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.delete")
    async def test_disconnect_calendar_http_error(self, mock_delete):
        """Test disconnecting calendar - HTTP error."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_delete.side_effect = httpx.HTTPStatusError("Not found", request=MagicMock(), response=mock_response)

        result = await self.client.disconnect_calendar(self.user_id, self.auth_token)

        assert result["success"] is False
        assert "error" in result

    @patch("telegram_bot.services.calendar_client.httpx.AsyncClient.delete")
    async def test_disconnect_calendar_request_error(self, mock_delete):
        """Test disconnecting calendar - request error."""
        import httpx

        mock_delete.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.disconnect_calendar(self.user_id, self.auth_token)

        assert result["success"] is False
        assert "error" in result
