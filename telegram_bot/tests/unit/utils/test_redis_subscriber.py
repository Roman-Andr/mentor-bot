"""Unit tests for telegram_bot/utils/redis_subscriber.py."""

import asyncio
import contextlib
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot
from redis.asyncio import Redis
from telegram_bot.utils.redis_subscriber import RedisNotificationSubscriber


class TestRedisNotificationSubscriber:
    """Test cases for RedisNotificationSubscriber."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock Bot."""
        bot = MagicMock(spec=Bot)
        bot.send_message = AsyncMock()
        return bot

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis."""
        redis = MagicMock(spec=Redis)
        redis.from_url = MagicMock(return_value=redis)
        redis.aclose = AsyncMock()
        return redis

    def test_initialization(self):
        """Test subscriber initialization."""
        sub = RedisNotificationSubscriber("redis://localhost:6379/0")
        assert sub.redis_url == "redis://localhost:6379/0"
        assert sub.redis is None
        assert sub.bot is None
        assert sub._running is False

    def test_initialization_default_url(self):
        """Test subscriber initialization with default URL."""
        with patch("telegram_bot.utils.redis_subscriber.settings") as mock_settings:
            mock_settings.REDIS_URL = "redis://default:6379/0"
            sub = RedisNotificationSubscriber()
            assert sub.redis_url == "redis://default:6379/0"

    async def test_start(self, mock_bot, mock_redis):
        """Test starting the subscriber."""
        with patch("telegram_bot.utils.redis_subscriber.Redis.from_url", return_value=mock_redis):
            sub = RedisNotificationSubscriber("redis://localhost:6379/0")
            await sub.start(mock_bot)

            assert sub.bot == mock_bot
            assert sub.redis is not None
            assert sub._running is True
            assert sub._task is not None

            # Clean up the task to avoid unhandled exception warning
            await sub.stop()

    async def test_stop(self, mock_redis):
        """Test stopping the subscriber."""
        sub = RedisNotificationSubscriber()
        sub._running = True
        sub.redis = mock_redis
        sub._task = MagicMock()
        sub._task.cancel = MagicMock()

        async def mock_task():
            pass

        task = asyncio.create_task(mock_task())
        sub._task = task

        await sub.stop()

        # Ensure the task is cleaned up
        with contextlib.suppress(asyncio.CancelledError):
            await task

        assert sub._running is False
        mock_redis.aclose.assert_called_once()

    async def test_stop_no_redis(self):
        """Test stopping subscriber when redis is None."""
        sub = RedisNotificationSubscriber()
        sub._running = True
        sub.redis = None

        await sub.stop()

        assert sub._running is False

    async def test_stop_redis_close_exception(self, mock_redis):
        """Test stopping subscriber when redis.aclose raises exception (lines 48-49)."""
        sub = RedisNotificationSubscriber()
        sub._running = True
        sub.redis = mock_redis
        mock_redis.aclose = AsyncMock(side_effect=Exception("Close failed"))

        with patch("telegram_bot.utils.redis_subscriber.logger"):
            await sub.stop()

            assert sub._running is False

    async def test_subscribe_no_redis(self):
        """Test subscribe when redis is None (line 55)."""
        sub = RedisNotificationSubscriber()
        sub.redis = None

        await sub._subscribe()

        # Should return early without error
        assert True

    async def test_subscribe_loop_notification(self, mock_bot, mock_redis):
        """Test _subscribe loop processes notification messages (lines 57-80)."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot
        sub.redis = mock_redis

        call_count = 0

        async def fake_get_message(**_kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"type": "message", "channel": "telegram_notifications", "data": '{"chat_id": 1, "text": "hi"}'}
            sub._running = False
            return None

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        mock_pubsub.get_message = AsyncMock(side_effect=fake_get_message)
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        sub._running = True
        sub._handle_notification = AsyncMock()

        await sub._subscribe()

        sub._handle_notification.assert_called_once_with('{"chat_id": 1, "text": "hi"}')
        mock_pubsub.unsubscribe.assert_called_once()
        mock_pubsub.close.assert_called_once()

    async def test_subscribe_loop_event(self, mock_bot, mock_redis):
        """Test _subscribe loop processes event messages (lines 57-80)."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot
        sub.redis = mock_redis

        call_count = 0

        async def fake_get_message(**_kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"type": "message", "channel": "telegram_events", "data": '{"type": "x"}'}
            sub._running = False
            return None

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        mock_pubsub.get_message = AsyncMock(side_effect=fake_get_message)
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        sub._running = True
        sub._handle_event = AsyncMock()

        await sub._subscribe()

        sub._handle_event.assert_called_once_with('{"type": "x"}')

    async def test_subscribe_loop_exception(self, mock_bot, mock_redis):
        """Test _subscribe loop handles exceptions (lines 57-80)."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot
        sub.redis = mock_redis

        call_count = 0

        async def fake_get_message(**_kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Redis error")
            sub._running = False

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        mock_pubsub.get_message = AsyncMock(side_effect=fake_get_message)
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        sub._running = True

        with patch("telegram_bot.utils.redis_subscriber.asyncio.sleep", new_callable=AsyncMock):
            await sub._subscribe()

    async def test_subscribe_loop_cancelled(self, mock_bot, mock_redis):
        """Test _subscribe loop handles CancelledError (lines 57-80)."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot
        sub.redis = mock_redis

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        mock_pubsub.get_message = AsyncMock(side_effect=asyncio.CancelledError)
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        sub._running = True

        await sub._subscribe()

        mock_pubsub.unsubscribe.assert_called_once()
        mock_pubsub.close.assert_called_once()

    async def test_handle_notification_success(self, mock_bot):
        """Test handling notification message successfully (lines 84-105)."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot

        payload = {"chat_id": 123456, "text": "Test message", "parse_mode": "HTML"}
        data = json.dumps(payload)

        await sub._handle_notification(data)

        mock_bot.send_message.assert_called_once_with(
            chat_id=123456,
            text="Test message",
            parse_mode="HTML",
        )

    async def test_handle_notification_invalid_payload(self, mock_bot):
        """Test handling notification with invalid payload."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot

        payload = {"chat_id": None, "text": "Test"}
        data = json.dumps(payload)

        await sub._handle_notification(data)

        mock_bot.send_message.assert_not_called()

    async def test_handle_notification_no_bot(self):
        """Test handling notification when bot is not initialized."""
        sub = RedisNotificationSubscriber()
        sub.bot = None

        payload = {"chat_id": 123456, "text": "Test"}
        data = json.dumps(payload)

        with patch("telegram_bot.utils.redis_subscriber.logger"):
            await sub._handle_notification(data)

    async def test_handle_notification_exception(self, mock_bot):
        """Test handling notification with exception."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot
        mock_bot.send_message = AsyncMock(side_effect=Exception("Send failed"))

        payload = {"chat_id": 123456, "text": "Test"}
        data = json.dumps(payload)

        with patch("telegram_bot.utils.redis_subscriber.logger"):
            await sub._handle_notification(data)

    async def test_handle_event_calendar_connected(self, mock_bot):
        """Test handling calendar_connected event (lines 109-118, 122-162)."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot

        payload = {"type": "calendar_connected", "user_id": 123}
        data = json.dumps(payload)

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.find_telegram_id_by_user_id = AsyncMock(return_value=456)
            mock_cache.get_user = AsyncMock(return_value={"locale": "en"})

            with patch("telegram_bot.utils.redis_subscriber.t") as mock_t:
                mock_t.side_effect = lambda key, **_kwargs: f"Translated {key}"

                with patch("telegram_bot.keyboards.calendar_kb.get_calendar_connected_keyboard") as mock_kb:
                    mock_kb.return_value = MagicMock()

                    await sub._handle_event(data)

                    mock_bot.send_message.assert_called_once()

    async def test_handle_event_unknown_type(self):
        """Test handling unknown event type."""
        sub = RedisNotificationSubscriber()

        payload = {"type": "unknown_event"}
        data = json.dumps(payload)

        with patch("telegram_bot.utils.redis_subscriber.logger"):
            await sub._handle_event(data)

    async def test_handle_event_user_deleted_invalidates_cache(self):
        """Test user_deleted event clears cached auth state."""
        sub = RedisNotificationSubscriber()

        payload = {"type": "user_deleted", "user_id": 123, "telegram_id": 456}
        data = json.dumps(payload)

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.delete_user = AsyncMock(return_value=True)

            await sub._handle_event(data)

        mock_cache.delete_user.assert_awaited_once_with(456)

    async def test_handle_user_removed_falls_back_to_user_id_lookup(self):
        """Test removal event can resolve telegram_id from cached user_id."""
        sub = RedisNotificationSubscriber()

        payload = {"type": "user_deactivated", "user_id": 123}

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.find_telegram_id_by_user_id = AsyncMock(return_value=456)
            mock_cache.delete_user = AsyncMock(return_value=True)

            await sub._handle_user_removed(payload)

        mock_cache.find_telegram_id_by_user_id.assert_awaited_once_with(123)
        mock_cache.delete_user.assert_awaited_once_with(456)

    async def test_handle_user_removed_missing_telegram_id(self):
        """Test removal event logs and returns when telegram_id cannot be resolved."""
        sub = RedisNotificationSubscriber()

        payload = {"type": "user_deleted", "user_id": 123}

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.find_telegram_id_by_user_id = AsyncMock(return_value=None)
            mock_cache.delete_user = AsyncMock()

            with patch("telegram_bot.utils.redis_subscriber.logger") as mock_logger:
                await sub._handle_user_removed(payload)

        mock_cache.find_telegram_id_by_user_id.assert_awaited_once_with(123)
        mock_cache.delete_user.assert_not_awaited()
        mock_logger.warning.assert_called_once()

    async def test_handle_user_removed_delete_failure(self):
        """Test removal event logs when cache invalidation returns false."""
        sub = RedisNotificationSubscriber()

        payload = {"type": "user_deleted", "telegram_id": 456}

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.delete_user = AsyncMock(return_value=False)

            with patch("telegram_bot.utils.redis_subscriber.logger") as mock_logger:
                await sub._handle_user_removed(payload)

        mock_cache.delete_user.assert_awaited_once_with(456)
        mock_logger.warning.assert_called_once()

    async def test_handle_calendar_connected_no_user_id(self, mock_bot):
        """Test calendar_connected event with missing user_id."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot

        payload = {"type": "calendar_connected"}
        data = json.dumps(payload)

        with patch("telegram_bot.utils.redis_subscriber.logger"):
            await sub._handle_calendar_connected(payload)

        mock_bot.send_message.assert_not_called()

    async def test_handle_calendar_connected_no_telegram_id(self, mock_bot):
        """Test calendar_connected event when telegram_id not found."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot

        payload = {"type": "calendar_connected", "user_id": 123}
        data = json.dumps(payload)

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.find_telegram_id_by_user_id = AsyncMock(return_value=None)

            with patch("telegram_bot.utils.redis_subscriber.logger"):
                await sub._handle_calendar_connected(payload)

        mock_bot.send_message.assert_not_called()

    async def test_handle_calendar_connected_no_bot(self):
        """Test calendar_connected event when bot not initialized (lines 135-136)."""
        sub = RedisNotificationSubscriber()
        sub.bot = None

        payload = {"type": "calendar_connected", "user_id": 123}

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.find_telegram_id_by_user_id = AsyncMock(return_value=456)
            with patch("telegram_bot.utils.redis_subscriber.logger"):
                await sub._handle_calendar_connected(payload)

    async def test_handle_calendar_connected_exception(self, mock_bot):
        """Test calendar_connected event with exception (line 162)."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot

        payload = {"type": "calendar_connected", "user_id": 123}

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.find_telegram_id_by_user_id = AsyncMock(side_effect=Exception("Cache error"))

            with patch("telegram_bot.utils.redis_subscriber.logger"):
                await sub._handle_calendar_connected(payload)

    async def test_handle_calendar_connected_no_user_data(self, mock_bot):
        """Test calendar_connected event when user_data is None (lines 135-136)."""
        sub = RedisNotificationSubscriber()
        sub.bot = mock_bot

        payload = {"type": "calendar_connected", "user_id": 123}

        with patch("telegram_bot.utils.redis_subscriber.user_cache") as mock_cache:
            mock_cache.find_telegram_id_by_user_id = AsyncMock(return_value=456)
            mock_cache.get_user = AsyncMock(return_value=None)

            with patch("telegram_bot.utils.redis_subscriber.t") as mock_t:
                mock_t.side_effect = lambda key, **_kwargs: f"Translated {key}"

                with patch("telegram_bot.keyboards.calendar_kb.get_calendar_connected_keyboard") as mock_kb:
                    mock_kb.return_value = MagicMock()

                    await sub._handle_calendar_connected(payload)

                    mock_bot.send_message.assert_called_once()

    async def test_handle_event_exception(self):
        """Test handle_event with exception (line 118)."""
        sub = RedisNotificationSubscriber()

        payload = {"type": "calendar_connected", "user_id": 123}
        data = "invalid json"

        with patch("telegram_bot.utils.redis_subscriber.logger"):
            await sub._handle_event(data)


class TestRedisSubscriberSingleton:
    """Test the subscriber singleton instance."""

    def test_singleton_exists(self):
        """Test that subscriber singleton exists."""
        from telegram_bot.utils.redis_subscriber import subscriber

        assert subscriber is not None
        assert isinstance(subscriber, RedisNotificationSubscriber)
