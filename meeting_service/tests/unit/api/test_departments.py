"""Unit tests for departments API endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from meeting_service.api import deps
from meeting_service.api.endpoints.departments import router as departments_router
from meeting_service.config import settings
from meeting_service.models.department import Department


def create_test_app() -> FastAPI:
    """Create test app with dependency overrides for service auth."""
    app = FastAPI()

    # Override service auth dependencies
    app.dependency_overrides[deps.verify_service_api_key] = lambda: True
    app.dependency_overrides[deps.get_meeting_service_dep] = lambda: deps.MeetingServiceDep()

    app.include_router(departments_router, prefix="/api/v1/departments")
    return app


class TestCreateDepartment:
    """Tests for POST /api/v1/departments/ endpoint."""

    def test_create_department_success(self):
        """Test creating a new department successfully."""
        # Arrange
        app = create_test_app()
        client = TestClient(app)

        department_data = {
            "name": "Engineering",
            "description": "Software engineering department",
        }

        mock_dept = MagicMock()
        mock_dept.id = 1
        mock_dept.name = "Engineering"
        mock_dept.description = "Software engineering department"

        mock_session = AsyncMock()

        # Mock the query for existing department (returns None - no conflict)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Mock the add and refresh operations
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        async def mock_refresh(obj):
            obj.id = 1

        mock_session.refresh = mock_refresh

        mock_session_class = MagicMock()
        mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("meeting_service.database.AsyncSessionLocal", mock_session_class):
            # Act
            response = client.post("/api/v1/departments/", json=department_data)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == "Engineering"
            assert data["description"] == "Software engineering department"

    def test_create_department_conflict(self):
        """Test creating a department that already exists."""
        # Arrange
        app = create_test_app()
        client = TestClient(app)

        department_data = {
            "name": "Engineering",
            "description": "Software engineering department",
        }

        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Existing department",
        )

        mock_session = AsyncMock()

        # Mock the query for existing department (returns existing - conflict)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_dept
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_session_class = MagicMock()
        mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("meeting_service.database.AsyncSessionLocal", mock_session_class):
            # Act
            response = client.post("/api/v1/departments/", json=department_data)

            # Assert
            assert response.status_code == status.HTTP_409_CONFLICT
            assert "already exists" in response.json()["detail"].lower()


class TestGetDepartment:
    """Tests for GET /api/v1/departments/{department_name} endpoint."""

    def test_get_department_success(self):
        """Test getting a department by name successfully."""
        # Arrange
        app = create_test_app()
        client = TestClient(app)

        mock_dept = Department(
            id=1,
            name="Engineering",
            description="Software engineering department",
        )

        mock_session = AsyncMock()

        # Mock the query for department
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_dept
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_session_class = MagicMock()
        mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("meeting_service.database.AsyncSessionLocal", mock_session_class):
            # Act
            response = client.get("/api/v1/departments/Engineering")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == 1
            assert data["name"] == "Engineering"
            assert data["description"] == "Software engineering department"

    def test_get_department_not_found(self):
        """Test getting a non-existent department."""
        # Arrange
        app = create_test_app()
        client = TestClient(app)

        mock_session = AsyncMock()

        # Mock the query for department (returns None - not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_session_class = MagicMock()
        mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("meeting_service.database.AsyncSessionLocal", mock_session_class):
            # Act
            response = client.get("/api/v1/departments/NonExistent")

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in response.json()["detail"].lower()

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
