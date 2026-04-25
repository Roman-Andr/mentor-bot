"""File upload rate limiting using Redis."""

import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from functools import wraps
from typing import Any, TypeVar

from aiogram.types import Message
from redis.asyncio import Redis
from redis.exceptions import RedisError

from telegram_bot.config import settings

T = TypeVar("T")

# Default rate limits for file uploads
DEFAULT_UPLOAD_CALLS = 10  # Max uploads per period
DEFAULT_UPLOAD_PERIOD = 3600  # 1 hour window


class FileUploadRateLimiter:
    """Rate limiter specifically for file uploads using Redis."""

    def __init__(self, redis_client: Redis | None = None) -> None:
        """Initialize file upload rate limiter with Redis connection."""
        self.redis = redis_client
        self._key_prefix = "file_upload"

    def _make_key(self, user_id: int) -> str:
        """Generate Redis key for file upload rate limit tracking."""
        return f"{self._key_prefix}:{user_id}"

    async def _get_rate_limit_data(self, user_id: int) -> dict[str, Any] | None:
        """Get rate limit data from Redis."""
        if not self.redis:
            return None
        try:
            data = await self.redis.get(self._make_key(user_id))
            if data:
                return json.loads(data)
        except (RedisError, json.JSONDecodeError):
            return None
        return None

    async def _set_rate_limit_data(
        self, user_id: int, data: dict[str, Any], ttl: int
    ) -> bool:
        """Set rate limit data in Redis with TTL."""
        if not self.redis:
            return False
        try:
            await self.redis.set(
                self._make_key(user_id), json.dumps(data), ex=max(ttl, 1)
            )
            return True
        except RedisError:
            return False

    async def is_rate_limited(
        self, user_id: int, calls: int = DEFAULT_UPLOAD_CALLS, period: int = DEFAULT_UPLOAD_PERIOD
    ) -> tuple[bool, int, int]:
        """Check if user is rate limited for file uploads.

        Returns:
            tuple of (is_limited, remaining_calls, retry_after_seconds)

        """
        if not self.redis:
            return False, calls, 0

        now = datetime.now(UTC).timestamp()

        data = await self._get_rate_limit_data(user_id)

        if data is None:
            # First upload in this window
            await self._set_rate_limit_data(
                user_id, {"start_time": now, "count": 1}, period
            )
            return False, calls - 1, 0

        start_time = data.get("start_time", now)
        count = data.get("count", 0)
        elapsed = int(now - start_time)

        # Check if window has expired
        if elapsed >= period:
            # Reset window
            await self._set_rate_limit_data(
                user_id, {"start_time": now, "count": 1}, period
            )
            return False, calls - 1, 0

        # Within window, check count
        if count >= calls:
            retry_after = period - elapsed
            return True, 0, retry_after

        # Increment count
        await self._set_rate_limit_data(
            user_id, {"start_time": start_time, "count": count + 1}, period - elapsed
        )
        return False, calls - count - 1, 0


# Global rate limiter instance
file_rate_limiter = FileUploadRateLimiter()


async def check_file_upload_rate_limit(
    message: Message,
    max_uploads: int = DEFAULT_UPLOAD_CALLS,
    window_seconds: int = DEFAULT_UPLOAD_PERIOD,
) -> tuple[bool, int]:
    """Check if user has exceeded file upload rate limit.

    Args:
        message: The message containing the file upload
        max_uploads: Maximum number of uploads allowed in the window
        window_seconds: Time window in seconds

    Returns:
        tuple of (is_limited, retry_after_seconds)

    """
    if not message.from_user:
        return False, 0

    user_id = message.from_user.id
    is_limited, _, retry_after = await file_rate_limiter.is_rate_limited(
        user_id, calls=max_uploads, period=window_seconds
    )
    return is_limited, retry_after


def file_upload_rate_limit(
    max_uploads: int = DEFAULT_UPLOAD_CALLS,
    window_seconds: int = DEFAULT_UPLOAD_PERIOD,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Apply file upload rate limiting to a handler.

    Args:
        max_uploads: Maximum number of uploads allowed in the window
        window_seconds: Time window in seconds

    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T | None:
            # Find message in args or kwargs
            message = None
            for arg in args:
                if isinstance(arg, Message):
                    message = arg
                    break

            if not message:
                message = kwargs.get("message")

            # Try to check rate limit, but fail open on any errors (e.g., test mocks)
            try:
                if message and message.from_user:
                    is_limited, retry_after = await check_file_upload_rate_limit(
                        message, max_uploads, window_seconds
                    )

                    if is_limited:
                        # Rate limit exceeded - send error message
                        from telegram_bot.i18n import t

                        locale = kwargs.get("locale", "en")
                        minutes = retry_after // 60
                        if minutes > 0:
                            error_msg = t(
                                "tasks.upload_rate_limited_minutes",
                                locale=locale,
                                minutes=minutes,
                            )
                        else:
                            error_msg = t(
                                "tasks.upload_rate_limited_seconds",
                                locale=locale,
                                seconds=retry_after,
                            )
                        await message.answer(error_msg)
                        return None
            except Exception:
                # Fail open on any error (e.g., test mocks, Redis errors)
                pass

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def connect_rate_limiter() -> None:
    """Connect rate limiter to Redis."""
    if not file_rate_limiter.redis:
        file_rate_limiter.redis = Redis.from_url(str(settings.REDIS_URL))


async def disconnect_rate_limiter() -> None:
    """Disconnect rate limiter from Redis."""
    if file_rate_limiter.redis:
        await file_rate_limiter.redis.aclose()
        file_rate_limiter.redis = None
