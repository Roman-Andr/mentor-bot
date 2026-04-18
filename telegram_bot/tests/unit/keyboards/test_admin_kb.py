"""Unit tests for telegram_bot admin keyboards."""

from aiogram.types import InlineKeyboardMarkup

from telegram_bot.keyboards.admin import get_admin_keyboard


class TestGetAdminKeyboard:
    """Test cases for get_admin_keyboard."""

    def test_admin_keyboard_structure(self):
        """Test admin panel keyboard structure."""
        keyboard = get_admin_keyboard(locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Should have 4 rows (2+2+2+2 buttons)
        assert len(keyboard.inline_keyboard) == 4

    def test_admin_keyboard_buttons_count(self):
        """Test correct number of buttons."""
        keyboard = get_admin_keyboard(locale="en")

        # Count all buttons
        total_buttons = sum(len(row) for row in keyboard.inline_keyboard)
        assert total_buttons == 8  # stats, users, checklists, knowledge, settings, reports, alerts, back

    def test_admin_keyboard_has_stats_button(self):
        """Test stats button presence."""
        keyboard = get_admin_keyboard(locale="en")

        all_buttons = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert any("\U0001f4ca" in btn for btn in all_buttons)  # Stats emoji

    def test_admin_keyboard_has_users_button(self):
        """Test users button presence."""
        keyboard = get_admin_keyboard(locale="en")

        all_buttons = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert any("\U0001f465" in btn for btn in all_buttons)  # Users emoji

    def test_admin_keyboard_has_back_button(self):
        """Test back button presence and callback."""
        keyboard = get_admin_keyboard(locale="en")

        # Find back button
        back_button = None
        for row in keyboard.inline_keyboard:
            for btn in row:
                if btn.callback_data == "menu":
                    back_button = btn
                    break

        assert back_button is not None
        assert "\u2190" in back_button.text

    def test_admin_keyboard_different_locale(self):
        """Test admin keyboard with different locale."""
        keyboard = get_admin_keyboard(locale="ru")

        assert isinstance(keyboard, InlineKeyboardMarkup)
