"""Unit tests for core/telegram.py module."""

from unittest.mock import AsyncMock, MagicMock, patch

from auth_service.core import telegram


class TestVerifyTelegramApiKey:
    """Tests for verify_telegram_api_key function."""

    def test_verify_telegram_api_key_valid(self):
        """Test verify_telegram_api_key with valid key."""
        with patch.object(telegram.settings, "TELEGRAM_API_KEY", "valid-api-key"):
            result = telegram.verify_telegram_api_key("valid-api-key")
            assert result is True

    def test_verify_telegram_api_key_invalid(self):
        """Test verify_telegram_api_key with invalid key."""
        with patch.object(telegram.settings, "TELEGRAM_API_KEY", "valid-api-key"):
            result = telegram.verify_telegram_api_key("invalid-api-key")
            assert result is False

    def test_verify_telegram_api_key_empty(self):
        """Test verify_telegram_api_key with empty key."""
        with patch.object(telegram.settings, "TELEGRAM_API_KEY", "valid-api-key"):
            result = telegram.verify_telegram_api_key("")
            assert result is False

    def test_verify_telegram_api_key_none(self):
        """Test verify_telegram_api_key when settings key is empty."""
        with patch.object(telegram.settings, "TELEGRAM_API_KEY", ""):
            result = telegram.verify_telegram_api_key("")
            assert result is True  # Both empty means they match


class TestVerifyTelegramUserExists:
    """Tests for verify_telegram_user_exists function."""

    async def test_verify_telegram_user_exists_true(self):
        """Test verify_telegram_user_exists when user exists."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # User exists
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await telegram.verify_telegram_user_exists(mock_db, 123456789)

        assert result is True
        mock_db.execute.assert_called_once()

    async def test_verify_telegram_user_exists_false(self):
        """Test verify_telegram_user_exists when user does not exist."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # User does not exist
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await telegram.verify_telegram_user_exists(mock_db, 999999999)

        assert result is False
        mock_db.execute.assert_called_once()

    async def test_verify_telegram_user_exists_executes_query(self):
        """Test that execute is called with a query."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        await telegram.verify_telegram_user_exists(mock_db, 123456789)

        # Check that execute was called with some argument
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args[0]
        assert len(call_args) > 0  # Some query was passed
