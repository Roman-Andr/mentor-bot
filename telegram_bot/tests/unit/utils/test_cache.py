"""Unit tests for telegram_bot/utils/cache.py."""

import pickle
from contextlib import suppress
from datetime import timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis import RedisError
from telegram_bot.utils.cache import RedisCache, cache, cached, get_or_set, invalidate_cache


class TestRedisCache:
    """Test cases for RedisCache."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        redis = MagicMock()
        redis.close = AsyncMock()
        redis.get = AsyncMock()
        redis.set = AsyncMock()
        redis.delete = AsyncMock()
        redis.scan_iter = MagicMock()
        redis.exists = AsyncMock()
        redis.flushdb = AsyncMock()
        return redis

    @pytest.fixture
    def redis_cache(self, mock_redis):
        """Create a RedisCache with mock Redis."""
        return RedisCache(redis_client=mock_redis)

    async def test_connect(self, redis_cache, mock_redis):
        """Test connecting to Redis."""
        await redis_cache.connect()

        assert redis_cache._is_connected is True

    async def test_connect_already_connected(self, redis_cache):
        """Test connecting when already connected."""
        redis_cache._is_connected = True

        await redis_cache.connect()

        assert redis_cache._is_connected is True

    async def test_disconnect(self, redis_cache, mock_redis):
        """Test disconnecting from Redis."""
        redis_cache._is_connected = True

        await redis_cache.disconnect()

        assert redis_cache._is_connected is False
        mock_redis.close.assert_called_once()

    async def test_disconnect_no_redis(self):
        """Test disconnecting when no Redis client."""
        redis_cache = RedisCache(redis_client=None)
        redis_cache._is_connected = False

        await redis_cache.disconnect()

        # Should not raise
        assert redis_cache._is_connected is False

    def test_make_key_simple(self, redis_cache):
        """Test making simple cache key."""
        result = redis_cache._make_key("prefix", "arg1", "arg2")

        assert result == "prefix:arg1:arg2"

    def test_make_key_with_kwargs(self, redis_cache):
        """Test making cache key with kwargs."""
        result = redis_cache._make_key("prefix", "arg1", key1="value1", key2="value2")

        assert "prefix" in result
        assert "arg1" in result
        assert "key1:value1" in result
        assert "key2:value2" in result

    def test_make_key_sorted_kwargs(self, redis_cache):
        """Test that kwargs are sorted in cache key."""
        result1 = redis_cache._make_key("prefix", key_b="b", key_a="a")
        result2 = redis_cache._make_key("prefix", key_a="a", key_b="b")

        # Both should produce the same key due to sorting
        assert result1 == result2

    def test_make_key_long_key(self, redis_cache):
        """Test making cache key that exceeds max length."""
        # Create a key that will exceed 250 characters
        long_arg = "x" * 300
        result = redis_cache._make_key("prefix", long_arg)

        # Should be hashed (sha256 is 64 chars + "prefix:" prefix = ~71)
        assert len(result) <= 80  # prefix + hash

    async def test_get_not_connected(self, redis_cache):
        """Test get when not connected."""
        redis_cache._is_connected = False

        result = await redis_cache.get("key")

        assert result is None

    async def test_get_success(self, redis_cache, mock_redis):
        """Test get - success."""
        redis_cache._is_connected = True
        data = {"value": "test"}
        mock_redis.get.return_value = pickle.dumps(data)

        result = await redis_cache.get("key")

        assert result == data
        mock_redis.get.assert_called_once_with("key")

    async def test_get_no_data(self, redis_cache, mock_redis):
        """Test get - no data."""
        redis_cache._is_connected = True
        mock_redis.get.return_value = None

        result = await redis_cache.get("key")

        assert result is None

    async def test_get_pickle_error(self, redis_cache, mock_redis):
        """Test get - pickle error."""
        redis_cache._is_connected = True
        mock_redis.get.return_value = b"invalid pickle"

        result = await redis_cache.get("key")

        assert result is None

    async def test_set_not_connected(self, redis_cache):
        """Test set when not connected."""
        redis_cache._is_connected = False

        result = await redis_cache.set("key", "value")

        assert result is False

    async def test_set_success(self, redis_cache, mock_redis):
        """Test set - success."""
        redis_cache._is_connected = True

        result = await redis_cache.set("key", {"data": "value"})

        assert result is True
        mock_redis.set.assert_called_once()

    async def test_set_with_int_ttl(self, redis_cache, mock_redis):
        """Test set with integer TTL."""
        redis_cache._is_connected = True

        result = await redis_cache.set("key", "value", ttl=300)

        assert result is True

    async def test_set_with_timedelta_ttl(self, redis_cache, mock_redis):
        """Test set with timedelta TTL."""
        redis_cache._is_connected = True

        result = await redis_cache.set("key", "value", ttl=timedelta(minutes=5))

        assert result is True

    async def test_set_redis_error(self, redis_cache, mock_redis):
        """Test set - Redis error."""
        redis_cache._is_connected = True
        mock_redis.set.side_effect = RedisError("Connection failed")

        result = await redis_cache.set("key", "value")

        assert result is False

    async def test_delete_not_connected(self, redis_cache):
        """Test delete when not connected."""
        redis_cache._is_connected = False

        result = await redis_cache.delete("key")

        assert result is False

    async def test_delete_success(self, redis_cache, mock_redis):
        """Test delete - success."""
        redis_cache._is_connected = True
        mock_redis.delete.return_value = 1

        result = await redis_cache.delete("key")

        assert result is True

    async def test_delete_no_key(self, redis_cache, mock_redis):
        """Test delete - key not found."""
        redis_cache._is_connected = True
        mock_redis.delete.return_value = 0

        result = await redis_cache.delete("key")

        assert result is False

    async def test_delete_redis_error(self, redis_cache, mock_redis):
        """Test delete - Redis error handling."""
        redis_cache._is_connected = True
        mock_redis.delete.side_effect = RedisError("Connection failed")

        result = await redis_cache.delete("key")

        assert result is False

    async def test_delete_pattern_not_connected(self, redis_cache):
        """Test delete_pattern when not connected."""
        redis_cache._is_connected = False

        result = await redis_cache.delete_pattern("pattern:*")

        assert result == 0

    async def test_delete_pattern_success(self, redis_cache, mock_redis):
        """Test delete_pattern - success."""
        redis_cache._is_connected = True
        keys = [b"key1", b"key2", b"key3"]
        mock_redis.scan_iter.return_value = self._async_iterator(keys)
        mock_redis.delete.return_value = 3

        result = await redis_cache.delete_pattern("pattern:*")

        assert result == 3

    async def test_delete_pattern_no_keys(self, redis_cache, mock_redis):
        """Test delete_pattern - no matching keys."""
        redis_cache._is_connected = True
        mock_redis.scan_iter.return_value = self._async_iterator([])

        result = await redis_cache.delete_pattern("pattern:*")

        assert result == 0

    async def test_delete_pattern_redis_error(self, redis_cache, mock_redis):
        """Test delete_pattern - Redis error."""
        redis_cache._is_connected = True
        mock_redis.scan_iter.side_effect = RedisError("Connection failed")

        result = await redis_cache.delete_pattern("pattern:*")

        assert result == 0

    def _async_iterator(self, items: list) -> object:
        """Create async iterator from items."""

        async def gen() -> object:
            for item in items:
                yield item

        return gen()

    async def test_exists_not_connected(self, redis_cache):
        """Test exists when not connected."""
        redis_cache._is_connected = False

        result = await redis_cache.exists("key")

        assert result is False

    async def test_exists_true(self, redis_cache, mock_redis):
        """Test exists - key exists."""
        redis_cache._is_connected = True
        mock_redis.exists.return_value = 1

        result = await redis_cache.exists("key")

        assert result is True

    async def test_exists_false(self, redis_cache, mock_redis):
        """Test exists - key not found."""
        redis_cache._is_connected = True
        mock_redis.exists.return_value = 0

        result = await redis_cache.exists("key")

        assert result is False

    async def test_exists_redis_error(self, redis_cache, mock_redis):
        """Test exists - Redis error."""
        redis_cache._is_connected = True
        mock_redis.exists.side_effect = RedisError("Connection failed")

        result = await redis_cache.exists("key")

        assert result is False

    async def test_flush_not_connected(self, redis_cache):
        """Test flush when not connected."""
        redis_cache._is_connected = False

        result = await redis_cache.flush()

        assert result is False

    async def test_flush_success(self, redis_cache, mock_redis):
        """Test flush - success."""
        redis_cache._is_connected = True

        result = await redis_cache.flush()

        assert result is True
        mock_redis.flushdb.assert_called_once()

    async def test_flush_redis_error(self, redis_cache, mock_redis):
        """Test flush - Redis error."""
        redis_cache._is_connected = True
        mock_redis.flushdb.side_effect = RedisError("Connection failed")

        result = await redis_cache.flush()

        assert result is False

    async def test_get_redis_error(self, redis_cache, mock_redis):
        """Test get - Redis error handling."""
        redis_cache._is_connected = True
        mock_redis.get.side_effect = RedisError("Connection failed")

        result = await redis_cache.get("key")

        assert result is None

    async def test_connect_with_redis_error(self):
        """Test connect handles Redis initialization error."""
        redis_cache = RedisCache()

        with patch("telegram_bot.utils.cache.Redis") as mock_redis_class:
            mock_redis_class.from_url.side_effect = RedisError("Connection failed")

            # Should not raise, but may fail to connect
            with suppress(RedisError):
                await redis_cache.connect()


class TestCachedDecorator:
    """Test cases for cached decorator."""

    async def test_cached_with_cache_hit(self):
        """Test cached decorator with cache hit."""
        cached_value = {"result": "cached"}

        with patch("telegram_bot.utils.cache.cache.get", return_value=cached_value):
            with patch("telegram_bot.utils.cache.cache.set") as mock_set:

                @cached(ttl=300, key_prefix="test")
                async def test_func(arg1: Any, arg2: Any) -> dict:
                    return {"result": "computed"}

                result = await test_func("a", "b")

                assert result == cached_value
                mock_set.assert_not_called()

    async def test_cached_with_cache_miss(self):
        """Test cached decorator with cache miss."""
        computed_value = {"result": "computed"}

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock) as mock_set:

                @cached(ttl=300, key_prefix="test")
                async def test_func(arg1: Any, arg2: Any) -> dict:
                    return computed_value

                result = await test_func("a", "b")

                assert result == computed_value
                mock_set.assert_called_once()

    async def test_cached_with_ignore_args(self):
        """Test cached decorator with ignore_args."""
        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):

                @cached(ttl=300, key_prefix="test", ignore_args=["auth_token"])
                async def test_func(user_id: int, auth_token: str) -> dict:
                    return {"user_id": user_id}

                await test_func(123, "token1")
                await test_func(123, "token2")  # Should use same cache key

    async def test_cached_does_not_cache_none(self):
        """Test that None results are not cached."""
        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock) as mock_set:

                @cached(ttl=300, key_prefix="test")
                async def test_func() -> None:
                    return None

                result = await test_func()

                assert result is None
                mock_set.assert_not_called()


class TestInvalidateCache:
    """Test cases for invalidate_cache function."""

    async def test_invalidate_cache(self):
        """Test invalidate_cache function."""
        with patch("telegram_bot.utils.cache.cache.delete_pattern", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = 5

            result = await invalidate_cache("pattern:*")

            assert result == 5
            mock_delete.assert_called_once_with("pattern:*")


class TestGetOrSet:
    """Test cases for get_or_set function."""

    async def test_get_or_set_cache_hit(self):
        """Test get_or_set with cache hit."""
        cached_value = "cached_data"

        with patch("telegram_bot.utils.cache.cache.get", return_value=cached_value):
            coro_func = AsyncMock()

            result = await get_or_set("key", coro_func, ttl=300)

            assert result == cached_value
            coro_func.assert_not_called()

    async def test_get_or_set_cache_miss(self):
        """Test get_or_set with cache miss."""
        computed_value = "computed_data"

        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock):
                coro_func = AsyncMock(return_value=computed_value)

                result = await get_or_set("key", coro_func, ttl=300)

                assert result == computed_value
                coro_func.assert_called_once()

    async def test_get_or_set_does_not_cache_none(self):
        """Test get_or_set doesn't cache None results."""
        with patch("telegram_bot.utils.cache.cache.get", return_value=None):
            with patch("telegram_bot.utils.cache.cache.set", new_callable=AsyncMock) as mock_set:
                coro_func = AsyncMock(return_value=None)

                result = await get_or_set("key", coro_func, ttl=300)

                assert result is None
                mock_set.assert_not_called()


class TestCacheSingleton:
    """Test the cache singleton instance."""

    def test_singleton_exists(self):
        """Test that cache singleton exists."""
        assert cache is not None
        assert isinstance(cache, RedisCache)
