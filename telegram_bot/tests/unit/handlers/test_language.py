"""Unit tests for telegram_bot/handlers/language.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import User as TgUser

from telegram_bot.handlers.language import cb_language_menu, cmd_language, set_language


class TestLanguageHandlers:
    """Test cases for language handlers."""

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
        cb.data = "language_menu"
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
        cb.data = "set_lang_en"
        cb.answer = AsyncMock()
        cb.message = None
        return cb

    async def test_cmd_language(self, mock_message):
        """Test language command."""
        with patch("telegram_bot.handlers.language.get_language_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cmd_language(mock_message, locale="en")

        mock_message.answer.assert_called_once()

    async def test_cmd_language_russian(self, mock_message):
        """Test language command with Russian locale."""
        with patch("telegram_bot.handlers.language.get_language_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cmd_language(mock_message, locale="ru")

        mock_message.answer.assert_called_once()

    async def test_cb_language_menu(self, mock_callback):
        """Test language menu callback."""
        with patch("telegram_bot.handlers.language.get_language_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_language_menu(mock_callback, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_cb_language_menu_no_message(self, mock_callback_no_message):
        """Test language menu callback with no message."""
        with patch("telegram_bot.handlers.language.get_language_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await cb_language_menu(mock_callback_no_message, locale="en")

        mock_callback_no_message.answer.assert_called_once()

    async def test_set_language_english(self, mock_callback):
        """Test setting language to English."""
        mock_callback.data = "set_lang_en"
        tg_user = MagicMock(spec=TgUser)
        tg_user.id = 123456

        with patch(
            "telegram_bot.handlers.language.user_cache.update_user_field",
            new_callable=AsyncMock,
        ) as mock_update:
            with patch("telegram_bot.handlers.language.get_language_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await set_language(mock_callback, tg_user=tg_user)

        mock_callback.answer.assert_called_once()
        mock_update.assert_called_once_with(123456, "language", "en")

    async def test_set_language_russian(self, mock_callback):
        """Test setting language to Russian."""
        mock_callback.data = "set_lang_ru"
        tg_user = MagicMock(spec=TgUser)
        tg_user.id = 123456

        with patch(
            "telegram_bot.handlers.language.user_cache.update_user_field",
            new_callable=AsyncMock,
        ) as mock_update:
            with patch("telegram_bot.handlers.language.get_language_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await set_language(mock_callback, tg_user=tg_user)

        mock_callback.answer.assert_called_once()
        mock_update.assert_called_once_with(123456, "language", "ru")

    async def test_set_language_invalid(self, mock_callback):
        """Test setting invalid language."""
        mock_callback.data = "set_lang_fr"
        tg_user = MagicMock(spec=TgUser)

        await set_language(mock_callback, tg_user=tg_user)

        mock_callback.answer.assert_called_once_with("Unsupported language")

    async def test_set_language_not_tguser(self, mock_callback):
        """Test setting language when tg_user is not a TgUser instance."""
        mock_callback.data = "set_lang_en"
        non_user = MagicMock()  # Not a TgUser

        with patch(
            "telegram_bot.handlers.language.user_cache.update_user_field",
            new_callable=AsyncMock,
        ) as mock_update:
            with patch("telegram_bot.handlers.language.get_language_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await set_language(mock_callback, tg_user=non_user)

        # Should not update cache since it's not a TgUser
        mock_update.assert_not_called()
        mock_callback.answer.assert_called_once()

    async def test_set_language_with_message(self, mock_callback):
        """Test setting language and editing message."""
        mock_callback.data = "set_lang_en"
        tg_user = MagicMock(spec=TgUser)
        tg_user.id = 123456

        with patch("telegram_bot.handlers.language.user_cache.update_user_field", new_callable=AsyncMock):
            with patch("telegram_bot.handlers.language.get_language_keyboard") as mock_kb:
                mock_kb.return_value = MagicMock()

                await set_language(mock_callback, tg_user=tg_user)

        mock_callback.message.edit_text.assert_called_once()
