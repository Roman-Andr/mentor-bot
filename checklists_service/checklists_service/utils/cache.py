"""Cache utilities for Redis."""

import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import redis.asyncio as redis

from checklists_service.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager."""

    def __init__(self) -> None:
        """Initialize cache manager without immediate connection."""
        self.redis_client = None
        self.is_connected = False

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                str(settings.REDIS_URL),
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("Redis cache connected")
        except Exception as e:
            logger.warning(f"Redis cache not available: {e}")
            self.is_connected = False

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self.is_connected:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.exception(f"Cache get error: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with TTL."""
        if not self.is_connected:
            return

        try:
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str),
            )
        except Exception as e:
            logger.exception(f"Cache set error: {e}")

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if not self.is_connected:
            return

        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.exception(f"Cache delete error: {e}")

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        if not self.is_connected:
            return

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
        except Exception as e:
            logger.exception(f"Cache delete pattern error: {e}")


# Global cache instance
cache = CacheManager()
T = TypeVar("T", bound=Callable[..., Any])


def cached(ttl: int = 300, key_prefix: str = "cache") -> Callable[[T], T]:
    """Decorate for caching function results."""

    def decorator(func: T) -> T:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{args!s}:{kwargs!s}"

            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
