"""Unit tests for password reset API endpoints."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from auth_service.main import app
from auth_service.models import PasswordResetToken, User
from auth_service.core.enums import UserRole


def get_test_client():
    """Create a TestClient without lifespan events."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def active_user():
    """Create an active user for testing."""
    return User(
        id=1,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        employee_id="EMP001",
        password_hash="$2b$12$testhash",
        is_active=True,
        is_verified=True,
        role=UserRole.NEWBIE,
    )


@pytest.fixture
def inactive_user():
    """Create an inactive user for testing."""
    return User(
        id=2,
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        employee_id="EMP002",
        password_hash="$2b$12$testhash",
        is_active=False,
        is_verified=True,
        role=UserRole.NEWBIE,
    )


class TestPasswordResetRequestEndpoint:
    """Tests for POST /api/v1/password-reset/request endpoint."""

    def test_request_reset_success(self, active_user):
        """Test successful password reset request returns generic message."""
        # Patch the PasswordResetService class where it's imported in the endpoint module
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.request_reset = AsyncMock(return_value=(True, "raw-token-123", active_user))

            with patch("auth_service.api.endpoints.password_reset.notification_service_client") as mock_client:
                mock_client.send_password_reset_email = AsyncMock(return_value=True)

                client = get_test_client()
                response = client.post(
                    "/api/v1/password-reset/request",
                    json={"email": "test@example.com"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "If an account with this email exists" in data["message"]

    def test_request_reset_nonexistent_email(self):
        """Test password reset request for non-existent email returns generic message (no enumeration)."""
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            # Return success=True but token=None (no email sent)
            mock_service.request_reset = AsyncMock(return_value=(True, None, None))

            client = get_test_client()
            response = client.post(
                "/api/v1/password-reset/request",
                json={"email": "nonexistent@example.com"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # Should return same message to prevent email enumeration
            assert "If an account with this email exists" in data["message"]

    def test_request_reset_inactive_user(self, inactive_user):
        """Test password reset request for inactive user returns generic message."""
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            # Return success=True but token=None (no email sent)
            mock_service.request_reset = AsyncMock(return_value=(True, None, None))

            client = get_test_client()
            response = client.post(
                "/api/v1/password-reset/request",
                json={"email": "inactive@example.com"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_request_reset_rate_limited(self, active_user):
        """Test password reset request when rate limit exceeded."""
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            # Return success=True but token=None (rate limited)
            mock_service.request_reset = AsyncMock(return_value=(True, None, None))

            client = get_test_client()
            response = client.post(
                "/api/v1/password-reset/request",
                json={"email": "test@example.com"},
            )

            # Should still return 200 to prevent enumeration
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_request_reset_invalid_email_format(self):
        """Test password reset request with invalid email format returns 422."""
        client = get_test_client()
        response = client.post(
            "/api/v1/password-reset/request",
            json={"email": "not-an-email"},
        )

        assert response.status_code == 422


class TestPasswordResetValidateEndpoint:
    """Tests for POST /api/v1/password-reset/validate endpoint."""

    def test_validate_token_success(self, active_user):
        """Test validating a valid reset token."""
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.validate_token = AsyncMock(return_value=active_user)

            client = get_test_client()
            response = client.post(
                "/api/v1/password-reset/validate",
                json={"token": "valid-reset-token"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Token is valid" in data["message"]

    def test_validate_token_invalid(self):
        """Test validating an invalid or expired token returns 400."""
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.validate_token = AsyncMock(return_value=None)

            client = get_test_client()
            response = client.post(
                "/api/v1/password-reset/validate",
                json={"token": "invalid-token"},
            )

            assert response.status_code == 400
            assert "Invalid or expired token" in response.json()["detail"]

    def test_validate_token_missing(self):
        """Test validating with missing token returns 422."""
        client = get_test_client()
        response = client.post(
            "/api/v1/password-reset/validate",
            json={},
        )

        assert response.status_code == 422


class TestPasswordResetConfirmEndpoint:
    """Tests for POST /api/v1/password-reset/confirm endpoint."""

    def test_confirm_reset_success(self, active_user):
        """Test successful password reset confirmation."""
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.validate_token = AsyncMock(return_value=active_user)
            mock_service.confirm_reset = AsyncMock(return_value=True)

            with patch("auth_service.api.endpoints.password_reset.notification_service_client") as mock_client:
                mock_client.send_password_reset_confirmation_email = AsyncMock(return_value=True)

                client = get_test_client()
                response = client.post(
                    "/api/v1/password-reset/confirm",
                    json={"token": "valid-token", "new_password": "newSecurePass123"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "Password updated successfully" in data["message"]

    def test_confirm_reset_invalid_token(self):
        """Test password reset confirmation with invalid token returns 400."""
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.validate_token = AsyncMock(return_value=None)  # Validate returns None first
            mock_service.confirm_reset = AsyncMock(return_value=False)

            client = get_test_client()
            response = client.post(
                "/api/v1/password-reset/confirm",
                json={"token": "invalid-token", "new_password": "newSecurePass123"},
            )

            assert response.status_code == 400
            assert "Invalid or expired token" in response.json()["detail"]

    def test_confirm_reset_weak_password(self):
        """Test password reset confirmation with weak password returns 422."""
        client = get_test_client()
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={"token": "valid-token", "new_password": "weak"},  # Too short
        )

        assert response.status_code == 422
        # Pydantic validation error for min_length
        assert "password" in response.text.lower() or "new_password" in response.text.lower()

    def test_confirm_reset_missing_token(self):
        """Test password reset confirmation with missing token returns 422."""
        client = get_test_client()
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={"new_password": "newSecurePass123"},
        )

        assert response.status_code == 422

    def test_confirm_reset_missing_password(self):
        """Test password reset confirmation with missing password returns 422."""
        client = get_test_client()
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={"token": "valid-token"},
        )

        assert response.status_code == 422


class TestPasswordResetIntegration:
    """Integration tests for the full password reset flow."""

    def test_full_flow_success(self, active_user):
        """Test the complete password reset flow: request -> validate -> confirm."""
        token = "reset-token-123"

        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.request_reset = AsyncMock(return_value=(True, token, active_user))
            mock_service.validate_token = AsyncMock(return_value=active_user)
            mock_service.confirm_reset = AsyncMock(return_value=True)

            with patch("auth_service.api.endpoints.password_reset.notification_service_client") as mock_client:
                mock_client.send_password_reset_email = AsyncMock(return_value=True)
                mock_client.send_password_reset_confirmation_email = AsyncMock(return_value=True)

                client = get_test_client()

                # Request
                response = client.post(
                    "/api/v1/password-reset/request",
                    json={"email": "test@example.com"},
                )
                assert response.status_code == 200
                assert response.json()["success"] is True


class TestPasswordResetServiceUnit:
    """Unit tests for PasswordResetService."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def mock_uow(self):
        """Create a mock unit of work."""
        uow = MagicMock()
        uow.users = MagicMock()
        uow.users.get_by_email = AsyncMock()
        uow.users.get_by_id = AsyncMock()
        uow.commit = AsyncMock()
        uow.rollback = AsyncMock()
        return uow

    def test_token_generation(self, mock_uow, mock_session, active_user):
        """Test that tokens are generated with correct format."""
        from auth_service.services.password_reset import PasswordResetService

        service = PasswordResetService(mock_uow, mock_session)
        token = service._generate_token()

        # Token should be non-empty and reasonable length
        assert len(token) > 20
        # Should be URL-safe (no problematic characters)
        assert " " not in token
        assert "\n" not in token

    def test_token_hashing(self, mock_uow, mock_session):
        """Test that token hashing produces consistent results."""
        from auth_service.services.password_reset import PasswordResetService

        service = PasswordResetService(mock_uow, mock_session)
        token = "test-token-123"
        hash1 = service._hash_token(token)
        hash2 = service._hash_token(token)

        # Same token should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_token_hashing_different_tokens(self, mock_uow, mock_session):
        """Test that different tokens produce different hashes."""
        from auth_service.services.password_reset import PasswordResetService

        service = PasswordResetService(mock_uow, mock_session)
        hash1 = service._hash_token("token-1")
        hash2 = service._hash_token("token-2")

        assert hash1 != hash2

    @pytest.mark.asyncio
    async def test_request_reset_creates_token(self, mock_uow, mock_session, active_user):
        """Test that request_reset creates a token record."""
        from auth_service.services.password_reset import PasswordResetService
        from sqlalchemy import select

        mock_uow.users.get_by_email = AsyncMock(return_value=active_user)
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))

        service = PasswordResetService(mock_uow, mock_session)
        # Mock _count_recent_requests to return 0 (not rate limited)
        service._count_recent_requests = AsyncMock(return_value=0)

        success, token, user = await service.request_reset("test@example.com")

        assert success is True
        assert token is not None
        assert user == active_user
        # Verify token was added to session
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_reset_nonexistent_user(self, mock_uow, mock_session):
        """Test that request_reset handles non-existent user gracefully."""
        from auth_service.services.password_reset import PasswordResetService

        mock_uow.users.get_by_email = AsyncMock(return_value=None)

        service = PasswordResetService(mock_uow, mock_session)
        success, token, user = await service.request_reset("nonexistent@example.com")

        # Should return success=True to prevent enumeration
        assert success is True
        assert token is None
        assert user is None

    @pytest.mark.asyncio
    async def test_validate_token_valid(self, mock_uow, mock_session, active_user):
        """Test validate_token with valid token."""
        from auth_service.services.password_reset import PasswordResetService

        token = "valid-token"
        token_hash = PasswordResetService._hash_token(token)

        # Create mock token record
        mock_token = MagicMock()
        mock_token.user_id = active_user.id
        mock_token.expires_at = datetime.now(UTC) + timedelta(hours=1)
        mock_token.used_at = None

        mock_uow.users.get_by_id = AsyncMock(return_value=active_user)

        # Mock the _get_token_record method
        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=mock_token)

        result = await service.validate_token(token)

        assert result == active_user

    @pytest.mark.asyncio
    async def test_validate_token_expired(self, mock_uow, mock_session):
        """Test validate_token with expired token."""
        from auth_service.services.password_reset import PasswordResetService

        token = "expired-token"

        # Create mock expired token record
        mock_token = MagicMock()
        mock_token.user_id = 1
        mock_token.expires_at = datetime.now(UTC) - timedelta(hours=1)  # Expired
        mock_token.used_at = None

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=mock_token)

        result = await service.validate_token(token)

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_token_already_used(self, mock_uow, mock_session):
        """Test validate_token with already used token."""
        from auth_service.services.password_reset import PasswordResetService

        token = "used-token"

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=None)  # Already used tokens return None

        result = await service.validate_token(token)

        assert result is None

    @pytest.mark.asyncio
    async def test_confirm_reset_success(self, mock_uow, mock_session, active_user):
        """Test confirm_reset successfully updates password."""
        from auth_service.services.password_reset import PasswordResetService

        token = "valid-token"
        new_password = "newSecurePass123"

        # Create mock token record
        mock_token = MagicMock()
        mock_token.user_id = active_user.id
        mock_token.expires_at = datetime.now(UTC) + timedelta(hours=1)
        mock_token.used_at = None

        mock_uow.users.get_by_id = AsyncMock(return_value=active_user)
        mock_session.flush = AsyncMock()

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=mock_token)

        result = await service.confirm_reset(token, new_password)

        assert result is True
        # Verify password was hashed and set
        assert active_user.password_hash is not None
        assert active_user.password_hash != "$2b$12$testhash"  # Should be new hash
        # Verify token was marked as used
        assert mock_token.used_at is not None
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_reset_invalid_token(self, mock_uow, mock_session):
        """Test confirm_reset with invalid token."""
        from auth_service.services.password_reset import PasswordResetService

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=None)

        result = await service.confirm_reset("invalid-token", "newPassword123")

        assert result is False

    @pytest.mark.asyncio
    async def test_rate_limiting(self, mock_uow, mock_session, active_user):
        """Test that rate limiting blocks after max requests."""
        from auth_service.services.password_reset import PasswordResetService

        mock_uow.users.get_by_email = AsyncMock(return_value=active_user)
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()

        service = PasswordResetService(mock_uow, mock_session)

        # Mock _count_recent_requests to return max value
        service._count_recent_requests = AsyncMock(return_value=PasswordResetService.MAX_REQUESTS_PER_HOUR)

        success, token, user = await service.request_reset("test@example.com")

        # Should return success=True to prevent enumeration, but no token
        assert success is True
        assert token is None
        assert user is None


class TestPasswordResetEndpointExceptions:
    """Tests for exception handling in password reset endpoints."""

    def test_confirm_reset_unexpected_exception(self, active_user):
        """Test that unexpected exceptions during confirm return 500."""
        with patch("auth_service.api.endpoints.password_reset.PasswordResetService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            # Raise an unexpected exception (not HTTPException)
            mock_service.validate_token = AsyncMock(side_effect=RuntimeError("Database connection failed"))

            client = get_test_client()
            response = client.post(
                "/api/v1/password-reset/confirm",
                json={"token": "valid-token", "new_password": "newSecurePass123"},
            )

            assert response.status_code == 500
            assert "Failed to reset password" in response.json()["detail"]
