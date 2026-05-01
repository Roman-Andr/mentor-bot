"""Cache utilities using Redis with decorator support."""

import hashlib
import pickle
from collections.abc import Awaitable, Callable
from datetime import timedelta
from functools import wraps
from typing import TypeVar

from redis import RedisError
from redis.asyncio import Redis

from telegram_bot.config import settings

T = TypeVar("T")


class RedisCache:
    """Redis-based cache with async operations."""

    def __init__(self, redis_client: Redis | None = None) -> None:
        """Initialize Redis cache."""
        self.redis = redis_client
        self._is_connected = False

    async def connect(self) -> None:
        """Connect to Redis if not already connected."""
        if not self._is_connected:
            if not self.redis:
                self.redis = Redis.from_url(str(settings.REDIS_URL))
            self._is_connected = True

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self._is_connected = False

    def _make_key(self, prefix: str, *args: object, **kwargs: object) -> str:
        """Generate cache key from function arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]

        # Add kwargs (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")

        key_string = ":".join(key_parts)
        # Hash long keys (Redis recommends keeping keys under 1KB for performance)
        MAX_KEY_LENGTH = 250
        if len(key_string) > MAX_KEY_LENGTH:
            key_string = f"{prefix}:{hashlib.sha256(key_string.encode()).hexdigest()}"

        return key_string

    async def get(self, key: str) -> object:
        """Get value from cache."""
        if not self._is_connected:
            return None

        try:
            data = await self.redis.get(key)
            if data:
                return pickle.loads(data)
        except (pickle.UnpicklingError, RedisError):
            return None
        return None

    async def set(self, key: str, value: object, ttl: int | timedelta | None = None) -> bool:
        """Set value in cache with TTL."""
        if not self._is_connected:
            return False

        try:
            if ttl is None:
                ttl = settings.REDIS_CACHE_TTL

            ttl_seconds = ttl.total_seconds() if isinstance(ttl, timedelta) else ttl

            await self.redis.set(
                key,
                pickle.dumps(value),
                ex=int(ttl_seconds) if ttl_seconds > 0 else None,
            )
        except RedisError:
            return False
        else:
            return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._is_connected:
            return False

        try:
            result = await self.redis.delete(key)
        except RedisError:
            return False
        else:
            return result > 0

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        if not self._is_connected:
            return 0

        try:
            keys = [key async for key in self.redis.scan_iter(match=pattern)]
        except RedisError:
            return 0
        else:
            if keys:
                return await self.redis.delete(*keys)
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._is_connected:
            return False

        try:
            return await self.redis.exists(key) == 1
        except RedisError:
            return False

    async def flush(self) -> bool:
        """Clear all cache entries."""
        if not self._is_connected:
            return False

        try:
            await self.redis.flushdb()
        except RedisError:
            return False
        else:
            return True


# Global cache instance
cache = RedisCache()


def cached(
    ttl: int | timedelta = 300,
    key_prefix: str = "",
    ignore_args: list[str] | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Cache async function results decorator."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: object, **kwargs: object) -> T:
            # Create cache key
            cache_kwargs = kwargs.copy()
            if ignore_args:
                for arg in ignore_args:
                    cache_kwargs.pop(arg, None)

            key = cache._make_key(  # noqa: SLF001
                f"{key_prefix}:{func.__module__}:{func.__name__}",
                *args,
                **cache_kwargs,
            )

            # Try to get from cache
            cached_result = await cache.get(key)
            if cached_result is not None:
                return cached_result

            # Call function if not in cache
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None:
                await cache.set(key, result, ttl)

            return result

        return wrapper

    return decorator


async def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching pattern."""
    return await cache.delete_pattern(pattern)


async def get_or_set[T](
    key: str,
    coro_func: Callable[[], Awaitable[T]],
    ttl: int | timedelta = 300,
) -> T:
    """Get value from cache or set it using coroutine."""
    cached_value = await cache.get(key)
    if cached_value is not None:
        return cached_value

    value = await coro_func()
    if value is not None:
        await cache.set(key, value, ttl)

    return value
