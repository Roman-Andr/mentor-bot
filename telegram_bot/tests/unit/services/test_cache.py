"""Unit tests for telegram_bot/services/cache.py."""

import pickle
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis import RedisError
from telegram_bot.services.cache import UserCache, user_cache


class TestUserCache:
    """Test cases for UserCache."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        redis = MagicMock()
        redis.close = AsyncMock()
        redis.get = AsyncMock()
        redis.set = AsyncMock()
        redis.delete = AsyncMock()
        redis.scan_iter = MagicMock()
        return redis

    @pytest.fixture
    def cache(self, mock_redis):
        """Create a UserCache with mock Redis."""
        return UserCache(redis_client=mock_redis)

    async def test_connect(self, cache, mock_redis):
        """Test connecting to Redis."""
        await cache.connect()

        assert cache._is_connected is True

    async def test_connect_creates_redis_client(self):
        """Test connect creates Redis client when none provided (line 26)."""
        cache = UserCache(redis_client=None)
        assert cache.redis is None

        # Mock Redis.from_url to avoid actual connection
        with patch("telegram_bot.services.cache.Redis") as mock_redis_class:
            mock_redis_instance = MagicMock()
            mock_redis_class.from_url.return_value = mock_redis_instance

            await cache.connect()

            assert cache._is_connected is True
            assert cache.redis is not None
            mock_redis_class.from_url.assert_called_once()

    async def test_connect_already_connected(self, cache):
        """Test connecting when already connected."""
        cache._is_connected = True

        await cache.connect()

        # Should not raise and remain connected
        assert cache._is_connected is True

    async def test_disconnect(self, cache, mock_redis):
        """Test disconnecting from Redis."""
        cache._is_connected = True

        await cache.disconnect()

        assert cache._is_connected is False
        mock_redis.close.assert_called_once()

    async def test_disconnect_no_redis(self):
        """Test disconnecting when no Redis client."""
        cache = UserCache(redis_client=None)
        cache._is_connected = False

        await cache.disconnect()

        # Should not raise
        assert cache._is_connected is False

    def test_user_key(self, cache):
        """Test generating user cache key."""
        result = cache._user_key(123456)

        assert result == "user:123456"

    def test_user_session_key(self, cache):
        """Test generating user session key."""
        result = cache._user_session_key(123456)

        assert result == "user_session:123456"

    async def test_get_user_not_connected(self, cache):
        """Test getting user when not connected."""
        cache._is_connected = False

        result = await cache.get_user(123456)

        assert result is None

    async def test_get_user_success(self, cache, mock_redis):
        """Test getting user data - success."""
        cache._is_connected = True
        user_data = {"id": 1, "name": "John"}
        mock_redis.get.return_value = pickle.dumps(user_data)

        result = await cache.get_user(123456)

        assert result == user_data
        mock_redis.get.assert_called_once_with("user:123456")

    async def test_get_user_no_data(self, cache, mock_redis):
        """Test getting user data - no data in cache."""
        cache._is_connected = True
        mock_redis.get.return_value = None

        result = await cache.get_user(123456)

        assert result is None

    async def test_get_user_pickle_error(self, cache, mock_redis):
        """Test getting user data - pickle error."""
        cache._is_connected = True
        mock_redis.get.return_value = b"invalid pickle data"

        result = await cache.get_user(123456)

        assert result is None

    async def test_get_user_redis_error(self, cache, mock_redis):
        """Test getting user data - Redis error."""
        cache._is_connected = True
        mock_redis.get.side_effect = RedisError("Connection failed")

        result = await cache.get_user(123456)

        assert result is None

    async def test_set_user_not_connected(self, cache):
        """Test setting user when not connected."""
        cache._is_connected = False

        result = await cache.set_user(123456, {"id": 1})

        assert result is False

    async def test_set_user_success(self, cache, mock_redis):
        """Test setting user data - success."""
        cache._is_connected = True
        user_data = {"id": 1, "name": "John"}

        result = await cache.set_user(123456, user_data)

        assert result is True
        mock_redis.set.assert_called_once()

    async def test_set_user_with_custom_ttl(self, cache, mock_redis):
        """Test setting user data with custom TTL."""
        cache._is_connected = True
        user_data = {"id": 1, "name": "John"}
        custom_ttl = timedelta(minutes=10)

        result = await cache.set_user(123456, user_data, ttl=custom_ttl)

        assert result is True
        mock_redis.set.assert_called_once()

    async def test_set_user_redis_error(self, cache, mock_redis):
        """Test setting user data - Redis error."""
        cache._is_connected = True
        mock_redis.set.side_effect = RedisError("Connection failed")

        result = await cache.set_user(123456, {"id": 1})

        assert result is False

    async def test_delete_user_not_connected(self, cache):
        """Test deleting user when not connected."""
        cache._is_connected = False

        result = await cache.delete_user(123456)

        assert result is False

    async def test_delete_user_success(self, cache, mock_redis):
        """Test deleting user data - success."""
        cache._is_connected = True
        mock_redis.delete.return_value = 2  # Number of keys deleted

        result = await cache.delete_user(123456)

        assert result is True
        mock_redis.delete.assert_called_once_with("user:123456", "user_session:123456")

    async def test_delete_user_redis_error(self, cache, mock_redis):
        """Test deleting user data - Redis error."""
        cache._is_connected = True
        mock_redis.delete.side_effect = RedisError("Connection failed")

        result = await cache.delete_user(123456)

        assert result is False

    async def test_get_session_not_connected(self, cache):
        """Test getting session when not connected."""
        cache._is_connected = False

        result = await cache.get_session(123456)

        assert result is None

    async def test_get_session_success(self, cache, mock_redis):
        """Test getting session data - success."""
        cache._is_connected = True
        session_data = {"token": "abc123"}
        mock_redis.get.return_value = pickle.dumps(session_data)

        result = await cache.get_session(123456)

        assert result == session_data

    async def test_get_session_no_data(self, cache, mock_redis):
        """Test getting session data - no data."""
        cache._is_connected = True
        mock_redis.get.return_value = None

        result = await cache.get_session(123456)

        assert result is None

    async def test_get_session_pickle_error(self, cache, mock_redis):
        """Test getting session data - pickle error."""
        cache._is_connected = True
        mock_redis.get.return_value = b"invalid data"

        result = await cache.get_session(123456)

        assert result is None

    async def test_set_session_not_connected(self, cache):
        """Test setting session when not connected."""
        cache._is_connected = False

        result = await cache.set_session(123456, {"token": "abc"})

        assert result is False

    async def test_set_session_success(self, cache, mock_redis):
        """Test setting session data - success."""
        cache._is_connected = True
        session_data = {"token": "abc123"}

        result = await cache.set_session(123456, session_data)

        assert result is True
        mock_redis.set.assert_called_once()

    async def test_set_session_redis_error(self, cache, mock_redis):
        """Test setting session data - Redis error (lines 123-124)."""
        cache._is_connected = True
        mock_redis.set.side_effect = RedisError("Connection failed")

        result = await cache.set_session(123456, {"token": "abc"})

        assert result is False

    async def test_update_user_field_success(self, cache, mock_redis):
        """Test updating user field - success."""
        cache._is_connected = True
        user_data = {"id": 1, "name": "John", "language": "en"}
        mock_redis.get.return_value = pickle.dumps(user_data)

        result = await cache.update_user_field(123456, "language", "ru")

        assert result is True

    async def test_update_user_field_no_user(self, cache, mock_redis):
        """Test updating user field - user not found."""
        cache._is_connected = True
        mock_redis.get.return_value = None

        result = await cache.update_user_field(123456, "language", "ru")

        assert result is False

    async def test_get_all_users_not_connected(self, cache):
        """Test getting all users when not connected."""
        cache._is_connected = False

        result = await cache.get_all_users()

        assert result == {}

    async def test_get_all_users_success(self, cache, mock_redis):
        """Test getting all users - success."""
        cache._is_connected = True

        # Create async iterator for scan_iter
        keys = [b"user:123", b"user:456"]
        mock_redis.scan_iter.return_value = self._async_iterator(keys)

        user1 = {"id": 1, "name": "User1"}
        user2 = {"id": 2, "name": "User2"}

        async def mock_get(key):
            if key == b"user:123":
                return pickle.dumps(user1)
            if key == b"user:456":
                return pickle.dumps(user2)
            return None

        mock_redis.get = mock_get

        result = await cache.get_all_users()

        assert len(result) == 2
        assert 123 in result
        assert 456 in result

    def _async_iterator(self, items):
        """Create async iterator helper."""

        async def gen():
            for item in items:
                yield item

        return gen()

    async def test_get_all_users_redis_error(self, cache, mock_redis):
        """Test getting all users - Redis error."""
        cache._is_connected = True
        mock_redis.scan_iter.side_effect = RedisError("Connection failed")

        result = await cache.get_all_users()

        assert result == {}

    async def test_cleanup_expired(self, cache):
        """Test cleanup expired (Redis auto-expires)."""
        result = await cache.cleanup_expired()

        assert result == 0  # Redis handles TTL automatically

    async def test_get_all_users_pickle_error(self, cache, mock_redis):
        """Test get_all_users with pickle error on single key (lines 155-156)."""
        cache._is_connected = True

        keys = [b"user:123", b"user:456"]
        mock_redis.scan_iter.return_value = self._async_iterator(keys)

        async def mock_get(key):
            if key == b"user:123":
                return b"invalid pickle data"
            user2 = {"id": 2, "name": "User2"}
            return pickle.dumps(user2)

        mock_redis.get = mock_get

        result = await cache.get_all_users()

        # Should skip the invalid key and return only valid user
        assert len(result) == 1
        assert 456 in result

    async def test_get_all_users_key_value_error(self, cache, mock_redis):
        """Test get_all_users with invalid key format causing ValueError (lines 155-156)."""
        cache._is_connected = True

        # Key with non-numeric user ID will cause ValueError in int() conversion
        keys = [b"user:abc", b"user:456"]
        mock_redis.scan_iter.return_value = self._async_iterator(keys)

        user2 = {"id": 2, "name": "User2"}

        async def mock_get(key):
            if key == b"user:456":
                return pickle.dumps(user2)
            return b"some_data"

        mock_redis.get = mock_get

        result = await cache.get_all_users()

        # Should skip invalid key and return valid user
        assert len(result) == 1
        assert 456 in result

    async def test_get_all_users_single_key_redis_error(self, cache, mock_redis):
        """Test get_all_users with RedisError on single key fetch (lines 155-156)."""
        cache._is_connected = True

        keys = [b"user:123", b"user:456"]
        mock_redis.scan_iter.return_value = self._async_iterator(keys)

        user2 = {"id": 2, "name": "User2"}

        async def mock_get(key):
            if key == b"user:123":
                msg = "Connection lost"
                raise RedisError(msg)
            return pickle.dumps(user2)

        mock_redis.get = mock_get

        result = await cache.get_all_users()

        # Should skip the key with error and return only valid user
        assert len(result) == 1
        assert 456 in result


class TestUserCacheSingleton:
    """Test the user_cache singleton instance."""

    def test_singleton_exists(self):
        """Test that user_cache singleton exists."""
        assert user_cache is not None
        assert isinstance(user_cache, UserCache)
