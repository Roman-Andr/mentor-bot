"""Unit tests for cache utilities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis import RedisError


class TestCacheManager:
    """Tests for CacheManager class."""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful Redis connection."""
        # Arrange
        with patch("meeting_service.utils.cache.settings") as mock_settings:
            mock_settings.REDIS_URL = "redis://localhost:6379"
            
            with patch("meeting_service.utils.cache.redis") as mock_redis:
                mock_client = AsyncMock()
                mock_client.ping = AsyncMock()
                mock_redis.from_url.return_value = mock_client
                
                from meeting_service.utils.cache import CacheManager
                
                cache = CacheManager()
                
                # Act
                await cache.connect()
                
                # Assert
                assert cache.is_connected is True
                assert cache.redis_client is not None
                mock_redis.from_url.assert_called_once()
                mock_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_redis_error(self):
        """Test Redis connection error handling."""
        # Arrange
        with patch("meeting_service.utils.cache.settings") as mock_settings:
            mock_settings.REDIS_URL = "redis://localhost:6379"
            
            with patch("meeting_service.utils.cache.redis") as mock_redis:
                mock_redis.from_url.side_effect = RedisError("Connection failed")
                
                from meeting_service.utils.cache import CacheManager
                
                cache = CacheManager()
                
                # Act
                await cache.connect()
                
                # Assert
                assert cache.is_connected is False
                assert cache.redis_client is None

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting from Redis."""
        # Arrange
        with patch("meeting_service.utils.cache.settings") as mock_settings:
            mock_settings.REDIS_URL = "redis://localhost:6379"
            
            with patch("meeting_service.utils.cache.redis") as mock_redis:
                mock_client = AsyncMock()
                mock_client.ping = AsyncMock()
                mock_redis.from_url.return_value = mock_client
                
                from meeting_service.utils.cache import CacheManager
                
                cache = CacheManager()
                await cache.connect()
                
                # Act
                await cache.disconnect()
                
                # Assert
                assert cache.is_connected is False
                mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self):
        """Test disconnect when not connected does nothing."""
        # Arrange
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.redis_client = None
        
        # Act - should not raise
        await cache.disconnect()
        
        # Assert
        assert cache.is_connected is False

    @pytest.mark.asyncio
    async def test_get_when_not_connected(self):
        """Test get returns None when not connected."""
        # Arrange
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = False
        
        # Act
        result = await cache.get("test_key")
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_when_redis_client_is_none(self):
        """Test get returns None when redis_client is None."""
        # Arrange
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = None
        
        # Act
        result = await cache.get("test_key")
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_redis_error(self):
        """Test get handles RedisError gracefully."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=RedisError("Get failed"))
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act
        result = await cache.get("test_key")
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_json_value(self):
        """Test get returns parsed JSON value."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value='{"key": "value"}')
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act
        result = await cache.get("test_key")
        
        # Assert
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_string_value(self):
        """Test get returns string value when not valid JSON."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value="plain_string")
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act
        result = await cache.get("test_key")
        
        # Assert
        assert result == "plain_string"

    @pytest.mark.asyncio
    async def test_get_none_value(self):
        """Test get returns None when Redis returns None."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=None)
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act
        result = await cache.get("test_key")
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_set_when_not_connected(self):
        """Test set does nothing when not connected."""
        # Arrange
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = False
        
        # Act - should not raise
        await cache.set("test_key", "value")
        
        # Assert - no exception raised

    @pytest.mark.asyncio
    async def test_set_when_redis_client_is_none(self):
        """Test set does nothing when redis_client is None."""
        # Arrange
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = None
        
        # Act - should not raise
        await cache.set("test_key", "value")
        
        # Assert - no exception raised

    @pytest.mark.asyncio
    async def test_set_redis_error(self):
        """Test set handles RedisError gracefully."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.setex = AsyncMock(side_effect=RedisError("Set failed"))
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act - should not raise
        await cache.set("test_key", "value")
        
        # Assert - no exception raised

    @pytest.mark.asyncio
    async def test_set_string_value(self):
        """Test set stores string value directly."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.setex = AsyncMock()
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act
        await cache.set("test_key", "string_value", ttl=100)
        
        # Assert
        mock_client.setex.assert_called_once_with("test_key", 100, "string_value")

    @pytest.mark.asyncio
    async def test_set_complex_object(self):
        """Test set serializes complex object to JSON."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.setex = AsyncMock()
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act
        await cache.set("test_key", {"key": "value"}, ttl=200)
        
        # Assert
        mock_client.setex.assert_called_once()
        call_args = mock_client.setex.call_args
        assert call_args[0][0] == "test_key"
        assert call_args[0][1] == 200
        assert '{"key": "value"}' in call_args[0][2]

    @pytest.mark.asyncio
    async def test_delete_when_not_connected(self):
        """Test delete does nothing when not connected."""
        # Arrange
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = False
        
        # Act - should not raise
        await cache.delete("test_key")
        
        # Assert - no exception raised

    @pytest.mark.asyncio
    async def test_delete_when_redis_client_is_none(self):
        """Test delete does nothing when redis_client is None."""
        # Arrange
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = None
        
        # Act - should not raise
        await cache.delete("test_key")
        
        # Assert - no exception raised

    @pytest.mark.asyncio
    async def test_delete_redis_error(self):
        """Test delete handles RedisError gracefully."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(side_effect=RedisError("Delete failed"))
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act - should not raise
        await cache.delete("test_key")
        
        # Assert - no exception raised

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """Test delete calls Redis delete."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock()
        
        from meeting_service.utils.cache import CacheManager
        
        cache = CacheManager()
        cache.is_connected = True
        cache.redis_client = mock_client
        
        # Act
        await cache.delete("test_key")
        
        # Assert
        mock_client.delete.assert_called_once_with("test_key")
