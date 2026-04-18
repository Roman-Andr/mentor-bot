"""Unit tests for password reset service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from auth_service.services.password_reset import PasswordResetService


class TestPasswordResetService:
    """Tests for PasswordResetService."""

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

    @pytest.fixture
    def active_user(self):
        """Create an active user for testing."""
        from auth_service.models import User
        from auth_service.core.enums import UserRole

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
    def inactive_user(self):
        """Create an inactive user for testing."""
        from auth_service.models import User
        from auth_service.core.enums import UserRole

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

    @pytest.mark.asyncio
    async def test_request_reset_inactive_user(self, mock_uow, mock_session, inactive_user):
        """Test request_reset returns no token for inactive user."""
        mock_uow.users.get_by_email = AsyncMock(return_value=inactive_user)

        service = PasswordResetService(mock_uow, mock_session)
        success, token, user = await service.request_reset("inactive@example.com")

        # Should return success=True to prevent enumeration, but no token
        assert success is True
        assert token is None
        assert user is None

    @pytest.mark.asyncio
    async def test_confirm_reset_token_not_found(self, mock_uow, mock_session):
        """Test confirm_reset returns False when token not found."""
        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=None)

        result = await service.confirm_reset("invalid-token", "newpassword123")

        assert result is False

    @pytest.mark.asyncio
    async def test_confirm_reset_token_expired(self, mock_uow, mock_session, active_user):
        """Test confirm_reset returns False when token expired."""
        from auth_service.models import PasswordResetToken

        # Create expired token record
        expired_token = PasswordResetToken(
            id=1,
            user_id=active_user.id,
            token_hash=PasswordResetService._hash_token("expired-token"),
            expires_at=datetime.now(UTC) - timedelta(hours=1),
            created_at=datetime.now(UTC),
            used_at=None,
        )

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=expired_token)

        result = await service.confirm_reset("expired-token", "newpassword123")

        assert result is False

    @pytest.mark.asyncio
    async def test_confirm_reset_user_not_found(self, mock_uow, mock_session, active_user):
        """Test confirm_reset returns False when user not found."""
        from auth_service.models import PasswordResetToken

        # Create valid token record
        valid_token = PasswordResetToken(
            id=1,
            user_id=active_user.id,
            token_hash=PasswordResetService._hash_token("valid-token"),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            created_at=datetime.now(UTC),
            used_at=None,
        )

        mock_uow.users.get_by_id = AsyncMock(return_value=None)

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=valid_token)

        result = await service.confirm_reset("valid-token", "newpassword123")

        assert result is False

    @pytest.mark.asyncio
    async def test_confirm_reset_user_inactive(self, mock_uow, mock_session, inactive_user):
        """Test confirm_reset returns False when user is inactive."""
        from auth_service.models import PasswordResetToken

        # Create valid token record
        valid_token = PasswordResetToken(
            id=1,
            user_id=inactive_user.id,
            token_hash=PasswordResetService._hash_token("valid-token"),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            created_at=datetime.now(UTC),
            used_at=None,
        )

        mock_uow.users.get_by_id = AsyncMock(return_value=inactive_user)

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=valid_token)

        result = await service.confirm_reset("valid-token", "newpassword123")

        assert result is False

    @pytest.mark.asyncio
    async def test_confirm_reset_success(self, mock_uow, mock_session, active_user):
        """Test confirm_reset succeeds with valid token and active user."""
        from auth_service.models import PasswordResetToken

        # Create valid token record
        valid_token = PasswordResetToken(
            id=1,
            user_id=active_user.id,
            token_hash=PasswordResetService._hash_token("valid-token"),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            created_at=datetime.now(UTC),
            used_at=None,
        )

        mock_uow.users.get_by_id = AsyncMock(return_value=active_user)
        mock_session.flush = AsyncMock()

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=valid_token)

        result = await service.confirm_reset("valid-token", "newSecurePass123")

        assert result is True
        assert valid_token.used_at is not None
        assert active_user.password_hash != "$2b$12$testhash"
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_token_record_success(self, mock_uow, mock_session, active_user):
        """Test _get_token_record returns token when found and not used."""
        from auth_service.models import PasswordResetToken

        token_hash = PasswordResetService._hash_token("test-token")
        mock_token = PasswordResetToken(
            id=1,
            user_id=active_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            created_at=datetime.now(UTC),
            used_at=None,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_token
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = PasswordResetService(mock_uow, mock_session)
        result = await service._get_token_record(token_hash)

        assert result == mock_token
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_token_record_not_found(self, mock_uow, mock_session):
        """Test _get_token_record returns None when token not found."""
        token_hash = PasswordResetService._hash_token("nonexistent-token")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = PasswordResetService(mock_uow, mock_session)
        result = await service._get_token_record(token_hash)

        assert result is None

    @pytest.mark.asyncio
    async def test_count_recent_requests(self, mock_uow, mock_session, active_user):
        """Test _count_recent_requests counts tokens correctly."""
        from auth_service.models import PasswordResetToken

        mock_token1 = MagicMock(spec=PasswordResetToken)
        mock_token2 = MagicMock(spec=PasswordResetToken)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_token1, mock_token2]
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = PasswordResetService(mock_uow, mock_session)
        count = await service._count_recent_requests(active_user.id)

        assert count == 2
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_validate_token_user_inactive(self, mock_uow, mock_session, inactive_user):
        """Test validate_token returns None when user is inactive."""
        from auth_service.models import PasswordResetToken

        token = "valid-token"

        # Create valid token record
        mock_token = PasswordResetToken(
            id=1,
            user_id=inactive_user.id,
            token_hash=PasswordResetService._hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            created_at=datetime.now(UTC),
            used_at=None,
        )

        mock_uow.users.get_by_id = AsyncMock(return_value=inactive_user)

        service = PasswordResetService(mock_uow, mock_session)
        service._get_token_record = AsyncMock(return_value=mock_token)

        result = await service.validate_token(token)

        assert result is None
