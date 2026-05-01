"""Unit tests for telegram_bot/handlers/common.py (profile and mentor related)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram_bot.handlers.common import (
    cmd_about,
    my_mentor,
    schedule_mentor,
)


class TestCmdAbout:
    """Test cases for cmd_about handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock()
        self.mock_message.answer = AsyncMock()

    async def test_about_command(self):
        """Test about command displays correctly."""
        await cmd_about(self.mock_message, locale="en")

        self.mock_message.answer.assert_called_once()


class TestMyMentor:
    """Test cases for my_mentor handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_message = MagicMock()
        self.mock_message.answer = AsyncMock()

        self.mock_callback = MagicMock()
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

        self.user = {"id": 1, "first_name": "John", "last_name": "Doe", "mentor_id": 2}
        self.test_token = "mock_token_for_testing"

    @patch("telegram_bot.handlers.common.auth_client")
    async def test_my_mentor_with_mentor(self, mock_auth):
        """Test my_mentor displays mentor info when assigned."""
        mentor_data = {
            "id": 2,
            "first_name": "Jane",
            "last_name": "Smith",
            "position": "Senior Developer",
            "department": {"name": "Engineering"},
            "email": "jane@example.com",
            "phone": "+1234567890",
        }
        mock_auth.get_mentor_info = AsyncMock(return_value=mentor_data)

        await my_mentor(self.mock_message, self.user, self.test_token, locale="en")

        mock_auth.get_mentor_info.assert_called_once_with(2, self.test_token)
        self.mock_message.answer.assert_called_once()

    @patch("telegram_bot.handlers.common.auth_client")
    async def test_my_mentor_no_mentor(self, mock_auth):
        """Test my_mentor displays no mentor message when unassigned."""
        user_no_mentor = {"id": 1, "first_name": "John", "last_name": "Doe"}

        await my_mentor(self.mock_message, user_no_mentor, self.test_token, locale="en")

        mock_auth.get_mentor_info.assert_not_called()
        self.mock_message.answer.assert_called_once()

    async def test_my_mentor_no_user(self):
        """Test my_mentor requires authentication."""
        await my_mentor(self.mock_message, None, self.test_token, locale="en")

        call_args = self.mock_message.answer.call_args
        assert "common.auth_required" in str(call_args)


class TestScheduleMentor:
    """Test cases for schedule_mentor handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_callback = MagicMock()
        self.mock_callback.answer = AsyncMock()
        self.mock_callback.message = MagicMock()
        self.mock_callback.message.edit_text = AsyncMock()

    async def test_schedule_mentor_callback(self):
        """Test schedule_mentor handler."""
        await schedule_mentor(self.mock_callback, locale="en")

        self.mock_callback.answer.assert_called_once()
        self.mock_callback.message.edit_text.assert_called_once()

    async def test_schedule_mentor_no_message(self):
        """Test schedule_mentor when callback has no message."""
        self.mock_callback.message = None

        result = await schedule_mentor(self.mock_callback, locale="en")

        assert result is None
