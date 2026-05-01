"""Unit tests for telegram_bot/utils/file_rate_limiter.py."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from aiogram.types import Message, User
from telegram_bot.utils.file_rate_limiter import (
    FileUploadRateLimiter,
    check_file_upload_rate_limit,
    connect_rate_limiter,
    disconnect_rate_limiter,
    file_rate_limiter,
    file_upload_rate_limit,
)


class TestFileUploadRateLimiterInit:
    """Test cases for FileUploadRateLimiter initialization."""

    def test_init_with_redis_client(self):
        """Test that initialization accepts Redis client."""
        mock_redis = MagicMock()
        limiter = FileUploadRateLimiter(redis_client=mock_redis)

        assert limiter.redis == mock_redis
        assert limiter._key_prefix == "file_upload"

    def test_init_without_redis_client(self):
        """Test that initialization works without Redis client."""
        limiter = FileUploadRateLimiter()

        assert limiter.redis is None


class TestFileUploadRateLimiterMakeKey:
    """Test cases for _make_key method."""

    def test_make_key(self):
        """Test key generation."""
        limiter = FileUploadRateLimiter()
        key = limiter._make_key(123456)

        assert key == "file_upload:123456"


class TestFileUploadRateLimiterGetSetData:
    """Test cases for Redis data operations."""

    async def test_get_rate_limit_data_success(self):
        """Test successful retrieval of rate limit data."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=b'{"start_time": 12345, "count": 3}')

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        data = await limiter._get_rate_limit_data(123456)

        assert data == {"start_time": 12345, "count": 3}
        mock_redis.get.assert_called_once_with("file_upload:123456")

    async def test_get_rate_limit_data_no_data(self):
        """Test retrieval when no data exists."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=None)

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        data = await limiter._get_rate_limit_data(123456)

        assert data is None

    async def test_get_rate_limit_data_redis_error(self):
        """Test handling of Redis error during get."""
        from redis.exceptions import RedisError

        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(side_effect=RedisError("Connection failed"))

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        data = await limiter._get_rate_limit_data(123456)

        assert data is None

    async def test_get_rate_limit_data_no_redis(self):
        """Test get when Redis is not connected."""
        limiter = FileUploadRateLimiter()
        data = await limiter._get_rate_limit_data(123456)

        assert data is None

    async def test_set_rate_limit_data_success(self):
        """Test successful storage of rate limit data."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock(return_value=True)

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        result = await limiter._set_rate_limit_data(123456, {"start_time": 12345, "count": 3}, 3600)

        assert result is True
        mock_redis.set.assert_called_once()

    async def test_set_rate_limit_data_redis_error(self):
        """Test handling of Redis error during set."""
        from redis.exceptions import RedisError

        mock_redis = MagicMock()
        mock_redis.set = AsyncMock(side_effect=RedisError("Connection failed"))

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        result = await limiter._set_rate_limit_data(123456, {"start_time": 12345, "count": 3}, 3600)

        assert result is False

    async def test_set_rate_limit_data_no_redis(self):
        """Test set when Redis is not connected."""
        limiter = FileUploadRateLimiter()
        result = await limiter._set_rate_limit_data(123456, {"start_time": 12345, "count": 3}, 3600)

        assert result is False


class TestFileUploadRateLimiterIsRateLimited:
    """Test cases for is_rate_limited method."""

    async def test_first_call_creates_entry(self):
        """Test first upload creates rate limit entry."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        is_limited, remaining, retry_after = await limiter.is_rate_limited(123456, calls=10, period=3600)

        assert is_limited is False
        assert remaining == 9
        assert retry_after == 0
        mock_redis.set.assert_called_once()

    async def test_within_limit_increments_count(self):
        """Test upload within limit increments count."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(return_value=f'{{"start_time": {start_time}, "count": 2}}'.encode())
        mock_redis.set = AsyncMock(return_value=True)

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        is_limited, remaining, retry_after = await limiter.is_rate_limited(123456, calls=10, period=3600)

        assert is_limited is False
        assert remaining == 7
        assert retry_after == 0

    async def test_limit_exceeded(self):
        """Test when rate limit is exceeded."""
        mock_redis = MagicMock()
        start_time = datetime.now(UTC).timestamp()
        mock_redis.get = AsyncMock(return_value=f'{{"start_time": {start_time}, "count": 10}}'.encode())

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        is_limited, remaining, retry_after = await limiter.is_rate_limited(123456, calls=10, period=3600)

        assert is_limited is True
        assert remaining == 0
        assert retry_after > 0

    async def test_window_expired_resets(self):
        """Test that expired window resets counter."""
        mock_redis = MagicMock()
        old_start_time = datetime.now(UTC).timestamp() - 3700  # 3700 seconds ago
        mock_redis.get = AsyncMock(return_value=f'{{"start_time": {old_start_time}, "count": 10}}'.encode())
        mock_redis.set = AsyncMock(return_value=True)

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        is_limited, remaining, retry_after = await limiter.is_rate_limited(123456, calls=10, period=3600)

        assert is_limited is False
        assert remaining == 9
        assert retry_after == 0

    async def test_redis_error_fails_open(self):
        """Test that Redis errors fail open (allow request)."""
        from redis.exceptions import RedisError

        mock_redis = MagicMock()
        # Simulate Redis failure - get returns None (handled internally), set succeeds
        mock_redis.get = AsyncMock(side_effect=RedisError("Connection failed"))
        mock_redis.set = AsyncMock(return_value=True)

        limiter = FileUploadRateLimiter(redis_client=mock_redis)
        is_limited, remaining, retry_after = await limiter.is_rate_limited(123456, calls=10, period=3600)

        # Should allow request (fail open)
        # _get_rate_limit_data catches RedisError and returns None (lines 42-43)
        # Then code treats it as first call (line 76-81) and returns calls - 1
        assert is_limited is False
        assert retry_after == 0
        assert remaining == 9

    async def test_is_rate_limited_no_redis(self):
        """Test is_rate_limited when Redis is not connected - line 69."""
        limiter = FileUploadRateLimiter()  # No redis client
        is_limited, remaining, retry_after = await limiter.is_rate_limited(123456, calls=10, period=3600)

        # Should fail open with full calls remaining (line 69)
        assert is_limited is False
        assert remaining == 10
        assert retry_after == 0


class TestCheckFileUploadRateLimit:
    """Test cases for check_file_upload_rate_limit function."""

    async def test_with_valid_user(self):
        """Test checking rate limit with valid user."""
        mock_message = MagicMock(spec=Message)
        mock_user = MagicMock(spec=User)
        mock_user.id = 123456
        mock_message.from_user = mock_user

        with patch.object(file_rate_limiter, "is_rate_limited", new_callable=AsyncMock) as mock_is_limited:
            mock_is_limited.return_value = (False, 9, 0)

            is_limited, retry_after = await check_file_upload_rate_limit(
                mock_message, max_uploads=10, window_seconds=3600
            )

            assert is_limited is False
            assert retry_after == 0
            mock_is_limited.assert_called_once_with(123456, calls=10, period=3600)

    async def test_without_user(self):
        """Test checking rate limit without user."""
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = None

        is_limited, retry_after = await check_file_upload_rate_limit(mock_message)

        assert is_limited is False
        assert retry_after == 0


class TestFileUploadRateLimitDecorator:
    """Test cases for file_upload_rate_limit decorator."""

    async def test_decorator_allows_request_when_not_limited(self):
        """Test that decorator allows request when not rate limited."""
        mock_handler = AsyncMock(return_value="handler_result")

        # Create properly mocked message
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = MagicMock()
        mock_message.from_user.id = 123456
        mock_message.answer = AsyncMock()

        decorated = file_upload_rate_limit(max_uploads=10, window_seconds=3600)(mock_handler)

        with patch.object(file_rate_limiter, "is_rate_limited", new_callable=AsyncMock) as mock_is_limited:
            mock_is_limited.return_value = (False, 9, 0)

            result = await decorated(mock_message, locale="en")

            assert result == "handler_result"
            mock_handler.assert_called_once()

    async def test_decorator_blocks_request_when_limited(self):
        """Test that decorator blocks request when rate limited."""
        mock_handler = AsyncMock(return_value="handler_result")

        mock_message = MagicMock(spec=Message)
        mock_message.from_user = MagicMock()
        mock_message.from_user.id = 123456
        mock_message.answer = AsyncMock()

        decorated = file_upload_rate_limit(max_uploads=10, window_seconds=3600)(mock_handler)

        with patch.object(file_rate_limiter, "is_rate_limited", new_callable=AsyncMock) as mock_is_limited:
            mock_is_limited.return_value = (True, 0, 300)

            result = await decorated(mock_message, locale="en")

            assert result is None
            mock_handler.assert_not_called()
            mock_message.answer.assert_called_once()

    async def test_decorator_blocks_with_seconds_remaining(self):
        """Test decorator blocks with seconds message when retry_after < 60 - line 184."""
        mock_handler = AsyncMock(return_value="handler_result")

        mock_message = MagicMock(spec=Message)
        mock_message.from_user = MagicMock()
        mock_message.from_user.id = 123456
        mock_message.answer = AsyncMock()

        decorated = file_upload_rate_limit(max_uploads=10, window_seconds=3600)(mock_handler)

        with patch.object(file_rate_limiter, "is_rate_limited", new_callable=AsyncMock) as mock_is_limited:
            # retry_after less than 60 seconds should trigger seconds message
            mock_is_limited.return_value = (True, 0, 45)  # 45 seconds

            result = await decorated(mock_message, locale="en")

            assert result is None
            mock_handler.assert_not_called()
            mock_message.answer.assert_called_once()
            # Check that seconds-based message was sent
            call_args = mock_message.answer.call_args[0][0]
            # Should reference seconds, not minutes
            assert "second" in call_args.lower() or "45" in call_args

    async def test_decorator_with_message_in_kwargs(self):
        """Test decorator finding message in kwargs."""
        mock_handler = AsyncMock(return_value="handler_result")

        mock_message = MagicMock(spec=Message)
        mock_message.from_user = MagicMock()
        mock_message.from_user.id = 123456
        mock_message.answer = AsyncMock()

        decorated = file_upload_rate_limit(max_uploads=10, window_seconds=3600)(mock_handler)

        with patch.object(file_rate_limiter, "is_rate_limited", new_callable=AsyncMock) as mock_is_limited:
            mock_is_limited.return_value = (False, 9, 0)

            result = await decorated(some_arg="test", message=mock_message, locale="en")

            assert result == "handler_result"
            mock_handler.assert_called_once()

    async def test_decorator_without_user(self):
        """Test decorator when message has no user."""
        mock_handler = AsyncMock(return_value="handler_result")

        mock_message = MagicMock(spec=Message)
        mock_message.from_user = None

        decorated = file_upload_rate_limit(max_uploads=10, window_seconds=3600)(mock_handler)

        result = await decorated(mock_message, locale="en")

        # Should allow request when no user (fail open)
        assert result == "handler_result"
        mock_handler.assert_called_once()


class TestConnectDisconnectRateLimiter:
    """Test cases for connect_rate_limiter and disconnect_rate_limiter."""

    @patch("telegram_bot.utils.file_rate_limiter.Redis")
    async def test_connect_rate_limiter(self, mock_redis_class):
        """Test connecting rate limiter to Redis."""
        mock_redis = MagicMock()
        mock_redis_class.from_url = Mock(return_value=mock_redis)

        await connect_rate_limiter()

        assert file_rate_limiter.redis == mock_redis
        mock_redis_class.from_url.assert_called_once()

    async def test_disconnect_rate_limiter(self):
        """Test disconnecting rate limiter from Redis."""
        mock_redis = MagicMock()
        mock_redis.aclose = AsyncMock()
        file_rate_limiter.redis = mock_redis

        await disconnect_rate_limiter()

        mock_redis.aclose.assert_called_once()
        assert file_rate_limiter.redis is None

    async def test_disconnect_without_connection(self):
        """Test disconnect when not connected."""
        # Reset the global instance
        file_rate_limiter.redis = None

        # Should not raise
        await disconnect_rate_limiter()

        assert file_rate_limiter.redis is None


class TestFileRateLimiterGlobalInstance:
    """Test global file_rate_limiter instance."""

    def test_global_instance_exists(self):
        """Test that global file_rate_limiter instance exists."""
        assert isinstance(file_rate_limiter, FileUploadRateLimiter)
