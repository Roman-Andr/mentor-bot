"""Unit tests for telegram_bot/middlewares/language.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot.middlewares.language import LanguageMiddleware


class TestLanguageMiddlewareInit:
    """Test cases for LanguageMiddleware initialization."""

    def test_init_success(self):
        """Test that LanguageMiddleware can be initialized."""
        middleware = LanguageMiddleware()
        assert isinstance(middleware, LanguageMiddleware)


class TestLanguageMiddlewareCall:
    """Test cases for LanguageMiddleware.__call__ method."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.middleware = LanguageMiddleware()
        self.mock_handler = AsyncMock(return_value="handler_result")

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_locale_from_user_cache(self, mock_user_cache):
        """Test locale extracted from user cache."""
        mock_user_cache.get_user = AsyncMock(return_value={"language": "ru"})

        mock_event = MagicMock()
        data = {"tg_user": MagicMock()}
        data["tg_user"].id = 123456

        result = await self.middleware.__call__(self.mock_handler, mock_event, data)

        # Verify cache was queried
        mock_user_cache.get_user.assert_called_once_with(123456)

        # Verify locale was set
        assert data["locale"] == "ru"

        # Verify handler was called
        self.mock_handler.assert_called_once_with(mock_event, data)
        assert result == "handler_result"

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_default_locale_when_no_user_data(self, mock_user_cache):
        """Test default locale when user has no language in cache."""
        mock_user_cache.get_user = AsyncMock(return_value={})  # Empty user data

        mock_event = MagicMock()
        data = {"tg_user": MagicMock()}
        data["tg_user"].id = 123456

        result = await self.middleware.__call__(self.mock_handler, mock_event, data)

        # Should default to "en"
        assert data["locale"] == "en"
        self.mock_handler.assert_called_once()

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_default_locale_when_user_not_in_cache(self, mock_user_cache):
        """Test default locale when user not found in cache."""
        mock_user_cache.get_user = AsyncMock(return_value=None)

        mock_event = MagicMock()
        data = {"tg_user": MagicMock()}
        data["tg_user"].id = 123456

        result = await self.middleware.__call__(self.mock_handler, mock_event, data)

        # Should default to "en"
        assert data["locale"] == "en"
        self.mock_handler.assert_called_once()

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_default_locale_when_no_tg_user(self, mock_user_cache):
        """Test default locale when no tg_user in data."""
        mock_event = MagicMock()
        data = {}  # No tg_user

        result = await self.middleware.__call__(self.mock_handler, mock_event, data)

        # Should default to "en"
        assert data["locale"] == "en"

        # Cache should not be queried
        mock_user_cache.get_user.assert_not_called()

        self.mock_handler.assert_called_once()

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_locale_with_tg_user_none(self, mock_user_cache):
        """Test when tg_user is explicitly None."""
        mock_event = MagicMock()
        data = {"tg_user": None}

        result = await self.middleware.__call__(self.mock_handler, mock_event, data)

        assert data["locale"] == "en"
        mock_user_cache.get_user.assert_not_called()

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_various_locales_from_cache(self, mock_user_cache):
        """Test various locales can be set from cache."""
        locales = ["en", "ru", "de", "fr", "es", "uk"]

        for locale in locales:
            mock_user_cache.get_user = AsyncMock(return_value={"language": locale})

            mock_event = MagicMock()
            data = {"tg_user": MagicMock()}
            data["tg_user"].id = 123456

            await self.middleware.__call__(self.mock_handler, mock_event, data)

            assert data["locale"] == locale

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_locale_persisted_in_data_for_handler(self, mock_user_cache):
        """Test that locale is available to handler in data dict."""
        mock_user_cache.get_user = AsyncMock(return_value={"language": "de"})

        mock_event = MagicMock()
        data = {"tg_user": MagicMock()}
        data["tg_user"].id = 123456

        # Capture what handler receives
        received_data = {}

        async def capture_handler(event, data):
            received_data.update(data)
            return "result"

        await self.middleware.__call__(capture_handler, mock_event, data)

        assert received_data["locale"] == "de"

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_handler_exception_propagated(self, mock_user_cache):
        """Test that handler exceptions are propagated."""
        mock_user_cache.get_user = AsyncMock(return_value={"language": "en"})

        mock_event = MagicMock()
        data = {"tg_user": MagicMock()}
        data["tg_user"].id = 123456

        async def failing_handler(event, data):
            raise ValueError("Handler error")

        with pytest.raises(ValueError, match="Handler error"):
            await self.middleware.__call__(failing_handler, mock_event, data)

    @patch("telegram_bot.middlewares.language.DEFAULT_LOCALE", "en")
    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_default_locale_constant(self, mock_user_cache):
        """Test DEFAULT_LOCALE constant is used as fallback."""
        mock_user_cache.get_user = AsyncMock(return_value=None)

        mock_event = MagicMock()
        data = {"tg_user": MagicMock()}

        result = await self.middleware.__call__(self.mock_handler, mock_event, data)

        assert data["locale"] == "en"

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_user_cache_exception_handling(self, mock_user_cache):
        """Test handling when user_cache raises exception."""
        mock_user_cache.get_user = AsyncMock(side_effect=Exception("Redis error"))

        mock_event = MagicMock()
        data = {"tg_user": MagicMock()}
        data["tg_user"].id = 123456

        # Should not raise - let the exception propagate (as middleware doesn't catch)
        with pytest.raises(Exception, match="Redis error"):
            await self.middleware.__call__(self.mock_handler, mock_event, data)


class TestLanguageMiddlewareIntegration:
    """Integration tests for language middleware."""

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_multiple_calls_same_user(self, mock_user_cache):
        """Test multiple calls for same user preserve locale."""
        middleware = LanguageMiddleware()
        mock_handler = AsyncMock(return_value="result")

        mock_user_cache.get_user = AsyncMock(return_value={"language": "fr"})

        for _ in range(3):
            mock_event = MagicMock()
            data = {"tg_user": MagicMock()}
            data["tg_user"].id = 123456

            await middleware.__call__(mock_handler, mock_event, data)

            assert data["locale"] == "fr"

        # Cache should be queried each time
        assert mock_user_cache.get_user.call_count == 3

    @patch("telegram_bot.middlewares.language.user_cache")
    async def test_different_users_different_locales(self, mock_user_cache):
        """Test different users can have different locales."""
        middleware = LanguageMiddleware()

        async def mock_get_user(user_id):
            locales = {1: "en", 2: "ru", 3: "de"}
            return {"language": locales.get(user_id, "en")}

        mock_user_cache.get_user = AsyncMock(side_effect=mock_get_user)

        results = {}

        async def capture_handler(event, data):
            results[data["tg_user"].id] = data["locale"]
            return "result"

        for user_id in [1, 2, 3]:
            mock_event = MagicMock()
            tg_user = MagicMock()
            tg_user.id = user_id
            data = {"tg_user": tg_user}

            await middleware.__call__(capture_handler, mock_event, data)

        assert results[1] == "en"
        assert results[2] == "ru"
        assert results[3] == "de"
