"""Unit tests for meeting API endpoints."""

from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from meeting_service.api import deps
from meeting_service.api.endpoints.meetings import router as meetings_router
from meeting_service.core.enums import MeetingStatus, MeetingType
from meeting_service.models import Meeting, UserMeeting


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


@pytest.fixture
def mock_user_employee():
    """Mock employee user."""
    class MockUser:
        def __init__(self) -> None:
            self.id = 100
            self.email = "user@example.com"
            self.role = "EMPLOYEE"
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


class TestGetMeetings:
    """Tests for GET /api/v1/meetings endpoint."""

    async def test_get_meetings_success(self, mock_uow, mock_user_hr):
        """Test getting meetings list successfully."""
        # Arrange
        now = datetime.now(UTC)
        meetings = [
            Meeting(
                id=1, title="HR Meeting", type=MeetingType.HR,
                is_mandatory=True, order=0, deadline_days=7, duration_minutes=60, created_at=now
            ),
            Meeting(
                id=2, title="Security Meeting", type=MeetingType.SECURITY,
                is_mandatory=True, order=1, deadline_days=7, duration_minutes=60, created_at=now
            ),
        ]
        mock_uow.meetings.find_meetings.return_value = (meetings, 2)

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings?skip=0&limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["meetings"]) == 2
        assert data["meetings"][0]["title"] == "HR Meeting"
        assert data["meetings"][1]["title"] == "Security Meeting"

    async def test_get_meetings_with_filters(self, mock_uow, mock_user_hr):
        """Test getting meetings with filters applied."""
        # Arrange
        now = datetime.now(UTC)
        meetings = [
            Meeting(
                id=1, title="HR Meeting", type=MeetingType.HR,
                department_id=1, is_mandatory=True, order=0, deadline_days=7, duration_minutes=60, created_at=now
            ),
        ]
        mock_uow.meetings.find_meetings.return_value = (meetings, 1)

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get(
            "/api/v1/meetings?meeting_type=HR&department_id=1&is_mandatory=true"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_uow.meetings.find_meetings.assert_called_once_with(
            skip=0,
            limit=50,
            meeting_type=MeetingType.HR,
            department_id=1,
            position=None,
            level=None,
            is_mandatory=True,
            search=None,
            sort_by=None,
            sort_order="asc",
        )

    async def test_get_meetings_default_pagination(self, mock_uow, mock_user_hr):
        """Test default pagination parameters."""
        # Arrange
        mock_uow.meetings.find_meetings.return_value = ([], 0)

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_uow.meetings.find_meetings.assert_called_once_with(
            skip=0,
            limit=50,  # default limit
            meeting_type=None,
            department_id=None,
            position=None,
            level=None,
            is_mandatory=None,
            search=None,
            sort_by=None,
            sort_order="asc",
        )


class TestCreateMeeting:
    """Tests for POST /api/v1/meetings endpoint."""

    async def test_create_meeting_success(self, mock_uow, mock_user_hr):
        """Test creating a meeting template successfully."""
        # Arrange
        new_meeting = Meeting(
            id=1,
            title="New Meeting",
            description="Test Description",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=datetime.now(UTC),
        )
        mock_uow.meetings.create.return_value = new_meeting

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        meeting_data = {
            "title": "New Meeting",
            "description": "Test Description",
            "type": "HR",
            "is_mandatory": True,
            "deadline_days": 7,
            "duration_minutes": 60,
        }

        # Act
        response = client.post("/api/v1/meetings", json=meeting_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Meeting"
        assert data["type"] == "HR"
        mock_uow.meetings.create.assert_called_once()

    async def test_create_meeting_validation_error(self, mock_uow, mock_user_hr):
        """Test creating meeting with invalid data returns 422."""
        # Arrange
        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Missing required field "title"
        meeting_data = {
            "type": "HR",
        }

        # Act
        response = client.post("/api/v1/meetings", json=meeting_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_create_meeting_minimal_data(self, mock_uow, mock_user_hr):
        """Test creating meeting with minimal required data."""
        # Arrange
        new_meeting = Meeting(
            id=1,
            title="Minimal Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=datetime.now(UTC),
        )
        mock_uow.meetings.create.return_value = new_meeting

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        meeting_data = {
            "title": "Minimal Meeting",
            "type": "HR",
        }

        # Act
        response = client.post("/api/v1/meetings", json=meeting_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED


class TestGetMeeting:
    """Tests for GET /api/v1/meetings/{meeting_id} endpoint."""

    async def test_get_meeting_success(self, mock_uow, mock_user_hr):
        """Test getting a specific meeting by ID."""
        # Arrange
        meeting = Meeting(
            id=1,
            title="Test Meeting",
            description="Description",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=datetime.now(UTC),
        )
        mock_uow.meetings.get_by_id.return_value = meeting

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Meeting"

    async def test_get_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test getting non-existent meeting returns 404."""
        # Arrange
        mock_uow.meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Meeting" in response.json()["detail"]


class TestUpdateMeeting:
    """Tests for PUT /api/v1/meetings/{meeting_id} endpoint."""

    async def test_update_meeting_success(self, mock_uow, mock_user_hr):
        """Test updating a meeting successfully."""
        # Arrange
        now = datetime.now(UTC)
        existing_meeting = Meeting(
            id=1,
            title="Old Title",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        updated_meeting = Meeting(
            id=1,
            title="New Title",
            description="Updated Description",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        mock_uow.meetings.get_by_id.return_value = existing_meeting
        mock_uow.meetings.update.return_value = updated_meeting

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        update_data = {
            "title": "New Title",
            "description": "Updated Description",
        }

        # Act
        response = client.put("/api/v1/meetings/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "Updated Description"

    async def test_update_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test updating non-existent meeting returns 404."""
        # Arrange
        mock_uow.meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        update_data = {"title": "New Title"}

        # Act
        response = client.put("/api/v1/meetings/999", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_meeting_partial(self, mock_uow, mock_user_hr):
        """Test partial update of a meeting."""
        # Arrange
        now = datetime.now(UTC)
        existing_meeting = Meeting(
            id=1,
            title="Old Title",
            description="Old Desc",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        updated_meeting = Meeting(
            id=1,
            title="New Title",
            description="Old Desc",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        mock_uow.meetings.get_by_id.return_value = existing_meeting
        mock_uow.meetings.update.return_value = updated_meeting

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        update_data = {"title": "New Title"}  # Only update title

        # Act
        response = client.put("/api/v1/meetings/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK


class TestDeleteMeeting:
    """Tests for DELETE /api/v1/meetings/{meeting_id} endpoint."""

    async def test_delete_meeting_success(self, mock_uow, mock_user_hr):
        """Test deleting a meeting successfully."""
        # Arrange
        meeting = Meeting(
            id=1, title="Test Meeting", type=MeetingType.HR,
            is_mandatory=True, order=0, deadline_days=7, duration_minutes=60, created_at=datetime.now(UTC)
        )
        mock_uow.meetings.get_by_id.return_value = meeting

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/meetings/1")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_uow.meetings.delete.assert_called_once_with(1)

    async def test_delete_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test deleting non-existent meeting returns 404."""
        # Arrange
        mock_uow.meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/meetings/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestConfirmMeeting:
    """Tests for POST /api/v1/meetings/{assignment_id}/confirm endpoint."""

    async def test_confirm_meeting_success(self, mock_uow, mock_user_hr):
        """Test confirming a meeting assignment."""
        # Arrange
        now = datetime.now(UTC)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        updated_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,
            created_at=now,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment
        mock_uow.user_meetings.update.return_value = updated_assignment

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.post("/api/v1/meetings/1/confirm")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "COMPLETED"

    async def test_confirm_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test confirming non-existent meeting returns 404."""
        # Arrange
        mock_uow.user_meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.post("/api/v1/meetings/999/confirm")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCancelMeeting:
    """Tests for POST /api/v1/meetings/{assignment_id}/cancel endpoint."""

    async def test_cancel_meeting_success(self, mock_uow, mock_user_hr):
        """Test canceling a meeting assignment."""
        # Arrange
        now = datetime.now(UTC)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        updated_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.CANCELLED,
            created_at=now,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment
        mock_uow.user_meetings.update.return_value = updated_assignment

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.post("/api/v1/meetings/1/cancel")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "CANCELLED"

    async def test_cancel_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test canceling non-existent meeting returns 404."""
        # Arrange
        mock_uow.user_meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.post("/api/v1/meetings/999/cancel")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetUserMeetings:
    """Tests for GET /api/v1/meetings/user/{user_id} endpoints."""

    async def test_get_user_meetings_success(self, mock_uow, mock_user_hr):
        """Test getting all meetings for a specific user."""
        # Arrange
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1, title="Test Meeting", type=MeetingType.HR,
            is_mandatory=True, order=0, deadline_days=7, duration_minutes=60, created_at=now
        )
        user_meeting = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        user_meeting.meeting = meeting

        mock_uow.user_meetings.find_by_user.return_value = ([user_meeting], 1)

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings/user/100")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["meetings"]) == 1
        assert data["meetings"][0]["user_id"] == 100

    async def test_get_user_upcoming_meetings(self, mock_uow, mock_user_hr):
        """Test getting upcoming meetings for a user."""
        # Arrange
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1, title="Upcoming Meeting", type=MeetingType.HR,
            is_mandatory=True, order=0, deadline_days=7, duration_minutes=60, created_at=now
        )
        user_meeting = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        user_meeting.meeting = meeting

        mock_uow.user_meetings.find_by_user.return_value = ([user_meeting], 1)

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings/user/100/upcoming")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["meetings"]) == 1

    async def test_get_user_meetings_with_limit(self, mock_uow, mock_user_hr):
        """Test getting user meetings with custom limit."""
        # Arrange
        mock_uow.user_meetings.find_by_user.return_value = ([], 0)

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/meetings/user/100?limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_uow.user_meetings.find_by_user.assert_called_once_with(
            user_id=100, skip=0, limit=10, status=None,
        )
