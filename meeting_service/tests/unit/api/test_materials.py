"""Unit tests for meeting materials API endpoints."""

from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from meeting_service.api import deps
from meeting_service.api.endpoints.meetings import router as meetings_router
from meeting_service.core.enums import MaterialType, MeetingType
from meeting_service.models import Meeting, MeetingMaterial


# Fixtures for mock users
@pytest.fixture
def mock_user_hr():
    """Mock HR user."""

    class MockUser:
        def __init__(self) -> None:
            self.id = 1
            self.email = "hr@example.com"
            self.role = "HR"
            self.is_active = True

        def has_role(self, roles: list[str]) -> bool:
            return self.role in roles

    return MockUser()


def create_test_app(mock_uow: Any, mock_user: Any) -> FastAPI:
    """Create test app with dependency overrides."""
    app = FastAPI()

    # Create a generator for UOW
    async def override_uow() -> Any:
        try:
            yield mock_uow
        finally:
            pass

    # Override dependencies
    app.dependency_overrides[deps.get_uow] = override_uow
    app.dependency_overrides[deps.get_current_active_user] = lambda: mock_user
    app.dependency_overrides[deps.require_hr] = lambda: mock_user

    app.include_router(meetings_router, prefix="/api/v1/meetings")
    return app


class TestGetMeetingMaterials:
    """Tests for GET /api/v1/meetings/{meeting_id}/materials endpoint."""

    async def test_get_materials_success(self, mock_uow, mock_user_hr):
        """Test getting all materials for a meeting."""
        # Arrange
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        materials = [
            MeetingMaterial(
                id=1,
                meeting_id=1,
                title="PDF Guide",
                description="Onboarding guide",
                url="https://example.com/guide.pdf",
                type=MaterialType.PDF,
                order=0,
                created_at=datetime.now(UTC),
            ),
            MeetingMaterial(
                id=2,
                meeting_id=1,
                title="Video Tutorial",
                description="Setup video",
                url="https://example.com/video.mp4",
                type=MaterialType.VIDEO,
                order=1,
                created_at=datetime.now(UTC),
            ),
        ]
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.materials.get_by_meeting.return_value = materials

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings/1/materials")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "PDF Guide"
        assert data[0]["type"] == "PDF"
        assert data[1]["title"] == "Video Tutorial"
        assert data[1]["type"] == "VIDEO"

    async def test_get_materials_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test getting materials for non-existent meeting returns 404."""
        # Arrange
        mock_uow.meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings/999/materials")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_materials_empty_list(self, mock_uow, mock_user_hr):
        """Test getting materials when meeting has no materials."""
        # Arrange
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.materials.get_by_meeting.return_value = []

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings/1/materials")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []


class TestAddMeetingMaterial:
    """Tests for POST /api/v1/meetings/{meeting_id}/materials endpoint."""

    async def test_add_material_success(self, mock_uow, mock_user_hr):
        """Test adding a material to a meeting."""
        # Arrange
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        new_material = MeetingMaterial(
            id=1,
            meeting_id=1,
            title="New Document",
            description="A helpful document",
            url="https://example.com/doc.pdf",
            type=MaterialType.PDF,
            order=0,
            created_at=datetime.now(UTC),
        )
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.materials.create.return_value = new_material

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        material_data = {
            "title": "New Document",
            "description": "A helpful document",
            "url": "https://example.com/doc.pdf",
            "type": "PDF",
        }

        # Act
        response = client.post("/api/v1/meetings/1/materials", json=material_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Document"
        assert data["meeting_id"] == 1
        assert data["type"] == "PDF"

    async def test_add_material_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test adding material to non-existent meeting returns 404."""
        # Arrange
        mock_uow.meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        material_data = {
            "title": "New Document",
            "url": "https://example.com/doc.pdf",
            "type": "PDF",
        }

        # Act
        response = client.post("/api/v1/meetings/999/materials", json=material_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Meeting" in response.json()["detail"]

    async def test_add_material_validation_error(self, mock_uow, mock_user_hr):
        """Test adding material with invalid data returns 422."""
        # Arrange
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        mock_uow.meetings.get_by_id.return_value = meeting

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Missing required field "title"
        material_data = {
            "url": "https://example.com/doc.pdf",
            "type": "PDF",
        }

        # Act
        response = client.post("/api/v1/meetings/1/materials", json=material_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_add_material_all_types(self, mock_uow, mock_user_hr):
        """Test adding materials of all supported types."""
        # Arrange
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        mock_uow.meetings.get_by_id.return_value = meeting

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        material_types = ["PDF", "LINK", "DOC", "IMAGE", "VIDEO"]

        for i, mat_type in enumerate(material_types):
            material = MeetingMaterial(
                id=i + 1,
                meeting_id=1,
                title=f"{mat_type} Material",
                url=f"https://example.com/file{i}",
                type=MaterialType(mat_type),
                order=i,
                created_at=datetime.now(UTC),
            )
            mock_uow.materials.create.return_value = material

            material_data = {
                "title": f"{mat_type} Material",
                "url": f"https://example.com/file{i}",
                "type": mat_type,
            }

            # Act
            response = client.post("/api/v1/meetings/1/materials", json=material_data)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED, f"Failed for type {mat_type}"
            data = response.json()
            assert data["type"] == mat_type


class TestDeleteMeetingMaterial:
    """Tests for DELETE /api/v1/meetings/materials/{material_id} endpoint."""

    async def test_delete_material_success(self, mock_uow, mock_user_hr):
        """Test deleting a material successfully."""
        # Arrange
        material = MeetingMaterial(
            id=1,
            meeting_id=1,
            title="Old Document",
            url="https://example.com/old.pdf",
            type=MaterialType.PDF,
            order=0,
            created_at=datetime.now(UTC),
        )
        mock_uow.materials.get_by_id.return_value = material

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/meetings/materials/1")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_uow.materials.delete.assert_called_once_with(1)

    async def test_delete_material_not_found(self, mock_uow, mock_user_hr):
        """Test deleting non-existent material returns 404."""
        # Arrange
        mock_uow.materials.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/meetings/materials/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Material" in response.json()["detail"]

    async def test_delete_material_without_description(self, mock_uow, mock_user_hr):
        """Test deleting material without description field."""
        # Arrange
        material = MeetingMaterial(
            id=2,
            meeting_id=1,
            title="No Desc Material",
            url="https://example.com/nodesc.pdf",
            type=MaterialType.PDF,
            order=0,
            created_at=datetime.now(UTC),
        )
        mock_uow.materials.get_by_id.return_value = material

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/meetings/materials/2")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
