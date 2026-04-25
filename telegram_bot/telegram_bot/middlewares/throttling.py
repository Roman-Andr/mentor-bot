"""Throttling middleware to limit user requests using Redis."""

import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import RedisError

from telegram_bot.config import settings


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to throttle user requests using Redis for distributed rate limiting."""

    def __init__(self, redis_client: Redis | None = None) -> None:
        """Initialize throttling middleware with Redis connection."""
        super().__init__()
        self.redis = redis_client
        self._default_calls = 5
        self._default_period = 60
        self._key_prefix = "throttle"

    def _make_key(self, user_id: int) -> str:
        """Generate Redis key for rate limit tracking."""
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
            logger.warning("Failed to get rate limit data (user_id={})", user_id)
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
            logger.warning("Failed to set rate limit data (user_id={})", user_id)
            return False

    async def _is_rate_limited(
        self, user_id: int, calls: int, period: int
    ) -> tuple[bool, int]:
        """Check if user is rate limited. Returns (is_limited, remaining_calls)."""
        if not self.redis:
            return False, calls

        now = datetime.now(UTC).timestamp()

        data = await self._get_rate_limit_data(user_id)

        if data is None:
            # First call in this window
            await self._set_rate_limit_data(
                user_id, {"start_time": now, "count": 1}, period
            )
            return False, calls - 1

        start_time = data.get("start_time", now)
        count = data.get("count", 0)

        # Check if window has expired
        if now - start_time >= period:
            # Reset window
            await self._set_rate_limit_data(
                user_id, {"start_time": now, "count": 1}, period
            )
            return False, calls - 1

        # Within window, check count
        if count >= calls:
            return True, 0

        # Increment count
        await self._set_rate_limit_data(
            user_id, {"start_time": start_time, "count": count + 1}, period
        )
        return False, calls - count - 1

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> object:
        """Process update with throttling."""
        rate_limit = get_flag(data, "rate_limit")
        if rate_limit is None:
            rate_limit = {"calls": self._default_calls, "period": self._default_period}

        tg_user = None
        if event.message:
            tg_user = event.message.from_user
        elif event.callback_query:
            tg_user = event.callback_query.from_user

        if tg_user and self.redis:
            user_id = tg_user.id
            calls = rate_limit.get("calls", self._default_calls)
            period = rate_limit.get("period", self._default_period)

            is_limited, remaining = await self._is_rate_limited(user_id, calls, period)

            if is_limited:
                logger.warning("Rate limit exceeded (user_id={})", user_id)
                if hasattr(event, "answer"):
                    await event.answer(
                        "Too many requests. Please wait a moment.", show_alert=True
                    )
                return None

        return await handler(event, data)


class ThrottlingService:
    """Service to manage throttling with shared Redis connection."""

    def __init__(self) -> None:
        """Initialize throttling service."""
        self.redis: Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        logger.info("Connecting to Redis for throttling")
        if not self.redis:
            self.redis = Redis.from_url(str(settings.REDIS_URL))

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        logger.info("Disconnecting from Redis for throttling")
        if self.redis:
            await self.redis.aclose()
            self.redis = None

    def create_middleware(self) -> ThrottlingMiddleware:
        """Create throttling middleware with shared Redis connection."""
        return ThrottlingMiddleware(redis_client=self.redis)


# Global throttling service instance
throttling_service = ThrottlingService()
