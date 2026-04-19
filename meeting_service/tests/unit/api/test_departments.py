"""Unit tests for departments API endpoints."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from meeting_service.api import deps
from meeting_service.api.endpoints.departments import router as departments_router
from meeting_service.config import settings
from meeting_service.models.department import Department


def create_mock_uow(mock_dept=None):
    """Create a mock Unit of Work with department repository."""
    mock_uow = MagicMock()
    mock_uow.departments = MagicMock()
    mock_uow.departments.get_by_name = AsyncMock(return_value=mock_dept)
    mock_uow.departments.create = AsyncMock(return_value=mock_dept)
    mock_uow.commit = AsyncMock()
    mock_uow.rollback = AsyncMock()
    return mock_uow


async def mock_get_uow() -> AsyncGenerator[MagicMock]:
    """Mock UOW dependency factory - will be overridden in tests."""
    yield MagicMock()


def create_test_app(mock_uow=None) -> FastAPI:
    """Create test app with dependency overrides for service auth and UOW."""
    app = FastAPI()

    # Override service auth dependencies
    app.dependency_overrides[deps.verify_service_api_key] = lambda: True
    app.dependency_overrides[deps.get_meeting_service_dep] = lambda: deps.MeetingServiceDep()

    # Override UOW dependency
    if mock_uow:
        async def get_mock_uow() -> AsyncGenerator[MagicMock]:
            yield mock_uow
        app.dependency_overrides[deps.get_uow] = get_mock_uow

    app.include_router(departments_router, prefix="/api/v1/departments")
    return app


class TestCreateDepartment:
    """Tests for POST /api/v1/departments/ endpoint."""

    def test_create_department_success(self):
        """Test creating a new department successfully."""
        # Arrange
        # Create a mock that will receive the ID after create is called
        captured_dept = None

        async def mock_create(dept) -> Department:
            nonlocal captured_dept
            dept.id = 1  # Simulate DB assigning ID
            captured_dept = dept
            return dept

        mock_uow = create_mock_uow(None)  # get_by_name returns None (no conflict)
        mock_uow.departments.create = mock_create

        app = create_test_app(mock_uow)
        client = TestClient(app)

        department_data = {
            "name": "Engineering",
            "description": "Software engineering department",
        }

        # Act
        response = client.post("/api/v1/departments/", json=department_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Engineering"
        assert data["description"] == "Software engineering department"
        mock_uow.departments.get_by_name.assert_called_once_with("Engineering")
        assert captured_dept is not None

    def test_create_department_conflict(self):
        """Test creating a department that already exists."""
        # Arrange
        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Existing department",
        )
        mock_uow = create_mock_uow(existing_dept)

        app = create_test_app(mock_uow)
        client = TestClient(app)

        department_data = {
            "name": "Engineering",
            "description": "Software engineering department",
        }

        # Act
        response = client.post("/api/v1/departments/", json=department_data)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"].lower()
        mock_uow.departments.get_by_name.assert_called_once_with("Engineering")


class TestGetDepartment:
    """Tests for GET /api/v1/departments/{department_name} endpoint."""

    def test_get_department_success(self):
        """Test getting a department by name successfully."""
        # Arrange
        mock_dept = Department(
            id=1,
            name="Engineering",
            description="Software engineering department",
        )
        mock_uow = create_mock_uow(mock_dept)

        app = create_test_app(mock_uow)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/departments/Engineering")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Engineering"
        assert data["description"] == "Software engineering department"
        mock_uow.departments.get_by_name.assert_called_once_with("Engineering")

    def test_get_department_not_found(self):
        """Test getting a non-existent department."""
        # Arrange
        mock_uow = create_mock_uow(None)

        app = create_test_app(mock_uow)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/departments/NonExistent")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
        mock_uow.departments.get_by_name.assert_called_once_with("NonExistent")

    def test_get_department_unauthorized_without_api_key(self):
        """Test that requests without valid service API key are rejected."""
        # Arrange
        app = FastAPI()

        # Don't override the auth - use the real implementation
        original_api_key = settings.SERVICE_API_KEY
        settings.SERVICE_API_KEY = "valid-key"

        try:
            app.include_router(departments_router, prefix="/api/v1/departments")
            client = TestClient(app)

            # Act - request without X-Service-Api-Key header
            response = client.get("/api/v1/departments/Engineering")

            # Assert
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        finally:
            settings.SERVICE_API_KEY = original_api_key

    def test_get_department_with_invalid_api_key(self):
        """Test that requests with invalid service API key are rejected."""
        # Arrange
        app = FastAPI()

        # Don't override the auth - use the real implementation
        original_api_key = settings.SERVICE_API_KEY
        settings.SERVICE_API_KEY = "valid-key"

        try:
            app.include_router(departments_router, prefix="/api/v1/departments")
            client = TestClient(app)

            # Act - request with invalid X-Service-Api-Key header
            response = client.get(
                "/api/v1/departments/Engineering",
                headers={"X-Service-Api-Key": "invalid-key"}
            )

            # Assert
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        finally:
            settings.SERVICE_API_KEY = original_api_key


class TestUpdateDepartment:
    """Tests for PUT /api/v1/departments/{department_name} endpoint."""

    def test_update_department_success(self):
        """Test updating a department successfully."""
        # Arrange
        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Original description",
        )
        mock_uow = create_mock_uow(existing_dept)
        mock_uow.departments.update = AsyncMock(return_value=existing_dept)

        app = create_test_app(mock_uow)
        client = TestClient(app)

        update_data = {
            "name": "Engineering",
            "description": "Updated description",
        }

        # Act
        response = client.put("/api/v1/departments/Engineering", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_uow.departments.update.assert_called_once()

    def test_update_department_rename_success(self):
        """Test renaming a department successfully."""
        # Arrange
        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Software engineering department",
        )

        # First get_by_name returns the existing dept (to check existence)
        # Second get_by_name returns None (no conflict with new name)
        mock_uow = MagicMock()
        mock_uow.departments = MagicMock()
        mock_uow.departments.get_by_name = AsyncMock(side_effect=[existing_dept, None])
        mock_uow.departments.update = AsyncMock(return_value=existing_dept)

        app = create_test_app(mock_uow)
        client = TestClient(app)

        update_data = {
            "name": "Engineering Dept",
            "description": "Software engineering department",
        }

        # Act
        response = client.put("/api/v1/departments/Engineering", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert existing_dept.name == "Engineering Dept"

    def test_update_department_not_found(self):
        """Test updating a non-existent department."""
        # Arrange
        mock_uow = create_mock_uow(None)  # Department not found

        app = create_test_app(mock_uow)
        client = TestClient(app)

        update_data = {
            "name": "NonExistent",
            "description": "Some description",
        }

        # Act
        response = client.put("/api/v1/departments/NonExistent", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_update_department_rename_conflict(self):
        """Test renaming a department to a name that already exists."""
        # Arrange
        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Software engineering department",
        )
        conflicting_dept = Department(
            id=2,
            name="Engineering Dept",
            description="Another department",
        )

        # First get_by_name returns the existing dept (to check existence)
        # Second get_by_name returns a different dept (conflict with new name)
        mock_uow = MagicMock()
        mock_uow.departments = MagicMock()
        mock_uow.departments.get_by_name = AsyncMock(side_effect=[existing_dept, conflicting_dept])

        app = create_test_app(mock_uow)
        client = TestClient(app)

        update_data = {
            "name": "Engineering Dept",
            "description": "Software engineering department",
        }

        # Act
        response = client.put("/api/v1/departments/Engineering", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"].lower()


class TestDeleteDepartment:
    """Tests for DELETE /api/v1/departments/{department_name} endpoint."""

    def test_delete_department_success(self):
        """Test deleting a department successfully."""
        # Arrange
        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Software engineering department",
        )
        mock_uow = create_mock_uow(existing_dept)
        mock_uow.departments.delete = AsyncMock()

        app = create_test_app(mock_uow)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/departments/Engineering")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"].lower()
        mock_uow.departments.delete.assert_called_once_with(1)

    def test_delete_department_not_found(self):
        """Test deleting a non-existent department."""
        # Arrange
        mock_uow = create_mock_uow(None)  # Department not found

        app = create_test_app(mock_uow)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/departments/NonExistent")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
