"""Tests for api/deps.py dependencies."""

from datetime import UTC, datetime
from types import TracebackType
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from checklists_service.api.deps import (
    AdminUser,
    AuthToken,
    ChecklistsServiceDep,
    CurrentUser,
    HRUser,
    MentorUser,
    ServiceAuth,
    UserInfo,
    get_auth_token,
    get_checklists_service_dep,
    get_current_active_user,
    get_current_user,
    get_uow,
    require_admin,
    require_hr,
    require_mentor_or_above,
    verify_service_api_key,
)
from checklists_service.core import AuthException, PermissionDenied


class TestUserInfo:
    """Test UserInfo class."""

    def test_user_info_initialization(self):
        """Test UserInfo initializes correctly from dict."""
        data = {
            "id": 1,
            "email": "test@example.com",
            "employee_id": "EMP001",
            "role": "ADMIN",
            "is_active": True,
            "is_verified": True,
            "department": {"id": 1, "name": "Engineering"},
            "position": "Developer",
            "level": "SENIOR",
            "first_name": "John",
            "last_name": "Doe",
            "telegram_id": "123456",
        }
        user = UserInfo(data)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.employee_id == "EMP001"
        assert user.role == "ADMIN"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.department == {"id": 1, "name": "Engineering"}
        assert user.position == "Developer"
        assert user.level == "SENIOR"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.telegram_id == "123456"

    def test_user_info_defaults(self):
        """Test UserInfo default values."""
        data = {"id": 1, "email": "test@example.com"}
        user = UserInfo(data)

        assert user.is_active is True
        assert user.is_verified is False
        assert user.role is None

    def test_has_role_single_match(self):
        """Test has_role with single matching role."""
        user = UserInfo({"id": 1, "role": "ADMIN"})
        assert user.has_role(["ADMIN"]) is True

    def test_has_role_multiple_roles(self):
        """Test has_role with multiple roles to check."""
        user = UserInfo({"id": 1, "role": "MENTOR"})
        assert user.has_role(["MENTOR", "HR", "ADMIN"]) is True

    def test_has_role_no_match(self):
        """Test has_role when role doesn't match."""
        user = UserInfo({"id": 1, "role": "EMPLOYEE"})
        assert user.has_role(["ADMIN", "HR"]) is False

    def test_has_role_none(self):
        """Test has_role when user has no role."""
        user = UserInfo({"id": 1})
        assert user.has_role(["ADMIN"]) is False

    def test_has_role_empty_list(self):
        """Test has_role with empty roles list."""
        user = UserInfo({"id": 1, "role": "ADMIN"})
        assert user.has_role([]) is False


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    async def test_get_current_user_success(self):
        """Test successful user authentication."""
        mock_request = MagicMock(spec=Request)
        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "valid_token"

        user_data = {
            "id": 1,
            "email": "test@example.com",
            "role": "ADMIN",
        }

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = user_data

        with patch("httpx.AsyncClient") as mock_client_cls, \
             patch("checklists_service.api.deps.auth_service_circuit_breaker") as mock_cb:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            mock_cb.call = AsyncMock(return_value=mock_response)

            result = await get_current_user(mock_request, credentials)

            assert result.id == 1
            assert result.email == "test@example.com"
            assert result.role == "ADMIN"

    async def test_get_current_user_no_credentials(self):
        """Test authentication fails without credentials."""
        mock_request = MagicMock(spec=Request)

        with pytest.raises(AuthException) as exc_info:
            await get_current_user(mock_request, None)

        assert exc_info.value.status_code == 401
        assert "Not authenticated" in str(exc_info.value.detail)

    async def test_get_current_user_auth_service_error(self):
        """Test handling of auth service error response."""
        mock_request = MagicMock(spec=Request)
        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "invalid_token"

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED

        with patch("httpx.AsyncClient") as mock_client_cls, \
             patch("checklists_service.api.deps.auth_service_circuit_breaker") as mock_cb:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            mock_cb.call = AsyncMock(return_value=mock_response)

            with pytest.raises(AuthException) as exc_info:
                await get_current_user(mock_request, credentials)

            assert exc_info.value.status_code == 401
            assert "Invalid authentication credentials" in str(exc_info.value.detail)

    async def test_get_current_user_circuit_breaker_open(self):
        """Test handling of circuit breaker open state."""
        mock_request = MagicMock(spec=Request)
        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "valid_token"

        with patch("httpx.AsyncClient") as mock_client_cls, \
             patch("checklists_service.api.deps.auth_service_circuit_breaker") as mock_cb:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            mock_cb.call = AsyncMock(side_effect=Exception("Circuit breaker is OPEN"))

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_request, credentials)

            assert exc_info.value.status_code == 503
            assert "Auth service temporarily unavailable" in str(exc_info.value.detail)

    async def test_get_current_user_exception(self):
        """Test handling of general exception."""
        mock_request = MagicMock(spec=Request)
        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "valid_token"

        with patch("httpx.AsyncClient") as mock_client_cls, \
             patch("checklists_service.api.deps.auth_service_circuit_breaker") as mock_cb:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            mock_cb.call = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

            with pytest.raises(AuthException) as exc_info:
                await get_current_user(mock_request, credentials)

            assert exc_info.value.status_code == 401


class TestGetCurrentActiveUser:
    """Test get_current_active_user dependency."""

    async def test_get_current_active_user_success(self):
        """Test getting active user succeeds."""
        user = UserInfo({"id": 1, "is_active": True})
        result = await get_current_active_user(user)
        assert result.id == 1
        assert result.is_active is True

    async def test_get_current_active_user_inactive(self):
        """Test getting inactive user raises exception."""
        user = UserInfo({"id": 1, "is_active": False})

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(user)

        assert exc_info.value.status_code == 400
        assert "Inactive user" in str(exc_info.value.detail)


class TestRequireAdmin:
    """Test require_admin dependency."""

    async def test_require_admin_success(self):
        """Test admin role passes."""
        user = UserInfo({"id": 1, "role": "ADMIN", "is_active": True})
        result = await require_admin(user)
        assert result.role == "ADMIN"

    async def test_require_admin_hr_passes(self):
        """Test HR role passes as admin."""
        user = UserInfo({"id": 1, "role": "HR", "is_active": True})
        result = await require_admin(user)
        assert result.role == "HR"

    async def test_require_admin_fails_for_employee(self):
        """Test employee role fails."""
        user = UserInfo({"id": 1, "role": "EMPLOYEE", "is_active": True})

        with pytest.raises(PermissionDenied) as exc_info:
            await require_admin(user)

        assert exc_info.value.status_code == 403
        assert "Admin access required" in str(exc_info.value.detail)

    async def test_require_admin_fails_for_mentor(self):
        """Test mentor role fails for admin requirement."""
        user = UserInfo({"id": 1, "role": "MENTOR", "is_active": True})

        with pytest.raises(PermissionDenied) as exc_info:
            await require_admin(user)

        assert exc_info.value.status_code == 403

    async def test_require_admin_fails_no_role(self):
        """Test user without role fails."""
        user = UserInfo({"id": 1, "is_active": True})

        with pytest.raises(PermissionDenied) as exc_info:
            await require_admin(user)

        assert exc_info.value.status_code == 403


class TestRequireHR:
    """Test require_hr dependency."""

    async def test_require_hr_success(self):
        """Test HR role passes."""
        user = UserInfo({"id": 1, "role": "HR", "is_active": True})
        result = await require_hr(user)
        assert result.role == "HR"

    async def test_require_hr_admin_passes(self):
        """Test admin role passes for HR requirement."""
        user = UserInfo({"id": 1, "role": "ADMIN", "is_active": True})
        result = await require_hr(user)
        assert result.role == "ADMIN"

    async def test_require_hr_fails_for_employee(self):
        """Test employee role fails."""
        user = UserInfo({"id": 1, "role": "EMPLOYEE", "is_active": True})

        with pytest.raises(PermissionDenied) as exc_info:
            await require_hr(user)

        assert exc_info.value.status_code == 403
        assert "HR access required" in str(exc_info.value.detail)


class TestRequireMentorOrAbove:
    """Test require_mentor_or_above dependency."""

    async def test_require_mentor_success(self):
        """Test mentor role passes."""
        user = UserInfo({"id": 1, "role": "MENTOR", "is_active": True})
        result = await require_mentor_or_above(user)
        assert result.role == "MENTOR"

    async def test_require_mentor_hr_passes(self):
        """Test HR role passes."""
        user = UserInfo({"id": 1, "role": "HR", "is_active": True})
        result = await require_mentor_or_above(user)
        assert result.role == "HR"

    async def test_require_mentor_admin_passes(self):
        """Test admin role passes."""
        user = UserInfo({"id": 1, "role": "ADMIN", "is_active": True})
        result = await require_mentor_or_above(user)
        assert result.role == "ADMIN"

    async def test_require_mentor_fails_for_employee(self):
        """Test employee role fails."""
        user = UserInfo({"id": 1, "role": "EMPLOYEE", "is_active": True})

        with pytest.raises(PermissionDenied) as exc_info:
            await require_mentor_or_above(user)

        assert exc_info.value.status_code == 403
        assert "Mentor access required" in str(exc_info.value.detail)


class TestGetAuthToken:
    """Test get_auth_token dependency."""

    async def test_get_auth_token_from_request(self):
        """Test extracting auth token from request state."""
        mock_request = MagicMock(spec=Request)
        mock_request.state.auth_token = "Bearer token123"

        result = await get_auth_token(mock_request)
        assert result == "Bearer token123"

    async def test_get_auth_token_none(self):
        """Test when no auth token in request state."""
        mock_request = MagicMock(spec=Request)
        # Don't set auth_token on state
        mock_request.state = MagicMock(spec=[])

        result = await get_auth_token(mock_request)
        assert result is None


class TestVerifyServiceAPIKey:
    """Test verify_service_api_key dependency."""

    async def test_verify_service_api_key_success(self):
        """Test valid API key passes."""
        with patch("checklists_service.api.deps.settings") as mock_settings:
            mock_settings.SERVICE_API_KEY = "secret-api-key"

            result = await verify_service_api_key("secret-api-key")
            assert result is True

    async def test_verify_service_api_key_no_key_configured(self):
        """Test when no API key is configured."""
        with patch("checklists_service.api.deps.settings") as mock_settings:
            mock_settings.SERVICE_API_KEY = None

            result = await verify_service_api_key("some-key")
            assert result is False

    async def test_verify_service_api_key_invalid_key(self):
        """Test invalid API key raises exception."""
        with patch("checklists_service.api.deps.settings") as mock_settings:
            mock_settings.SERVICE_API_KEY = "secret-api-key"

            with pytest.raises(HTTPException) as exc_info:
                await verify_service_api_key("wrong-key")

            assert exc_info.value.status_code == 401
            assert "Invalid service API key" in str(exc_info.value.detail)

    async def test_verify_service_api_key_missing_header(self):
        """Test missing API key header raises exception."""
        with patch("checklists_service.api.deps.settings") as mock_settings:
            mock_settings.SERVICE_API_KEY = "secret-api-key"

            with pytest.raises(HTTPException) as exc_info:
                await verify_service_api_key(None)

            assert exc_info.value.status_code == 401


class TestGetDBInDeps:
    """Test that get_db is accessible from deps module (re-exported or imported)."""

    def test_get_db_exists_in_database_base(self):
        """Test get_db function exists in database.base."""
        from checklists_service.database.base import get_db

        assert callable(get_db)


class TestGetChecklistsServiceDep:
    """Test get_checklists_service_dep dependency."""

    async def test_get_checklists_service_dep(self):
        """Test service dependency returns marker class."""
        result = await get_checklists_service_dep()
        assert isinstance(result, ChecklistsServiceDep)


class TestGetDB:
    """Test get_db dependency."""

    async def test_get_db_success(self):
        """Test database session creation and cleanup."""
        from checklists_service.database.base import get_db

        mock_session = AsyncMock()

        class MockAsyncSessionLocal:
            async def __aenter__(self):
                return mock_session
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        with patch("checklists_service.database.base.AsyncSessionLocal", MockAsyncSessionLocal):
            gen = get_db()
            session = await gen.__anext__()

            assert session == mock_session
            mock_session.commit.assert_not_awaited()

            # Complete the generator (simulate end of request)
            try:
                await gen.__anext__()
            except StopAsyncIteration:
                pass

            mock_session.commit.assert_awaited_once()

    async def test_get_db_rollback_on_error(self):
        """Test database session rolls back on error."""
        from checklists_service.database.base import get_db

        mock_session = AsyncMock()

        class MockAsyncSessionLocal:
            async def __aenter__(self):
                return mock_session
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        with patch("checklists_service.database.base.AsyncSessionLocal", MockAsyncSessionLocal):
            gen = get_db()
            await gen.__anext__()

            # Simulate an exception during request
            try:
                await gen.athrow(ValueError("Test error"))
            except ValueError:
                pass

            mock_session.rollback.assert_awaited_once()


class TestGetUOW:
    """Test get_uow dependency for Unit of Work."""

    async def test_get_uow_success(self):
        """Test successful UOW with commit."""
        from checklists_service.api.deps import get_uow

        mock_uow = MagicMock()
        mock_uow.commit = AsyncMock()
        mock_uow.rollback = AsyncMock()

        # Create a mock session factory that returns our mock uow
        mock_session_factory = MagicMock()
        mock_session_factory.return_value = MagicMock()

        with patch("checklists_service.api.deps.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow_instance = MagicMock()
            mock_uow_instance.commit = AsyncMock()
            mock_uow_instance.rollback = AsyncMock()
            mock_uow_instance.__aenter__ = AsyncMock(return_value=mock_uow_instance)
            mock_uow_instance.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow_instance

            gen = get_uow()
            uow = await gen.__anext__()
            assert uow is mock_uow_instance

            # Complete normally (should commit)
            try:
                await gen.__anext__()
            except StopAsyncIteration:
                pass

            # Commit should be called when exiting without exception
            mock_uow_instance.commit.assert_awaited_once()

    async def test_get_uow_rollback_on_error(self):
        """Test UOW rolls back on exception (lines 160-162)."""
        from checklists_service.api.deps import get_uow

        with patch("checklists_service.api.deps.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow_instance = MagicMock()
            mock_uow_instance.commit = AsyncMock()
            mock_uow_instance.rollback = AsyncMock()
            mock_uow_instance.__aenter__ = AsyncMock(return_value=mock_uow_instance)
            mock_uow_instance.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow_instance

            gen = get_uow()
            await gen.__anext__()

            # Simulate an exception during request
            try:
                await gen.athrow(ValueError("Test error"))
            except ValueError:
                pass

            # Rollback should be called on exception
            mock_uow_instance.rollback.assert_awaited_once()




