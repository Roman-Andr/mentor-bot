"""Unit tests for notification_service/services/telegram.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from _pytest.logging import LogCaptureFixture
from notification_service.config import settings
from notification_service.services.telegram import TelegramService


class TestTelegramServiceInit:
    """Tests for TelegramService initialization."""

    def test_init_sets_token_from_settings(self) -> None:
        """TelegramService initializes with token from settings."""
        service = TelegramService()
        assert service.token == settings.TELEGRAM_BOT_TOKEN

    def test_init_builds_api_url_correctly(self) -> None:
        """API URL is built with token from settings."""
        service = TelegramService()
        expected_url = f"{settings.TELEGRAM_API_URL}{settings.TELEGRAM_BOT_TOKEN}"
        assert service.api_url == expected_url


class TestTelegramSendMessage:
    """Tests for TelegramService.send_message method."""

    async def test_send_message_makes_post_request_to_sendmessage(self) -> None:
        """SendMessage endpoint is called with correct parameters."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text="Hello World")

        assert result is True
        mock_client.post.assert_awaited_once()
        call_args = mock_client.post.call_args
        assert call_args.kwargs["json"]["chat_id"] == 123456789
        assert call_args.kwargs["json"]["text"] == "Hello World"
        assert call_args.kwargs["json"]["parse_mode"] == "HTML"

    async def test_send_message_returns_true_on_success(self) -> None:
        """Returns True when Telegram API responds with ok: True."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 123}}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text="Test message")

        assert result is True

    async def test_send_message_returns_false_on_api_error(self) -> None:
        """Returns False when Telegram API responds with ok: False."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": False, "error_code": 400, "description": "Bad Request"}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text="Test")

        assert result is False

    async def test_send_message_returns_false_on_http_error(self) -> None:
        """Returns False when HTTP request raises an exception."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(side_effect=httpx.HTTPError("Connection failed"))

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text="Test")

        assert result is False

    async def test_send_message_returns_false_on_network_error(self) -> None:
        """Returns False when network request fails."""
        service = TelegramService()

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Network unreachable"))

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text="Test")

        assert result is False

    async def test_send_message_logs_api_error(self, caplog: LogCaptureFixture) -> None:
        """Logs error when Telegram API returns ok: False."""
        caplog.set_level("ERROR")
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": False, "error_code": 403, "description": "Forbidden"}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await service.send_message(chat_id=123456789, text="Test")

        assert "Telegram API error" in caplog.text

    async def test_send_message_logs_exception_on_failure(self, caplog: LogCaptureFixture) -> None:
        """Logs exception when message sending fails."""
        caplog.set_level("ERROR")
        service = TelegramService()

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))

        with patch("httpx.AsyncClient", return_value=mock_client):
            await service.send_message(chat_id=123456789, text="Test")

        assert "Failed to send Telegram message" in caplog.text

    async def test_send_message_with_html_formatting(self) -> None:
        """Messages can include HTML formatting."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        html_message = "<b>Bold</b> and <i>italic</i> text"

        with patch("httpx.AsyncClient", return_value=mock_client):
            await service.send_message(chat_id=123456789, text=html_message)

        call_kwargs = mock_client.post.call_args.kwargs
        assert call_kwargs["json"]["text"] == html_message
        assert call_kwargs["json"]["parse_mode"] == "HTML"

    async def test_send_message_with_special_characters(self) -> None:
        """Messages can include special characters."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        message_with_special = "Hello! Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text=message_with_special)

        assert result is True
        call_kwargs = mock_client.post.call_args.kwargs
        assert call_kwargs["json"]["text"] == message_with_special

    async def test_send_message_with_unicode(self) -> None:
        """Messages can include unicode characters and emojis."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        unicode_message = "Hello World! 🎉 Привет мир! 你好世界!"

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text=unicode_message)

        assert result is True
        call_kwargs = mock_client.post.call_args.kwargs
        assert call_kwargs["json"]["text"] == unicode_message

    async def test_send_message_with_long_text(self) -> None:
        """Long messages are handled correctly."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        long_message = "A" * 4000  # Telegram allows up to 4096 chars

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text=long_message)

        assert result is True

    async def test_send_message_with_negative_chat_id(self) -> None:
        """Group chat IDs (negative numbers) are handled correctly."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        group_chat_id = -1001234567890  # Typical group chat ID format

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=group_chat_id, text="Group message")

        assert result is True
        call_kwargs = mock_client.post.call_args.kwargs
        assert call_kwargs["json"]["chat_id"] == group_chat_id

    async def test_send_message_uses_correct_timeout(self) -> None:
        """Request uses correct timeout value."""
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await service.send_message(chat_id=123456789, text="Test")

        call_kwargs = mock_client.post.call_args.kwargs
        assert call_kwargs["timeout"] == 10.0


class TestTelegramServiceErrorHandling:
    """Tests for TelegramService error handling scenarios."""

    async def test_handles_invalid_token_response(self, caplog: LogCaptureFixture) -> None:
        """Handles response indicating invalid bot token."""
        caplog.set_level("ERROR")
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": False, "error_code": 401, "description": "Unauthorized"}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text="Test")

        assert result is False
        assert "Telegram API error" in caplog.text

    async def test_handles_chat_not_found_error(self, caplog: LogCaptureFixture) -> None:
        """Handles response indicating chat not found."""
        caplog.set_level("ERROR")
        service = TelegramService()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": False, "error_code": 400, "description": "Bad Request: chat not found"}

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_message(chat_id=123456789, text="Test")

        assert result is False
