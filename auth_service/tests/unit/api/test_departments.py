"""Unit tests for departments API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from auth_service.api import deps
from auth_service.core import ConflictException, NotFoundException
from auth_service.core.enums import UserRole
from auth_service.core.security import create_access_token
from auth_service.main import app
from auth_service.models import Department, User


def create_auth_headers(user_id: int = 1, role: UserRole = UserRole.ADMIN) -> dict:
    """Create authorization headers with JWT token."""
    token = create_access_token({"sub": str(user_id), "user_id": user_id, "role": role})
    return {"Authorization": f"Bearer {token}"}


def get_test_client():
    """Create a TestClient without lifespan events."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def sample_department():
    """Create a sample department."""
    return Department(
        id=1,
        name="Engineering",
        description="Software Engineering Department",
        created_at=datetime.now(UTC),
        updated_at=None,
    )


@pytest.fixture
def second_department():
    """Create a second department."""
    return Department(
        id=2,
        name="Marketing",
        description="Marketing and Sales Department",
        created_at=datetime.now(UTC),
        updated_at=None,
    )


class TestGetDepartments:
    """Tests for GET /api/v1/departments/ endpoint."""

    def test_get_departments_success(self, admin_user, mock_department_service, sample_department, second_department):
        """Test getting list of departments as admin."""
        departments = [sample_department, second_department]
        mock_department_service.get_departments = AsyncMock(return_value=(departments, 2))

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/departments/",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["departments"]) == 2
            assert data["departments"][0]["name"] == "Engineering"
            assert data["departments"][1]["name"] == "Marketing"
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)

    def test_get_departments_with_pagination(self, admin_user, mock_department_service, sample_department):
        """Test getting departments with pagination."""
        mock_department_service.get_departments = AsyncMock(return_value=([sample_department], 1))

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/departments/?skip=0&limit=10",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            call_args = mock_department_service.get_departments.call_args
            assert call_args.kwargs["skip"] == 0
            assert call_args.kwargs["limit"] == 10
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)

    def test_get_departments_with_search(self, admin_user, mock_department_service, sample_department):
        """Test getting departments with search filter."""
        mock_department_service.get_departments = AsyncMock(return_value=([sample_department], 1))

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/departments/?search=Engineering",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            call_args = mock_department_service.get_departments.call_args
            assert call_args.kwargs["search"] == "Engineering"
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)


class TestCreateDepartment:
    """Tests for POST /api/v1/departments/ endpoint."""

    def test_create_department_success(self, admin_user, mock_department_service, sample_department):
        """Test creating a new department."""
        mock_department_service.create_department = AsyncMock(return_value=sample_department)

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/departments/",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={
                    "name": "Engineering",
                    "description": "Software Engineering Department",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Engineering"
            assert data["description"] == "Software Engineering Department"
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)

    def test_create_department_conflict(self, admin_user, mock_department_service):
        """Test creating department with duplicate name returns 409."""
        mock_department_service.create_department = AsyncMock(
            side_effect=ConflictException("Department with this name already exists")
        )

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.post(
                "/api/v1/departments/",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={
                    "name": "Engineering",
                    "description": "Duplicate Department",
                },
            )

            assert response.status_code == 409
            assert "already exists" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)


class TestGetDepartmentById:
    """Tests for GET /api/v1/departments/{department_id} endpoint."""

    def test_get_department_by_id_success(self, admin_user, mock_department_service, sample_department):
        """Test getting department by ID."""
        mock_department_service.get_department_by_id = AsyncMock(return_value=sample_department)

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/departments/1",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["name"] == "Engineering"
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)

    def test_get_department_by_id_not_found(self, admin_user, mock_department_service):
        """Test getting non-existent department returns 404."""
        mock_department_service.get_department_by_id = AsyncMock(side_effect=NotFoundException("Department"))

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.get(
                "/api/v1/departments/999",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)


class TestUpdateDepartment:
    """Tests for PUT /api/v1/departments/{department_id} endpoint."""

    def test_update_department_success(self, admin_user, mock_department_service, sample_department):
        """Test updating a department."""
        updated = Department(
            id=sample_department.id,
            name="Updated Engineering",
            description="Updated Description",
            created_at=sample_department.created_at,
            updated_at=datetime.now(UTC),
        )
        mock_department_service.update_department = AsyncMock(return_value=updated)

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.put(
                "/api/v1/departments/1",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={
                    "name": "Updated Engineering",
                    "description": "Updated Description",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Engineering"
            assert data["description"] == "Updated Description"
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)

    def test_update_department_not_found(self, admin_user, mock_department_service):
        """Test updating non-existent department returns 404."""
        mock_department_service.update_department = AsyncMock(side_effect=NotFoundException("Department"))

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.put(
                "/api/v1/departments/999",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={"name": "New Name"},
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)

    def test_update_department_conflict(self, admin_user, mock_department_service):
        """Test updating department with duplicate name returns 409."""
        mock_department_service.update_department = AsyncMock(
            side_effect=ConflictException("Department with this name already exists")
        )

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.put(
                "/api/v1/departments/1",
                headers=create_auth_headers(admin_user.id, admin_user.role),
                json={"name": "Duplicate Name"},
            )

            assert response.status_code == 409
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)


class TestDeleteDepartment:
    """Tests for DELETE /api/v1/departments/{department_id} endpoint."""

    def test_delete_department_success(self, admin_user, mock_department_service):
        """Test deleting a department."""
        mock_department_service.delete_department = AsyncMock(return_value=None)

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.delete(
                "/api/v1/departments/1",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 200
            data = response.json()
            assert "deleted" in data["message"].lower()
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)

    def test_delete_department_not_found(self, admin_user, mock_department_service):
        """Test deleting non-existent department returns 404."""
        mock_department_service.delete_department = AsyncMock(side_effect=NotFoundException("Department"))

        async def mock_get_current_user() -> User:
            return admin_user

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user
        app.dependency_overrides[deps.get_department_service] = lambda: mock_department_service

        try:
            client = get_test_client()
            response = client.delete(
                "/api/v1/departments/999",
                headers=create_auth_headers(admin_user.id, admin_user.role),
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(deps.get_current_user, None)
            app.dependency_overrides.pop(deps.get_department_service, None)
