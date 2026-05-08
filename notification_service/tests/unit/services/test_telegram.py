"""Unit tests for notification_service/services/telegram.py."""

from unittest.mock import AsyncMock, MagicMock, patch

from _pytest.logging import LogCaptureFixture
from notification_service.services.telegram import TelegramService


class TestTelegramServiceInit:
    """Tests for TelegramService initialization."""

    def test_init_sets_channel(self) -> None:
        """TelegramService initializes with correct channel name."""
        service = TelegramService()
        assert service.channel == "telegram_notifications"
        assert service.redis is None

    async def test_get_redis_creates_connection_when_none(self) -> None:
        """_get_redis creates new Redis connection when redis is None."""
        from notification_service.config import settings
        from redis.asyncio import Redis

        service = TelegramService()
        assert service.redis is None

        with patch("notification_service.services.telegram.Redis") as mock_redis_cls:
            mock_redis_instance = MagicMock()
            mock_redis_cls.from_url.return_value = mock_redis_instance

            result = await service._get_redis()

            mock_redis_cls.from_url.assert_called_once_with(settings.REDIS_URL, decode_responses=True)
            assert result == mock_redis_instance
            assert service.redis == mock_redis_instance


class TestTelegramSendMessage:
    """Tests for TelegramService.send_message method."""

    async def test_send_message_publishes_to_redis(self) -> None:
        """SendMessage publishes message to Redis channel."""
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(return_value=1)

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            result = await service.send_message(chat_id=123456789, text="Hello World")

        assert result is True
        mock_redis.publish.assert_awaited_once()
        call_args = mock_redis.publish.call_args
        assert call_args.args[0] == "telegram_notifications"
        import json
        payload = json.loads(call_args.args[1])
        assert payload["chat_id"] == 123456789
        assert payload["text"] == "Hello World"
        assert payload["parse_mode"] == "HTML"

    async def test_send_message_returns_true_on_success(self) -> None:
        """Returns True when Redis publish succeeds."""
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(return_value=1)

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            result = await service.send_message(chat_id=123456789, text="Test message")

        assert result is True

    async def test_send_message_returns_false_on_redis_error(self) -> None:
        """Returns False when Redis publish fails."""
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(side_effect=Exception("Redis error"))

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            result = await service.send_message(chat_id=123456789, text="Test")

        assert result is False

    async def test_send_message_logs_exception_on_failure(self, caplog: LogCaptureFixture) -> None:
        """Logs exception when Redis publish fails."""
        caplog.set_level("ERROR")
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(side_effect=Exception("Connection failed"))

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            await service.send_message(chat_id=123456789, text="Test")

        assert "Failed to publish Telegram notification to Redis" in caplog.text

    async def test_send_message_with_html_formatting(self) -> None:
        """Messages can include HTML formatting."""
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(return_value=1)

        html_message = "<b>Bold</b> and <i>italic</i> text"

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            await service.send_message(chat_id=123456789, text=html_message)

        import json
        call_args = mock_redis.publish.call_args
        payload = json.loads(call_args.args[1])
        assert payload["text"] == html_message
        assert payload["parse_mode"] == "HTML"

    async def test_send_message_with_special_characters(self) -> None:
        """Messages can include special characters."""
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(return_value=1)

        message_with_special = "Hello! Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            result = await service.send_message(chat_id=123456789, text=message_with_special)

        assert result is True
        import json
        call_args = mock_redis.publish.call_args
        payload = json.loads(call_args.args[1])
        assert payload["text"] == message_with_special

    async def test_send_message_with_unicode(self) -> None:
        """Messages can include unicode characters and emojis."""
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(return_value=1)

        unicode_message = "Hello World! 🎉 Привет мир! 你好世界!"

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            result = await service.send_message(chat_id=123456789, text=unicode_message)

        assert result is True
        import json
        call_args = mock_redis.publish.call_args
        payload = json.loads(call_args.args[1])
        assert payload["text"] == unicode_message

    async def test_send_message_with_long_text(self) -> None:
        """Long messages are handled correctly."""
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(return_value=1)

        long_message = "A" * 4000

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            result = await service.send_message(chat_id=123456789, text=long_message)

        assert result is True

    async def test_send_message_with_negative_chat_id(self) -> None:
        """Group chat IDs (negative numbers) are handled correctly."""
        service = TelegramService()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(return_value=1)

        group_chat_id = -1001234567890

        with patch.object(service, "_get_redis", new=AsyncMock(return_value=mock_redis)):
            result = await service.send_message(chat_id=group_chat_id, text="Group message")

        assert result is True
        import json
        call_args = mock_redis.publish.call_args
        payload = json.loads(call_args.args[1])
        assert payload["chat_id"] == group_chat_id


class TestTelegramServiceCleanup:
    """Tests for TelegramService cleanup."""

    async def test_close_closes_redis_connection(self) -> None:
        """Close method closes Redis connection."""
        service = TelegramService()
        mock_redis = MagicMock()
        mock_redis.close = AsyncMock()
        service.redis = mock_redis

        await service.close()

        mock_redis.close.assert_awaited_once()
        assert service.redis is None

    async def test_close_handles_none_redis(self) -> None:
        """Close method handles None redis gracefully."""
        service = TelegramService()
        service.redis = None

        await service.close()

        # Should not raise any exception
        assert service.redis is None

    async def test_close_logs_error_on_failure(self, caplog: LogCaptureFixture) -> None:
        """Close method logs error when closing fails."""
        caplog.set_level("ERROR")
        service = TelegramService()
        mock_redis = MagicMock()
        mock_redis.close = AsyncMock(side_effect=Exception("Close failed"))
        service.redis = mock_redis

        await service.close()

        assert "Failed to close Redis connection" in caplog.text
        assert service.redis is None
