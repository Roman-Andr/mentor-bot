"""Unit tests for users API endpoints."""

from datetime import datetime
from typing import get_args
from unittest.mock import AsyncMock

import pytest
from auth_service.api import deps
from auth_service.api.deps import AdminUser, HRUser
from auth_service.core import ConflictException, NotFoundException
from auth_service.core.enums import UserRole
from auth_service.core.security import create_access_token
from auth_service.main import app
from auth_service.models import User
from fastapi.testclient import TestClient

# Get the actual dependency callables used by FastAPI
# So get_args returns (User, Depends(...)) and the Depends is at index 1
_admin_user_dependency = get_args(AdminUser)[1].dependency
_hr_user_dependency = get_args(HRUser)[1].dependency


def get_test_client():
    """Create a TestClient without lifespan events."""
    return TestClient(app)


def create_auth_headers(user_id: int = 1, role: UserRole = UserRole.ADMIN) -> dict:
    """Create authorization headers with JWT token."""
    token = create_access_token({"sub": str(user_id), "user_id": user_id, "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user():
    """Create an admin user."""
    from datetime import UTC

    return User(
        id=1,
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        employee_id="EMP001",
        is_active=True,
        is_verified=True,
        role=UserRole.ADMIN,
        created_at=datetime.now(UTC),
        language="ru",
        notification_telegram_enabled=True,
        notification_email_enabled=True,
    )


@pytest.fixture
def mentor_user():
    """Create a mentor user."""
    from datetime import UTC

    return User(
        id=2,
        email="mentor@example.com",
        first_name="Mentor",
        last_name="User",
        employee_id="EMP002",
        is_active=True,
        is_verified=True,
        role=UserRole.MENTOR,
        created_at=datetime.now(UTC),
        language="ru",
        notification_telegram_enabled=True,
        notification_email_enabled=True,
    )


@pytest.fixture
def newbie_user():
    """Create a newbie user."""
    from datetime import UTC

    user = User(
        id=3,
        email="newbie@example.com",
        first_name="Newbie",
        last_name="User",
        employee_id="EMP003",
        is_active=True,
        is_verified=True,
        role=UserRole.NEWBIE,
        created_at=datetime.now(UTC),
        language="ru",
        notification_telegram_enabled=True,
        notification_email_enabled=True,
    )
    # Add mentor assignment
    from auth_service.models import UserMentor

    mentor_relation = UserMentor(
        id=1,
        user_id=3,
        mentor_id=2,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    user.mentor_assignments.append(mentor_relation)
    return user


class TestGetUsers:
    """Tests for GET /api/v1/users/ endpoint."""

    def test_get_users_success(self, admin_user, mock_user_service):
        """Test getting list of users as admin."""
        users = [admin_user]
        mock_user_service.get_users = AsyncMock(return_value=(users, 1))

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["users"]) == 1
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_get_users_with_search_filter(self, admin_user, mock_user_service):
        """Test getting users with search filter."""
        users = [admin_user]
        mock_user_service.get_users = AsyncMock(return_value=(users, 1))

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/?search=admin",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            mock_user_service.get_users.assert_called_once()
            call_kwargs = mock_user_service.get_users.call_args.kwargs
            assert call_kwargs.get("search") == "admin"
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_get_users_with_role_filter(self, admin_user, mock_user_service):
        """Test getting users with role filter."""
        users = [admin_user]
        mock_user_service.get_users = AsyncMock(return_value=(users, 1))

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/?role=ADMIN",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            call_kwargs = mock_user_service.get_users.call_args.kwargs
            assert call_kwargs.get("role") == UserRole.ADMIN
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_get_users_with_department_filter(self, admin_user, mock_user_service):
        """Test getting users with department filter."""
        users = [admin_user]
        mock_user_service.get_users = AsyncMock(return_value=(users, 1))

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/?department_id=1",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            call_kwargs = mock_user_service.get_users.call_args.kwargs
            assert call_kwargs.get("department_id") == 1
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestCreateUser:
    """Tests for POST /api/v1/users/ endpoint."""

    def test_create_user_success(self, admin_user, mock_user_service):
        """Test creating a new user as admin."""
        from datetime import UTC

        new_user = User(
            id=4,
            email="new@example.com",
            first_name="New",
            last_name="User",
            employee_id="EMP004",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )
        mock_user_service.create_user = AsyncMock(return_value=new_user)

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/users/",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={
                    "email": "new@example.com",
                    "first_name": "New",
                    "last_name": "User",
                    "employee_id": "EMP004",
                    "password": "password123",
                    "role": "NEWBIE",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "new@example.com"
            assert data["employee_id"] == "EMP004"
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_create_user_conflict(self, admin_user, mock_user_service):
        """Test creating user with duplicate email returns 409."""
        mock_user_service.create_user = AsyncMock(side_effect=ConflictException("Email already registered"))

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/users/",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={
                    "email": "duplicate@example.com",
                    "first_name": "Duplicate",
                    "employee_id": "EMP005",
                    "password": "password123",
                },
            )

            assert response.status_code == 409
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestGetUserById:
    """Tests for GET /api/v1/users/{user_id} endpoint."""

    def test_get_user_by_id_self(self, admin_user, mock_user_service):
        """Test user can get their own info."""
        mock_user_service.get_user_by_id = AsyncMock(return_value=admin_user)

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                f"/api/v1/users/{admin_user.id}",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == admin_user.email
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_get_user_by_id_as_admin(self, admin_user, mock_user_service, newbie_user):
        """Test admin can get any user's info."""
        mock_user_service.get_user_by_id = AsyncMock(return_value=newbie_user)

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                f"/api/v1/users/{newbie_user.id}",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_get_user_by_id_not_found(self, admin_user, mock_user_service):
        """Test getting non-existent user returns 404."""
        mock_user_service.get_user_by_id = AsyncMock(side_effect=NotFoundException("User"))

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/999",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestUpdateUser:
    """Tests for PUT /api/v1/users/{user_id} endpoint."""

    def test_update_user_self(self, admin_user, mock_user_service):
        """Test user can update their own info."""
        from datetime import UTC

        updated_user = User(
            id=admin_user.id,
            email="updated@example.com",
            first_name="Updated",
            last_name="User",
            employee_id="EMP001",
            is_active=True,
            is_verified=True,
            role=UserRole.ADMIN,
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )
        mock_user_service.update_user = AsyncMock(return_value=updated_user)

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.put(
                f"/api/v1/users/{admin_user.id}",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={
                    "email": "updated@example.com",
                    "first_name": "Updated",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "updated@example.com"
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_update_user_as_admin(self, admin_user, mock_user_service, newbie_user):
        """Test admin can update any user."""
        from datetime import UTC

        updated_user = User(
            id=newbie_user.id,
            email="updated@example.com",
            first_name="Updated",
            last_name="User",
            employee_id="EMP003",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )
        mock_user_service.update_user = AsyncMock(return_value=updated_user)

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.put(
                f"/api/v1/users/{newbie_user.id}",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={
                    "email": "updated@example.com",
                    "first_name": "Updated",
                },
            )

            assert response.status_code == 200
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestDeactivateUser:
    """Tests for POST /api/v1/users/{user_id}/deactivate endpoint (covers lines 144-148)."""

    def test_deactivate_user_success(self, admin_user, mock_user_service):
        """Test admin can deactivate a user (covers lines 144-148)."""
        mock_user_service.deactivate_user = AsyncMock(return_value=None)

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/users/5/deactivate",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert "deactivated" in data["message"].lower()
            mock_user_service.deactivate_user.assert_awaited_once_with(5)
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_deactivate_user_not_found(self, admin_user, mock_user_service):
        """Test deactivating non-existent user returns 404 (covers lines 147-148)."""
        mock_user_service.deactivate_user = AsyncMock(side_effect=NotFoundException("User"))

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/users/999/deactivate",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestDeleteUser:
    """Tests for DELETE /api/v1/users/{user_id} endpoint."""

    def test_delete_user_success(self, admin_user, mock_user_service):
        """Test admin can permanently delete user."""
        mock_user_service.delete_user = AsyncMock(return_value=None)

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.delete(
                "/api/v1/users/5",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert "deleted" in data["message"].lower()
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_delete_user_not_found(self, admin_user, mock_user_service):
        """Test deleting non-existent user returns 404."""
        mock_user_service.delete_user = AsyncMock(side_effect=NotFoundException("User"))

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.delete(
                "/api/v1/users/999",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestGetUserByTelegramId:
    """Tests for GET /api/v1/users/by-telegram/{telegram_id} endpoint."""

    def test_get_user_by_telegram_id_success(self, admin_user, mock_user_service):
        """Test HR/admin can get user by Telegram ID."""
        from datetime import UTC

        user = User(
            id=5,
            email="telegram@example.com",
            first_name="Telegram",
            last_name="User",
            employee_id="EMP005",
            telegram_id=123456789,
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )
        mock_user_service.get_user_by_telegram_id = AsyncMock(return_value=user)

        async def mock_require_hr() -> User:
            return admin_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/by-telegram/123456789",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert data["telegram_id"] == 123456789
        finally:
            app.dependency_overrides.pop(_hr_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_get_user_by_telegram_id_not_found(self, admin_user, mock_user_service):
        """Test getting non-existent Telegram user returns 404."""
        mock_user_service.get_user_by_telegram_id = AsyncMock(return_value=None)

        async def mock_require_hr() -> User:
            return admin_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/by-telegram/999999",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(_hr_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestGetUserByEmail:
    """Tests for GET /api/v1/users/by-email/{email} endpoint."""

    def test_get_user_by_email_success(self, admin_user, mock_user_service):
        """Test HR/admin can get user by email."""
        from datetime import UTC

        user = User(
            id=6,
            email="findme@example.com",
            first_name="Find",
            last_name="Me",
            employee_id="EMP006",
            is_active=True,
            is_verified=True,
            role=UserRole.NEWBIE,
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )
        mock_user_service.get_user_by_email = AsyncMock(return_value=user)

        async def mock_require_hr() -> User:
            return admin_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/by-email/findme@example.com",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "findme@example.com"
        finally:
            app.dependency_overrides.pop(_hr_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestLinkTelegramAccount:
    """Tests for POST /api/v1/users/{user_id}/link-telegram endpoint."""

    def test_link_telegram_success(self, admin_user, mock_user_service):
        """Test linking Telegram account to user."""
        from datetime import UTC

        updated_user = User(
            id=admin_user.id,
            email=admin_user.email,
            first_name=admin_user.first_name,
            employee_id=admin_user.employee_id,
            telegram_id=987654321,
            username="@adminuser",
            is_active=True,
            is_verified=True,
            role=UserRole.ADMIN,
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )
        mock_user_service.link_telegram_account = AsyncMock(return_value=updated_user)

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                f"/api/v1/users/{admin_user.id}/link-telegram?telegram_id=987654321&username=@adminuser",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert data["telegram_id"] == 987654321
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_link_telegram_not_found_exception(self, admin_user, mock_user_service):
        """Test linking Telegram with NotFoundException returns 400 (covers line 203-204)."""
        mock_user_service.link_telegram_account = AsyncMock(side_effect=NotFoundException("User not found"))

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                f"/api/v1/users/{admin_user.id}/link-telegram?telegram_id=987654321",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 400
            assert "not found" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_link_telegram_conflict_exception(self, admin_user, mock_user_service):
        """Test linking Telegram with ConflictException returns 400 (covers line 203-204)."""
        mock_user_service.link_telegram_account = AsyncMock(side_effect=ConflictException("Telegram ID already linked"))

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                f"/api/v1/users/{admin_user.id}/link-telegram?telegram_id=987654321",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 400
            assert "already linked" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestChangeUserRole:
    """Tests for POST /api/v1/users/{user_id}/change-role endpoint."""

    def test_change_user_role_success(self, admin_user, mock_user_service, newbie_user):
        """Test admin can change user role."""
        from datetime import UTC

        updated_user = User(
            id=newbie_user.id,
            email=newbie_user.email,
            first_name=newbie_user.first_name,
            employee_id=newbie_user.employee_id,
            is_active=True,
            is_verified=True,
            role=UserRole.MENTOR,  # Changed from NEWBIE to MENTOR
            created_at=datetime.now(UTC),
            language="ru",
            notification_telegram_enabled=True,
            notification_email_enabled=True,
        )
        mock_user_service.update_user_role = AsyncMock(return_value=updated_user)

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                f"/api/v1/users/{newbie_user.id}/change-role?role=MENTOR",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "MENTOR"
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestChangePassword:
    """Tests for POST /api/v1/users/{user_id}/change-password endpoint."""

    def test_change_password_success(self, admin_user, mock_user_service):
        """Test user can change their password."""
        mock_user_service.change_password = AsyncMock(return_value=None)

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                f"/api/v1/users/{admin_user.id}/change-password?current_password=oldpass&new_password=newpass123",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert "password changed" in data["message"].lower()
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_change_password_wrong_current(self, admin_user, mock_user_service):
        """Test change password with wrong current password returns 400."""
        from auth_service.core import ValidationException

        mock_user_service.change_password = AsyncMock(side_effect=ValidationException("Current password is incorrect"))

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                f"/api/v1/users/{admin_user.id}/change-password?current_password=wrong&new_password=newpass123",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 400
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestGetUserByIdEdgeCases:
    """Additional edge case tests for GET /api/v1/users/{user_id}."""

    def test_get_user_by_id_permission_denied(self, newbie_user, mock_user_service):
        """Test that newbie cannot access another user's info."""
        mock_user_service.get_user_by_id = AsyncMock(return_value=None)

        async def mock_get_current() -> User:
            # newbie_user has no mentor assignments that would grant access
            return newbie_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            # Try to access a different user (id=999) who is not self, not HR/admin, and not a mentor
            response = client.get(
                "/api/v1/users/999",
                headers=create_auth_headers(newbie_user.id, newbie_user.role),
            )

            assert response.status_code == 403
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestUpdateUserEdgeCases:
    """Additional edge case tests for PUT /api/v1/users/{user_id}."""

    def test_update_user_permission_denied(self, newbie_user, mock_user_service):
        """Test that newbie cannot update another user's info."""
        mock_user_service.update_user = AsyncMock(return_value=None)

        async def mock_get_current() -> User:
            return newbie_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            # Try to update a different user (id=999)
            response = client.put(
                "/api/v1/users/999",
                headers=create_auth_headers(newbie_user.id, newbie_user.role),
                json={"first_name": "Hacked"},
            )

            assert response.status_code == 403
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_update_user_conflict_exception(self, admin_user, mock_user_service):
        """Test update user with ConflictException returns 409."""
        from auth_service.core import ConflictException

        mock_user_service.update_user = AsyncMock(side_effect=ConflictException("Email already in use"))

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.put(
                f"/api/v1/users/{admin_user.id}",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={"email": "duplicate@example.com"},
            )

            assert response.status_code == 409
            assert "Email already in use" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)

    def test_update_user_not_found_exception(self, admin_user, mock_user_service):
        """Test update user with NotFoundException returns 404 (covers line 126)."""
        mock_user_service.update_user = AsyncMock(side_effect=NotFoundException("User not found"))

        async def mock_get_current() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.put(
                f"/api/v1/users/{admin_user.id}",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={"email": "new@example.com"},
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestGetUserByEmailEdgeCases:
    """Additional edge case tests for GET /api/v1/users/by-email/{email}."""

    def test_get_user_by_email_not_found(self, admin_user, mock_user_service):
        """Test get user by email when user not found returns 404."""
        mock_user_service.get_user_by_email = AsyncMock(return_value=None)

        async def mock_require_hr() -> User:
            return admin_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/users/by-email/nonexistent@example.com",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 404
            assert "User not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(_hr_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestLinkTelegramEdgeCases:
    """Additional edge case tests for POST /api/v1/users/{user_id}/link-telegram."""

    def test_link_telegram_permission_denied(self, newbie_user, mock_user_service):
        """Test that newbie cannot link telegram to another user's account."""
        mock_user_service.link_telegram_account = AsyncMock(return_value=None)

        async def mock_get_current() -> User:
            return newbie_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            # Try to link telegram to a different user (id=999)
            response = client.post(
                "/api/v1/users/999/link-telegram?telegram_id=123456",
                headers=create_auth_headers(newbie_user.id, newbie_user.role),
            )

            assert response.status_code == 403
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestChangeUserRoleEdgeCases:
    """Additional edge case tests for POST /api/v1/users/{user_id}/change-role."""

    def test_change_user_role_validation_exception(self, admin_user, mock_user_service, newbie_user):
        """Test change user role with ValidationException returns 400."""
        from auth_service.core import ValidationException

        mock_user_service.update_user_role = AsyncMock(
            side_effect=ValidationException("Cannot change role of inactive user")
        )

        async def mock_require_admin() -> User:
            return admin_user

        app.dependency_overrides[_admin_user_dependency] = mock_require_admin
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            response = client.post(
                f"/api/v1/users/{newbie_user.id}/change-role?role=MENTOR",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 400
            assert "Cannot change role of inactive user" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(_admin_user_dependency, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestChangePasswordEdgeCases:
    """Additional edge case tests for POST /api/v1/users/{user_id}/change-password."""

    def test_change_password_permission_denied(self, newbie_user, mock_user_service):
        """Test that newbie cannot change another user's password."""
        mock_user_service.change_password = AsyncMock(return_value=None)

        async def mock_get_current() -> User:
            return newbie_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current
        app.dependency_overrides[deps.get_user_service] = lambda: mock_user_service

        try:
            client = get_test_client()
            # Try to change password for a different user (id=999)
            response = client.post(
                "/api/v1/users/999/change-password?current_password=old&new_password=new",
                headers=create_auth_headers(newbie_user.id, newbie_user.role),
            )

            assert response.status_code == 403
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_user_service, None)


class TestGetUserPreferences:
    """Tests for GET /api/v1/users/{user_id}/preferences endpoint."""

    async def test_get_user_preferences_service_auth(self, admin_user, mock_user_service):
        """Test getting user preferences via service auth (covers lines 325-351)."""
        from auth_service.api.endpoints.users import get_user_preferences

        mock_user_service.get_user_by_id = AsyncMock(return_value=admin_user)

        result = await get_user_preferences(
            user_id=admin_user.id,
            current_user=None,
            user_service=mock_user_service,
            is_service=True,
        )

        assert result.language == admin_user.language
        assert result.notification_telegram_enabled == admin_user.notification_telegram_enabled
        assert result.notification_email_enabled == admin_user.notification_email_enabled

    async def test_get_user_preferences_no_auth(self, mock_user_service):
        """Test getting user preferences without authentication raises permission denied (covers lines 329-341)."""
        from auth_service.api.endpoints.users import get_user_preferences
        from auth_service.core import PermissionDenied

        with pytest.raises(PermissionDenied):
            await get_user_preferences(
                user_id=1,
                current_user=None,
                user_service=mock_user_service,
                is_service=False,
            )

    async def test_get_user_preferences_self(self, admin_user, mock_user_service):
        """Test user can get their own preferences."""
        from auth_service.api.endpoints.users import get_user_preferences

        mock_user_service.get_user_by_id = AsyncMock(return_value=admin_user)

        result = await get_user_preferences(
            user_id=admin_user.id,
            current_user=admin_user,
            user_service=mock_user_service,
            is_service=False,
        )

        assert result.language == admin_user.language

    async def test_get_user_preferences_permission_denied(self, newbie_user, mock_user_service):
        """Test that a regular user cannot view another user's preferences (covers lines 336-341)."""
        from auth_service.api.endpoints.users import get_user_preferences
        from auth_service.core import PermissionDenied

        # newbie_user tries to access another user's (id=999) preferences
        with pytest.raises(PermissionDenied):
            await get_user_preferences(
                user_id=999,
                current_user=newbie_user,
                user_service=mock_user_service,
                is_service=False,
            )

    async def test_get_user_preferences_not_found(self, admin_user, mock_user_service):
        """Test getting preferences for non-existent user returns 404 (covers lines 343-354)."""
        from auth_service.api.endpoints.users import get_user_preferences
        from fastapi import HTTPException

        mock_user_service.get_user_by_id = AsyncMock(side_effect=NotFoundException("User"))

        with pytest.raises(HTTPException) as exc_info:
            await get_user_preferences(
                user_id=999,
                current_user=admin_user,
                user_service=mock_user_service,
                is_service=True,
            )

        assert exc_info.value.status_code == 404


class TestUpdateMyPreferences:
    """Tests for PUT /api/v1/users/me/preferences endpoint."""

    async def test_update_my_preferences_success(self, admin_user, mock_user_service):
        """Test updating current user's preferences."""
        from datetime import UTC

        from auth_service.api.endpoints.users import update_my_preferences
        from auth_service.schemas import UserPreferencesUpdate

        updated_user = User(
            id=admin_user.id,
            email=admin_user.email,
            first_name=admin_user.first_name,
            last_name=admin_user.last_name,
            employee_id=admin_user.employee_id,
            is_active=True,
            is_verified=True,
            role=admin_user.role,
            created_at=datetime.now(UTC),
            language="en",  # Changed from "ru"
            notification_telegram_enabled=False,  # Changed from True
            notification_email_enabled=False,  # Changed from True
        )
        mock_user_service.update_user_preferences = AsyncMock(return_value=updated_user)

        preferences_data = UserPreferencesUpdate(
            language="en",
            notification_telegram_enabled=False,
            notification_email_enabled=False,
        )

        result = await update_my_preferences(
            preferences_data=preferences_data,
            user_service=mock_user_service,
            current_user=admin_user,
        )

        assert result.language == "en"
        assert result.notification_telegram_enabled is False
        assert result.notification_email_enabled is False

    async def test_update_my_preferences_not_found(self, admin_user, mock_user_service):
        """Test updating preferences for non-existent user returns 404 (covers lines 364-378)."""
        from auth_service.api.endpoints.users import update_my_preferences
        from auth_service.schemas import UserPreferencesUpdate
        from fastapi import HTTPException

        mock_user_service.update_user_preferences = AsyncMock(side_effect=NotFoundException("User"))

        preferences_data = UserPreferencesUpdate(language="en")

        with pytest.raises(HTTPException) as exc_info:
            await update_my_preferences(
                preferences_data=preferences_data,
                user_service=mock_user_service,
                current_user=admin_user,
            )

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    async def test_get_my_preferences_not_found(self, admin_user, mock_user_service):
        """Test get_my_preferences with NotFoundException (covers lines 358-366)."""
        from auth_service.api.endpoints.users import get_my_preferences
        from fastapi import HTTPException

        mock_user_service.get_user_by_id = AsyncMock(side_effect=NotFoundException("User not found"))

        with pytest.raises(HTTPException) as exc_info:
            await get_my_preferences(
                user_service=mock_user_service,
                current_user=admin_user,
            )

        assert exc_info.value.status_code == 404

    async def test_get_my_preferences_success(self, admin_user, mock_user_service):
        """Test get_my_preferences success (covers line 360)."""
        from auth_service.api.endpoints.users import get_my_preferences

        mock_user_service.get_user_by_id = AsyncMock(return_value=admin_user)

        result = await get_my_preferences(
            user_service=mock_user_service,
            current_user=admin_user,
        )

        assert result.language == "ru"
        assert result.notification_telegram_enabled is True
