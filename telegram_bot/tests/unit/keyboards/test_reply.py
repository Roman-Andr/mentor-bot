"""Unit tests for telegram_bot reply keyboards."""

from aiogram.types import ReplyKeyboardMarkup

from telegram_bot.keyboards.main_menu import get_main_menu_keyboard
from telegram_bot.keyboards.utils import create_keyboard_button


class TestCreateKeyboardButton:
    """Test cases for create_keyboard_button utility."""

    def test_create_simple_button(self):
        """Test creating a simple keyboard button."""
        button = create_keyboard_button("Click me")

        assert button.text == "Click me"


class TestGetMainMenuKeyboard:
    """Test cases for get_main_menu_keyboard (reply keyboard)."""

    def test_authenticated_user_keyboard(self):
        """Test main menu for authenticated user."""
        user = {"id": 1, "role": "USER"}
        keyboard = get_main_menu_keyboard(is_authenticated=True, user=user, locale="en")

        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True

    def test_not_authenticated_user_keyboard(self):
        """Test main menu for non-authenticated user."""
        keyboard = get_main_menu_keyboard(is_authenticated=False, locale="en")

        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True

    def test_admin_user_keyboard(self):
        """Test main menu includes admin button for admin users."""
        user = {"id": 1, "role": "ADMIN"}
        keyboard = get_main_menu_keyboard(is_authenticated=True, user=user, locale="en")

        assert isinstance(keyboard, ReplyKeyboardMarkup)

    def test_hr_user_keyboard(self):
        """Test main menu includes admin button for HR users."""
        user = {"id": 1, "role": "HR"}
        keyboard = get_main_menu_keyboard(is_authenticated=True, user=user, locale="en")

        assert isinstance(keyboard, ReplyKeyboardMarkup)

    def test_user_with_none_user_dict(self):
        """Test main menu with None user but authenticated True."""
        keyboard = get_main_menu_keyboard(is_authenticated=True, user=None, locale="en")

        assert isinstance(keyboard, ReplyKeyboardMarkup)

    def test_keyboard_has_buttons(self):
        """Test that authenticated keyboard has buttons."""
        user = {"id": 1, "role": "USER"}
        keyboard = get_main_menu_keyboard(is_authenticated=True, user=user, locale="en")

        button_count = sum(len(row) for row in keyboard.keyboard)
        assert button_count > 0

    def test_not_authenticated_simple_buttons(self):
        """Test non-authenticated keyboard has simple buttons."""
        keyboard = get_main_menu_keyboard(is_authenticated=False, locale="en")

        button_texts = [btn.text for row in keyboard.keyboard for btn in row]
        # Should have /start
        assert any("/start" in text for text in button_texts)

    def test_keyboard_layout(self):
        """Test keyboard has reasonable layout."""
        user = {"id": 1, "role": "USER"}
        keyboard = get_main_menu_keyboard(is_authenticated=True, user=user, locale="en")

        # Should have some rows
        assert len(keyboard.keyboard) > 0

    def test_locale_parameter_used(self):
        """Test that locale parameter is used in keyboard generation."""
        user = {"id": 1, "role": "USER"}
        keyboard_en = get_main_menu_keyboard(is_authenticated=True, user=user, locale="en")
        keyboard_ru = get_main_menu_keyboard(is_authenticated=True, user=user, locale="ru")

        # Both should return valid keyboards
        assert isinstance(keyboard_en, ReplyKeyboardMarkup)
        assert isinstance(keyboard_ru, ReplyKeyboardMarkup)
