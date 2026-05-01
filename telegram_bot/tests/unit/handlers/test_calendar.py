"""Unit tests for telegram_bot/handlers/calendar.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Message
from telegram_bot.handlers.calendar import (
    calendar_menu,
    connect_calendar,
    disconnect_calendar,
)


class TestCalendarHandlers:
    """Test cases for calendar handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock(spec=Message)
        msg.from_user = MagicMock()
        msg.from_user.id = 123456
        msg.text = "/calendar"
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "calendar_menu"
        cb.answer = AsyncMock()
        msg_mock = MagicMock()
        msg_mock.chat = MagicMock()
        msg_mock.chat.id = 123456
        msg_mock.edit_text = AsyncMock()
        msg_mock.edit_reply_markup = AsyncMock()
        cb.message = msg_mock
        return cb

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        return {"id": 1, "first_name": "John", "email": "john@example.com"}

    @pytest.fixture
    def mock_auth_token(self):
        """Create a mock auth token."""
        return "test_auth_token_123"

    async def test_calendar_menu_callback_connected(self, mock_callback, mock_user, mock_auth_token):
        """Test calendar menu via callback - connected."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.check_connection_status",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.return_value = {"connected": True, "email": "user@example.com"}
            with patch("telegram_bot.handlers.calendar.get_calendar_connected_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await calendar_menu(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_calendar_menu_callback_not_connected(self, mock_callback, mock_user, mock_auth_token):
        """Test calendar menu via callback - not connected."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.check_connection_status",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.return_value = {"connected": False}
            with patch("telegram_bot.handlers.calendar.get_calendar_not_connected_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await calendar_menu(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_calendar_menu_message_connected(self, mock_message, mock_user, mock_auth_token):
        """Test calendar menu via message - connected."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.check_connection_status",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.return_value = {"connected": True, "email": "user@example.com"}
            with patch("telegram_bot.handlers.calendar.get_calendar_connected_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await calendar_menu(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_calendar_menu_message_not_connected(self, mock_message, mock_user, mock_auth_token):
        """Test calendar menu via message - not connected."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.check_connection_status",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.return_value = {"connected": False}
            with patch("telegram_bot.handlers.calendar.get_calendar_not_connected_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await calendar_menu(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_calendar_menu_no_user_callback(self, mock_callback, mock_auth_token):
        """Test calendar menu via callback without user."""
        await calendar_menu(mock_callback, None, mock_auth_token, locale="en")

        # Answer is called once at start for callback, once for auth message
        assert mock_callback.answer.call_count >= 1

    async def test_calendar_menu_no_user_message(self, mock_message, mock_auth_token):
        """Test calendar menu via message without user."""
        await calendar_menu(mock_message, None, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_calendar_menu_check_error(self, mock_callback, mock_user, mock_auth_token):
        """Test calendar menu when status check fails."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.check_connection_status",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.side_effect = Exception("Connection error")
            with patch("telegram_bot.handlers.calendar.get_calendar_not_connected_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await calendar_menu(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_connect_calendar_success(self, mock_callback, mock_user):
        """Test connect calendar - success."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.get_connect_url",
            new_callable=AsyncMock,
        ) as mock_get_url:
            mock_get_url.return_value = "https://auth.google.com/calendar?code=abc123"
            with patch("telegram_bot.handlers.calendar.get_calendar_connect_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await connect_calendar(mock_callback, mock_user, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_connect_calendar_no_user(self, mock_callback):
        """Test connect calendar without user."""
        await connect_calendar(mock_callback, None, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_connect_calendar_error(self, mock_callback, mock_user):
        """Test connect calendar when error occurs."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.get_connect_url",
            new_callable=AsyncMock,
        ) as mock_get_url:
            mock_get_url.side_effect = Exception("Auth error")

            await connect_calendar(mock_callback, mock_user, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_disconnect_calendar_success(self, mock_callback, mock_user, mock_auth_token):
        """Test disconnect calendar - success."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.disconnect_calendar",
            new_callable=AsyncMock,
        ) as mock_disconnect:
            mock_disconnect.return_value = {"status": "success"}

            await disconnect_calendar(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_disconnect_calendar_no_user(self, mock_callback, mock_auth_token):
        """Test disconnect calendar without user."""
        await disconnect_calendar(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_disconnect_calendar_failure(self, mock_callback, mock_user, mock_auth_token):
        """Test disconnect calendar - failure."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.disconnect_calendar",
            new_callable=AsyncMock,
        ) as mock_disconnect:
            mock_disconnect.return_value = {"success": False, "error": "Not connected"}

            await disconnect_calendar(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_disconnect_calendar_error(self, mock_callback, mock_user, mock_auth_token):
        """Test disconnect calendar when error occurs."""
        with patch(
            "telegram_bot.handlers.calendar.calendar_client.disconnect_calendar",
            new_callable=AsyncMock,
        ) as mock_disconnect:
            mock_disconnect.side_effect = Exception("Disconnect error")

            await disconnect_calendar(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_calendar_menu_english_text(self, mock_message, mock_user, mock_auth_token):
        """Test calendar menu triggered by English text."""
        mock_message.text = "Calendar"

        with patch(
            "telegram_bot.handlers.calendar.calendar_client.check_connection_status",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.return_value = {"connected": False}
            with patch("telegram_bot.handlers.calendar.get_calendar_not_connected_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await calendar_menu(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_calendar_menu_russian_text(self, mock_message, mock_user, mock_auth_token):
        """Test calendar menu triggered by Russian text."""
        mock_message.text = "\u041a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u044c"

        with patch(
            "telegram_bot.handlers.calendar.calendar_client.check_connection_status",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.return_value = {"connected": False}
            with patch("telegram_bot.handlers.calendar.get_calendar_not_connected_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await calendar_menu(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()
