"""Unit tests for API dependencies."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException, status

from feedback_service.api.deps import (
    UserInfo,
    get_current_active_user,
    get_current_user,
    get_current_user_from_cookie,
    get_current_user_optional,
    require_admin,
    require_auth,
    require_hr_or_admin,
    verify_service_api_key,
)


class TestUserInfo:
    """Tests for UserInfo class."""

    def test_user_info_initialization(self) -> None:
        """Test UserInfo initializes correctly from dict."""
        data = {
            "id": 1,
            "email": "test@example.com",
            "employee_id": "EMP001",
            "role": "USER",
            "is_active": True,
            "is_verified": True,
            "department": {"id": 1, "name": "Engineering"},
            "position": "Developer",
            "level": "Senior",
            "first_name": "John",
            "last_name": "Doe",
            "telegram_id": "123456",
        }

        user = UserInfo(data)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.employee_id == "EMP001"
        assert user.role == "USER"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.department == {"id": 1, "name": "Engineering"}
        assert user.department_id == 1
        assert user.position == "Developer"
        assert user.level == "Senior"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.telegram_id == "123456"

    def test_user_info_no_department(self) -> None:
        """Test UserInfo handles missing department."""
        data = {"id": 1, "role": "USER"}

        user = UserInfo(data)

        assert user.department is None
        assert user.department_id is None

    def test_has_role_true(self) -> None:
        """Test has_role returns True when role matches."""
        data = {"id": 1, "role": "ADMIN"}
        user = UserInfo(data)

        assert user.has_role(["ADMIN", "HR"]) is True

    def test_has_role_false(self) -> None:
        """Test has_role returns False when role doesn't match."""
        data = {"id": 1, "role": "USER"}
        user = UserInfo(data)

        assert user.has_role(["ADMIN", "HR"]) is False

    def test_has_role_no_role(self) -> None:
        """Test has_role returns False when user has no role."""
        data = {"id": 1}
        user = UserInfo(data)

        assert user.has_role(["ADMIN"]) is False


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    async def test_get_current_user_no_credentials(self) -> None:
        """Test 401 when no credentials provided."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in exc_info.value.detail

    @patch("httpx.AsyncClient.get")
    async def test_get_current_user_success(self, mock_get: MagicMock) -> None:
        """Test successful authentication."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "email": "test@example.com",
            "role": "USER",
        }
        mock_get.return_value = mock_response

        result = await get_current_user(mock_credentials)

        assert result.id == 1
        assert result.email == "test@example.com"
        assert result.role == "USER"

    @patch("httpx.AsyncClient.get")
    async def test_get_current_user_invalid_credentials(self, mock_get: MagicMock) -> None:
        """Test 401 when auth service returns non-200."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid_token"

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("httpx.AsyncClient.get")
    async def test_get_current_user_auth_service_unavailable(self, mock_get: MagicMock) -> None:
        """Test 503 when auth service is unavailable."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        mock_get.side_effect = httpx.RequestError("Connection failed")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestGetCurrentUserOptional:
    """Tests for get_current_user_optional dependency."""

    async def test_get_current_user_optional_no_credentials(self) -> None:
        """Test returns None when no credentials provided."""
        result = await get_current_user_optional(None)
        assert result is None

    @patch("httpx.AsyncClient.get")
    async def test_get_current_user_optional_success(self, mock_get: MagicMock) -> None:
        """Test successful authentication returns user."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "email": "test@example.com",
            "role": "USER",
        }
        mock_get.return_value = mock_response

        result = await get_current_user_optional(mock_credentials)

        assert result is not None
        assert result.id == 1
        assert result.email == "test@example.com"

    @patch("httpx.AsyncClient.get")
    async def test_get_current_user_optional_non_200_status(self, mock_get: MagicMock) -> None:
        """Test returns None when auth service returns non-200."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid_token"

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = await get_current_user_optional(mock_credentials)

        assert result is None

    @patch("httpx.AsyncClient.get")
    async def test_get_current_user_optional_request_error(self, mock_get: MagicMock) -> None:
        """Test returns None when auth service is unavailable."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await get_current_user_optional(mock_credentials)

        assert result is None


class TestGetCurrentUserFromCookie:
    """Tests for get_current_user_from_cookie dependency."""

    async def test_get_current_user_from_cookie_returns_none(self) -> None:
        """Test returns None (placeholder implementation)."""
        request = MagicMock()
        result = await get_current_user_from_cookie(request)
        assert result is None


class TestRequireAuth:
    """Tests for require_auth dependency."""

    async def test_require_auth_no_service_no_user_raises(self) -> None:
        """Test raises 401 when neither service auth nor user auth provided."""
        with pytest.raises(HTTPException) as exc_info:
            await require_auth(False, None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in exc_info.value.detail

    async def test_require_auth_service_auth_passes(self) -> None:
        """Test passes when service auth is provided."""
        result = await require_auth(True, None)
        assert result is None  # Returns current_user which is None

    async def test_require_auth_user_auth_passes(self) -> None:
        """Test passes when user auth is provided."""
        mock_user = MagicMock()
        mock_user.id = 1
        result = await require_auth(False, mock_user)
        assert result is mock_user


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency."""

    async def test_get_current_active_user_success(self) -> None:
        """Test active user passes through."""
        mock_user = MagicMock()
        mock_user.is_active = True

        result = await get_current_active_user(mock_user)

        assert result == mock_user

    async def test_get_current_active_user_inactive(self) -> None:
        """Test 400 when user is inactive."""
        mock_user = MagicMock()
        mock_user.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(mock_user)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in exc_info.value.detail


class TestRequireAdmin:
    """Tests for require_admin dependency."""

    async def test_require_admin_success(self) -> None:
        """Test admin user passes through."""
        mock_user = MagicMock()
        mock_user.has_role = MagicMock(return_value=True)

        result = await require_admin(mock_user)

        assert result == mock_user

    async def test_require_admin_forbidden(self) -> None:
        """Test 403 when user is not admin."""
        mock_user = MagicMock()
        mock_user.has_role = MagicMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            await require_admin(mock_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in exc_info.value.detail


class TestRequireHrOrAdmin:
    """Tests for require_hr_or_admin dependency."""

    async def test_require_hr_or_admin_success(self) -> None:
        """Test HR/Admin user passes through."""
        mock_user = MagicMock()
        mock_user.has_role = MagicMock(return_value=True)

        result = await require_hr_or_admin(mock_user)

        assert result == mock_user
        mock_user.has_role.assert_called_once_with(["HR", "ADMIN"])

    async def test_require_hr_or_admin_forbidden(self) -> None:
        """Test 403 when user is not HR or Admin."""
        mock_user = MagicMock()
        mock_user.has_role = MagicMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            await require_hr_or_admin(mock_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "HR or Admin access required" in exc_info.value.detail


class TestCheckUserAccess:
    """Tests for check_user_access helper function."""

    def test_check_user_access_view_own_data(self) -> None:
        """Test user can always view their own data."""
        from feedback_service.api.deps import check_user_access

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.has_role = MagicMock(return_value=False)

        result = check_user_access(mock_user, 1, ["HR", "ADMIN"], "pulse surveys")

        assert result == 1

    def test_check_user_access_view_other_data_without_permission(self) -> None:
        """Test 403 when user tries to view another user's data without permission."""
        from feedback_service.api.deps import check_user_access

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.has_role = MagicMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            check_user_access(mock_user, 2, ["HR", "ADMIN"], "pulse surveys")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Can only view your own" in exc_info.value.detail

    def test_check_user_access_view_other_data_with_permission(self) -> None:
        """Test HR/Admin can view other user's data."""
        from feedback_service.api.deps import check_user_access

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.has_role = MagicMock(return_value=True)

        result = check_user_access(mock_user, 2, ["HR", "ADMIN"], "pulse surveys")

        assert result == 2

    def test_check_user_access_no_user_id_without_permission(self) -> None:
        """Test returns current user_id when no user_id specified and no permission."""
        from feedback_service.api.deps import check_user_access

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.has_role = MagicMock(return_value=False)

        result = check_user_access(mock_user, None, ["HR", "ADMIN"], "pulse surveys")

        assert result == 1

    def test_check_user_access_no_user_id_with_permission(self) -> None:
        """Test returns None when no user_id specified but user has permission."""
        from feedback_service.api.deps import check_user_access

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.has_role = MagicMock(return_value=True)

        result = check_user_access(mock_user, None, ["HR", "ADMIN"], "pulse surveys")

        assert result is None


class TestVerifyServiceApiKey:
    """Tests for verify_service_api_key dependency."""

    @patch("feedback_service.api.deps.settings")
    async def test_verify_service_api_key_no_key_configured(self, mock_settings: MagicMock) -> None:
        """Test 500 when no API key configured."""
        mock_settings.SERVICE_API_KEY = None

        with pytest.raises(HTTPException) as exc_info:
            await verify_service_api_key("some_key")

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "not configured" in exc_info.value.detail.lower()

    @patch("feedback_service.api.deps.settings")
    async def test_verify_service_api_key_valid(self, mock_settings: MagicMock) -> None:
        """Test returns True when valid key provided."""
        mock_settings.SERVICE_API_KEY = "secret_key"

        result = await verify_service_api_key("secret_key")

        assert result is True

    @patch("feedback_service.api.deps.settings")
    async def test_verify_service_api_key_invalid(self, mock_settings: MagicMock) -> None:
        """Test 401 when invalid key provided."""
        mock_settings.SERVICE_API_KEY = "secret_key"

        with pytest.raises(HTTPException) as exc_info:
            await verify_service_api_key("wrong_key")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid service API key" in exc_info.value.detail

    @patch("feedback_service.api.deps.settings")
    async def test_verify_service_api_key_missing(self, mock_settings: MagicMock) -> None:
        """Test 401 when no key provided."""
        mock_settings.SERVICE_API_KEY = "secret_key"

        with pytest.raises(HTTPException) as exc_info:
            await verify_service_api_key(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUow:
    """Tests for get_uow dependency."""

    @patch("feedback_service.api.deps.SqlAlchemyUnitOfWork")
    @patch("feedback_service.api.deps.AsyncSessionLocal")
    async def test_get_uow_yields_uow_instance(
        self, mock_session_local: MagicMock, mock_uow_class: MagicMock
    ) -> None:
        """Test get_uow yields a SqlAlchemyUnitOfWork instance."""
        # Arrange
        from feedback_service.api.deps import get_uow

        mock_uow = MagicMock()
        mock_uow_class.return_value.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow_class.return_value.__aexit__ = AsyncMock(return_value=None)

        # Act
        gen = get_uow()
        result = await gen.__anext__()

        # Assert
        assert result == mock_uow
        mock_uow_class.assert_called_once_with(mock_session_local)

        # Clean up generator
        from contextlib import suppress
        with suppress(StopAsyncIteration):
            await gen.__anext__()

    @patch("feedback_service.api.deps.SqlAlchemyUnitOfWork")
    @patch("feedback_service.api.deps.AsyncSessionLocal")
    async def test_get_uow_closes_on_exit(
        self, mock_session_local: MagicMock, mock_uow_class: MagicMock
    ) -> None:
        """Test get_uow properly closes UOW on generator exit."""
        # Arrange
        from feedback_service.api.deps import get_uow

        mock_aexit = AsyncMock(return_value=None)
        mock_uow_class.return_value.__aenter__ = AsyncMock(return_value=MagicMock())
        mock_uow_class.return_value.__aexit__ = mock_aexit

        # Act
        gen = get_uow()
        await gen.__anext__()

        # Clean up
        from contextlib import suppress
        with suppress(StopAsyncIteration):
            await gen.__anext__()

        # Assert
        mock_aexit.assert_called_once()

    @patch("feedback_service.api.deps.SqlAlchemyUnitOfWork")
    @patch("feedback_service.api.deps.AsyncSessionLocal")
    async def test_get_uow_handles_exception(
        self, mock_session_local: MagicMock, mock_uow_class: MagicMock
    ) -> None:
        """Test get_uow properly handles exceptions during yield."""
        # Arrange
        from feedback_service.api.deps import get_uow

        mock_aexit = AsyncMock(return_value=None)
        mock_uow_class.return_value.__aenter__ = AsyncMock(return_value=MagicMock())
        mock_uow_class.return_value.__aexit__ = mock_aexit

        # Act & Assert
        gen = get_uow()
        await gen.__anext__()

        # Simulate exception
        with pytest.raises(ValueError, match="Test error"):
            await gen.athrow(ValueError("Test error"))

        # Assert __aexit__ was called with exception info
        mock_aexit.assert_called_once()
