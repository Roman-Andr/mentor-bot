"""Unit tests for telegram_bot settings keyboards."""

from aiogram.types import InlineKeyboardMarkup

from telegram_bot.keyboards.settings_kb import get_settings_keyboard


class TestGetSettingsKeyboard:
    """Test cases for get_settings_keyboard."""

    def test_settings_keyboard_structure(self):
        """Test settings menu keyboard structure."""
        keyboard = get_settings_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Language + back

    def test_settings_keyboard_buttons(self):
        """Test buttons in settings keyboard."""
        keyboard = get_settings_keyboard(locale="en")

        # First button should be language
        assert "\U0001f310" in keyboard.inline_keyboard[0][0].text
        assert keyboard.inline_keyboard[0][0].callback_data == "language_menu"

        # Second button should be back
        assert "\u2190" in keyboard.inline_keyboard[1][0].text
        assert keyboard.inline_keyboard[1][0].callback_data == "main_menu"

    def test_settings_keyboard_different_locale(self):
        """Test settings keyboard with different locale."""
        keyboard_ru = get_settings_keyboard(locale="ru")
        keyboard_en = get_settings_keyboard(locale="en")

        assert isinstance(keyboard_ru, InlineKeyboardMarkup)
        assert isinstance(keyboard_en, InlineKeyboardMarkup)

    def test_settings_keyboard_default_locale(self):
        """Test settings keyboard with default locale."""
        keyboard = get_settings_keyboard("en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
