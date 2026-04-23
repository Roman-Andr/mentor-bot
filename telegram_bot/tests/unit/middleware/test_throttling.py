"""Unit tests for telegram_bot/middlewares/throttling.py."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from telegram_bot.middlewares.throttling import (
    ThrottlingMiddleware,
    ThrottlingService,
    throttling_service,
)


class TestThrottlingMiddlewareInit:
    """Test cases for ThrottlingMiddleware initialization."""

    def test_init_with_redis_client(self):
        """Test that initialization accepts Redis client."""
        mock_redis = MagicMock()
        middleware = ThrottlingMiddleware(redis_client=mock_redis)

        assert middleware.redis == mock_redis
        assert middleware._default_calls == 5
        assert middleware._default_period == 60
        assert middleware._key_prefix == "throttle"

    def test_init_without_redis_client(self):
        """Test that initialization works without Redis client."""
        middleware = ThrottlingMiddleware()

        assert middleware.redis is None


class TestThrottlingMiddlewareMakeKey:
    """Test cases for _make_key method."""

    def test_make_key(self):
        """Test key generation."""
        middleware = ThrottlingMiddleware()
        key = middleware._make_key(123456)

        assert key == "throttle:123456"


class TestThrottlingMiddlewareGetSetData:
    """Test cases for Redis data operations."""

    async def test_get_rate_limit_data_success(self):
        """Test successful retrieval of rate limit data."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=b'{"start_time": 12345, "count": 3}')

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        data = await middleware._get_rate_limit_data(123456)

        assert data == {"start_time": 12345, "count": 3}
        mock_redis.get.assert_called_once_with("throttle:123456")

    async def test_get_rate_limit_data_no_data(self):
        """Test retrieval when no data exists."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=None)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        data = await middleware._get_rate_limit_data(123456)

        assert data is None

    async def test_get_rate_limit_data_redis_error(self):
        """Test handling of Redis error during get."""
        from redis.exceptions import RedisError

        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(side_effect=RedisError("Connection failed"))

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        data = await middleware._get_rate_limit_data(123456)

        assert data is None

    async def test_get_rate_limit_data_no_redis(self):
        """Test get when Redis is not connected."""
        middleware = ThrottlingMiddleware()
        data = await middleware._get_rate_limit_data(123456)

        assert data is None

    async def test_set_rate_limit_data_success(self):
        """Test successful storage of rate limit data."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        result = await middleware._set_rate_limit_data(
            123456, {"start_time": 12345, "count": 3}, 60
        )

        assert result is True
        mock_redis.set.assert_called_once()

    async def test_set_rate_limit_data_redis_error(self):
        """Test handling of Redis error during set."""
        from redis.exceptions import RedisError

        mock_redis = MagicMock()
        mock_redis.set = AsyncMock(side_effect=RedisError("Connection failed"))

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        result = await middleware._set_rate_limit_data(
            123456, {"start_time": 12345, "count": 3}, 60
        )

        assert result is False

    async def test_set_rate_limit_data_no_redis(self):
        """Test set when Redis is not connected."""
        middleware = ThrottlingMiddleware()
        result = await middleware._set_rate_limit_data(
            123456, {"start_time": 12345, "count": 3}, 60
        )

        assert result is False


class TestThrottlingMiddlewareIsRateLimited:
    """Test cases for _is_rate_limited method."""

    async def test_first_call_creates_entry(self):
        """Test first call creates rate limit entry."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        is_limited, remaining = await middleware._is_rate_limited(123456, 5, 60)

        assert is_limited is False
        assert remaining == 4
        mock_redis.set.assert_called_once()

    async def test_within_limit_increments_count(self):
        """Test call within limit increments count."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(
            return_value=f'{{"start_time": {start_time}, "count": 2}}'.encode()
        )
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        is_limited, remaining = await middleware._is_rate_limited(123456, 5, 60)

        assert is_limited is False
        assert remaining == 2

    async def test_limit_exceeded(self):
        """Test when rate limit is exceeded."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(
            return_value=f'{{"start_time": {start_time}, "count": 5}}'.encode()
        )

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        is_limited, remaining = await middleware._is_rate_limited(123456, 5, 60)

        assert is_limited is True
        assert remaining == 0

    async def test_window_expired_resets(self):
        """Test that expired window resets counter."""
        mock_redis = MagicMock()
        old_start_time = datetime.now(UTC).timestamp() - 70  # 70 seconds ago
        mock_redis.get = AsyncMock(
            return_value=f'{{"start_time": {old_start_time}, "count": 5}}'.encode()
        )
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        is_limited, remaining = await middleware._is_rate_limited(123456, 5, 60)

        assert is_limited is False
        assert remaining == 4

    async def test_redis_error_fails_open(self):
        """Test that Redis errors fail open (allow request)."""
        from redis.exceptions import RedisError

        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(side_effect=RedisError("Connection failed"))
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        is_limited, _remaining = await middleware._is_rate_limited(123456, 5, 60)

        assert is_limited is False

    async def test_is_rate_limited_no_redis(self):
        """Test _is_rate_limited when Redis is not connected - line 63."""
        middleware = ThrottlingMiddleware()  # No redis client
        is_limited, remaining = await middleware._is_rate_limited(123456, 5, 60)

        # Should fail open with full calls remaining
        assert is_limited is False
        assert remaining == 5


class TestThrottlingMiddlewareCall:
    """Test cases for __call__ method."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.mock_handler = AsyncMock(return_value="handler_result")

    async def test_no_rate_limit_uses_default(self):
        """Test that default rate limit is used when no flag set."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)

        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = None  # No rate limit flag

            result = await middleware.__call__(self.mock_handler, mock_event, data)

            # Should call handler
            self.mock_handler.assert_called_once()
            assert result == "handler_result"

    async def test_rate_limit_not_exceeded(self):
        """Test handler is called when rate limit not exceeded."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(
            return_value=f'{{"start_time": {start_time}, "count": 2}}'.encode()
        )
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)

        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should be called
            self.mock_handler.assert_called_once()
            assert result == "handler_result"

    async def test_rate_limit_exceeded(self):
        """Test throttling when rate limit exceeded."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(
            return_value=f'{{"start_time": {start_time}, "count": 5}}'.encode()
        )

        middleware = ThrottlingMiddleware(redis_client=mock_redis)

        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None
        mock_event.answer = AsyncMock()

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should NOT be called
            self.mock_handler.assert_not_called()

            # Event.answer should be called with throttling message
            mock_event.answer.assert_called_once()
            call_args = mock_event.answer.call_args
            assert "Too many requests" in call_args[0][0]

            # Result should be None
            assert result is None

    async def test_no_user_in_event(self):
        """Test handling when event has no user."""
        mock_redis = MagicMock()

        middleware = ThrottlingMiddleware(redis_client=mock_redis)

        mock_event = MagicMock()
        mock_event.message = None
        mock_event.callback_query = None

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should be called even without user
            self.mock_handler.assert_called_once()
            assert result == "handler_result"

    async def test_no_redis_allows_all(self):
        """Test that requests pass through when Redis is not connected."""
        middleware = ThrottlingMiddleware()

        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should be called
            self.mock_handler.assert_called_once()
            assert result == "handler_result"

    async def test_custom_rate_limit(self):
        """Test custom rate limit from flag."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(
            return_value=f'{{"start_time": {start_time}, "count": 3}}'.encode()
        )
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)

        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 10, "period": 120}

            await middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should be called because 3 < 10
            self.mock_handler.assert_called_once()

    async def test_event_without_answer_method(self):
        """Test throttling when event has no answer method."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(
            return_value=f'{{"start_time": {start_time}, "count": 5}}'.encode()
        )

        middleware = ThrottlingMiddleware(redis_client=mock_redis)

        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None
        # Remove answer method
        del mock_event.answer

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            # Should not raise AttributeError
            result = await middleware.__call__(self.mock_handler, mock_event, data)

            # Handler not called, but no answer sent
            self.mock_handler.assert_not_called()
            assert result is None

    async def test_callback_query_user_extraction(self):
        """Test extracting user from callback_query - line 117."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(
            return_value=f'{{"start_time": {start_time}, "count": 5}}'.encode()
        )

        middleware = ThrottlingMiddleware(redis_client=mock_redis)

        mock_event = MagicMock()
        mock_event.message = None
        mock_event.callback_query = MagicMock()
        mock_event.callback_query.from_user = MagicMock()
        mock_event.callback_query.from_user.id = 123456
        mock_event.answer = AsyncMock()

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            await middleware.__call__(self.mock_handler, mock_event, data)

            # User should be extracted from callback_query and throttled
            self.mock_handler.assert_not_called()
            mock_event.answer.assert_called_once()


class TestThrottlingService:
    """Test cases for ThrottlingService."""

    def test_init(self):
        """Test ThrottlingService initialization."""
        service = ThrottlingService()
        assert service.redis is None

    @patch("telegram_bot.middlewares.throttling.Redis")
    async def test_connect(self, mock_redis_class):
        """Test Redis connection."""
        mock_redis = MagicMock()
        mock_redis_class.from_url = Mock(return_value=mock_redis)

        service = ThrottlingService()
        await service.connect()

        assert service.redis == mock_redis
        mock_redis_class.from_url.assert_called_once()

    @patch("telegram_bot.middlewares.throttling.Redis")
    async def test_connect_already_connected(self, mock_redis_class):
        """Test connect when already connected."""
        mock_redis = MagicMock()

        service = ThrottlingService()
        service.redis = mock_redis

        await service.connect()

        # Should not create new connection
        mock_redis_class.from_url.assert_not_called()

    async def test_disconnect(self):
        """Test Redis disconnection."""
        mock_redis = MagicMock()
        mock_redis.aclose = AsyncMock()

        service = ThrottlingService()
        service.redis = mock_redis

        await service.disconnect()

        mock_redis.aclose.assert_called_once()
        assert service.redis is None

    async def test_disconnect_no_redis(self):
        """Test disconnect when Redis is not connected."""
        service = ThrottlingService()

        # Should not raise
        await service.disconnect()

        assert service.redis is None

    @patch("telegram_bot.middlewares.throttling.Redis")
    async def test_create_middleware(self, mock_redis_class):
        """Test middleware creation."""
        mock_redis = MagicMock()
        mock_redis_class.from_url = Mock(return_value=mock_redis)

        service = ThrottlingService()
        await service.connect()

        middleware = service.create_middleware()

        assert middleware.redis == mock_redis


class TestThrottlingIntegration:
    """Integration tests for throttling middleware."""

    async def test_multiple_users_tracked_separately(self):
        """Test that different users are tracked separately."""
        from datetime import UTC, datetime

        mock_redis = MagicMock()
        now = datetime.now(UTC).timestamp()

        # Simulate user 1 at limit, user 2 not
        async def mock_get(key):
            key_str = key.decode() if isinstance(key, bytes) else key
            if ":1" in key_str:
                # User 1 at limit (recent timestamp)
                return f'{{"start_time": {now}, "count": 5}}'.encode()
            # User 2 not at limit
            return f'{{"start_time": {now}, "count": 1}}'.encode()

        mock_redis.get = mock_get
        mock_redis.set = AsyncMock(return_value=True)

        middleware = ThrottlingMiddleware(redis_client=mock_redis)
        mock_handler = AsyncMock(return_value="result")

        # Create events for different users
        event_user1 = MagicMock()
        event_user1.message = MagicMock()
        event_user1.message.from_user = MagicMock()
        event_user1.message.from_user.id = 1
        event_user1.callback_query = None
        event_user1.answer = AsyncMock()

        event_user2 = MagicMock()
        event_user2.message = MagicMock()
        event_user2.message.from_user = MagicMock()
        event_user2.message.from_user.id = 2
        event_user2.callback_query = None

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            # User 1 should be throttled
            result1 = await middleware.__call__(mock_handler, event_user1, {})
            assert result1 is None
            mock_handler.assert_not_called()

            # Reset mock for user 2
            mock_handler.reset_mock()

            # User 2 should not be throttled
            result2 = await middleware.__call__(mock_handler, event_user2, {})
            assert result2 == "result"


class TestThrottlingServiceGlobalInstance:
    """Test global throttling_service instance."""

    def test_global_instance_exists(self):
        """Test that global throttling_service instance exists."""
        assert isinstance(throttling_service, ThrottlingService)
