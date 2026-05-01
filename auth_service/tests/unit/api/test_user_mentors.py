"""Unit tests for user-mentors API endpoints."""

from datetime import UTC, datetime
from typing import get_args
from unittest.mock import AsyncMock, patch

import pytest
from auth_service.api import deps
from auth_service.api.deps import HRUser
from auth_service.core.enums import UserRole
from auth_service.core.security import create_access_token
from auth_service.main import app
from auth_service.models import User, UserMentor
from fastapi.testclient import TestClient

# Get the actual HRUser dependency callable used by FastAPI
# So get_args returns (User, Depends(...)) and the Depends is at index 1
_hr_user_dependency = get_args(HRUser)[1].dependency


@pytest.fixture(autouse=True)
def mock_lifespan_db_operations():
    """Patch DB operations during app lifespan to avoid connection errors."""
    with patch("auth_service.main.init_db"), patch("auth_service.main.create_default_admin_user"):
        yield


def create_auth_headers(user_id: int = 1, role: UserRole = UserRole.HR) -> dict:
    """Create authorization headers with JWT token."""
    token = create_access_token({"sub": str(user_id), "user_id": user_id, "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def hr_user():
    """Create an HR user."""
    return User(
        id=1,
        email="hr@example.com",
        first_name="HR",
        last_name="User",
        employee_id="EMP001",
        is_active=True,
        is_verified=True,
        role=UserRole.HR,
    )


@pytest.fixture
def mentor_user():
    """Create a mentor user."""
    return User(
        id=2,
        email="mentor@example.com",
        first_name="Mentor",
        last_name="User",
        employee_id="EMP002",
        is_active=True,
        is_verified=True,
        role=UserRole.MENTOR,
    )


@pytest.fixture
def newbie_user():
    """Create a newbie user."""
    return User(
        id=3,
        email="newbie@example.com",
        first_name="Newbie",
        last_name="User",
        employee_id="EMP003",
        is_active=True,
        is_verified=True,
        role=UserRole.NEWBIE,
    )


@pytest.fixture
def sample_relation(newbie_user, mentor_user):
    """Create a sample user-mentor relationship."""
    return UserMentor(
        id=1,
        user_id=newbie_user.id,
        mentor_id=mentor_user.id,
        is_active=True,
        notes="Test mentor relationship",
        created_at=datetime.now(UTC),
        updated_at=None,
    )


class TestGetUserMentors:
    """Tests for GET /api/v1/user-mentors/ endpoint."""

    def test_get_all_relations(self, hr_user, mock_uow, sample_relation):
        """Test getting all user-mentor relations."""
        mock_uow.user_mentors.get_all = AsyncMock(return_value=[sample_relation])

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/user-mentors/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["relations"]) == 1
        assert data["relations"][0]["user_id"] == 3
        assert data["relations"][0]["mentor_id"] == 2

    def test_get_relations_by_user_id(self, hr_user, mock_uow, sample_relation, newbie_user):
        """Test getting relations filtered by user_id."""
        mock_uow.user_mentors.get_by_user_id = AsyncMock(return_value=[sample_relation])

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/user-mentors/?user_id={newbie_user.id}",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 200
        mock_uow.user_mentors.get_by_user_id.assert_called_once_with(newbie_user.id)

    def test_get_relations_by_mentor_id(self, hr_user, mock_uow, sample_relation, mentor_user):
        """Test getting relations filtered by mentor_id."""
        mock_uow.user_mentors.get_by_mentor_id = AsyncMock(return_value=[sample_relation])

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/user-mentors/?mentor_id={mentor_user.id}",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 200
        mock_uow.user_mentors.get_by_mentor_id.assert_called_once_with(mentor_user.id)


class TestCreateUserMentor:
    """Tests for POST /api/v1/user-mentors/ endpoint."""

    def test_create_relation_user_is_own_mentor(self, hr_user, mock_uow, newbie_user):
        """Test creating relation where user is their own mentor returns 422 (covers line 51)."""

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/user-mentors/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
                json={
                    "user_id": newbie_user.id,
                    "mentor_id": newbie_user.id,  # Same as user_id
                    "notes": "Self assignment",
                },
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 422
        assert "own mentor" in response.json()["detail"].lower()

    def test_create_relation_success(self, hr_user, mock_uow, sample_relation, newbie_user, mentor_user):
        """Test creating a new user-mentor relationship."""
        mock_uow.user_mentors.get_by_user_and_mentor = AsyncMock(return_value=None)
        mock_uow.user_mentors.get_active_by_user_id = AsyncMock(return_value=None)
        mock_uow.user_mentors.create = AsyncMock(return_value=sample_relation)

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/user-mentors/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
                json={
                    "user_id": newbie_user.id,
                    "mentor_id": mentor_user.id,
                    "notes": "New mentor assignment",
                },
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == newbie_user.id
        assert data["mentor_id"] == mentor_user.id
        assert data["is_active"] is True

    def test_create_relation_already_exists(self, hr_user, mock_uow, sample_relation, newbie_user, mentor_user):
        """Test creating relation that already exists returns 409."""
        mock_uow.user_mentors.get_by_user_and_mentor = AsyncMock(return_value=sample_relation)

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/user-mentors/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
                json={
                    "user_id": newbie_user.id,
                    "mentor_id": mentor_user.id,
                },
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.usefixtures("mentor_user")
    def test_create_relation_user_has_active_mentor(self, hr_user, mock_uow, sample_relation, newbie_user):
        """Test creating relation when user already has active mentor returns 409."""
        mock_uow.user_mentors.get_by_user_and_mentor = AsyncMock(return_value=None)
        mock_uow.user_mentors.get_active_by_user_id = AsyncMock(return_value=sample_relation)

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/user-mentors/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
                json={
                    "user_id": newbie_user.id,
                    "mentor_id": 999,  # Different mentor
                },
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 409
        assert "active mentor" in response.json()["detail"].lower()


class TestUpdateUserMentor:
    """Tests for PUT /api/v1/user-mentors/{relation_id} endpoint."""

    def test_update_relation_success(self, hr_user, mock_uow, sample_relation, newbie_user, mentor_user):
        """Test updating a user-mentor relationship."""
        updated = UserMentor(
            id=sample_relation.id,
            user_id=newbie_user.id,
            mentor_id=mentor_user.id,
            is_active=False,  # Deactivated
            notes="Updated notes",
            created_at=sample_relation.created_at,
            updated_at=datetime.now(UTC),
        )
        mock_uow.user_mentors.get_by_id = AsyncMock(return_value=sample_relation)
        mock_uow.user_mentors.update = AsyncMock(return_value=updated)

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.put(
                "/api/v1/user-mentors/1",
                headers=create_auth_headers(hr_user.id, hr_user.role),
                json={
                    "is_active": False,
                    "notes": "Updated notes",
                },
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["notes"] == "Updated notes"

    def test_update_relation_not_found(self, hr_user, mock_uow):
        """Test updating non-existent relation returns 404."""
        mock_uow.user_mentors.get_by_id = AsyncMock(return_value=None)

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.put(
                "/api/v1/user-mentors/999",
                headers=create_auth_headers(hr_user.id, hr_user.role),
                json={"is_active": False},
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteUserMentor:
    """Tests for DELETE /api/v1/user-mentors/{relation_id} endpoint."""

    def test_delete_relation_success(self, hr_user, mock_uow):
        """Test deleting a user-mentor relationship."""
        mock_uow.user_mentors.delete = AsyncMock(return_value=True)

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.delete(
                "/api/v1/user-mentors/1",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    def test_delete_relation_not_found(self, hr_user, mock_uow):
        """Test deleting non-existent relation returns 404."""
        mock_uow.user_mentors.delete = AsyncMock(return_value=False)

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_uow():
            yield mock_uow

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_uow] = mock_get_uow

        with TestClient(app) as client:
            response = client.delete(
                "/api/v1/user-mentors/999",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_uow, None)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
