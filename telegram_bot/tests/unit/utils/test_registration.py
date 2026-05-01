"""Unit tests for telegram_bot/utils/registration.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram_bot.utils.registration import register_by_token


class TestRegisterByToken:
    """Test cases for register_by_token function."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up common mocks."""
        self.mock_tg_user = MagicMock()
        self.mock_tg_user.id = 123456
        self.mock_tg_user.username = "testuser"
        self.mock_tg_user.first_name = "John"
        self.mock_tg_user.last_name = "Doe"

        self.mock_state = MagicMock()
        self.mock_state.clear = AsyncMock()

    @patch("telegram_bot.utils.registration.validate_invitation_token")
    async def test_invalid_token_format(self, mock_validate):
        """Test registration with invalid token format."""
        mock_validate.return_value = False

        success, result = await register_by_token("bad_token", self.mock_tg_user, self.mock_state)

        assert success is False
        assert "Invalid token format" in result

    @patch("telegram_bot.utils.registration.validate_invitation_token")
    @patch("telegram_bot.utils.registration.auth_client")
    async def test_expired_or_invalid_token(self, mock_auth, mock_validate):
        """Test registration with expired/invalid token."""
        mock_validate.return_value = True
        mock_auth.validate_invitation_token = AsyncMock(return_value=None)

        success, result = await register_by_token("expired_token", self.mock_tg_user, self.mock_state)

        assert success is False
        assert "Invalid or expired" in result

    @patch("telegram_bot.utils.registration.validate_invitation_token")
    @patch("telegram_bot.utils.registration.auth_client")
    async def test_registration_api_failure(self, mock_auth, mock_validate):
        """Test when registration API call fails."""
        mock_validate.return_value = True
        mock_auth.validate_invitation_token = AsyncMock(return_value={"token": "valid"})
        mock_auth.register_with_invitation = AsyncMock(return_value=None)

        success, result = await register_by_token("valid_token", self.mock_tg_user, self.mock_state)

        assert success is False
        assert "Registration failed" in result

    @patch("telegram_bot.utils.registration.validate_invitation_token")
    @patch("telegram_bot.utils.registration.auth_client")
    @patch("telegram_bot.utils.registration.user_cache")
    async def test_registration_user_data_fetch_fails(self, mock_cache, mock_auth, mock_validate):
        """Test when registration succeeds but user data fetch fails."""
        mock_validate.return_value = True
        mock_auth.validate_invitation_token = AsyncMock(return_value={"token": "valid"})
        mock_auth.register_with_invitation = AsyncMock(
            return_value={
                "access_token": "access_123",
                "refresh_token": "refresh_123",
            }
        )
        mock_auth.get_current_user = AsyncMock(return_value=None)

        success, result = await register_by_token("valid_token", self.mock_tg_user, self.mock_state)

        assert success is False
        assert "Failed to retrieve user information" in result

    @patch("telegram_bot.utils.registration.validate_invitation_token")
    @patch("telegram_bot.utils.registration.auth_client")
    @patch("telegram_bot.utils.registration.user_cache")
    async def test_registration_success(self, mock_cache, mock_auth, mock_validate):
        """Test successful registration with user caching."""
        mock_validate.return_value = True
        mock_auth.validate_invitation_token = AsyncMock(return_value={"token": "valid"})
        mock_auth.register_with_invitation = AsyncMock(
            return_value={
                "access_token": "access_123",
                "refresh_token": "refresh_123",
            }
        )
        user_data = {"id": 1, "first_name": "John", "email": "john@example.com"}
        mock_auth.get_current_user = AsyncMock(return_value=user_data)
        mock_cache.set_user = AsyncMock(return_value=True)

        success, result = await register_by_token("valid_token", self.mock_tg_user, self.mock_state)

        assert success is True
        assert result == user_data
        # Verify cache was set with correct data including tokens
        mock_cache.set_user.assert_called_once()
        call_args = mock_cache.set_user.call_args
        assert call_args[0][0] == 123456  # telegram_id
        assert call_args[0][1]["id"] == 1
        assert call_args[0][1]["access_token"] == "access_123"
        assert call_args[0][1]["refresh_token"] == "refresh_123"
        # Verify state was cleared
        self.mock_state.clear.assert_called_once()
