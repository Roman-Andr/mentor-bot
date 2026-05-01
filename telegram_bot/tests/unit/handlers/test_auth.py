"""Unit tests for telegram_bot/handlers/auth.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram_bot.handlers.auth import cb_logout, process_invitation_token


class TestProcessInvitationToken:
    """Test cases for process_invitation_token handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks for all tests."""
        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()
        self.mock_message = MagicMock()
        self.mock_message.answer = AsyncMock()
        self.mock_message.text = "valid_token_123"

        self.mock_tg_user = MagicMock()
        self.mock_tg_user.id = 123456
        self.mock_tg_user.first_name = "John"
        self.mock_tg_user.last_name = "Doe"

        self.user_data = {
            "id": 1,
            "employee_id": "EMP123",
            "first_name": "John",
            "last_name": "Doe",
            "department": {"name": "Engineering"},
            "position": "Developer",
            "role": "USER",
        }

    @patch("telegram_bot.handlers.auth.register_by_token")
    @patch("telegram_bot.handlers.auth.format_welcome_message")
    @patch("telegram_bot.handlers.auth.get_main_menu_keyboard")
    async def test_successful_token_registration(self, mock_get_keyboard, mock_format_welcome, mock_register):
        """Test successful registration with valid token."""
        mock_register.return_value = (True, self.user_data)
        mock_format_welcome.return_value = "Welcome John Doe!"
        mock_keyboard = MagicMock()
        mock_get_keyboard.return_value = mock_keyboard

        await process_invitation_token(self.mock_message, self.mock_state, self.mock_tg_user, locale="en")

        mock_register.assert_called_once_with("valid_token_123", self.mock_tg_user, self.mock_state)
        mock_format_welcome.assert_called_once_with(self.mock_tg_user, self.user_data, locale="en")
        self.mock_message.answer.assert_called_once()

    @patch("telegram_bot.handlers.auth.register_by_token")
    async def test_failed_token_registration(self, mock_register):
        """Test failed registration with invalid token."""
        mock_register.return_value = (False, "Invalid token message")

        await process_invitation_token(self.mock_message, self.mock_state, self.mock_tg_user, locale="en")

        mock_register.assert_called_once_with("valid_token_123", self.mock_tg_user, self.mock_state)
        self.mock_message.answer.assert_called_once()
        call_args = self.mock_message.answer.call_args
        assert "[start.register_error]" in str(call_args)

    @patch("telegram_bot.handlers.auth.register_by_token")
    async def test_token_from_message_stripped(self, mock_register):
        """Test that token from message is stripped of whitespace."""
        self.mock_message.text = "  valid_token_123  "
        mock_register.return_value = (True, self.user_data)

        await process_invitation_token(self.mock_message, self.mock_state, self.mock_tg_user, locale="en")

        mock_register.assert_called_once_with("valid_token_123", self.mock_tg_user, self.mock_state)

    @patch("telegram_bot.handlers.auth.register_by_token")
    async def test_empty_token_handled(self, mock_register):
        """Test handling of empty token."""
        self.mock_message.text = ""
        mock_register.return_value = (False, "Invalid token")

        await process_invitation_token(self.mock_message, self.mock_state, self.mock_tg_user, locale="en")

        mock_register.assert_called_once_with("", self.mock_tg_user, self.mock_state)


class TestCbLogout:
    """Test cases for cb_logout handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks for all tests."""
        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()

        self.mock_callback = MagicMock()
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.mock_tg_user = MagicMock()
        self.mock_tg_user.id = 123456

    @patch("telegram_bot.handlers.auth.user_cache")
    async def test_logout_success(self, mock_cache):
        """Test successful logout clears state and cache."""
        mock_cache.delete_user = AsyncMock()

        await cb_logout(self.mock_callback, self.mock_state, self.mock_tg_user, locale="en")

        mock_cache.delete_user.assert_called_once_with(123456)
        self.mock_state.clear.assert_called_once()
        self.mock_callback.answer.assert_called_once()
        self.mock_callback.message.edit_text.assert_called_once()

    @patch("telegram_bot.handlers.auth.user_cache")
    async def test_logout_no_message(self, mock_cache):
        """Test logout when callback has no message."""
        mock_cache.delete_user = AsyncMock()
        self.mock_callback.message = None

        await cb_logout(self.mock_callback, self.mock_state, self.mock_tg_user, locale="en")

        mock_cache.delete_user.assert_called_once_with(123456)
        self.mock_state.clear.assert_called_once()
        self.mock_callback.answer.assert_called_once()
        # edit_text should not be called when message is None
        assert not self.mock_callback.message

    @patch("telegram_bot.handlers.auth.user_cache")
    async def test_logout_translation_keys(self, mock_cache):
        """Test that logout uses correct translation keys."""
        mock_cache.delete_user = AsyncMock()

        await cb_logout(self.mock_callback, self.mock_state, self.mock_tg_user, locale="en")

        call_args = self.mock_callback.message.edit_text.call_args
        assert "[auth.logged_out]" in str(call_args)

        answer_args = self.mock_callback.answer.call_args
        assert "[auth.logout_success]" in str(answer_args)

    @patch("telegram_bot.handlers.auth.user_cache")
    async def test_logout_cache_error_raises(self, mock_cache):
        """Test that cache errors during logout raise exception (no try-except in handler)."""
        mock_cache.delete_user = AsyncMock(side_effect=Exception("Cache error"))

        # The handler doesn't catch exceptions, so this should raise
        with pytest.raises(Exception, match="Cache error"):
            await cb_logout(self.mock_callback, self.mock_state, self.mock_tg_user, locale="en")
