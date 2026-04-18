"""Unit tests for telegram_bot/middlewares/auth.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot
from aiogram.types import CallbackQuery, InlineQuery, Message, Update, User

from telegram_bot.middlewares import auth as auth_module
from telegram_bot.middlewares.auth import AuthMiddleware


class TestAuthMiddleware:
    """Test cases for AuthMiddleware."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot."""
        return MagicMock(spec=Bot)

    @pytest.fixture
    def middleware(self, mock_bot):
        """Create auth middleware with mock bot."""
        return AuthMiddleware(bot=mock_bot)

    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler."""
        return AsyncMock(return_value="handler_result")

    @pytest.fixture
    def mock_tg_user(self):
        """Create a mock Telegram user."""
        user = MagicMock(spec=User)
        user.id = 123456
        user.first_name = "John"
        user.last_name = "Doe"
        user.username = "testuser"
        return user

    async def test_message_event(self, middleware, mock_handler, mock_tg_user):
        """Test auth middleware with message event."""
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = mock_tg_user

        event = MagicMock(spec=Message)
        event.message = mock_message
        event.callback_query = None
        event.inline_query = None

        data = {}

        with patch.object(auth_module.user_cache, "get_user", AsyncMock(return_value=None)):
            with patch.object(auth_module.auth_client, "authenticate_with_telegram", AsyncMock(return_value=None)):
                result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert data["tg_user"] == mock_tg_user
        assert data["user"] is None
        assert data["auth_token"] is None
        assert data["is_authenticated"] is False
        mock_handler.assert_called_once()

    async def test_callback_query_event(self, middleware, mock_handler, mock_tg_user):
        """Test auth middleware with callback query event (line 36)."""
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.from_user = mock_tg_user

        event = MagicMock()
        event.message = None
        event.callback_query = mock_callback
        event.inline_query = None

        data = {}

        with patch.object(auth_module.user_cache, "get_user", AsyncMock(return_value=None)):
            with patch.object(auth_module.auth_client, "authenticate_with_telegram", AsyncMock(return_value=None)):
                result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert data["tg_user"] == mock_tg_user
        mock_handler.assert_called_once()

    async def test_inline_query_event(self, middleware, mock_handler, mock_tg_user):
        """Test auth middleware with inline query event (line 38)."""
        mock_inline = MagicMock(spec=InlineQuery)
        mock_inline.from_user = mock_tg_user

        event = MagicMock()
        event.message = None
        event.callback_query = None
        event.inline_query = mock_inline

        data = {}

        with patch.object(auth_module.user_cache, "get_user", AsyncMock(return_value=None)):
            with patch.object(auth_module.auth_client, "authenticate_with_telegram", AsyncMock(return_value=None)):
                result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert data["tg_user"] == mock_tg_user
        mock_handler.assert_called_once()

    async def test_no_user_event(self, middleware, mock_handler):
        """Test auth middleware with no user in event."""
        event = MagicMock()
        event.message = None
        event.callback_query = None
        event.inline_query = None

        data = {}

        result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert "tg_user" not in data  # No user attached
        mock_handler.assert_called_once()

    async def test_cached_user(self, middleware, mock_handler, mock_tg_user):
        """Test auth middleware with cached user data."""
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = mock_tg_user

        event = MagicMock(spec=Message)
        event.message = mock_message
        event.callback_query = None
        event.inline_query = None

        data = {}
        cached_user = {"id": 1, "first_name": "John", "access_token": "token123"}

        with patch.object(auth_module.user_cache, "get_user", AsyncMock(return_value=cached_user)):
            result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert data["user"] == cached_user
        assert data["auth_token"] == "token123"
        assert data["is_authenticated"] is True

    async def test_authentication_success(self, middleware, mock_handler, mock_tg_user):
        """Test successful authentication flow (lines 56-61)."""
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = mock_tg_user

        event = MagicMock(spec=Message)
        event.message = mock_message
        event.callback_query = None
        event.inline_query = None

        data = {}
        auth_result = {
            "access_token": "access_123",
            "refresh_token": "refresh_123",
        }
        user_data = {"id": 1, "first_name": "John", "email": "john@example.com"}

        mock_set_user = AsyncMock(return_value=True)
        with patch.object(auth_module.user_cache, "get_user", AsyncMock(return_value=None)):
            with patch.object(auth_module.user_cache, "set_user", mock_set_user):
                with patch.object(auth_module.auth_client, "authenticate_with_telegram", AsyncMock(return_value=auth_result)):
                    with patch.object(auth_module.auth_client, "get_current_user", AsyncMock(return_value=user_data)):
                        result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert data["user"] == {**user_data, "access_token": "access_123", "refresh_token": "refresh_123"}
        assert data["auth_token"] == "access_123"
        assert data["is_authenticated"] is True
        mock_set_user.assert_called_once()

    async def test_authentication_api_failure(self, middleware, mock_handler, mock_tg_user):
        """Test authentication when API call fails."""
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = mock_tg_user

        event = MagicMock(spec=Message)
        event.message = mock_message
        event.callback_query = None
        event.inline_query = None

        data = {}

        with patch.object(auth_module.user_cache, "get_user", AsyncMock(return_value=None)):
            with patch.object(auth_module.auth_client, "authenticate_with_telegram", AsyncMock(return_value=None)):
                result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert data["user"] is None
        assert data["auth_token"] is None
        assert data["is_authenticated"] is False

    async def test_authentication_no_access_token(self, middleware, mock_handler, mock_tg_user):
        """Test authentication when auth result has no access_token."""
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = mock_tg_user

        event = MagicMock(spec=Message)
        event.message = mock_message
        event.callback_query = None
        event.inline_query = None

        data = {}

        with patch.object(auth_module.user_cache, "get_user", AsyncMock(return_value=None)):
            with patch.object(auth_module.auth_client, "authenticate_with_telegram", AsyncMock(return_value={"refresh_token": "refresh_123"})):
                result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert data["user"] is None  # No access_token, so user not fetched

    async def test_get_current_user_returns_none(self, middleware, mock_handler, mock_tg_user):
        """Test when get_current_user returns None (lines 56-61 partially)."""
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = mock_tg_user

        event = MagicMock(spec=Message)
        event.message = mock_message
        event.callback_query = None
        event.inline_query = None

        data = {}
        auth_result = {
            "access_token": "access_123",
            "refresh_token": "refresh_123",
        }

        with patch.object(auth_module.user_cache, "get_user", AsyncMock(return_value=None)):
            with patch.object(auth_module.auth_client, "authenticate_with_telegram", AsyncMock(return_value=auth_result)):
                with patch.object(auth_module.auth_client, "get_current_user", AsyncMock(return_value=None)):
                    result = await middleware.__call__(mock_handler, event, data)

        assert result == "handler_result"
        assert data["user"] is None
        assert data["is_authenticated"] is False
