"""Cache utilities for Redis."""

import json
import logging
from collections.abc import Callable
from functools import wraps
from json import JSONDecodeError
from typing import TypeVar

import redis.asyncio as redis
from redis import RedisError

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
        except RedisError as e:
            logger.warning("Redis cache not available: %s", e)
            self.is_connected = False

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False

    async def get(self, key: str) -> object | None:
        """Get value from cache."""
        if not self.is_connected:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
        except (RedisError, JSONDecodeError):
            logger.exception("Cache get error")
        return None

    async def set(self, key: str, value: object, ttl: int = 3600) -> None:
        """Set value in cache with TTL."""
        if not self.is_connected:
            return

        try:
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str),
            )
        except RedisError:
            logger.exception("Cache set error")

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if not self.is_connected:
            return

        try:
            await self.redis_client.delete(key)
        except RedisError:
            logger.exception("Cache delete error")

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        if not self.is_connected:
            return

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
        except RedisError:
            logger.exception("Cache delete pattern error")


# Global cache instance
cache = CacheManager()
T = TypeVar("T", bound=Callable[..., object])


def cached(ttl: int = 300, key_prefix: str = "cache") -> Callable[[T], T]:
    """Decorate for caching function results."""

    def decorator(func: T) -> T:
        @wraps(func)
        async def wrapper(*args: object, **kwargs: object) -> object:
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
