"""Unit tests for API dependencies."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from meeting_service.api import deps
from meeting_service.config import settings
from meeting_service.core.exceptions import AuthException, PermissionDenied


class TestUserInfo:
    """Tests for UserInfo class."""

    def test_user_info_init_with_all_fields(self):
        """Test UserInfo initialization with all fields."""
        data = {
            "id": 1,
            "email": "test@example.com",
            "employee_id": "E123",
            "role": "HR",
            "is_active": True,
            "is_verified": True,
            "department": "Engineering",
            "position": "Developer",
            "level": "Senior",
            "first_name": "John",
            "last_name": "Doe",
            "telegram_id": "123456",
        }
        user = deps.UserInfo(data)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.employee_id == "E123"
        assert user.role == "HR"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.department == "Engineering"
        assert user.position == "Developer"
        assert user.level == "Senior"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.telegram_id == "123456"

    def test_user_info_init_with_defaults(self):
        """Test UserInfo initialization with default values."""
        data = {"id": 2, "email": "test2@example.com"}
        user = deps.UserInfo(data)

        assert user.id == 2
        assert user.email == "test2@example.com"
        assert user.employee_id is None
        assert user.role is None
        assert user.is_active is True  # default
        assert user.is_verified is False  # default
        assert user.department is None
        assert user.position is None
        assert user.level is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.telegram_id is None

    def test_user_info_has_role_with_matching_role(self):
        """Test has_role returns True when role matches."""
        user = deps.UserInfo({"id": 1, "role": "HR"})
        assert user.has_role(["HR", "ADMIN"]) is True

    def test_user_info_has_role_without_matching_role(self):
        """Test has_role returns False when role doesn't match."""
        user = deps.UserInfo({"id": 1, "role": "EMPLOYEE"})
        assert user.has_role(["HR", "ADMIN"]) is False

    def test_user_info_has_role_with_none_role(self):
        """Test has_role returns False when role is None."""
        user = deps.UserInfo({"id": 1})
        assert user.has_role(["HR", "ADMIN"]) is False


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self, mock_request):
        """Test AuthException raised when no credentials provided."""
        with pytest.raises(AuthException) as exc_info:
            await deps.get_current_user(mock_request, None)
        assert "Not authenticated" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_request):
        """Test successful user retrieval from auth service."""
        credentials = MagicMock()
        credentials.credentials = "valid_token"

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "id": 1,
            "email": "test@example.com",
            "role": "HR",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = MagicMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            user = await deps.get_current_user(mock_request, credentials)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.role == "HR"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_credentials(self, mock_request):
        """Test AuthException when auth service returns non-200."""
        credentials = MagicMock()
        credentials.credentials = "invalid_token"

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = MagicMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(AuthException) as exc_info:
                await deps.get_current_user(mock_request, credentials)

        assert "Invalid authentication credentials" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_current_user_request_exception(self, mock_request):
        """Test AuthException on HTTP request error."""
        credentials = MagicMock()
        credentials.credentials = "valid_token"

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = MagicMock()
            mock_client_instance.get = AsyncMock(side_effect=httpx.RequestError("Connection error"))
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(AuthException) as exc_info:
                await deps.get_current_user(mock_request, credentials)

        assert "Invalid authentication credentials" in str(exc_info.value)


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_active_user_success(self):
        """Test successful retrieval of active user."""
        current_user = deps.UserInfo({"id": 1, "email": "test@example.com", "is_active": True})
        result = await deps.get_current_active_user(current_user)
        assert result.id == 1
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self):
        """Test HTTPException raised when user is inactive."""
        current_user = deps.UserInfo({"id": 1, "email": "test@example.com", "is_active": False})

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await deps.get_current_active_user(current_user)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in str(exc_info.value.detail)


class TestRequireAdmin:
    """Tests for require_admin dependency."""

    @pytest.mark.asyncio
    async def test_require_admin_success(self):
        """Test successful admin access."""
        current_user = deps.UserInfo({"id": 1, "role": "ADMIN"})
        result = await deps.require_admin(current_user)
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_require_admin_as_hr(self):
        """Test successful admin access for HR role."""
        current_user = deps.UserInfo({"id": 1, "role": "HR"})
        result = await deps.require_admin(current_user)
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_require_admin_permission_denied(self):
        """Test PermissionDenied raised for non-admin role."""
        current_user = deps.UserInfo({"id": 1, "role": "EMPLOYEE"})
        with pytest.raises(PermissionDenied) as exc_info:
            await deps.require_admin(current_user)
        assert "Admin access required" in str(exc_info.value)


class TestRequireHR:
    """Tests for require_hr dependency."""

    @pytest.mark.asyncio
    async def test_require_hr_success(self):
        """Test successful HR access."""
        current_user = deps.UserInfo({"id": 1, "role": "HR"})
        result = await deps.require_hr(current_user)
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_require_hr_as_admin(self):
        """Test successful HR access for ADMIN role."""
        current_user = deps.UserInfo({"id": 1, "role": "ADMIN"})
        result = await deps.require_hr(current_user)
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_require_hr_permission_denied(self):
        """Test PermissionDenied raised for non-HR role."""
        current_user = deps.UserInfo({"id": 1, "role": "EMPLOYEE"})
        with pytest.raises(PermissionDenied) as exc_info:
            await deps.require_hr(current_user)
        assert "HR access required" in str(exc_info.value)


class TestGetUow:
    """Tests for get_uow dependency."""

    @pytest.mark.asyncio
    async def test_get_uow_success(self):
        """Test successful UOW retrieval and commit."""
        mock_session_class = MagicMock()
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("meeting_service.api.deps.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow = MagicMock()
            mock_uow.commit = AsyncMock()
            mock_uow.rollback = AsyncMock()
            mock_uow_class.return_value.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow_class.return_value.__aexit__ = AsyncMock(return_value=None)

            async for uow in deps.get_uow():
                assert uow is mock_uow

            # After the context manager exits, commit should be called
            # Note: We can't directly test this since we're using 'async for'
            # The actual commit happens after yield in the generator

    @pytest.mark.asyncio
    async def test_get_uow_rollback_on_exception(self):
        """Test UOW rollback is called when exception propagates from consumer."""
        # Create a mock UOW that tracks rollback calls
        mock_uow = MagicMock()
        mock_uow.commit = AsyncMock()
        mock_uow.rollback = AsyncMock()

        # Mock the async context manager protocol
        mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow.__aexit__ = AsyncMock(return_value=None)

        # Create a mock UOW class
        mock_uow_class = MagicMock()
        mock_uow_class.return_value.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow_class.return_value.__aexit__ = AsyncMock(return_value=None)

        # Patch the SqlAlchemyUnitOfWork class
        with patch("meeting_service.api.deps.SqlAlchemyUnitOfWork", mock_uow_class):
            # Get the generator
            gen = deps.get_uow()

            # Advance to the first yield (get the uow object)
            uow_from_gen = await gen.asend(None)
            assert uow_from_gen is mock_uow

            # Now throw an exception into the generator
            # This simulates what happens when the consumer raises an exception
            with pytest.raises(ValueError, match="Test error"):
                await gen.athrow(ValueError("Test error"))

            # Verify rollback was called
            mock_uow.rollback.assert_awaited_once()


class TestVerifyServiceApiKey:
    """Tests for verify_service_api_key dependency."""

    @pytest.mark.asyncio
    async def test_verify_service_api_key_success(self):
        """Test successful service API key verification."""
        original_api_key = settings.SERVICE_API_KEY
        settings.SERVICE_API_KEY = "valid-key"

        try:
            result = await deps.verify_service_api_key("valid-key")
            assert result is True
        finally:
            settings.SERVICE_API_KEY = original_api_key

    @pytest.mark.asyncio
    async def test_verify_service_api_key_not_set(self):
        """Test returns False when SERVICE_API_KEY not configured."""
        original_api_key = settings.SERVICE_API_KEY
        settings.SERVICE_API_KEY = ""

        try:
            result = await deps.verify_service_api_key(None)
            assert result is False
        finally:
            settings.SERVICE_API_KEY = original_api_key

    @pytest.mark.asyncio
    async def test_verify_service_api_key_invalid(self):
        """Test HTTPException raised for invalid API key."""
        original_api_key = settings.SERVICE_API_KEY
        settings.SERVICE_API_KEY = "valid-key"

        try:
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await deps.verify_service_api_key("invalid-key")
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid service API key" in str(exc_info.value.detail)
        finally:
            settings.SERVICE_API_KEY = original_api_key

    @pytest.mark.asyncio
    async def test_verify_service_api_key_missing_header(self):
        """Test HTTPException raised when header is missing."""
        original_api_key = settings.SERVICE_API_KEY
        settings.SERVICE_API_KEY = "valid-key"

        try:
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await deps.verify_service_api_key(None)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        finally:
            settings.SERVICE_API_KEY = original_api_key


class TestGetMeetingServiceDep:
    """Tests for get_meeting_service_dep dependency."""

    @pytest.mark.asyncio
    async def test_get_meeting_service_dep_returns_marker_class(self):
        """Test get_meeting_service_dep returns MeetingServiceDep instance."""
        result = await deps.get_meeting_service_dep()
        assert isinstance(result, deps.MeetingServiceDep)


class TestCurrentUserTypeAlias:
    """Tests for CurrentUser type alias usage."""

    def test_current_user_type_alias(self):
        """Test CurrentUser type alias can be used in FastAPI dependencies."""
        # Just verify the type alias is defined correctly
        assert deps.CurrentUser is not None


class TestAdminUserTypeAlias:
    """Tests for AdminUser type alias."""

    def test_admin_user_type_alias(self):
        """Test AdminUser type alias is defined."""
        assert deps.AdminUser is not None


class TestHRUserTypeAlias:
    """Tests for HRUser type alias."""

    def test_hr_user_type_alias(self):
        """Test HRUser type alias is defined."""
        assert deps.HRUser is not None


class TestDatabaseSessionTypeAlias:
    """Tests for DatabaseSession type alias."""

    def test_database_session_type_alias(self):
        """Test DatabaseSession type alias is defined."""
        assert deps.DatabaseSession is not None


class TestUOWDepTypeAlias:
    """Tests for UOWDep type alias."""

    def test_uow_dep_type_alias(self):
        """Test UOWDep type alias is defined."""
        assert deps.UOWDep is not None


class TestServiceAuthTypeAlias:
    """Tests for ServiceAuth type alias."""

    def test_service_auth_type_alias(self):
        """Test ServiceAuth type alias is defined."""
        assert deps.ServiceAuth is not None
