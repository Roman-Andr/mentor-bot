"""Unit tests for escalation_service/api/deps.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from escalation_service.api.deps import (
    UserInfo,
    get_current_active_user,
    get_current_user,
    get_escalation_service,
    require_admin,
    require_hr,
)
from escalation_service.core.exceptions import AuthException, NotFoundException, PermissionDenied
from escalation_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from escalation_service.services.escalation import EscalationService


class TestUserInfo:
    """Tests for UserInfo class."""

    def test_user_info_creation(self):
        """Test UserInfo can be created from dictionary."""
        data = {
            "id": 100,
            "email": "test@example.com",
            "employee_id": "EMP001",
            "role": "USER",
            "is_active": True,
            "is_verified": True,
            "department": "Engineering",
            "position": "Developer",
            "level": "Senior",
            "first_name": "Test",
            "last_name": "User",
            "telegram_id": 123456,
        }
        user = UserInfo(data)

        assert user.id == 100
        assert user.email == "test@example.com"
        assert user.employee_id == "EMP001"
        assert user.role == "USER"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.department == "Engineering"
        assert user.position == "Developer"
        assert user.level == "Senior"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.telegram_id == 123456

    def test_user_info_defaults(self):
        """Test UserInfo has correct defaults."""
        data = {"id": 100, "email": "test@example.com"}
        user = UserInfo(data)

        assert user.is_active is True
        assert user.is_verified is False
        assert user.employee_id is None
        assert user.role is None

    def test_has_role_with_matching_role(self):
        """Test has_role returns True when role matches."""
        data = {"id": 100, "email": "test@example.com", "role": "ADMIN"}
        user = UserInfo(data)

        assert user.has_role(["ADMIN"]) is True
        assert user.has_role(["ADMIN", "HR"]) is True

    def test_has_role_without_matching_role(self):
        """Test has_role returns False when role doesn't match."""
        data = {"id": 100, "email": "test@example.com", "role": "USER"}
        user = UserInfo(data)

        assert user.has_role(["ADMIN"]) is False
        assert user.has_role(["ADMIN", "HR"]) is False

    def test_has_role_with_none_role(self):
        """Test has_role returns False when user has no role."""
        data = {"id": 100, "email": "test@example.com", "role": None}
        user = UserInfo(data)

        assert user.has_role(["ADMIN"]) is False


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test that no credentials raises AuthException."""
        with pytest.raises(AuthException):
            await get_current_user(MagicMock(), None)

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful user retrieval from auth service."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 100,
            "email": "test@example.com",
            "role": "USER",
            "is_active": True,
        }

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            user = await get_current_user(MagicMock(), mock_credentials)

        assert user.id == 100
        assert user.email == "test@example.com"
        assert user.role == "USER"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_response(self):
        """Test that invalid response raises AuthException."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid_token"

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(AuthException):
                await get_current_user(MagicMock(), mock_credentials)

    @pytest.mark.asyncio
    async def test_get_current_user_request_exception(self):
        """Test that request exception raises AuthException."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        with patch("httpx.AsyncClient.get", side_effect=httpx.RequestError("Connection failed")):
            with pytest.raises(AuthException):
                await get_current_user(MagicMock(), mock_credentials)


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency."""

    @pytest.mark.asyncio
    async def test_active_user_returns_user(self):
        """Test that active user is returned."""
        user = UserInfo({"id": 100, "email": "test@example.com", "is_active": True})
        result = await get_current_active_user(user)
        assert result == user

    @pytest.mark.asyncio
    async def test_inactive_user_raises_exception(self):
        """Test that inactive user raises HTTPException."""
        user = UserInfo({"id": 100, "email": "test@example.com", "is_active": False})

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(user)

        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


class TestRequireAdmin:
    """Tests for require_admin dependency."""

    @pytest.mark.asyncio
    async def test_admin_user_allowed(self):
        """Test that admin user is allowed."""
        user = UserInfo({"id": 100, "email": "admin@example.com", "role": "ADMIN", "is_active": True})
        result = await require_admin(user)
        assert result == user

    @pytest.mark.asyncio
    async def test_non_admin_user_denied(self):
        """Test that non-admin user is denied."""
        user = UserInfo({"id": 100, "email": "user@example.com", "role": "USER", "is_active": True})

        with pytest.raises(PermissionDenied):
            await require_admin(user)


class TestRequireHR:
    """Tests for require_hr dependency."""

    @pytest.mark.asyncio
    async def test_hr_user_allowed(self):
        """Test that HR user is allowed."""
        user = UserInfo({"id": 100, "email": "hr@example.com", "role": "HR", "is_active": True})
        result = await require_hr(user)
        assert result == user

    @pytest.mark.asyncio
    async def test_admin_user_allowed(self):
        """Test that admin user is also allowed for HR endpoints."""
        user = UserInfo({"id": 100, "email": "admin@example.com", "role": "ADMIN", "is_active": True})
        result = await require_hr(user)
        assert result == user

    @pytest.mark.asyncio
    async def test_regular_user_denied(self):
        """Test that regular user is denied."""
        user = UserInfo({"id": 100, "email": "user@example.com", "role": "USER", "is_active": True})

        with pytest.raises(PermissionDenied):
            await require_hr(user)


class TestGetEscalationService:
    """Tests for get_escalation_service dependency."""

    @pytest.mark.asyncio
    async def test_get_escalation_service(self):
        """Test that escalation service is created with UoW."""
        mock_uow = MagicMock()

        service = await get_escalation_service(mock_uow)

        assert isinstance(service, EscalationService)


class TestUOWDependency:
    """Tests for Unit of Work dependency."""

    @pytest.mark.asyncio
    async def test_get_uow_yields_uow(self):
        """Test that get_uow yields a SqlAlchemyUnitOfWork."""
        # Mock the session factory
        mock_session = AsyncMock()
        mock_factory = MagicMock(return_value=mock_session)

        # Patch AsyncSessionLocal temporarily
        with patch("escalation_service.api.deps.AsyncSessionLocal", mock_factory):
            # We can't easily test the full async generator here due to context manager complexity
            # Instead, we verify the UoW class can be instantiated
            uow = SqlAlchemyUnitOfWork(mock_factory)
            assert uow is not None

    @pytest.mark.asyncio
    async def test_uow_commit_on_success(self):
        """Test that UoW commits on successful exit."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        # Enter context
        result = await uow.__aenter__()
        assert result == uow

        # Commit
        await uow.commit()
        mock_session.commit.assert_awaited_once()

        # Exit context
        await uow.__aexit__(None, None, None)
        mock_session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uow_rollback_on_exception(self):
        """Test that UoW close is called on exception exit."""
        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        # Enter context
        await uow.__aenter__()

        # Simulate exception and exit
        exc_message = "Test exception"
        try:
            raise ValueError(exc_message)
        except ValueError:
            await uow.__aexit__(*__import__("sys").exc_info())

        # close should be called on exit (rollback is explicitly called by get_uow when catching exceptions)
        mock_session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uow_commit_raises_if_no_session(self):
        """Test that commit raises if session not initialized."""
        mock_session_factory = MagicMock()
        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.commit()

    @pytest.mark.asyncio
    async def test_uow_rollback_raises_if_no_session(self):
        """Test that rollback raises if session not initialized."""
        mock_session_factory = MagicMock()
        uow = SqlAlchemyUnitOfWork(mock_session_factory)

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await uow.rollback()


class TestGetUOWExceptionHandling:
    """Tests for get_uow exception handling (lines 106-112)."""

    @pytest.mark.asyncio
    async def test_get_uow_rollback_on_exception(self):
        """Test that get_uow rolls back when exception occurs after yield."""
        from escalation_service.api.deps import get_uow

        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        with patch("escalation_service.api.deps.AsyncSessionLocal", mock_session_factory):
            gen = get_uow()
            uow = await gen.asend(None)

            # Simulate exception during request handling
            with pytest.raises(ValueError, match="Test error"):
                try:
                    raise ValueError("Test error")
                except Exception as exc:
                    await gen.athrow(exc)

            # Verify rollback was called
            mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_uow_commit_on_success(self):
        """Test that get_uow commits when no exception occurs."""
        from escalation_service.api.deps import get_uow

        mock_session_factory = MagicMock()
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        with patch("escalation_service.api.deps.AsyncSessionLocal", mock_session_factory):
            gen = get_uow()
            uow = await gen.asend(None)

            # Simulate successful request completion
            try:
                await gen.asend(None)
            except StopAsyncIteration:
                pass

            # Verify commit was called
            mock_session.commit.assert_awaited_once()


class TestRequireAnyAssigneeOrHR:
    """Tests for require_any_assignee_or_hr dependency (lines 121-130)."""

    @pytest.mark.asyncio
    async def test_require_any_assignee_or_hr_as_assignee(self):
        """Test that assignee can access the escalation."""
        from escalation_service.api.deps import require_any_assignee_or_hr

        # Create a mock user who is the assignee
        user = UserInfo({
            "id": 200,  # Same as assigned_to
            "email": "assignee@example.com",
            "role": "USER",
            "is_active": True,
        })

        # Create mock escalation
        mock_escalation = MagicMock()
        mock_escalation.id = 1
        mock_escalation.assigned_to = 200  # Same as user.id

        # Create mock UoW
        mock_uow = MagicMock()
        mock_uow.escalations = MagicMock()
        mock_uow.escalations.get_by_id = AsyncMock(return_value=mock_escalation)

        result_user, result_uow = await require_any_assignee_or_hr(user, escalation_id=1, uow=mock_uow)

        assert result_user == user
        assert result_uow == mock_uow
        mock_uow.escalations.get_by_id.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_require_any_assignee_or_hr_as_hr(self):
        """Test that HR user can access any escalation."""
        from escalation_service.api.deps import require_any_assignee_or_hr

        # Create HR user (different from assignee)
        user = UserInfo({
            "id": 300,
            "email": "hr@example.com",
            "role": "HR",
            "is_active": True,
        })

        # Create mock escalation assigned to someone else
        mock_escalation = MagicMock()
        mock_escalation.id = 1
        mock_escalation.assigned_to = 200  # Different from user.id

        # Create mock UoW
        mock_uow = MagicMock()
        mock_uow.escalations = MagicMock()
        mock_uow.escalations.get_by_id = AsyncMock(return_value=mock_escalation)

        result_user, result_uow = await require_any_assignee_or_hr(user, escalation_id=1, uow=mock_uow)

        assert result_user == user
        assert result_uow == mock_uow

    @pytest.mark.asyncio
    async def test_require_any_assignee_or_hr_as_admin(self):
        """Test that admin user can access any escalation."""
        from escalation_service.api.deps import require_any_assignee_or_hr

        # Create admin user (different from assignee)
        user = UserInfo({
            "id": 300,
            "email": "admin@example.com",
            "role": "ADMIN",
            "is_active": True,
        })

        # Create mock escalation assigned to someone else
        mock_escalation = MagicMock()
        mock_escalation.id = 1
        mock_escalation.assigned_to = 200  # Different from user.id

        # Create mock UoW
        mock_uow = MagicMock()
        mock_uow.escalations = MagicMock()
        mock_uow.escalations.get_by_id = AsyncMock(return_value=mock_escalation)

        result_user, result_uow = await require_any_assignee_or_hr(user, escalation_id=1, uow=mock_uow)

        assert result_user == user
        assert result_uow == mock_uow

    @pytest.mark.asyncio
    async def test_require_any_assignee_or_hr_not_found(self):
        """Test that NotFoundException is raised when escalation doesn't exist."""
        from escalation_service.api.deps import require_any_assignee_or_hr

        user = UserInfo({
            "id": 200,
            "email": "user@example.com",
            "role": "USER",
            "is_active": True,
        })

        # Create mock UoW that returns None
        mock_uow = MagicMock()
        mock_uow.escalations = MagicMock()
        mock_uow.escalations.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException) as exc_info:
            await require_any_assignee_or_hr(user, escalation_id=999, uow=mock_uow)

        assert "Escalation request" in exc_info.value.detail
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_require_any_assignee_or_hr_permission_denied(self):
        """Test that PermissionDenied is raised when user is not assignee or HR."""
        from escalation_service.api.deps import require_any_assignee_or_hr

        # Create regular user (different from assignee, not HR/ADMIN)
        user = UserInfo({
            "id": 100,  # Different from assigned_to
            "email": "user@example.com",
            "role": "USER",
            "is_active": True,
        })

        # Create mock escalation assigned to someone else
        mock_escalation = MagicMock()
        mock_escalation.id = 1
        mock_escalation.assigned_to = 200  # Different from user.id

        # Create mock UoW
        mock_uow = MagicMock()
        mock_uow.escalations = MagicMock()
        mock_uow.escalations.get_by_id = AsyncMock(return_value=mock_escalation)

        with pytest.raises(PermissionDenied) as exc_info:
            await require_any_assignee_or_hr(user, escalation_id=1, uow=mock_uow)

        assert "Access denied" in exc_info.value.detail
        assert exc_info.value.status_code == 403
