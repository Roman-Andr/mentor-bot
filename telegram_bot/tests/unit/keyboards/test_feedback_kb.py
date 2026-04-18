"""Unit tests for telegram_bot/keyboards/feedback_kb.py."""


from telegram_bot.keyboards.feedback_kb import (
    get_anonymity_choice_keyboard,
    get_experience_rating_keyboard,
    get_feedback_menu_keyboard,
    get_pulse_rating_keyboard,
)


class TestFeedbackKeyboards:
    """Test cases for feedback keyboards."""

    def test_get_feedback_menu_keyboard(self):
        """Test feedback menu keyboard."""
        result = get_feedback_menu_keyboard(locale="en")

        assert result is not None
        assert hasattr(result, "inline_keyboard")
        keyboard = result.inline_keyboard
        assert len(keyboard) >= 3

    def test_get_feedback_menu_keyboard_russian(self):
        """Test feedback menu keyboard - Russian locale."""
        result = get_feedback_menu_keyboard(locale="ru")

        assert result is not None
        assert hasattr(result, "inline_keyboard")

    def test_get_experience_rating_keyboard(self):
        """Test experience rating keyboard."""
        result = get_experience_rating_keyboard(locale="en")

        assert result is not None
        assert hasattr(result, "inline_keyboard")
        keyboard = result.inline_keyboard
        # Should have 3 rows: ratings 5-3, ratings 2-1, back button
        assert len(keyboard) == 3

    def test_get_experience_rating_keyboard_russian(self):
        """Test experience rating keyboard - Russian locale."""
        result = get_experience_rating_keyboard(locale="ru")

        assert result is not None
        assert hasattr(result, "inline_keyboard")

    def test_get_experience_rating_keyboard_emojis(self):
        """Test experience rating keyboard has correct emojis for ratings."""
        result = get_experience_rating_keyboard(locale="en")
        keyboard = result.inline_keyboard

        # Check that the keyboard contains rating buttons
        all_buttons = []
        for row in keyboard:
            all_buttons.extend(row)

        # Should have 5 rating buttons + 1 back button = 6 total
        assert len(all_buttons) == 6

        # Check callback data contains rate_ prefix
        callback_datas = [btn.callback_data for btn in all_buttons if hasattr(btn, "callback_data")]
        rate_callbacks = [cd for cd in callback_datas if cd and cd.startswith("rate_")]
        assert len(rate_callbacks) == 5

    def test_get_pulse_rating_keyboard(self):
        """Test pulse rating keyboard."""
        result = get_pulse_rating_keyboard(locale="en")

        assert result is not None
        assert hasattr(result, "inline_keyboard")
        keyboard = result.inline_keyboard
        # Should have 4 rows: ratings 10-7, 6-3, 2-1, back button
        assert len(keyboard) == 4

    def test_get_pulse_rating_keyboard_russian(self):
        """Test pulse rating keyboard - Russian locale."""
        result = get_pulse_rating_keyboard(locale="ru")

        assert result is not None
        assert hasattr(result, "inline_keyboard")

    def test_get_pulse_rating_keyboard_emojis(self):
        """Test pulse rating keyboard has correct emojis for ratings."""
        result = get_pulse_rating_keyboard(locale="en")
        keyboard = result.inline_keyboard

        # Check that the keyboard contains rating buttons
        all_buttons = []
        for row in keyboard:
            all_buttons.extend(row)

        # Should have 10 rating buttons + 1 back button = 11 total
        assert len(all_buttons) == 11

        # Check callback data contains pulse_ prefix
        callback_datas = [btn.callback_data for btn in all_buttons if hasattr(btn, "callback_data")]
        pulse_callbacks = [cd for cd in callback_datas if cd and cd.startswith("pulse_")]
        assert len(pulse_callbacks) == 10

    def test_get_pulse_rating_keyboard_layout(self):
        """Test pulse rating keyboard has correct row layout."""
        result = get_pulse_rating_keyboard(locale="en")
        keyboard = result.inline_keyboard

        # First row: 4 buttons (10, 9, 8, 7)
        assert len(keyboard[0]) == 4
        # Second row: 4 buttons (6, 5, 4, 3)
        assert len(keyboard[1]) == 4
        # Third row: 2 buttons (2, 1)
        assert len(keyboard[2]) == 2
        # Fourth row: 1 button (back)
        assert len(keyboard[3]) == 1

    def test_get_experience_rating_keyboard_layout(self):
        """Test experience rating keyboard has correct row layout."""
        result = get_experience_rating_keyboard(locale="en")
        keyboard = result.inline_keyboard

        # First row: 3 buttons (5, 4, 3)
        assert len(keyboard[0]) == 3
        # Second row: 2 buttons (2, 1)
        assert len(keyboard[1]) == 2
        # Third row: 1 button (back)
        assert len(keyboard[2]) == 1

    def test_get_anonymity_choice_keyboard_pulse(self):
        """Test anonymity choice keyboard for pulse survey (lines 96-116)."""
        result = get_anonymity_choice_keyboard(locale="en", survey_type="pulse")

        assert result is not None
        assert hasattr(result, "inline_keyboard")
        keyboard = result.inline_keyboard

        # Should have 2 rows: 2 anonymity buttons, 1 back button
        assert len(keyboard) == 2
        assert len(keyboard[0]) == 2  # Anonymous and Attributed buttons
        assert len(keyboard[1]) == 1  # Back button

    def test_get_anonymity_choice_keyboard_experience(self):
        """Test anonymity choice keyboard for experience rating."""
        result = get_anonymity_choice_keyboard(locale="en", survey_type="experience")

        assert result is not None
        keyboard = result.inline_keyboard

        # Check callback data contains experience prefix
        all_buttons = []
        for row in keyboard:
            all_buttons.extend(row)

        callback_datas = [btn.callback_data for btn in all_buttons if hasattr(btn, "callback_data")]
        assert any("experience_anon_choice" in cd for cd in callback_datas if cd)

    def test_get_anonymity_choice_keyboard_comments(self):
        """Test anonymity choice keyboard for comments."""
        result = get_anonymity_choice_keyboard(locale="en", survey_type="comment")

        assert result is not None
        keyboard = result.inline_keyboard

        # Check callback data contains comment prefix
        all_buttons = []
        for row in keyboard:
            all_buttons.extend(row)

        callback_datas = [btn.callback_data for btn in all_buttons if hasattr(btn, "callback_data")]
        assert any("comment_anon_choice" in cd for cd in callback_datas if cd)

    def test_get_anonymity_choice_keyboard_russian(self):
        """Test anonymity choice keyboard with Russian locale."""
        result = get_anonymity_choice_keyboard(locale="ru", survey_type="pulse")

        assert result is not None
        assert hasattr(result, "inline_keyboard")

    def test_get_anonymity_choice_keyboard_layout(self):
        """Test anonymity choice keyboard has correct row layout."""
        result = get_anonymity_choice_keyboard(locale="en", survey_type="pulse")
        keyboard = result.inline_keyboard

        # First row: 2 buttons (Anonymous, Attributed)
        assert len(keyboard[0]) == 2
        # Second row: 1 button (Back)
        assert len(keyboard[1]) == 1
        # Check back button has correct callback data
        back_button = keyboard[1][0]
        assert back_button.callback_data == "feedback_menu"
