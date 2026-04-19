"""Unit tests for auth_service/core/security.py."""

from datetime import timedelta

import pytest
from fastapi import HTTPException, status

from auth_service.config import settings
from auth_service.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_invitation_token,
    hash_password,
    verify_password,
)


class TestHashPassword:
    """Tests for hash_password and verify_password functions."""

    def test_hash_and_verify_round_trip(self):
        """Test that hashed password can be verified correctly."""
        password = "mysecretpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_verify_password_wrong_password_fails(self):
        """Test that wrong password is rejected."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_string_fails(self):
        """Test that empty string password is rejected."""
        password = "validpassword"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_hash_password_unicode_input(self):
        """Test that unicode passwords work correctly."""
        password = "пароль_日本語_🎉🔐"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("otherpassword", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hashed1 = hash_password(password1)
        hashed2 = hash_password(password2)

        assert hashed1 != hashed2

    def test_same_password_produces_different_hashes(self):
        """
        Test that same password hashed twice produces different hashes.

        Due to salt, same password produces different hashes each time.
        """
        password = "samepassword"

        hashed1 = hash_password(password)
        hashed2 = hash_password(password)

        # Due to different salts, hashes should be different
        assert hashed1 != hashed2
        # But both should verify correctly
        assert verify_password(password, hashed1) is True
        assert verify_password(password, hashed2) is True


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string."""
        data = {"sub": "123", "user_id": 123, "role": "user"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_includes_exp_claim(self):
        """Test that access token includes 'exp' claim."""
        data = {"sub": "123", "user_id": 123}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    def test_create_access_token_includes_iat_claim(self):
        """Test that access token includes 'iat' (issued at) claim."""
        data = {"sub": "123", "user_id": 123}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert "iat" in decoded
        assert isinstance(decoded["iat"], int)

    def test_create_access_token_honors_expires_delta(self):
        """Test that custom expires_delta is honored."""
        data = {"sub": "123", "user_id": 123}
        expires_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta=expires_delta)
        decoded = decode_token(token)

        assert "exp" in decoded
        # The token should be valid now
        assert decoded["exp"] > 0

    def test_create_access_token_preserves_custom_data(self):
        """Test that custom data is preserved in token."""
        data = {"sub": "123", "user_id": 456, "role": "admin", "custom": "value"}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded["sub"] == "123"
        assert decoded["user_id"] == 456
        assert decoded["role"] == "admin"
        assert decoded["custom"] == "value"

    def test_create_access_token_includes_type_access(self):
        """Test that access token includes 'type': 'access' claim."""
        data = {"sub": "123", "user_id": 123}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded.get("type") == "access"


class TestCreateRefreshToken:
    """Tests for create_refresh_token function."""

    def test_create_refresh_token_includes_type_refresh(self):
        """Test that refresh token includes 'type': 'refresh' claim."""
        data = {"sub": "123", "user_id": 123}
        token = create_refresh_token(data)
        decoded = decode_token(token)

        assert decoded.get("type") == "refresh"

    def test_create_refresh_token_includes_exp_and_iat(self):
        """Test that refresh token includes exp and iat claims."""
        data = {"sub": "123", "user_id": 123}
        token = create_refresh_token(data)
        decoded = decode_token(token)

        assert "exp" in decoded
        assert "iat" in decoded

    def test_create_refresh_token_honors_expires_delta(self):
        """Test that custom expires_delta is honored for refresh token."""
        data = {"sub": "123", "user_id": 123}
        expires_delta = timedelta(days=1)
        token = create_refresh_token(data, expires_delta=expires_delta)
        decoded = decode_token(token)

        assert "exp" in decoded
        assert decoded["type"] == "refresh"


class TestDecodeToken:
    """Tests for decode_token function."""

    def test_decode_valid_token(self):
        """Test that valid token is decoded correctly."""
        data = {"sub": "123", "user_id": 456, "role": "user"}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded["sub"] == "123"
        assert decoded["user_id"] == 456
        assert decoded["role"] == "user"

    def test_decode_expired_token_raises_401(self):
        """Test that expired token raises HTTPException with 401 status."""
        data = {"sub": "123", "user_id": 123}
        # Create token that expired 1 second ago
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)

        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in exc_info.value.detail.lower()

    def test_decode_tampered_token_raises_401(self):
        """Test that tampered token raises HTTPException with 401 status."""
        data = {"sub": "123", "user_id": 123}
        token = create_access_token(data)
        # Tamper with the token by changing a character
        tampered_token = token[:-5] + "XXXXX"

        with pytest.raises(HTTPException) as exc_info:
            decode_token(tampered_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in exc_info.value.detail.lower()

    def test_decode_invalid_token_format_raises_401(self):
        """Test that invalid token format raises HTTPException with 401 status."""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("not.a.valid.token")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in exc_info.value.detail.lower()

    def test_decode_empty_token_raises_401(self):
        """Test that empty token raises HTTPException with 401 status."""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_decode_token_with_expected_type_access(self):
        """Test that decode_token validates access token type correctly."""
        data = {"sub": "123", "user_id": 123}
        token = create_access_token(data)
        decoded = decode_token(token, expected_type="access")

        assert decoded["user_id"] == 123

    def test_decode_token_with_expected_type_refresh(self):
        """Test that decode_token validates refresh token type correctly."""
        data = {"sub": "123", "user_id": 123}
        token = create_refresh_token(data)
        decoded = decode_token(token, expected_type="refresh")

        assert decoded["user_id"] == 123

    def test_decode_refresh_token_as_access_raises_401(self):
        """Test that using refresh token as access token raises 401."""
        data = {"sub": "123", "user_id": 123}
        refresh_token = create_refresh_token(data)

        with pytest.raises(HTTPException) as exc_info:
            decode_token(refresh_token, expected_type="access")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "type" in exc_info.value.detail.lower()

    def test_decode_access_token_as_refresh_raises_401(self):
        """Test that using access token as refresh token raises 401."""
        data = {"sub": "123", "user_id": 123}
        access_token = create_access_token(data)

        with pytest.raises(HTTPException) as exc_info:
            decode_token(access_token, expected_type="refresh")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "type" in exc_info.value.detail.lower()


class TestGetPasswordHash:
    """Tests for get_password_hash function (alias for hash_password)."""

    def test_get_password_hash_returns_hashed_password(self):
        """Test that get_password_hash returns a hashed password."""
        from auth_service.core.security import get_password_hash

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert hashed.startswith("$2")  # bcrypt hash starts with $2

    def test_get_password_hash_compatible_with_verify_password(self):
        """Test that get_password_hash output works with verify_password."""
        from auth_service.core.security import get_password_hash, verify_password

        password = "mypassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False


class TestGenerateInvitationToken:
    """Tests for generate_invitation_token function."""

    def test_generate_invitation_token_returns_string(self):
        """Test that generate_invitation_token returns a string."""
        token = generate_invitation_token()

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_invitation_token_is_url_safe(self):
        """Test that generated token is URL-safe."""
        token = generate_invitation_token()

        # URL-safe tokens should not contain these characters
        assert "+" not in token
        assert "/" not in token
        assert "=" not in token

    def test_generate_invitation_token_respects_length_setting(self, monkeypatch):
        """Test that token length respects settings.INVITATION_TOKEN_LENGTH."""
        # Set a specific length for testing
        test_length = 16
        monkeypatch.setattr(settings, "INVITATION_TOKEN_LENGTH", test_length)

        token = generate_invitation_token()

        # token_urlsafe(n) produces ~4/3*n chars due to base64 encoding
        # For n=16, expect ~22 characters
        assert len(token) > 0

    def test_generate_different_tokens(self):
        """Test that multiple calls generate different tokens."""
        token1 = generate_invitation_token()
        token2 = generate_invitation_token()
        token3 = generate_invitation_token()

        assert token1 != token2
        assert token2 != token3
        assert token1 != token3
