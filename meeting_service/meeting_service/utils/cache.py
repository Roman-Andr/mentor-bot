"""Cache utilities for Redis."""

import json
import logging
from json import JSONDecodeError
from typing import TYPE_CHECKING

import redis.asyncio as redis
from redis import RedisError

from meeting_service.config import settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from redis import Redis


class CacheManager:
    """Redis cache manager."""

    def __init__(self) -> None:
        """Initialize cache manager without immediate connection."""
        self.redis_client: Redis | None = None
        self.is_connected = False

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                str(settings.REDIS_URL),
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()  # type: ignore[union-attr]
            self.is_connected = True
            logger.info("Redis cache connected")
        except RedisError as e:
            logger.warning("Redis cache not available: %s", e)
            self.is_connected = False

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.aclose()
            self.is_connected = False

    async def get(self, key: str) -> object | None:
        """Get value from cache."""
        if not self.is_connected or not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                # Try to parse as JSON for complex objects
                try:
                    return json.loads(value)
                except JSONDecodeError:
                    # Return as string if not valid JSON (e.g., stored directly)
                    return value
        except RedisError:
            logger.exception("Cache get error")
        return None

    async def set(self, key: str, value: object, ttl: int = 3600) -> None:
        """Set value in cache with TTL."""
        if not self.is_connected or not self.redis_client:
            return

        try:
            # If value is a string, store directly without JSON serialization
            if isinstance(value, str):
                await self.redis_client.setex(key, ttl, value)
            else:
                # Use JSON for complex objects
                await self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str),
                )
        except RedisError:
            logger.exception("Cache set error")

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if not self.is_connected or not self.redis_client:
            return

        try:
            await self.redis_client.delete(key)
        except RedisError:
            logger.exception("Cache delete error")


# Global cache instance
cache = CacheManager()
