"""Unit tests for telegram_bot settings keyboards."""

from aiogram.types import InlineKeyboardMarkup
from telegram_bot.keyboards.settings_kb import get_notifications_keyboard, get_settings_keyboard


class TestGetSettingsKeyboard:
    """Test cases for get_settings_keyboard."""

    def test_settings_keyboard_structure(self):
        """Test settings menu keyboard structure."""
        keyboard = get_settings_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # Language + Notifications + back

    def test_settings_keyboard_buttons(self):
        """Test buttons in settings keyboard."""
        keyboard = get_settings_keyboard(locale="en")

        # First button should be language
        assert "\U0001f310" in keyboard.inline_keyboard[0][0].text
        assert keyboard.inline_keyboard[0][0].callback_data == "language_menu"

        # Second button should be notifications
        assert "\U0001f514" in keyboard.inline_keyboard[1][0].text
        assert keyboard.inline_keyboard[1][0].callback_data == "notifications_menu"

        # Third button should be back
        assert "\u2190" in keyboard.inline_keyboard[2][0].text
        assert keyboard.inline_keyboard[2][0].callback_data == "main_menu"

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


class TestGetNotificationsKeyboard:
    """Test cases for get_notifications_keyboard."""

    def test_notifications_keyboard_structure(self):
        """Test notifications keyboard structure."""
        keyboard = get_notifications_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # Telegram + Email + back

    def test_notifications_keyboard_telegram_enabled(self):
        """Test notifications keyboard with Telegram enabled."""
        keyboard = get_notifications_keyboard(locale="en", telegram_enabled=True)

        # First button should be Telegram with "on" status
        assert "\U0001f4f2" in keyboard.inline_keyboard[0][0].text
        assert keyboard.inline_keyboard[0][0].callback_data == "toggle_telegram"

    def test_notifications_keyboard_telegram_disabled(self):
        """Test notifications keyboard with Telegram disabled."""
        keyboard = get_notifications_keyboard(locale="en", telegram_enabled=False)

        # First button should be Telegram
        assert "\U0001f4f2" in keyboard.inline_keyboard[0][0].text
        assert keyboard.inline_keyboard[0][0].callback_data == "toggle_telegram"

    def test_notifications_keyboard_email_enabled(self):
        """Test notifications keyboard with Email enabled."""
        keyboard = get_notifications_keyboard(locale="en", email_enabled=True)

        # Second button should be Email
        assert "\U0001f4e7" in keyboard.inline_keyboard[1][0].text
        assert keyboard.inline_keyboard[1][0].callback_data == "toggle_email"

    def test_notifications_keyboard_email_disabled(self):
        """Test notifications keyboard with Email disabled."""
        keyboard = get_notifications_keyboard(locale="en", email_enabled=False)

        # Second button should be Email
        assert "\U0001f4e7" in keyboard.inline_keyboard[1][0].text
        assert keyboard.inline_keyboard[1][0].callback_data == "toggle_email"

    def test_notifications_keyboard_both_disabled(self):
        """Test notifications keyboard with both disabled."""
        keyboard = get_notifications_keyboard(locale="en", telegram_enabled=False, email_enabled=False)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3

    def test_notifications_keyboard_different_locale(self):
        """Test notifications keyboard with different locale."""
        keyboard_ru = get_notifications_keyboard(locale="ru")
        keyboard_en = get_notifications_keyboard(locale="en")

        assert isinstance(keyboard_ru, InlineKeyboardMarkup)
        assert isinstance(keyboard_en, InlineKeyboardMarkup)

    def test_notifications_keyboard_back_button(self):
        """Test notifications keyboard back button."""
        keyboard = get_notifications_keyboard(locale="en")

        # Third button should be back to settings
        assert "\u2190" in keyboard.inline_keyboard[2][0].text
        assert keyboard.inline_keyboard[2][0].callback_data == "settings_menu"
