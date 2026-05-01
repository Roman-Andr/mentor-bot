"""Unit tests for auth API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from auth_service.api import deps
from auth_service.core.enums import UserRole
from auth_service.core.security import create_access_token
from auth_service.main import app
from auth_service.models import User
from auth_service.schemas import Token


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
        language="ru",
        notification_telegram_enabled=True,
        notification_email_enabled=True,
    )


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login endpoint."""

    def test_login_success(self, mock_auth_service, active_user):
        """Test successful login returns token."""
        # Setup mock token response
        token = Token(
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            token_type="bearer",
            expires_at=datetime.now(UTC),
            user_id=active_user.id,
            role=active_user.role,
        )
        mock_auth_service.authenticate_user = AsyncMock(return_value=(active_user, token))

        # Use dependency override instead of patching
        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/auth/login",
                data={"username": "test@example.com", "password": "password123"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "access_token_123"
            assert data["refresh_token"] == "refresh_token_123"
            assert data["user_id"] == active_user.id
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)

    def test_login_invalid_credentials(self, mock_auth_service):
        """Test login with invalid credentials returns 401."""
        from auth_service.core import AuthException
        mock_auth_service.authenticate_user = AsyncMock(side_effect=AuthException("Invalid email or password"))

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/auth/login",
                data={"username": "test@example.com", "password": "wrongpassword"},
            )

            assert response.status_code == 401
            assert "Invalid email or password" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)


class TestRefreshTokenEndpoint:
    """Tests for POST /api/v1/auth/refresh endpoint."""

    def test_refresh_success(self, mock_auth_service, active_user):
        """Test successful token refresh."""
        token = Token(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            token_type="bearer",
            expires_at=datetime.now(UTC),
            user_id=active_user.id,
            role=active_user.role,
        )
        mock_auth_service.refresh_access_token = AsyncMock(return_value=token)

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid_refresh_token"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "new_access_token"
            assert data["user_id"] == active_user.id
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)

    def test_refresh_invalid_token(self, mock_auth_service):
        """Test refresh with invalid token returns 401."""
        from auth_service.core import AuthException
        mock_auth_service.refresh_access_token = AsyncMock(side_effect=AuthException("Invalid refresh token"))

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "invalid_token"},
            )

            assert response.status_code == 401
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)


class TestTelegramAuthEndpoint:
    """Tests for POST /api/v1/auth/telegram endpoint."""

    def test_telegram_auth_success(self, mock_auth_service, active_user):
        """Test successful Telegram authentication."""
        active_user.telegram_id = 123456789
        token = Token(
            access_token="tg_access_token",
            refresh_token="tg_refresh_token",
            token_type="bearer",
            expires_at=datetime.now(UTC),
            user_id=active_user.id,
            role=active_user.role,
        )
        mock_auth_service.authenticate_with_telegram = AsyncMock(return_value=(active_user, token))

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=True):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/telegram",
                    json={"api_key": "test-api-key", "telegram_id": 123456789},
                    headers={"X-API-Key": "test-api-key"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == active_user.id
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)

    def test_telegram_auth_invalid_api_key(self, mock_auth_service):
        """Test Telegram auth with invalid API key returns 401."""
        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=False):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/telegram",
                    json={"api_key": "wrong-key", "telegram_id": 123456789},
                    headers={"X-API-Key": "wrong-key"},
                )

            assert response.status_code == 401
            assert "Invalid API key" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)

    def test_telegram_auth_api_key_mismatch(self, mock_auth_service):
        """Test Telegram auth with API key mismatch returns 401."""
        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=True):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/telegram",
                    json={"api_key": "different-key", "telegram_id": 123456789},
                    headers={"X-API-Key": "test-api-key"},
                )

            assert response.status_code == 401
            assert "API key mismatch" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)


class TestGetCurrentUserEndpoint:
    """Tests for GET /api/v1/auth/me endpoint."""

    def test_get_current_user_success(self):
        """Test getting current user info."""
        from datetime import UTC, datetime
        user = User(
            id=1,
            email="user@example.com",
            first_name="Test",
            last_name="User",
            employee_id="EMP001",
            is_active=True,
            is_verified=True,
            role=UserRole.MENTOR,
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )

        # Create valid token
        access_token = create_access_token({"sub": "1", "user_id": 1, "role": UserRole.MENTOR})

        # Mock the get_current_user dependency
        async def mock_get_current() -> User:
            return user

        app.dependency_overrides[deps.get_current_user] = mock_get_current

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code != 200:
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "user@example.com"
            assert data["role"] == "MENTOR"
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)


class TestRegisterWithInvitation:
    """Tests for POST /api/v1/auth/register/{invitation_token} endpoint."""

    def test_register_with_invitation_success(self, mock_auth_service):
        """Test successful registration with invitation."""
        user = User(
            id=2,
            email="new@example.com",
            first_name="New",
            last_name="User",
            employee_id="EMP002",
            telegram_id=123456789,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
        )

        token = Token(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            token_type="bearer",
            expires_at=datetime.now(UTC),
            user_id=user.id,
            role=user.role,
        )

        mock_auth_service.register_with_invitation_and_telegram = AsyncMock(return_value=user)
        mock_auth_service.create_token_for_user = MagicMock(return_value=token)
        mock_auth_service.auto_create_user_checklists = AsyncMock()

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=True):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/register/invite-token-123",
                    json={
                        "telegram_id": 123456789,
                        "username": "newuser",
                        "first_name": "New",
                        "last_name": "User",
                    },
                    headers={"X-API-Key": "test-api-key"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 2
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)

    def test_register_invalid_api_key(self, mock_auth_service):
        """Test registration with invalid API key returns 401."""
        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=False):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/register/invite-token-123",
                    json={"telegram_id": 123456789},
                    headers={"X-API-Key": "wrong-key"},
                )

            assert response.status_code == 401
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)


class TestTelegramAuthEdgeCases:
    """Tests for POST /api/v1/auth/telegram edge cases."""

    def test_telegram_auth_not_found_exception(self, mock_auth_service):
        """Test Telegram auth with NotFoundException returns 401."""
        from auth_service.core import NotFoundException
        mock_auth_service.authenticate_with_telegram = AsyncMock(
            side_effect=NotFoundException("User not found")
        )

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=True):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/telegram",
                    json={"api_key": "test-api-key", "telegram_id": 123456789},
                    headers={"X-API-Key": "test-api-key"},
                )

            assert response.status_code == 401
            assert "User not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)


class TestRefreshTokenEdgeCases:
    """Tests for POST /api/v1/auth/refresh edge cases."""

    def test_refresh_exception_path_caught_as_auth_exception(self, mock_auth_service):
        """Test refresh token with exception raises 401."""
        from auth_service.core import AuthException
        mock_auth_service.refresh_access_token = AsyncMock(side_effect=AuthException("Token expired"))

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "expired_token"},
            )

            assert response.status_code == 401
            assert "Token expired" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)


class TestRegisterWithInvitationEdgeCases:
    """Tests for POST /api/v1/auth/register/{invitation_token} edge cases."""

    def test_register_auto_create_checklists_exception(self, mock_auth_service):
        """Test registration when auto_create_user_checklists raises exception."""
        from datetime import UTC
        user = User(
            id=2,
            email="new@example.com",
            first_name="New",
            last_name="User",
            employee_id="EMP002",
            telegram_id=123456789,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
        )

        token = Token(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            token_type="bearer",
            expires_at=datetime.now(UTC),
            user_id=user.id,
            role=user.role,
        )

        mock_auth_service.register_with_invitation_and_telegram = AsyncMock(return_value=user)
        mock_auth_service.create_token_for_user = MagicMock(return_value=token)
        # Simulate exception during auto-create checklists
        mock_auth_service.auto_create_user_checklists = AsyncMock(side_effect=Exception("Service unavailable"))

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=True):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/register/invite-token-123",
                    json={
                        "telegram_id": 123456789,
                        "username": "newuser",
                        "first_name": "New",
                        "last_name": "User",
                    },
                    headers={"X-API-Key": "test-api-key"},
                )

            # Should still succeed even if auto-create checklists fails
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 2
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)

    def test_register_validation_exception(self, mock_auth_service):
        """Test registration with ValidationException returns 400."""
        from auth_service.core import ValidationException
        mock_auth_service.register_with_invitation_and_telegram = AsyncMock(
            side_effect=ValidationException("Invalid invitation token")
        )

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=True):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/register/invite-token-123",
                    json={
                        "telegram_id": 123456789,
                        "username": "newuser",
                        "first_name": "New",
                        "last_name": "User",
                    },
                    headers={"X-API-Key": "test-api-key"},
                )

            assert response.status_code == 400
            assert "Invalid invitation token" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)

    def test_register_conflict_exception(self, mock_auth_service):
        """Test registration with ConflictException returns 400."""
        from auth_service.core import ConflictException
        mock_auth_service.register_with_invitation_and_telegram = AsyncMock(
            side_effect=ConflictException("User already registered")
        )

        app.dependency_overrides[deps.get_auth_service] = lambda: mock_auth_service

        try:
            with patch("auth_service.api.endpoints.auth.verify_telegram_api_key", return_value=True):
                client = get_test_client()
                response = client.post(
                    "/api/v1/auth/register/invite-token-123",
                    json={
                        "telegram_id": 123456789,
                        "username": "newuser",
                        "first_name": "New",
                        "last_name": "User",
                    },
                    headers={"X-API-Key": "test-api-key"},
                )

            assert response.status_code == 400
            assert "User already registered" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(deps.get_auth_service, None)


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout endpoint."""

    def test_logout_success(self):
        """Test logout returns success message."""
        client = get_test_client()
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"


