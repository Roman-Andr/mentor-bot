"""Unit tests for API dependencies."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException, status

from feedback_service.api.deps import (
    UserInfo,
    get_current_active_user,
    get_current_user,
    require_admin,
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
        assert "unavailable" in exc_info.value.detail.lower()


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
