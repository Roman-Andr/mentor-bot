"""Unit tests for telegram_bot/handlers/feedback.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.handlers.feedback import (
    MAX_PULSE_RATING,
    MIN_PULSE_RATING,
    feedback_menu,
    process_comment_anonymity_choice,
    process_comments,
    process_experience_anonymity_choice,
    process_experience_rating,
    process_pulse_anonymity_choice,
    process_pulse_rating,
    start_comments,
    start_experience_rating,
    start_pulse_survey,
)
from telegram_bot.states.feedback_states import FeedbackStates


class TestFeedbackHandlers:
    """Test cases for feedback handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock(spec=Message)
        msg.from_user = MagicMock()
        msg.from_user.id = 123456
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "feedback_menu"
        cb.answer = AsyncMock()
        msg_mock = MagicMock()
        msg_mock.chat = MagicMock()
        msg_mock.chat.id = 123456
        msg_mock.edit_text = AsyncMock()
        cb.message = msg_mock
        return cb

    @pytest.fixture
    def mock_state(self):
        """Create a mock FSM state."""
        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()
        state.clear = AsyncMock()
        state.get_data = AsyncMock(return_value={})
        return state

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        return {"id": 1, "first_name": "John", "email": "john@example.com"}

    @pytest.fixture
    def mock_auth_token(self):
        """Create a mock auth token."""
        return "test_auth_token_123"

    async def test_feedback_menu_callback(self, mock_callback, mock_state):
        """Test feedback menu via callback."""
        with patch("telegram_bot.handlers.feedback.format_feedback_menu", return_value="Feedback Menu"):
            with patch("telegram_bot.handlers.feedback.get_feedback_menu_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await feedback_menu(mock_callback, mock_state, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_feedback_menu_message(self, mock_message, mock_state):
        """Test feedback menu via message."""
        with patch("telegram_bot.handlers.feedback.format_feedback_menu", return_value="Feedback Menu"):
            with patch("telegram_bot.handlers.feedback.get_feedback_menu_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await feedback_menu(mock_message, mock_state, locale="en")

        mock_message.answer.assert_called_once()

    async def test_start_pulse_survey(self, mock_callback, mock_state):
        """Test starting pulse survey."""
        with patch("telegram_bot.handlers.feedback.get_anonymity_choice_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await start_pulse_survey(mock_callback, mock_state, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_state.set_state.assert_called_once_with(FeedbackStates.waiting_for_anonymity_choice)
        mock_callback.answer.assert_called_once()

    async def test_process_pulse_rating_success(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing valid pulse rating."""
        mock_callback.data = "pulse_8"

        with patch(
            "telegram_bot.handlers.feedback.feedback_client.submit_pulse_survey",
            new_callable=AsyncMock,
        ) as mock_submit:
            mock_submit.return_value = True
            with patch(
                "telegram_bot.handlers.feedback.get_feedback_menu_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await process_pulse_rating(
                    mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
                )

        mock_submit.assert_called_once_with(rating=8, is_anonymous=False, auth_token=mock_auth_token)
        mock_state.clear.assert_called_once()

    async def test_process_pulse_rating_invalid_format(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing pulse rating with invalid format."""
        mock_callback.data = "pulse_invalid"

        await process_pulse_rating(
            mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
        )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_pulse_rating_out_of_range_high(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing pulse rating out of range (too high)."""
        mock_callback.data = f"pulse_{MAX_PULSE_RATING + 1}"

        await process_pulse_rating(
            mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
        )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_pulse_rating_out_of_range_low(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing pulse rating out of range (too low)."""
        mock_callback.data = f"pulse_{MIN_PULSE_RATING - 1}"

        await process_pulse_rating(
            mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
        )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_pulse_rating_submit_failed(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing pulse rating when submit fails."""
        mock_callback.data = "pulse_5"

        with patch(
            "telegram_bot.handlers.feedback.feedback_client.submit_pulse_survey",
            new_callable=AsyncMock,
        ) as mock_submit:
            mock_submit.return_value = False

            await process_pulse_rating(
                mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
            )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_pulse_rating_no_user(self, mock_callback, mock_state, mock_auth_token):
        """Test processing pulse rating without user."""
        mock_callback.data = "pulse_5"

        with patch("telegram_bot.handlers.feedback.get_feedback_menu_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await process_pulse_rating(
                mock_callback, mock_state, None, mock_auth_token, locale="en"
            )

        mock_state.clear.assert_called_once()

    async def test_start_experience_rating(self, mock_callback, mock_state):
        """Test starting experience rating."""
        with patch("telegram_bot.handlers.feedback.get_anonymity_choice_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await start_experience_rating(mock_callback, mock_state, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_process_experience_rating_success(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing valid experience rating."""
        mock_callback.data = "rate_4"

        with patch(
            "telegram_bot.handlers.feedback.feedback_client.submit_experience_rating",
            new_callable=AsyncMock,
        ) as mock_submit:
            mock_submit.return_value = True
            with patch(
                "telegram_bot.handlers.feedback.get_feedback_menu_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await process_experience_rating(
                    mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
                )

        mock_submit.assert_called_once_with(rating=4, is_anonymous=False, auth_token=mock_auth_token)

    async def test_process_experience_rating_submit_failed(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing experience rating when submit fails."""
        mock_callback.data = "rate_3"

        with patch(
            "telegram_bot.handlers.feedback.feedback_client.submit_experience_rating",
            new_callable=AsyncMock,
        ) as mock_submit:
            mock_submit.return_value = False

            await process_experience_rating(
                mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
            )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_experience_rating_no_user(self, mock_callback, mock_state, mock_auth_token):
        """Test processing experience rating without user."""
        mock_callback.data = "rate_5"

        with patch("telegram_bot.handlers.feedback.get_feedback_menu_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await process_experience_rating(
                mock_callback, mock_state, None, mock_auth_token, locale="en"
            )

        mock_callback.message.edit_text.assert_called_once()

    async def test_start_comments(self, mock_callback, mock_state):
        """Test starting comments."""
        with patch("telegram_bot.handlers.feedback.get_anonymity_choice_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await start_comments(mock_callback, mock_state, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_state.set_state.assert_called_once_with(FeedbackStates.waiting_for_comment_anonymity)
        mock_callback.answer.assert_called_once()

    async def test_process_comments_success(self, mock_message, mock_state, mock_user, mock_auth_token):
        """Test processing valid comments."""
        mock_message.text = "This is a valid comment with enough length."

        with patch(
            "telegram_bot.handlers.feedback.feedback_client.submit_comment",
            new_callable=AsyncMock,
        ) as mock_submit:
            mock_submit.return_value = True
            with patch(
                "telegram_bot.handlers.feedback.get_feedback_menu_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await process_comments(
                    mock_message, mock_state, mock_user, mock_auth_token, locale="en"
                )

        mock_submit.assert_called_once()
        mock_state.clear.assert_called_once()

    async def test_process_comments_too_short(self, mock_message, mock_state, mock_user, mock_auth_token):
        """Test processing comment that is too short."""
        mock_message.text = "Short"

        await process_comments(
            mock_message, mock_state, mock_user, mock_auth_token, locale="en"
        )

        mock_message.answer.assert_called_once()
        mock_state.clear.assert_not_called()

    async def test_process_comments_submit_failed(self, mock_message, mock_state, mock_user, mock_auth_token):
        """Test processing comment when submit fails."""
        mock_message.text = "This is a valid comment with enough length for submission."

        with patch(
            "telegram_bot.handlers.feedback.feedback_client.submit_comment",
            new_callable=AsyncMock,
        ) as mock_submit:
            mock_submit.return_value = False

            await process_comments(
                mock_message, mock_state, mock_user, mock_auth_token, locale="en"
            )

        mock_message.answer.assert_called_once()
        mock_state.clear.assert_not_called()

    async def test_process_comments_no_user(self, mock_message, mock_state, mock_auth_token):
        """Test processing comment without user."""
        mock_message.text = "This is a valid comment with enough length."

        with patch("telegram_bot.handlers.feedback.get_feedback_menu_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await process_comments(
                mock_message, mock_state, None, mock_auth_token, locale="en"
            )

        mock_message.answer.assert_called_once()
        mock_state.clear.assert_called_once()

    async def test_feedback_menu_command(self, mock_message, mock_state):
        """Test feedback menu via command."""
        mock_message.text = "/feedback"

        with patch("telegram_bot.handlers.feedback.format_feedback_menu", return_value="Feedback Menu"):
            with patch("telegram_bot.handlers.feedback.get_feedback_menu_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await feedback_menu(mock_message, mock_state, locale="en")

        mock_message.answer.assert_called_once()

    async def test_feedback_menu_russian_text(self, mock_message, mock_state):
        """Test feedback menu via Russian text."""
        mock_message.text = "\u041e\u0431\u0440\u0430\u0442\u043d\u0430\u044f \u0441\u0432\u044f\u0437\u044c"

        with patch("telegram_bot.handlers.feedback.format_feedback_menu", return_value="Feedback Menu"):
            with patch("telegram_bot.handlers.feedback.get_feedback_menu_keyboard") as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await feedback_menu(mock_message, mock_state, locale="en")

        mock_message.answer.assert_called_once()

    async def test_process_pulse_anonymity_choice_success(self, mock_callback, mock_state):
        """Test processing pulse anonymity choice - success."""
        mock_callback.data = "pulse_anon_choice_true"

        with patch("telegram_bot.handlers.feedback.get_pulse_rating_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await process_pulse_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_state.update_data.assert_called_once_with(is_anonymous=True)
        mock_state.set_state.assert_called_once_with(FeedbackStates.waiting_for_pulse_rating)
        mock_callback.answer.assert_called_once()

    async def test_process_pulse_anonymity_choice_invalid_format(self, mock_callback, mock_state):
        """Test processing pulse anonymity choice with invalid format."""
        mock_callback.data = "pulse_anon_choice_invalid"

        with patch("telegram_bot.handlers.feedback.get_pulse_rating_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await process_pulse_anonymity_choice(mock_callback, mock_state, locale="en")

        # When parsing fails, is_anonymous becomes False ("invalid" != "true")
        # and it proceeds normally (no exception is raised as split works fine)
        mock_state.update_data.assert_called_once_with(is_anonymous=False)
        mock_state.set_state.assert_called_once_with(FeedbackStates.waiting_for_pulse_rating)
        mock_callback.answer.assert_called_once()

    async def test_process_experience_anonymity_choice_success(self, mock_callback, mock_state):
        """Test processing experience anonymity choice - success."""
        mock_callback.data = "experience_anon_choice_false"

        with patch("telegram_bot.handlers.feedback.get_experience_rating_keyboard") as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await process_experience_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_state.update_data.assert_called_once_with(is_anonymous=False)
        mock_state.set_state.assert_called_once_with(FeedbackStates.waiting_for_experience_rating)
        mock_callback.answer.assert_called_once()

    async def test_process_experience_anonymity_choice_invalid_format(self, mock_callback, mock_state):
        """Test processing experience anonymity choice with invalid format."""
        mock_callback.data = "experience_anon_choice_invalid"

        with patch("telegram_bot.handlers.feedback.get_experience_rating_keyboard") as mock_kb:
            mock_kb.return_value = MagicMock()

            await process_experience_anonymity_choice(mock_callback, mock_state, locale="en")

        # When parsing fails, is_anonymous becomes False ("invalid" != "true")
        mock_state.update_data.assert_called_once_with(is_anonymous=False)
        mock_state.set_state.assert_called_once_with(FeedbackStates.waiting_for_experience_rating)
        mock_callback.answer.assert_called_once()

    async def test_process_comment_anonymity_choice_success(self, mock_callback, mock_state):
        """Test processing comment anonymity choice - success."""
        mock_callback.data = "comment_anon_choice_true"

        await process_comment_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_state.update_data.assert_called_once_with(is_anonymous=True)
        mock_state.set_state.assert_called_once_with(FeedbackStates.waiting_for_comments)
        mock_callback.answer.assert_called_once()

    async def test_process_comment_anonymity_choice_invalid_format(self, mock_callback, mock_state):
        """Test processing comment anonymity choice with invalid format."""
        mock_callback.data = "comment_anon_choice_invalid"

        await process_comment_anonymity_choice(mock_callback, mock_state, locale="en")

        # When parsing fails, is_anonymous becomes False ("invalid" != "true")
        mock_state.update_data.assert_called_once_with(is_anonymous=False)
        mock_state.set_state.assert_called_once_with(FeedbackStates.waiting_for_comments)
        mock_callback.answer.assert_called_once()

    async def test_process_pulse_anonymity_choice_index_error(self, mock_callback, mock_state):
        """Test process_pulse_anonymity_choice when split raises IndexError."""
        # Create a mock string that raises IndexError on split()[-1]
        class RaisingString:
            def split(self, sep):
                return RaisingList()

        class RaisingList(list):
            def __getitem__(self, index):
                if index == -1:
                    msg = "Simulated IndexError"
                    raise IndexError(msg)
                return super().__getitem__(index)

        mock_callback.data = RaisingString()

        await process_pulse_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_pulse_anonymity_choice_value_error(self, mock_callback, mock_state):
        """Test process_pulse_anonymity_choice when comparison raises ValueError."""
        # Create a mock that raises ValueError on == comparison
        class RaisingString:
            def split(self, sep):
                return [RaisingComparison()]

        class RaisingComparison:
            def __eq__(self, other):
                msg = "Simulated ValueError"
                raise ValueError(msg)

        mock_callback.data = RaisingString()

        await process_pulse_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_experience_anonymity_choice_index_error(self, mock_callback, mock_state):
        """Test process_experience_anonymity_choice when split raises IndexError."""
        class RaisingString:
            def split(self, sep):
                return RaisingList()

        class RaisingList(list):
            def __getitem__(self, index):
                if index == -1:
                    msg = "Simulated IndexError"
                    raise IndexError(msg)
                return super().__getitem__(index)

        mock_callback.data = RaisingString()

        await process_experience_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_experience_anonymity_choice_value_error(self, mock_callback, mock_state):
        """Test process_experience_anonymity_choice when comparison raises ValueError."""
        class RaisingString:
            def split(self, sep):
                return [RaisingComparison()]

        class RaisingComparison:
            def __eq__(self, other):
                msg = "Simulated ValueError"
                raise ValueError(msg)

        mock_callback.data = RaisingString()

        await process_experience_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_comment_anonymity_choice_index_error(self, mock_callback, mock_state):
        """Test process_comment_anonymity_choice when split raises IndexError."""
        class RaisingString:
            def split(self, sep):
                return RaisingList()

        class RaisingList(list):
            def __getitem__(self, index):
                if index == -1:
                    msg = "Simulated IndexError"
                    raise IndexError(msg)
                return super().__getitem__(index)

        mock_callback.data = RaisingString()

        await process_comment_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_comment_anonymity_choice_value_error(self, mock_callback, mock_state):
        """Test process_comment_anonymity_choice when comparison raises ValueError."""
        class RaisingString:
            def split(self, sep):
                return [RaisingComparison()]

        class RaisingComparison:
            def __eq__(self, other):
                msg = "Simulated ValueError"
                raise ValueError(msg)

        mock_callback.data = RaisingString()

        await process_comment_anonymity_choice(mock_callback, mock_state, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_experience_rating_invalid_format(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing experience rating with invalid format."""
        mock_callback.data = "rate_invalid"

        await process_experience_rating(
            mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
        )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_process_experience_rating_anonymous_true(self, mock_callback, mock_state, mock_user, mock_auth_token):
        """Test processing experience rating with anonymous=true."""
        mock_callback.data = "rate_5_anon_true"

        with patch(
            "telegram_bot.handlers.feedback.feedback_client.submit_experience_rating",
            new_callable=AsyncMock,
        ) as mock_submit:
            mock_submit.return_value = True
            with patch(
                "telegram_bot.handlers.feedback.get_feedback_menu_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await process_experience_rating(
                    mock_callback, mock_state, mock_user, mock_auth_token, locale="en"
                )

        mock_submit.assert_called_once_with(rating=5, is_anonymous=True, auth_token=mock_auth_token)
        mock_state.clear.assert_called_once()
