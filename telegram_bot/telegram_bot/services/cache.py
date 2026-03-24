"""User-specific cache for authentication data."""

import pickle
from datetime import timedelta
from typing import Any

from redis import RedisError
from redis.asyncio import Redis

from telegram_bot.config import settings


class UserCache:
    """Cache for user authentication and session data."""

    def __init__(self, redis_client: Redis | None = None) -> None:
        """Initialize user cache."""
        self.redis = redis_client
        self._is_connected = False
        self.ttl = timedelta(seconds=settings.REDIS_CACHE_TTL)

    async def connect(self) -> None:
        """Connect to Redis."""
        if not self._is_connected:
            if not self.redis:
                self.redis = Redis.from_url(str(settings.REDIS_URL))
            self._is_connected = True

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self._is_connected = False

    def _user_key(self, telegram_id: int) -> str:
        """Generate cache key for user."""
        return f"user:{telegram_id}"

    def _user_session_key(self, telegram_id: int) -> str:
        """Generate cache key for user session."""
        return f"user_session:{telegram_id}"

    async def get_user(self, telegram_id: int) -> dict[str, Any] | None:
        """Get user data from cache."""
        if not self._is_connected:
            return None

        try:
            data = await self.redis.get(self._user_key(telegram_id))
            if data:
                return pickle.loads(data)
        except pickle.UnpicklingError, RedisError:
            return None
        return None

    async def set_user(
        self,
        telegram_id: int,
        user_data: dict[str, Any],
        ttl: timedelta | None = None,
    ) -> bool:
        """Set user data in cache."""
        if not self._is_connected:
            return False

        try:
            ttl_seconds = (ttl or self.ttl).total_seconds()
            await self.redis.set(
                self._user_key(telegram_id),
                pickle.dumps(user_data),
                ex=int(ttl_seconds),
            )
        except RedisError:
            return False
        else:
            return True

    async def delete_user(self, telegram_id: int) -> bool:
        """Delete user data from cache."""
        if not self._is_connected:
            return False

        try:
            await self.redis.delete(
                self._user_key(telegram_id),
                self._user_session_key(telegram_id),
            )
        except RedisError:
            return False
        else:
            return True

    async def get_session(self, telegram_id: int) -> dict[str, Any] | None:
        """Get user session data."""
        if not self._is_connected:
            return None

        try:
            data = await self.redis.get(self._user_session_key(telegram_id))
            if data:
                return pickle.loads(data)
        except pickle.UnpicklingError, RedisError:
            return None
        return None

    async def set_session(
        self,
        telegram_id: int,
        session_data: dict[str, Any],
        ttl: timedelta | None = None,
    ) -> bool:
        """Set user session data."""
        if not self._is_connected:
            return False

        try:
            ttl_seconds = (ttl or self.ttl).total_seconds()
            await self.redis.set(
                self._user_session_key(telegram_id),
                pickle.dumps(session_data),
                ex=int(ttl_seconds),
            )
        except RedisError:
            return False
        else:
            return True

    async def update_user_field(
        self,
        telegram_id: int,
        field: str,
        value: object,
    ) -> bool:
        """Update specific field in user data."""
        user_data = await self.get_user(telegram_id)
        if user_data:
            user_data[field] = value
            return await self.set_user(telegram_id, user_data)
        return False

    async def get_all_users(self) -> dict[int, dict[str, Any]]:
        """Get all cached users (for admin purposes)."""
        if not self._is_connected:
            return {}

        try:
            users = {}
            async for key in self.redis.scan_iter(match="user:*"):
                try:
                    data = await self.redis.get(key)
                    if data:
                        # Extract telegram_id from key
                        telegram_id = int(key.decode().split(":")[1])
                        users[telegram_id] = pickle.loads(data)
                except pickle.UnpicklingError, RedisError, ValueError:
                    continue
        except RedisError:
            return {}
        else:
            return users

    async def cleanup_expired(self) -> int:
        """Cleanup expired sessions (Redis handles TTL automatically)."""
        return 0  # Redis auto-expires keys with TTL


# Global user cache instance
user_cache = UserCache()
