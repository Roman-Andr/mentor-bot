"""Unit tests for telegram_bot/keyboards/admin_detail.py."""

from telegram_bot.keyboards.admin_detail import (
    get_admin_checklists_keyboard,
    get_admin_stats_keyboard,
    get_admin_users_keyboard,
    get_back_to_admin_checklists_keyboard,
    get_back_to_admin_panel_keyboard,
    get_back_to_admin_stats_keyboard,
    get_back_to_admin_users_keyboard,
)


class TestAdminDetailKeyboards:
    """Test cases for admin detail keyboards."""

    def test_get_admin_stats_keyboard(self):
        """Test admin stats keyboard."""
        builder = get_admin_stats_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")
        assert len(markup.inline_keyboard) >= 2

    def test_get_admin_stats_keyboard_russian(self):
        """Test admin stats keyboard - Russian locale."""
        builder = get_admin_stats_keyboard(locale="ru")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_admin_users_keyboard(self):
        """Test admin users keyboard."""
        builder = get_admin_users_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")
        assert len(markup.inline_keyboard) >= 3

    def test_get_admin_users_keyboard_russian(self):
        """Test admin users keyboard - Russian locale."""
        builder = get_admin_users_keyboard(locale="ru")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_admin_checklists_keyboard(self):
        """Test admin checklists keyboard."""
        builder = get_admin_checklists_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")
        assert len(markup.inline_keyboard) >= 3

    def test_get_admin_checklists_keyboard_russian(self):
        """Test admin checklists keyboard - Russian locale."""
        builder = get_admin_checklists_keyboard(locale="ru")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_back_to_admin_users_keyboard(self):
        """Test back to admin users keyboard."""
        builder = get_back_to_admin_users_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")
        assert len(markup.inline_keyboard) == 1

    def test_get_back_to_admin_users_keyboard_russian(self):
        """Test back to admin users keyboard - Russian locale."""
        builder = get_back_to_admin_users_keyboard(locale="ru")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_back_to_admin_checklists_keyboard(self):
        """Test back to admin checklists keyboard."""
        builder = get_back_to_admin_checklists_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_back_to_admin_panel_keyboard(self):
        """Test back to admin panel keyboard."""
        builder = get_back_to_admin_panel_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_back_to_admin_stats_keyboard(self):
        """Test back to admin stats keyboard."""
        builder = get_back_to_admin_stats_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")
