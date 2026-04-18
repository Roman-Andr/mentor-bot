"""Unit tests for telegram_bot dialogue (FAQ) keyboards."""

from aiogram.types import InlineKeyboardMarkup

from telegram_bot.keyboards.dialogue_kb import (
    get_dialogue_step_keyboard,
    get_faq_menu_keyboard,
)


class TestGetFaqMenuKeyboard:
    """Test cases for get_faq_menu_keyboard."""

    def test_faq_menu_with_scenarios(self):
        """Test FAQ menu keyboard with scenarios."""
        scenarios = [
            {"id": 1, "title": "How to login"},
            {"id": 2, "title": "Reset password"},
            {"id": 3, "title": "Contact support"},
        ]
        keyboard = get_faq_menu_keyboard(scenarios, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 4  # 3 scenarios + back button

    def test_faq_menu_empty_scenarios(self):
        """Test FAQ menu keyboard with empty scenarios."""
        scenarios = []
        keyboard = get_faq_menu_keyboard(scenarios, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1  # Just back button

    def test_faq_menu_single_scenario(self):
        """Test FAQ menu keyboard with single scenario."""
        scenarios = [{"id": 1, "title": "Single question"}]
        keyboard = get_faq_menu_keyboard(scenarios, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2


class TestGetDialogueStepKeyboard:
    """Test cases for get_dialogue_step_keyboard."""

    def test_choice_step_with_options(self):
        """Test keyboard for CHOICE step with options."""
        step = {
            "id": 1,
            "answer_type": "CHOICE",
            "options": [
                {"label": "Option 1", "next_step": 2},
                {"label": "Option 2", "next_step": 3},
            ],
            "is_final": False,
        }
        keyboard = get_dialogue_step_keyboard(step, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) >= 3  # 2 options + back + menu

    def test_choice_step_no_options(self):
        """Test keyboard for CHOICE step without options."""
        step = {
            "id": 1,
            "answer_type": "CHOICE",
            "options": [],
            "is_final": False,
        }
        keyboard = get_dialogue_step_keyboard(step, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_link_step_with_url(self):
        """Test keyboard for LINK step with URL."""
        step = {
            "id": 1,
            "answer_type": "LINK",
            "answer_content": "https://example.com",
            "is_final": False,
        }
        keyboard = get_dialogue_step_keyboard(step, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Should have link button, back button, and menu button
        assert len(keyboard.inline_keyboard) >= 2

    def test_link_step_without_url(self):
        """Test keyboard for LINK step without URL."""
        step = {
            "id": 1,
            "answer_type": "LINK",
            "is_final": False,
        }
        keyboard = get_dialogue_step_keyboard(step, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_text_step(self):
        """Test keyboard for TEXT step."""
        step = {
            "id": 1,
            "answer_type": "TEXT",
            "is_final": False,
        }
        keyboard = get_dialogue_step_keyboard(step, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_final_step(self):
        """Test keyboard for final step (no back button)."""
        step = {
            "id": 1,
            "answer_type": "CHOICE",
            "options": [{"label": "Option 1", "next_step": 2}],
            "is_final": True,
        }
        keyboard = get_dialogue_step_keyboard(step, locale="en")

        assert isinstance(keyboard, InlineKeyboardMarkup)
