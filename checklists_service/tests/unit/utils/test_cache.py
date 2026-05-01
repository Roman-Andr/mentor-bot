"""Tests for cache utilities."""

import json
import logging
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from checklists_service.utils.cache import CacheManager, cached
from redis import RedisError

if TYPE_CHECKING:
    pass

DEFAULT_TTL = 3600
TTL_300 = 300
TTL_600 = 600


class TestCacheManagerGracefulDegrade:
    """Test graceful degradation when not connected."""

    async def test_get_returns_none_when_not_connected(self) -> None:
        """get() returns None when is_connected=False."""
        cm = CacheManager()
        cm.is_connected = False

        result = await cm.get("key")
        assert result is None

    async def test_set_returns_none_when_not_connected(self) -> None:
        """set() returns None when is_connected=False."""
        cm = CacheManager()
        cm.is_connected = False

        result = await cm.set("key", "value")
        assert result is None

    async def test_delete_returns_none_when_not_connected(self) -> None:
        """delete() returns None when is_connected=False."""
        cm = CacheManager()
        cm.is_connected = False

        result = await cm.delete("key")
        assert result is None

    async def test_delete_pattern_returns_none_when_not_connected(self) -> None:
        """delete_pattern() returns None when is_connected=False."""
        cm = CacheManager()
        cm.is_connected = False

        result = await cm.delete_pattern("pattern:*")
        assert result is None


class TestCacheManagerJSONRoundTrip:
    """Test JSON round-trip via fake redis_client."""

    async def test_get_json_round_trip(self) -> None:
        """get() returns deserialized JSON value."""
        cm = CacheManager()
        cm.is_connected = True

        # Fake redis client
        fake_value = json.dumps({"data": "test", "number": 42})
        cm.redis_client = AsyncMock()
        cm.redis_client.get = AsyncMock(return_value=fake_value)

        result = await cm.get("my_key")

        assert result == {"data": "test", "number": 42}
        cm.redis_client.get.assert_called_once_with("my_key")

    async def test_get_returns_none_for_missing_key(self) -> None:
        """get() returns None when key doesn't exist."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.get = AsyncMock(return_value=None)

        result = await cm.get("missing_key")

        assert result is None

    async def test_set_json_serialization(self) -> None:
        """set() serializes value to JSON."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.setex = AsyncMock(return_value=True)

        await cm.set("my_key", {"data": "test"}, ttl=TTL_600)

        expected_json = json.dumps({"data": "test"}, default=str)
        cm.redis_client.setex.assert_called_once_with("my_key", TTL_600, expected_json)

    async def test_set_uses_default_ttl(self) -> None:
        """set() uses default TTL of 3600."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.setex = AsyncMock(return_value=True)

        await cm.set("my_key", "simple_value")

        cm.redis_client.setex.assert_called_once()
        args = cm.redis_client.setex.call_args[0]
        assert args[1] == DEFAULT_TTL


class TestCacheManagerErrorHandling:
    """Test that JSONDecodeError and RedisError are swallowed."""

    async def test_get_swallows_json_decode_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """get() swallows JSONDecodeError and logs exception."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.get = AsyncMock(return_value="invalid json{{")

        with caplog.at_level(logging.ERROR):
            result = await cm.get("key")

        assert result is None
        assert "Cache get error" in caplog.text

    async def test_get_swallows_redis_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """get() swallows RedisError and logs exception."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.get = AsyncMock(side_effect=RedisError("connection lost"))

        with caplog.at_level(logging.ERROR):
            result = await cm.get("key")

        assert result is None
        assert "Cache get error" in caplog.text

    async def test_set_swallows_redis_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """set() swallows RedisError and logs exception."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.setex = AsyncMock(side_effect=RedisError("connection lost"))

        with caplog.at_level(logging.ERROR):
            result = await cm.set("key", "value")

        assert result is None
        assert "Cache set error" in caplog.text

    async def test_delete_swallows_redis_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """delete() swallows RedisError and logs exception."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.delete = AsyncMock(side_effect=RedisError("connection lost"))

        with caplog.at_level(logging.ERROR):
            result = await cm.delete("key")

        assert result is None
        assert "Cache delete error" in caplog.text

    async def test_delete_pattern_swallows_redis_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """delete_pattern() swallows RedisError and logs exception."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.keys = AsyncMock(side_effect=RedisError("connection lost"))

        with caplog.at_level(logging.ERROR):
            result = await cm.delete_pattern("pattern:*")

        assert result is None
        assert "Cache delete pattern error" in caplog.text


class TestCachedDecorator:
    """Test @cached decorator behavior."""

    async def test_cache_miss_calls_function_and_writes_result(self) -> None:
        """Cache miss: calls underlying function and writes result to cache."""
        # Clear any existing cached value
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()

        with patch("checklists_service.utils.cache.cache", mock_cache):
            call_count = 0

            @cached(ttl=TTL_300, key_prefix="test")
            async def expensive_function(arg1: str, arg2: int) -> dict:
                nonlocal call_count
                call_count += 1
                return {"result": f"{arg1}-{arg2}", "calls": call_count}

            result = await expensive_function("hello", 42)

            assert result == {"result": "hello-42", "calls": 1}
            assert call_count == 1

            # Verify cache.set was called with the result
            mock_cache.set.assert_called_once()
            args = mock_cache.set.call_args[0]
            assert args[1] == {"result": "hello-42", "calls": 1}
            assert args[2] == TTL_300

    async def test_cache_hit_skips_function(self) -> None:
        """Cache hit: returns cached value without calling function."""
        cached_value = {"cached": True, "data": "from_cache"}

        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value=cached_value)
        mock_cache.set = AsyncMock()

        with patch("checklists_service.utils.cache.cache", mock_cache):
            call_count = 0

            @cached(ttl=TTL_300, key_prefix="test")
            async def expensive_function(_arg1: str) -> dict:
                nonlocal call_count
                call_count += 1
                return {"fresh": True}

            result = await expensive_function("test")

            assert result == cached_value
            assert call_count == 0  # Function was not called
            mock_cache.set.assert_not_called()  # Cache not updated

    async def test_cache_key_generation(self) -> None:
        """Cache key is generated correctly with prefix, function name, args, kwargs."""
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()

        with patch("checklists_service.utils.cache.cache", mock_cache):

            @cached(ttl=TTL_600, key_prefix="custom")
            async def my_function(arg1: str, arg2: int = 0) -> str:
                return f"{arg1}-{arg2}"

            await my_function("hello", arg2=42)

            # Check the cache key format
            mock_cache.get.assert_called_once()
            cache_key = mock_cache.get.call_args[0][0]
            assert cache_key.startswith("custom:my_function:")
            assert "hello" in cache_key
            assert "42" in cache_key

    async def test_cached_preserves_function_metadata(self) -> None:
        """@cached decorator preserves function name and docstring."""
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()

        with patch("checklists_service.utils.cache.cache", mock_cache):

            @cached(ttl=300)
            async def documented_function(x: int) -> int:
                """Return double the input value."""
                return x * 2

            assert documented_function.__name__ == "documented_function"
            assert documented_function.__doc__ == "Return double the input value."


class TestCacheManagerConnection:
    """Test CacheManager connection lifecycle."""

    @patch("checklists_service.utils.cache.redis.from_url")
    async def test_connect_success(self, mock_from_url: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
        """connect() sets is_connected=True on successful ping."""
        cm = CacheManager()

        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        mock_from_url.return_value = mock_client

        with caplog.at_level(logging.INFO):
            await cm.connect()

        assert cm.is_connected is True
        assert "Redis cache connected" in caplog.text

    @patch("checklists_service.utils.cache.redis.from_url")
    async def test_connect_failure(self, mock_from_url: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
        """connect() sets is_connected=False on RedisError."""
        cm = CacheManager()

        mock_from_url.side_effect = RedisError("connection refused")

        with caplog.at_level(logging.WARNING):
            await cm.connect()

        assert cm.is_connected is False
        assert "Redis cache not available" in caplog.text

    async def test_disconnect_closes_client(self) -> None:
        """disconnect() closes redis client and sets is_connected=False."""
        cm = CacheManager()
        cm.is_connected = True
        cm.redis_client = AsyncMock()
        cm.redis_client.close = AsyncMock()

        await cm.disconnect()

        assert cm.is_connected is False
        cm.redis_client.close.assert_called_once()


class TestCacheManagerDeletePattern:
    """Test delete_pattern with keys matching."""

    async def test_delete_pattern_deletes_matching_keys(self) -> None:
        """delete_pattern() deletes all keys matching the pattern."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.keys = AsyncMock(return_value=["key1", "key2", "key3"])
        cm.redis_client.delete = AsyncMock(return_value=3)

        await cm.delete_pattern("user:*")

        cm.redis_client.keys.assert_called_once_with("user:*")
        cm.redis_client.delete.assert_called_once_with("key1", "key2", "key3")

    async def test_delete_pattern_no_matching_keys(self) -> None:
        """delete_pattern() does nothing if no keys match."""
        cm = CacheManager()
        cm.is_connected = True

        cm.redis_client = AsyncMock()
        cm.redis_client.keys = AsyncMock(return_value=[])
        cm.redis_client.delete = AsyncMock()

        await cm.delete_pattern("nomatch:*")

        cm.redis_client.keys.assert_called_once_with("nomatch:*")
        cm.redis_client.delete.assert_not_called()
