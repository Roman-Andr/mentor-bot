"""Unit tests for telegram_bot/handlers/meetings.py."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.handlers.meetings import (
    cancel_meeting,
    confirm_meeting,
    meeting_details,
    meetings_menu,
    my_meetings,
    process_meeting_datetime,
    process_meeting_description,
    process_meeting_duration,
    process_meeting_title,
    start_schedule_meeting,
)
from telegram_bot.states.meeting_states import MeetingStates


class TestMeetingsHandlers:
    """Test cases for meetings handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock(spec=Message)
        msg.from_user = MagicMock()
        msg.from_user.id = 123456
        msg.text = "/meetings"
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "meetings_menu"
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
        state.update_data = AsyncMock()
        state.get_data = AsyncMock()
        state.clear = AsyncMock()
        return state

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        return {"id": 1, "first_name": "John", "email": "john@example.com"}

    @pytest.fixture
    def mock_auth_token(self):
        """Create a mock auth token."""
        return "test_auth_token_123"

    @pytest.fixture
    def mock_meetings(self):
        """Create mock meetings data."""
        return [
            {
                "id": 1,
                "title": "Meeting 1",
                "scheduled_at": datetime.now(tz=UTC).isoformat(),
                "status": "scheduled",
                "participants": [{"email": "user@example.com"}],
            },
        ]

    async def test_meetings_menu_callback(
        self, mock_callback, mock_user, mock_auth_token, mock_meetings
    ):
        """Test meetings menu via callback."""
        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_upcoming_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_meetings
            with patch(
                "telegram_bot.handlers.meetings.format_meeting_list", return_value="Meeting List"
            ):
                with patch(
                    "telegram_bot.handlers.meetings.get_meetings_menu_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await meetings_menu(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_meetings_menu_message(
        self, mock_message, mock_user, mock_auth_token, mock_meetings
    ):
        """Test meetings menu via message."""
        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_upcoming_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_meetings
            with patch(
                "telegram_bot.handlers.meetings.format_meeting_list",
                return_value="Meeting List",
            ):
                with patch(
                    "telegram_bot.handlers.meetings.get_meetings_menu_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await meetings_menu(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_meetings_menu_no_user(self, mock_message, mock_auth_token):
        """Test meetings menu without user."""
        await meetings_menu(mock_message, None, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_meetings_menu_no_meetings(
        self, mock_callback, mock_user, mock_auth_token
    ):
        """Test meetings menu with no meetings."""
        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_upcoming_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []
            with patch(
                "telegram_bot.handlers.meetings.get_meetings_menu_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await meetings_menu(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_start_schedule_meeting(self, mock_callback, mock_state):
        """Test starting meeting scheduling."""
        await start_schedule_meeting(mock_callback, mock_state, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_state.set_state.assert_called_once_with(MeetingStates.waiting_for_title)
        mock_callback.answer.assert_called_once()

    async def test_start_schedule_meeting_no_message(self, mock_callback, mock_state):
        """Test starting meeting scheduling with no message."""
        mock_callback.message = None

        await start_schedule_meeting(mock_callback, mock_state, locale="en")

        mock_state.set_state.assert_not_called()

    async def test_process_meeting_title_valid(self, mock_message, mock_state):
        """Test processing valid meeting title."""
        mock_message.text = "Team Standup"

        await process_meeting_title(mock_message, mock_state, locale="en")

        mock_state.update_data.assert_called_once_with(title="Team Standup")
        mock_state.set_state.assert_called_once_with(MeetingStates.waiting_for_description)
        mock_message.answer.assert_called_once()

    async def test_process_meeting_title_too_short(self, mock_message, mock_state):
        """Test processing meeting title that is too short."""
        mock_message.text = "AB"

        await process_meeting_title(mock_message, mock_state, locale="en")

        mock_message.answer.assert_called_once()
        mock_state.update_data.assert_not_called()

    async def test_process_meeting_title_empty(self, mock_message, mock_state):
        """Test processing empty meeting title."""
        mock_message.text = "   "

        await process_meeting_title(mock_message, mock_state, locale="en")

        mock_message.answer.assert_called_once()
        mock_state.update_data.assert_not_called()

    async def test_process_meeting_description(self, mock_message, mock_state):
        """Test processing meeting description."""
        mock_message.text = "Weekly team sync meeting"

        await process_meeting_description(mock_message, mock_state, locale="en")

        mock_state.update_data.assert_called_once_with(description="Weekly team sync meeting")
        mock_state.set_state.assert_called_once_with(MeetingStates.waiting_for_datetime)

    async def test_process_meeting_description_skip(self, mock_message, mock_state):
        """Test processing skip description."""
        mock_message.text = "skip"

        await process_meeting_description(mock_message, mock_state, locale="en")

        mock_state.update_data.assert_called_once_with(description="")
        mock_state.set_state.assert_called_once_with(MeetingStates.waiting_for_datetime)

    async def test_process_meeting_description_skip_russian(self, mock_message, mock_state):
        """Test processing skip description in Russian."""
        mock_message.text = "\u043f\u0440\u043e\u043f\u0443\u0441\u0442\u0438\u0442\u044c"  # "пропустить"

        await process_meeting_description(mock_message, mock_state, locale="en")

        mock_state.update_data.assert_called_once_with(description="")

    async def test_process_meeting_datetime_valid(self, mock_message, mock_state):
        """Test processing valid meeting datetime."""
        mock_message.text = "2024-12-25 14:30"

        await process_meeting_datetime(mock_message, mock_state, locale="en")

        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once_with(MeetingStates.waiting_for_duration)
        mock_message.answer.assert_called_once()

    async def test_process_meeting_datetime_invalid(self, mock_message, mock_state):
        """Test processing invalid meeting datetime."""
        mock_message.text = "invalid-datetime"

        await process_meeting_datetime(mock_message, mock_state, locale="en")

        mock_message.answer.assert_called_once()
        mock_state.update_data.assert_not_called()
        mock_state.set_state.assert_not_called()

    async def test_process_meeting_duration_valid(self, mock_message, mock_state, mock_user, mock_auth_token):
        """Test processing valid meeting duration - success."""
        mock_message.text = "60"
        mock_state.get_data.return_value = {
            "title": "Team Standup",
            "description": "Weekly sync",
            "scheduled_at": "2024-12-25T14:30:00+00:00",
            "datetime_str": "2024-12-25 14:30",
        }

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.create_meeting",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = {"id": 123, "title": "Team Standup"}

            await process_meeting_duration(mock_message, mock_state, mock_user, mock_auth_token, locale="en")

        mock_create.assert_called_once()
        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()

    async def test_process_meeting_duration_too_short(self, mock_message, mock_state, mock_user, mock_auth_token):
        """Test processing meeting duration that is too short."""
        mock_message.text = "10"

        await process_meeting_duration(mock_message, mock_state, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_process_meeting_duration_too_long(self, mock_message, mock_state, mock_user, mock_auth_token):
        """Test processing meeting duration that is too long."""
        mock_message.text = "500"

        await process_meeting_duration(mock_message, mock_state, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_process_meeting_duration_invalid_number(self, mock_message, mock_state, mock_user, mock_auth_token):
        """Test processing invalid meeting duration."""
        mock_message.text = "abc"
        mock_state.get_data.return_value = {
            "title": "Team Standup",
            "description": "Weekly sync",
            "scheduled_at": "2024-12-25T14:30:00+00:00",
        }

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.create_meeting",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = {"id": 123, "title": "Team Standup"}

            await process_meeting_duration(mock_message, mock_state, mock_user, mock_auth_token, locale="en")

        # Should default to 60 minutes
        mock_create.assert_called_once()

    async def test_process_meeting_duration_create_failed(self, mock_message, mock_state, mock_user, mock_auth_token):
        """Test processing meeting duration when create fails."""
        mock_message.text = "60"
        mock_state.get_data.return_value = {
            "title": "Team Standup",
            "description": "Weekly sync",
            "scheduled_at": "2024-12-25T14:30:00+00:00",
        }

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.create_meeting",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = None

            await process_meeting_duration(mock_message, mock_state, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()
        mock_state.clear.assert_called_once()

    async def test_my_meetings_success(
        self, mock_callback, mock_user, mock_auth_token, mock_meetings
    ):
        """Test my meetings - success."""
        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_user_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_meetings
            with patch(
                "telegram_bot.handlers.meetings.format_meeting_list",
                return_value="Meeting List",
            ):
                with patch(
                    "telegram_bot.handlers.meetings.get_my_meetings_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await my_meetings(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_my_meetings_no_user(self, mock_callback, mock_auth_token):
        """Test my meetings without user."""
        await my_meetings(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_my_meetings_empty(
        self, mock_callback, mock_user, mock_auth_token
    ):
        """Test my meetings with no meetings."""
        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_user_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []
            with patch(
                "telegram_bot.handlers.meetings.get_my_meetings_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await my_meetings(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()

    async def test_meeting_details_success(self, mock_callback, mock_user, mock_auth_token, mock_meetings):
        """Test meeting details - success."""
        mock_callback.data = "meeting_1"

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_user_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_meetings
            with patch(
                "telegram_bot.handlers.meetings.get_meeting_details_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await meeting_details(
                    mock_callback, mock_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_meeting_details_not_found(
        self, mock_callback, mock_user, mock_auth_token
    ):
        """Test meeting details - not found."""
        mock_callback.data = "meeting_999"

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_user_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [{"id": 1, "title": "Meeting 1"}]

            await meeting_details(
                mock_callback, mock_user, mock_auth_token, locale="en"
            )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_meeting_details_no_auth(self, mock_callback, mock_user):
        """Test meeting details without auth token."""
        await meeting_details(mock_callback, mock_user, None, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_confirm_meeting_success(self, mock_callback, mock_user, mock_auth_token):
        """Test confirming meeting - success."""
        mock_callback.data = "confirm_meeting_123"

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.confirm_meeting",
            new_callable=AsyncMock,
        ) as mock_confirm:
            mock_confirm.return_value = True

            await confirm_meeting(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_confirm.assert_called_once_with(123, 1, mock_auth_token)
        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_confirm_meeting_failure(self, mock_callback, mock_user, mock_auth_token):
        """Test confirming meeting - failure."""
        mock_callback.data = "confirm_meeting_123"

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.confirm_meeting",
            new_callable=AsyncMock,
        ) as mock_confirm:
            mock_confirm.return_value = False

            await confirm_meeting(mock_callback, mock_user, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_confirm_meeting_no_user(self, mock_callback, mock_auth_token):
        """Test confirming meeting without user."""
        mock_callback.data = "confirm_meeting_123"

        await confirm_meeting(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_cancel_meeting_success(self, mock_callback, mock_user, mock_auth_token):
        """Test cancelling meeting - success."""
        mock_callback.data = "cancel_meeting_123"

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.cancel_meeting",
            new_callable=AsyncMock,
        ) as mock_cancel:
            mock_cancel.return_value = True

            await cancel_meeting(
                mock_callback, mock_user, mock_auth_token, locale="en"
            )

        mock_cancel.assert_called_once_with(
            123, 1, mock_auth_token, "Cancelled via Telegram"
        )
        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_cancel_meeting_failure(self, mock_callback, mock_user, mock_auth_token):
        """Test cancelling meeting - failure."""
        mock_callback.data = "cancel_meeting_123"

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.cancel_meeting",
            new_callable=AsyncMock,
        ) as mock_cancel:
            mock_cancel.return_value = False

            await cancel_meeting(
                mock_callback, mock_user, mock_auth_token, locale="en"
            )

        mock_callback.answer.assert_called_once()

    async def test_cancel_meeting_no_user(self, mock_callback, mock_auth_token):
        """Test cancelling meeting without user."""
        mock_callback.data = "cancel_meeting_123"

        await cancel_meeting(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_meetings_menu_english_text(
        self, mock_message, mock_user, mock_auth_token, mock_meetings
    ):
        """Test meetings menu triggered by English text."""
        mock_message.text = "Meetings"

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_upcoming_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_meetings
            with patch(
                "telegram_bot.handlers.meetings.format_meeting_list",
                return_value="Meeting List",
            ):
                with patch(
                    "telegram_bot.handlers.meetings.get_meetings_menu_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await meetings_menu(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_meetings_menu_russian_text(
        self, mock_message, mock_user, mock_auth_token, mock_meetings
    ):
        """Test meetings menu triggered by Russian text."""
        mock_message.text = "\u0412\u0441\u0442\u0440\u0435\u0447\u0438"

        with patch(
            "telegram_bot.handlers.meetings.meeting_client.get_upcoming_meetings",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_meetings
            with patch(
                "telegram_bot.handlers.meetings.format_meeting_list",
                return_value="Meeting List",
            ):
                with patch(
                    "telegram_bot.handlers.meetings.get_meetings_menu_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await meetings_menu(mock_message, mock_user, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()
