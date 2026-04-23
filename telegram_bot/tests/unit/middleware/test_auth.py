"""Unit tests for telegram_bot/middlewares/auth.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot.middlewares.auth import AuthMiddleware


class TestAuthMiddleware:
    """Test cases for AuthMiddleware."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_bot = MagicMock()
        self.middleware = AuthMiddleware(self.mock_bot)

        # Mock handler
        self.mock_handler = AsyncMock(return_value="handler_result")

        # Mock event with message
        self.mock_event_message = MagicMock()
        self.mock_event_message.message = MagicMock()
        self.mock_event_message.message.from_user = MagicMock()
        self.mock_event_message.message.from_user.id = 123456
        self.mock_event_message.callback_query = None
        self.mock_event_message.inline_query = None

        # Data dict
        self.data = {}

    @patch("telegram_bot.middlewares.auth.user_cache")
    async def test_authenticated_user_from_cache(self, mock_cache):
        """Test middleware with cached user data."""
        user_data = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "access_token": "cached_token_123",
        }
        mock_cache.get_user = AsyncMock(return_value=user_data)

        await self.middleware.__call__(
            self.mock_handler, self.mock_event_message, self.data
        )

        assert self.data["user"] == user_data
        assert self.data["auth_token"] == "cached_token_123"
        assert self.data["is_authenticated"] is True
        self.mock_handler.assert_called_once()

    @patch("telegram_bot.middlewares.auth.user_cache")
    async def test_user_not_in_cache(self, mock_cache):
        """Test middleware when user not in cache."""
        mock_cache.get_user = AsyncMock(return_value=None)

        await self.middleware.__call__(
            self.mock_handler, self.mock_event_message, self.data
        )

        assert self.data["is_authenticated"] is False
        self.mock_handler.assert_called_once()

    async def test_no_user_in_event(self):
        """Test middleware when event has no user."""
        mock_event_no_user = MagicMock()
        mock_event_no_user.message = None
        mock_event_no_user.callback_query = None
        mock_event_no_user.inline_query = None

        await self.middleware.__call__(
            self.mock_handler, mock_event_no_user, self.data
        )

        # Should still call handler
        self.mock_handler.assert_called_once()


class TestAuthMiddlewareInit:
    """Test cases for AuthMiddleware initialization."""

    def test_init_with_bot(self):
        """Test middleware initialization with bot."""
        mock_bot = MagicMock()
        middleware = AuthMiddleware(mock_bot)

        assert middleware.bot == mock_bot
