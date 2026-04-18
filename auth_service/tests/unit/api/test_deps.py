"""Unit tests for API dependencies (api/deps.py)."""

from datetime import UTC, datetime
from typing import get_args, get_origin
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from auth_service.api import deps
from auth_service.core import AuthException, PermissionDenied, UserRole
from auth_service.models import User


class TestGetUow:
    """Tests for get_uow dependency."""

    async def test_get_uow_exception_rollback(self):
        """Test get_uow rolls back and re-raises on exception (covers lines 26-28)."""
        from auth_service.repositories.unit_of_work import SqlAlchemyUnitOfWork

        # Create a mock UOW
        mock_uow = MagicMock(spec=SqlAlchemyUnitOfWork)
        mock_uow.commit = AsyncMock()
        mock_uow.rollback = AsyncMock()
        mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow.__aexit__ = AsyncMock(return_value=None)

        # Create mock session factory
        mock_session_factory = MagicMock()

        # Patch SqlAlchemyUnitOfWork to return our mock
        with patch.object(deps, 'SqlAlchemyUnitOfWork', return_value=mock_uow):
            gen = deps.get_uow()
            uow = await gen.__anext__()  # Get the UOW from generator

            # Simulate an exception during UOW use
            with pytest.raises(ValueError, match="Test error"):
                try:
                    raise ValueError("Test error")
                except Exception:
                    await gen.athrow(ValueError("Test error"))

        # Verify rollback was called
        mock_uow.rollback.assert_awaited_once()

    async def test_get_uow_success_commit(self):
        """Test get_uow commits on successful completion."""
        from auth_service.repositories.unit_of_work import SqlAlchemyUnitOfWork

        # Create a mock UOW
        mock_uow = MagicMock(spec=SqlAlchemyUnitOfWork)
        mock_uow.commit = AsyncMock()
        mock_uow.rollback = AsyncMock()
        mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow.__aexit__ = AsyncMock(return_value=None)

        # Patch SqlAlchemyUnitOfWork
        with patch.object(deps, 'SqlAlchemyUnitOfWork', return_value=mock_uow):
            async for uow in deps.get_uow():
                # Normal operation without exception
                pass

        # Verify commit was called
        mock_uow.commit.assert_awaited_once()
        mock_uow.rollback.assert_not_awaited()


class TestGetAuthService:
    """Tests for get_auth_service dependency."""

    async def test_get_auth_service_returns_instance(self, mock_uow):
        """Test get_auth_service returns AuthService instance."""
        from auth_service.services import AuthService

        auth_service = await deps.get_auth_service(mock_uow)

        assert isinstance(auth_service, AuthService)
        assert auth_service._uow == mock_uow


class TestGetUserService:
    """Tests for get_user_service dependency."""

    async def test_get_user_service_returns_instance(self, mock_uow):
        """Test get_user_service returns UserService instance."""
        from auth_service.services import UserService

        user_service = await deps.get_user_service(mock_uow)

        assert isinstance(user_service, UserService)
        assert user_service._uow == mock_uow


class TestGetInvitationService:
    """Tests for get_invitation_service dependency."""

    async def test_get_invitation_service_returns_instance(self, mock_uow):
        """Test get_invitation_service returns InvitationService instance."""
        from auth_service.services import InvitationService

        invitation_service = await deps.get_invitation_service(mock_uow)

        assert isinstance(invitation_service, InvitationService)
        assert invitation_service._uow == mock_uow


class TestGetDepartmentService:
    """Tests for get_department_service dependency."""

    async def test_get_department_service_returns_instance(self, mock_uow):
        """Test get_department_service returns DepartmentService instance."""
        from auth_service.services import DepartmentService

        department_service = await deps.get_department_service(mock_uow)

        assert isinstance(department_service, DepartmentService)
        assert department_service._uow == mock_uow


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    async def test_get_current_user_no_credentials(self):
        """Test get_current_user raises AuthException when no credentials."""
        mock_auth_service = MagicMock()

        with pytest.raises(AuthException) as exc_info:
            await deps.get_current_user(None, mock_auth_service)

        assert "Not authenticated" in str(exc_info.value.detail)

    async def test_get_current_user_valid_token(self, admin_user):
        """Test get_current_user returns user with valid token."""
        mock_auth_service = MagicMock()
        mock_auth_service.get_current_user = AsyncMock(return_value=admin_user)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        user = await deps.get_current_user(credentials, mock_auth_service)

        assert user == admin_user
        mock_auth_service.get_current_user.assert_called_once_with("valid_token")

    async def test_get_current_user_inactive_user(self):
        """Test get_current_user raises AuthException when user is inactive."""
        from datetime import UTC
        inactive_user = User(
            id=1,
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            employee_id="EMP001",
            is_active=False,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
        )

        mock_auth_service = MagicMock()
        mock_auth_service.get_current_user = AsyncMock(return_value=inactive_user)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        # The inactive user check raises HTTPException but it's caught and wrapped in AuthException
        with pytest.raises(AuthException) as exc_info:
            await deps.get_current_user(credentials, mock_auth_service)

        # The AuthException wraps the HTTPException with a generic message
        assert "Invalid authentication credentials" in str(exc_info.value.detail)

    async def test_get_current_user_auth_exception(self):
        """Test get_current_user raises AuthException on auth service error."""
        mock_auth_service = MagicMock()
        mock_auth_service.get_current_user = AsyncMock(side_effect=AuthException("Invalid token"))

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")

        with pytest.raises(AuthException) as exc_info:
            await deps.get_current_user(credentials, mock_auth_service)

        assert "Invalid authentication credentials" in str(exc_info.value.detail)

    async def test_get_current_user_generic_exception(self):
        """Test get_current_user raises AuthException on generic error."""
        mock_auth_service = MagicMock()
        mock_auth_service.get_current_user = AsyncMock(side_effect=ValueError("Some error"))

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

        with pytest.raises(AuthException) as exc_info:
            await deps.get_current_user(credentials, mock_auth_service)

        assert "Invalid authentication credentials" in str(exc_info.value.detail)


class TestRequireRole:
    """Tests for require_role factory function."""

    async def test_require_admin_success(self, admin_user):
        """Test require_admin allows admin user."""
        require_admin = deps.require_role([UserRole.ADMIN])

        user = await require_admin(admin_user)

        assert user == admin_user

    async def test_require_admin_denies_non_admin(self, hr_user):
        """Test require_admin denies non-admin user."""
        require_admin = deps.require_role([UserRole.ADMIN])

        with pytest.raises(PermissionDenied):
            await require_admin(hr_user)

    async def test_require_hr_success(self, hr_user):
        """Test require_hr_allows_hr_user."""
        require_hr = deps.require_role([UserRole.HR, UserRole.ADMIN])

        user = await require_hr(hr_user)

        assert user == hr_user

    async def test_require_hr_allows_admin(self, admin_user):
        """Test require_hr allows admin user."""
        require_hr = deps.require_role([UserRole.HR, UserRole.ADMIN])

        user = await require_hr(admin_user)

        assert user == admin_user

    async def test_require_hr_denies_newbie(self, newbie_user):
        """Test require_hr denies newbie user."""
        require_hr = deps.require_role([UserRole.HR, UserRole.ADMIN])

        with pytest.raises(PermissionDenied):
            await require_hr(newbie_user)

    async def test_require_mentor_success(self, mentor_user):
        """Test require_mentor allows mentor user."""
        require_mentor = deps.require_role([UserRole.MENTOR, UserRole.HR, UserRole.ADMIN])

        user = await require_mentor(mentor_user)

        assert user == mentor_user

    async def test_require_mentor_allows_hr(self, hr_user):
        """Test require_mentor allows HR user."""
        require_mentor = deps.require_role([UserRole.MENTOR, UserRole.HR, UserRole.ADMIN])

        user = await require_mentor(hr_user)

        assert user == hr_user

    async def test_require_mentor_allows_admin(self, admin_user):
        """Test require_mentor allows admin user."""
        require_mentor = deps.require_role([UserRole.MENTOR, UserRole.HR, UserRole.ADMIN])

        user = await require_mentor(admin_user)

        assert user == admin_user

    async def test_require_mentor_denies_newbie(self, newbie_user):
        """Test require_mentor denies newbie user."""
        require_mentor = deps.require_role([UserRole.MENTOR, UserRole.HR, UserRole.ADMIN])

        with pytest.raises(PermissionDenied):
            await require_mentor(newbie_user)


class TestTypeAliases:
    """Tests for type alias annotations."""

    def test_admin_user_is_annotated(self):
        """Test AdminUser is an Annotated type."""
        origin = get_origin(deps.AdminUser)
        assert origin is not None

    def test_hr_user_is_annotated(self):
        """Test HRUser is an Annotated type."""
        origin = get_origin(deps.HRUser)
        assert origin is not None

    def test_mentor_user_is_annotated(self):
        """Test MentorUser is an Annotated type."""
        origin = get_origin(deps.MentorUser)
        assert origin is not None

    def test_current_user_is_annotated(self):
        """Test CurrentUser is an Annotated type."""
        origin = get_origin(deps.CurrentUser)
        assert origin is not None

    def test_uow_dep_is_annotated(self):
        """Test UOWDep is an Annotated type."""
        origin = get_origin(deps.UOWDep)
        assert origin is not None

    def test_user_service_dep_is_annotated(self):
        """Test UserServiceDep is an Annotated type."""
        origin = get_origin(deps.UserServiceDep)
        assert origin is not None

    def test_invitation_service_dep_is_annotated(self):
        """Test InvitationServiceDep is an Annotated type."""
        origin = get_origin(deps.InvitationServiceDep)
        assert origin is not None

    def test_auth_service_dep_is_annotated(self):
        """Test AuthServiceDep is an Annotated type."""
        origin = get_origin(deps.AuthServiceDep)
        assert origin is not None

    def test_department_service_dep_is_annotated(self):
        """Test DepartmentServiceDep is an Annotated type."""
        origin = get_origin(deps.DepartmentServiceDep)
        assert origin is not None
