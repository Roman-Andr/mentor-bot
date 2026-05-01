"""Unit tests for auth_service/schemas/auth.py."""

from datetime import UTC, datetime, timedelta

import pytest
from auth_service.core import UserRole
from auth_service.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TelegramApiKeyAuth,
    TelegramAuthRequest,
    TelegramRegistrationRequest,
    Token,
    TokenPayload,
)


class TestToken:
    """Tests for Token schema."""

    def test_token_expires_in_future(self):
        """Test expires_in returns positive seconds for future expiration."""
        future_time = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            access_token="test_access",
            refresh_token="test_refresh",
            expires_at=future_time,
            user_id=1,
            role=UserRole.NEWBIE,
        )
        assert token.expires_in > 0
        assert token.expires_in <= 3600  # At most 1 hour

    def test_token_expires_in_past(self):
        """Test expires_in returns 0 for expired token."""
        past_time = datetime.now(UTC) - timedelta(hours=1)
        token = Token(
            access_token="test_access",
            refresh_token="test_refresh",
            expires_at=past_time,
            user_id=1,
            role=UserRole.NEWBIE,
        )
        assert token.expires_in == 0

    def test_token_expires_in_now(self):
        """Test expires_in returns 0 for token expiring now."""
        now = datetime.now(UTC)
        token = Token(
            access_token="test_access",
            refresh_token="test_refresh",
            expires_at=now,
            user_id=1,
            role=UserRole.NEWBIE,
        )
        # Due to timing, this could be 0 or a small positive number
        assert token.expires_in >= 0
        assert token.expires_in < 1  # Should be very close to 0


class TestTokenPayload:
    """Tests for TokenPayload schema."""

    def test_token_payload_creation(self):
        """Test TokenPayload can be created with valid data."""
        payload = TokenPayload(sub="1", user_id=1, role=UserRole.NEWBIE)
        assert payload.sub == "1"
        assert payload.user_id == 1
        assert payload.role == UserRole.NEWBIE


class TestLoginRequest:
    """Tests for LoginRequest schema."""

    def test_login_request_valid_email(self):
        """Test LoginRequest accepts valid email."""
        request = LoginRequest(email="test@example.com", password="password123")
        assert request.email == "test@example.com"
        assert request.password == "password123"


class TestRefreshTokenRequest:
    """Tests for RefreshTokenRequest schema."""

    def test_refresh_token_request(self):
        """Test RefreshTokenRequest can be created."""
        request = RefreshTokenRequest(refresh_token="test_refresh_token")
        assert request.refresh_token == "test_refresh_token"


class TestPasswordResetRequest:
    """Tests for PasswordResetRequest schema."""

    def test_password_reset_request(self):
        """Test PasswordResetRequest can be created."""
        request = PasswordResetRequest(email="test@example.com")
        assert request.email == "test@example.com"


class TestPasswordResetConfirm:
    """Tests for PasswordResetConfirm schema."""

    def test_password_reset_confirm_valid_password(self):
        """Test PasswordResetConfirm accepts valid password (8+ chars)."""
        confirm = PasswordResetConfirm(token="test_token", new_password="newpass123")
        assert confirm.token == "test_token"
        assert confirm.new_password == "newpass123"

    def test_password_reset_confirm_short_password_raises(self):
        """Test PasswordResetConfirm rejects short password (< 8 chars)."""
        with pytest.raises(ValueError):
            PasswordResetConfirm(token="test_token", new_password="short")


class TestChangePasswordRequest:
    """Tests for ChangePasswordRequest schema."""

    def test_change_password_request_valid(self):
        """Test ChangePasswordRequest accepts valid passwords."""
        request = ChangePasswordRequest(current_password="oldpass123", new_password="newpass123")
        assert request.current_password == "oldpass123"
        assert request.new_password == "newpass123"

    def test_change_password_request_short_new_password_raises(self):
        """Test ChangePasswordRequest rejects short new password."""
        with pytest.raises(ValueError):
            ChangePasswordRequest(current_password="oldpass123", new_password="short")


class TestTelegramAuthRequest:
    """Tests for TelegramAuthRequest schema."""

    def test_telegram_auth_request_full(self):
        """Test TelegramAuthRequest with all fields."""
        request = TelegramAuthRequest(
            telegram_id=123456789,
            username="@testuser",
            first_name="Test",
            last_name="User",
        )
        assert request.telegram_id == 123456789
        assert request.username == "@testuser"
        assert request.first_name == "Test"
        assert request.last_name == "User"

    def test_telegram_auth_request_minimal(self):
        """Test TelegramAuthRequest with minimal fields."""
        request = TelegramAuthRequest(telegram_id=123456789, first_name="Test")
        assert request.telegram_id == 123456789
        assert request.first_name == "Test"
        assert request.username is None
        assert request.last_name is None


class TestTelegramRegistrationRequest:
    """Tests for TelegramRegistrationRequest schema."""

    def test_telegram_registration_request_full(self):
        """Test TelegramRegistrationRequest with all fields."""
        request = TelegramRegistrationRequest(
            telegram_id=123456789,
            username="@testuser",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
        )
        assert request.telegram_id == 123456789
        assert request.username == "@testuser"
        assert request.first_name == "Test"
        assert request.last_name == "User"
        assert request.phone == "+1234567890"

    def test_telegram_registration_request_minimal(self):
        """Test TelegramRegistrationRequest with minimal fields."""
        request = TelegramRegistrationRequest(telegram_id=123456789)
        assert request.telegram_id == 123456789
        assert request.username is None
        assert request.first_name is None
        assert request.last_name is None
        assert request.phone is None

    def test_telegram_registration_request_phone_too_long_raises(self):
        """Test TelegramRegistrationRequest rejects phone number > 20 chars."""
        with pytest.raises(ValueError):
            TelegramRegistrationRequest(telegram_id=123456789, phone="1" * 21)


class TestTelegramApiKeyAuth:
    """Tests for TelegramApiKeyAuth schema."""

    def test_telegram_api_key_auth(self):
        """Test TelegramApiKeyAuth can be created."""
        auth = TelegramApiKeyAuth(api_key="test_api_key", telegram_id=123456789)
        assert auth.api_key == "test_api_key"
        assert auth.telegram_id == 123456789
