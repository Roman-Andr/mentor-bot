"""Unit tests for telegram_bot/handlers/escalation.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.handlers.escalation import (
    escalation_details,
    escalation_menu,
    list_my_escalations,
    my_escalations,
    new_escalation,
    process_escalation_description,
    process_escalation_title,
    process_escalation_type,
    view_escalation_from_notification,
)
from telegram_bot.states.escalation_states import EscalationStates


class TestEscalationHandlers:
    """Test cases for escalation handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        msg = MagicMock(spec=Message)
        msg.from_user = MagicMock()
        msg.from_user.id = 123456
        msg.text = "/escalate"
        msg.answer = AsyncMock()
        return msg

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query."""
        cb = MagicMock(spec=CallbackQuery)
        cb.id = "callback_123"
        cb.from_user = MagicMock()
        cb.from_user.id = 123456
        cb.data = "escalate_menu"
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
    def mock_escalations(self):
        """Create mock escalations data with new schema."""
        return [
            {
                "id": 1,
                "reason": "Escalation 1",  # escalation_service uses 'reason'
                "status": "open",
                "type": "IT",  # escalation_service uses 'type'
                "context": {"description": "Test description"},
            },
            {
                "id": 2,
                "reason": "Escalation 2",
                "status": "in_progress",
                "type": "HR",
                "context": {"description": "Test description"},
            },
        ]

    async def test_escalation_menu_callback(
        self, mock_callback, mock_user, mock_auth_token, mock_escalations
    ):
        """Test escalation menu via callback."""
        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_user_escalations",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_escalations
            with patch(
                "telegram_bot.handlers.escalation.format_escalation_list",
                return_value="Escalation List",
            ):
                with patch(
                    "telegram_bot.handlers.escalation.get_escalation_menu_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await escalation_menu(
                        mock_callback, mock_user, mock_auth_token, locale="en"
                    )

        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()

    async def test_escalation_menu_message(
        self, mock_message, mock_user, mock_auth_token, mock_escalations
    ):
        """Test escalation menu via message."""
        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_user_escalations",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_escalations
            with patch(
                "telegram_bot.handlers.escalation.format_escalation_list",
                return_value="Escalation List",
            ):
                with patch(
                    "telegram_bot.handlers.escalation.get_escalation_menu_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await escalation_menu(
                        mock_message, mock_user, mock_auth_token, locale="en"
                    )

        mock_message.answer.assert_called_once()

    async def test_escalation_menu_no_user(self, mock_message, mock_auth_token):
        """Test escalation menu without user."""
        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_user_escalations",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []

            await escalation_menu(mock_message, None, mock_auth_token, locale="en")

        mock_message.answer.assert_called_once()

    async def test_escalation_menu_no_escalations(
        self, mock_callback, mock_user, mock_auth_token
    ):
        """Test escalation menu with no escalations."""
        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_user_escalations",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []
            with patch(
                "telegram_bot.handlers.escalation.get_escalation_menu_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await escalation_menu(
                    mock_callback, mock_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()

    async def test_new_escalation(self, mock_callback, mock_state):
        """Test starting new escalation."""
        with patch(
            "telegram_bot.handlers.escalation.get_new_escalation_keyboard"
        ) as mock_kb:
            mock_kb.return_value.as_markup.return_value = MagicMock()

            await new_escalation(mock_callback, mock_state, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_process_escalation_type_question(self, mock_callback, mock_state):
        """Test processing question escalation type."""
        mock_callback.data = "escalate_question"

        await process_escalation_type(mock_callback, mock_state, locale="en")

        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once_with(EscalationStates.waiting_for_description)
        mock_callback.answer.assert_called_once()

    async def test_process_escalation_type_mentor(self, mock_callback, mock_state):
        """Test processing mentor escalation type."""
        mock_callback.data = "escalate_mentor"

        await process_escalation_type(mock_callback, mock_state, locale="en")

        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once_with(EscalationStates.waiting_for_description)

    async def test_process_escalation_type_hr(self, mock_callback, mock_state):
        """Test processing HR escalation type."""
        mock_callback.data = "escalate_hr"

        await process_escalation_type(mock_callback, mock_state, locale="en")

        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once_with(EscalationStates.waiting_for_description)

    async def test_process_escalation_type_technical(self, mock_callback, mock_state):
        """Test processing technical escalation type."""
        mock_callback.data = "escalate_technical"

        await process_escalation_type(mock_callback, mock_state, locale="en")

        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once_with(EscalationStates.waiting_for_description)

    async def test_process_escalation_description_success(self, mock_message, mock_state):
        """Test processing valid escalation description."""
        mock_message.text = "This is a valid description with enough length to pass validation."

        await process_escalation_description(mock_message, mock_state, locale="en")

        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once_with(EscalationStates.waiting_for_title)
        mock_message.answer.assert_called_once()

    async def test_process_escalation_description_too_short(self, mock_message, mock_state):
        """Test processing description that is too short."""
        mock_message.text = "Short"

        await process_escalation_description(mock_message, mock_state, locale="en")

        mock_message.answer.assert_called_once()
        mock_state.update_data.assert_not_called()
        mock_state.set_state.assert_not_called()

    async def test_process_escalation_title_success(
        self, mock_message, mock_state, mock_user, mock_auth_token
    ):
        """Test processing valid escalation title."""
        mock_message.text = "Valid Title"
        mock_state.get_data.return_value = {
            "category": "Technical",
            "description": "This is a valid description.",
        }

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.create_escalation",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = {"id": 123, "reason": "Valid Title"}

            await process_escalation_title(
                mock_message, mock_state, mock_user, mock_auth_token, locale="en"
            )

        mock_create.assert_called_once()
        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()

    async def test_process_escalation_title_too_short(
        self, mock_message, mock_state, mock_user, mock_auth_token
    ):
        """Test processing title that is too short."""
        mock_message.text = "AB"

        await process_escalation_title(
            mock_message, mock_state, mock_user, mock_auth_token, locale="en"
        )

        mock_message.answer.assert_called_once()
        mock_state.clear.assert_not_called()

    async def test_process_escalation_title_create_failed(
        self, mock_message, mock_state, mock_user, mock_auth_token
    ):
        """Test processing title when create fails."""
        mock_message.text = "Valid Title"
        mock_state.get_data.return_value = {
            "category": "Technical",
            "description": "This is a valid description.",
        }

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.create_escalation",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = None

            await process_escalation_title(
                mock_message, mock_state, mock_user, mock_auth_token, locale="en"
            )

        mock_message.answer.assert_called_once()
        mock_state.clear.assert_called_once()

    async def test_my_escalations_success(
        self, mock_callback, mock_user, mock_auth_token, mock_escalations
    ):
        """Test my escalations with data."""
        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_user_escalations",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_escalations
            with patch(
                "telegram_bot.handlers.escalation.format_escalation_list",
                return_value="Escalation List",
            ):
                with patch(
                    "telegram_bot.handlers.escalation.get_my_escalations_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await my_escalations(
                        mock_callback, mock_user, mock_auth_token, locale="en"
                    )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_my_escalations_no_user(self, mock_callback, mock_auth_token):
        """Test my escalations without user."""
        await my_escalations(mock_callback, None, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_my_escalations_empty(
        self, mock_callback, mock_user, mock_auth_token
    ):
        """Test my escalations with no data."""
        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_user_escalations",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []
            with patch(
                "telegram_bot.handlers.escalation.get_my_escalations_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await my_escalations(
                    mock_callback, mock_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()

    async def test_escalation_details_success(self, mock_callback, mock_auth_token):
        """Test escalation details - success."""
        mock_callback.data = "escalation_123"
        # Use escalation_service schema: reason (not title), type (not category), context.description
        escalation_data = {
            "id": 123,
            "reason": "Test Escalation",
            "status": "open",
            "type": "IT",
            "created_at": "2024-01-15",
            "context": {"description": "Test description"},
        }

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = escalation_data
            with patch(
                "telegram_bot.handlers.escalation.get_escalation_details_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await escalation_details(mock_callback, mock_auth_token, locale="en")

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_escalation_details_not_found(self, mock_callback, mock_auth_token):
        """Test escalation details - not found."""
        mock_callback.data = "escalation_999"

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            await escalation_details(mock_callback, mock_auth_token, locale="en")

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_escalation_details_no_auth(self, mock_callback):
        """Test escalation details without auth token."""
        mock_callback.data = "escalation_123"

        await escalation_details(mock_callback, None, locale="en")

        mock_callback.answer.assert_called_once()

    async def test_escalation_details_various_statuses(
        self, mock_callback, mock_auth_token
    ):
        """Test escalation details with different statuses."""
        statuses = ["open", "in_progress", "resolved", "closed"]

        for idx, status in enumerate(statuses):
            mock_callback.data = f"escalation_{idx + 1}"  # ID should be a number
            # Use escalation_service schema
            escalation_data = {
                "id": idx + 1,
                "reason": "Test",
                "status": status,
                "type": "GENERAL",
                "created_at": "2024-01-15",
                "context": {"description": "Test"},
            }

            with patch(
                "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = escalation_data
                with patch(
                    "telegram_bot.handlers.escalation.get_escalation_details_keyboard"
                ) as mock_kb:
                    mock_kb.return_value.as_markup.return_value = MagicMock()

                    await escalation_details(
                        mock_callback, mock_auth_token, locale="en"
                    )

            # Reset the mock for next iteration
            mock_callback.message.edit_text.reset_mock()
            mock_callback.answer.reset_mock()

    async def test_view_escalation_from_notification_success(
        self, mock_callback, mock_user, mock_auth_token
    ):
        """Test viewing escalation from notification - success."""
        mock_callback.data = "escalation:view:123"
        escalation_data = {
            "id": 123,
            "reason": "Test Escalation",
            "status": "PENDING",
            "type": "IT",
            "priority": "MEDIUM",
            "created_at": "2024-01-15",
            "user_id": 1,  # Same as mock_user["id"]
            "context": {"description": "Test description"},
        }

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = escalation_data

            await view_escalation_from_notification(
                mock_callback, mock_user, mock_auth_token, locale="en"
            )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_view_escalation_from_notification_no_auth(
        self, mock_callback, mock_auth_token
    ):
        """Test viewing escalation from notification without auth."""
        mock_callback.data = "escalation:view:123"

        await view_escalation_from_notification(
            mock_callback, None, mock_auth_token, locale="en"
        )

        mock_callback.answer.assert_called_once()

    async def test_view_escalation_from_notification_not_found(
        self, mock_callback, mock_user, mock_auth_token
    ):
        """Test viewing escalation from notification - escalation not found."""
        mock_callback.data = "escalation:view:999"

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            await view_escalation_from_notification(
                mock_callback, mock_user, mock_auth_token, locale="en"
            )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_view_escalation_from_notification_unauthorized(
        self, mock_callback, mock_auth_token
    ):
        """Test viewing escalation from notification - user not authorized."""
        mock_callback.data = "escalation:view:123"
        # User with different ID than escalation owner
        different_user = {"id": 999, "first_name": "Other", "role": "USER"}
        escalation_data = {
            "id": 123,
            "reason": "Test Escalation",
            "status": "PENDING",
            "type": "IT",
            "user_id": 1,  # Different from different_user["id"]
            "assigned_to": 2,  # Different from different_user["id"]
            "context": {"description": "Test description"},
        }

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = escalation_data

            await view_escalation_from_notification(
                mock_callback, different_user, mock_auth_token, locale="en"
            )

        mock_callback.answer.assert_called_once()
        assert "show_alert" in mock_callback.answer.call_args.kwargs

    async def test_view_escalation_from_notification_assigned_to_user(
        self, mock_callback, mock_auth_token
    ):
        """Test viewing escalation when assigned to current user."""
        mock_callback.data = "escalation:view:123"
        # User is the assignee
        assigned_user = {"id": 5, "first_name": "Assignee", "role": "USER"}
        escalation_data = {
            "id": 123,
            "reason": "Test Escalation",
            "status": "PENDING",
            "type": "IT",
            "user_id": 1,  # Different user created it
            "assigned_to": 5,  # Same as assigned_user["id"]
            "context": {"description": "Test description"},
        }

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = escalation_data

            await view_escalation_from_notification(
                mock_callback, assigned_user, mock_auth_token, locale="en"
            )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_view_escalation_from_notification_hr_role(
        self, mock_callback, mock_auth_token
    ):
        """Test viewing escalation as HR user."""
        mock_callback.data = "escalation:view:123"
        # User is HR (can view any escalation)
        hr_user = {"id": 10, "first_name": "HR", "role": "HR"}
        escalation_data = {
            "id": 123,
            "reason": "Test Escalation",
            "status": "PENDING",
            "type": "IT",
            "user_id": 99,  # Different user
            "assigned_to": 88,  # Different user
            "context": {"description": "Test description"},
        }

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = escalation_data

            await view_escalation_from_notification(
                mock_callback, hr_user, mock_auth_token, locale="en"
            )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_view_escalation_with_assigned_name(
        self, mock_callback, mock_user, mock_auth_token
    ):
        """Test viewing escalation with assigned_to_name field."""
        mock_callback.data = "escalation:view:123"
        escalation_data = {
            "id": 123,
            "reason": "Test Escalation",
            "status": "PENDING",
            "type": "IT",
            "priority": "MEDIUM",
            "created_at": "2024-01-15",
            "user_id": 1,
            "assigned_to": 2,
            "assigned_to_name": "John Doe",
            "context": {"description": "Test description"},
        }

        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_escalation_status",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = escalation_data

            await view_escalation_from_notification(
                mock_callback, mock_user, mock_auth_token, locale="en"
            )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    async def test_list_my_escalations(self, mock_callback, mock_user, mock_auth_token):
        """Test list_my_escalations calls my_escalations."""
        with patch(
            "telegram_bot.handlers.escalation.escalation_client.get_user_escalations",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = []
            with patch(
                "telegram_bot.handlers.escalation.get_my_escalations_keyboard"
            ) as mock_kb:
                mock_kb.return_value.as_markup.return_value = MagicMock()

                await list_my_escalations(
                    mock_callback, mock_user, mock_auth_token, locale="en"
                )

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()
