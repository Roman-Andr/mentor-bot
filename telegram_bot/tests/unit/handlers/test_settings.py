"""Unit tests for telegram_bot/handlers/settings.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot.handlers.settings import cb_settings_menu, cmd_settings


class TestSettingsHandlers:
    """Test cases for settings handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 123456
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock()
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "settings_menu"
        cb.answer = AsyncMock()
        cb.message = MagicMock()
        cb.message.chat = MagicMock()
        cb.message.chat.id = 123456
        cb.message.edit_text = AsyncMock()
        return cb

    @pytest.fixture
    def mock_callback_no_message(self):
        """Create a mock callback query with no message."""
        cb = MagicMock()
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "settings_menu"
        cb.answer = AsyncMock()
        cb.message = None
        return cb

    async def test_cmd_settings(self, mock_message):
        """Test settings command."""
        with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cmd_settings(mock_message, locale="en")

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "parse_mode" in call_args.kwargs
        assert call_args.kwargs["parse_mode"] == "Markdown"

    async def test_cmd_settings_russian(self, mock_message):
        """Test settings command with Russian locale."""
        with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cmd_settings(mock_message, locale="ru")

        mock_message.answer.assert_called_once()

    async def test_cb_settings_menu(self, mock_callback):
        """Test settings menu callback."""
        with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_settings_menu(mock_callback, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()
        call_args = mock_callback.message.edit_text.call_args
        assert "parse_mode" in call_args.kwargs
        assert call_args.kwargs["parse_mode"] == "Markdown"

    async def test_cb_settings_menu_no_message(self, mock_callback_no_message):
        """Test settings menu callback with no message."""
        with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_settings_menu(mock_callback_no_message, locale="en")

        mock_callback_no_message.answer.assert_called_once()

    async def test_cmd_settings_english_text(self, mock_message):
        """Test settings command triggered by English text."""
        mock_message.text = "Settings"

        with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cmd_settings(mock_message, locale="en")

        mock_message.answer.assert_called_once()

    async def test_cmd_settings_russian_text(self, mock_message):
        """Test settings command triggered by Russian text."""
        mock_message.text = "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438"

        with patch("telegram_bot.handlers.settings.get_settings_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cmd_settings(mock_message, locale="ru")

        mock_message.answer.assert_called_once()
