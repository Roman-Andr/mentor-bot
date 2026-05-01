"""Unit tests for user_meetings API endpoints."""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from meeting_service.api import deps
from meeting_service.api.endpoints.user_meetings import router as user_meetings_router
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


class MockUser:
    """Mock user for testing."""

    def __init__(self, user_id: int) -> None:
        """
        Initialize mock user.

        Args:
            user_id: User ID.

        """
        self.id = user_id
        self.email = f"user{user_id}@example.com"
        self.role = "EMPLOYEE"
        self.is_active = True

    def has_role(self, roles: list[str]) -> bool:
        """
        Check if user has any of the given roles.

        Args:
            roles: List of roles to check.

        Returns:
            True if user has any of the roles.

        """
        return self.role in roles


@pytest.fixture
def mock_user_employee():
    """Mock employee user factory."""

    def _create_user(user_id: int = 100) -> MockUser:
        return MockUser(user_id)

    return _create_user


def create_test_app(mock_uow: Any, mock_user: Any, *, require_hr_only: bool = False) -> FastAPI:
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

    if require_hr_only:
        app.dependency_overrides[deps.require_hr] = lambda: mock_user
    else:
        app.dependency_overrides[deps.require_hr] = lambda: mock_user

    app.include_router(user_meetings_router, prefix="/api/v1/user-meetings")
    return app


class TestGetMyMeetings:
    """Tests for GET /api/v1/user-meetings/my endpoint."""

    async def test_get_my_meetings_success(self, mock_uow, mock_user_employee):
        """Test getting current user's meetings."""
        # Arrange
        user = mock_user_employee(100)
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1,
            title="My Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
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

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/my")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["user_id"] == 100

    async def test_get_my_meetings_with_status_filter(self, mock_uow, mock_user_employee):
        """Test getting meetings filtered by status."""
        # Arrange
        user = mock_user_employee(100)
        mock_uow.user_meetings.find_by_user.return_value = ([], 0)

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/my?status=SCHEDULED")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_uow.user_meetings.find_by_user.assert_called_once_with(
            user_id=100, skip=0, limit=50, status=MeetingStatus.SCHEDULED
        )

    async def test_get_my_meetings_pagination(self, mock_uow, mock_user_employee):
        """Test pagination parameters."""
        # Arrange
        user = mock_user_employee(100)
        mock_uow.user_meetings.find_by_user.return_value = ([], 100)

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/my?skip=10&limit=20")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1  # (10 // 20) + 1
        assert data["size"] == 20


class TestAssignMeeting:
    """Tests for POST /api/v1/user-meetings/assign endpoint."""

    async def test_assign_meeting_success(self, mock_uow, mock_user_hr):
        """Test HR assigning a meeting to a user."""
        # Arrange
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.user_meetings.get_user_meeting.return_value = None

        assignment = UserMeeting(
            id=1,
            user_id=200,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        mock_uow.user_meetings.create.return_value = assignment

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        assignment_data = {
            "user_id": 200,
            "meeting_id": 1,
            "scheduled_at": None,
        }

        # Act
        response = client.post("/api/v1/user-meetings/assign", json=assignment_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == 200
        assert data["meeting_id"] == 1
        assert data["status"] == "SCHEDULED"

    async def test_assign_meeting_with_schedule(self, mock_uow, mock_user_hr):
        """Test assigning meeting with scheduled time."""
        # Arrange
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.user_meetings.get_user_meeting.return_value = None

        scheduled_time = datetime.now(UTC) + timedelta(days=1)
        assignment = UserMeeting(
            id=1,
            user_id=200,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            scheduled_at=scheduled_time,
            created_at=now,
        )
        mock_uow.user_meetings.create.return_value = assignment

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        with patch("meeting_service.services.meeting.GoogleCalendarService") as mock_gc:
            mock_gc_instance = MagicMock()
            mock_gc_instance.create_event = AsyncMock(return_value={"id": "event-123"})
            mock_gc.return_value = mock_gc_instance

            assignment_data = {
                "user_id": 200,
                "meeting_id": 1,
                "scheduled_at": scheduled_time.isoformat(),
            }

            # Act
            response = client.post("/api/v1/user-meetings/assign", json=assignment_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK

    async def test_assign_meeting_already_assigned(self, mock_uow, mock_user_hr):
        """Test assigning already assigned meeting returns 400."""
        # Arrange
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        mock_uow.meetings.get_by_id.return_value = meeting

        existing = UserMeeting(id=1, user_id=200, meeting_id=1, status=MeetingStatus.SCHEDULED, created_at=now)
        mock_uow.user_meetings.get_user_meeting.return_value = existing

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        assignment_data = {
            "user_id": 200,
            "meeting_id": 1,
        }

        # Act
        response = client.post("/api/v1/user-meetings/assign", json=assignment_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already assigned" in response.json()["detail"]

    async def test_assign_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test assigning non-existent meeting returns 400."""
        # Arrange
        mock_uow.meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        assignment_data = {
            "user_id": 200,
            "meeting_id": 999,
        }

        # Act
        response = client.post("/api/v1/user-meetings/assign", json=assignment_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetAssignment:
    """Tests for GET /api/v1/user-meetings/{assignment_id} endpoint."""

    async def test_get_assignment_own_meeting(self, mock_uow, mock_user_employee):
        """Test user getting their own assignment."""
        # Arrange
        user = mock_user_employee(100)
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        assignment.meeting = meeting
        mock_uow.user_meetings.get_by_id.return_value = assignment

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == 100

    async def test_get_assignment_as_hr(self, mock_uow, mock_user_hr):
        """Test HR getting any user's assignment."""
        # Arrange
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        assignment = UserMeeting(
            id=1,
            user_id=200,  # Different user
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        assignment.meeting = meeting
        mock_uow.user_meetings.get_by_id.return_value = assignment

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == 200

    async def test_get_assignment_forbidden(self, mock_uow, mock_user_employee):
        """Test user trying to get another user's assignment."""
        # Arrange
        user = mock_user_employee(100)
        assignment = UserMeeting(
            id=1,
            user_id=200,  # Different user
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=datetime.now(UTC),
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/1")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_assignment_not_found(self, mock_uow, mock_user_employee):
        """Test getting non-existent assignment."""
        # Arrange
        user = mock_user_employee(100)
        mock_uow.user_meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateAssignment:
    """Tests for PATCH /api/v1/user-meetings/{assignment_id} endpoint."""

    async def test_update_assignment_own_meeting(self, mock_uow, mock_user_employee):
        """Test user updating their own assignment."""
        # Arrange
        user = mock_user_employee(100)
        now = datetime.now(UTC)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        updated = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,
            created_at=now,
        )
        mock_uow.user_meetings.update.return_value = updated

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        update_data = {"status": "COMPLETED"}

        # Act
        response = client.patch("/api/v1/user-meetings/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK

    async def test_update_assignment_not_found(self, mock_uow, mock_user_employee):
        """Test updating non-existent assignment."""
        # Arrange
        user = mock_user_employee(100)
        mock_uow.user_meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        update_data = {"status": "COMPLETED"}

        # Act
        response = client.patch("/api/v1/user-meetings/999", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_assignment_as_hr(self, mock_uow, mock_user_hr):
        """Test HR updating any user's assignment."""
        # Arrange
        now = datetime.now(UTC)
        assignment = UserMeeting(
            id=1,
            user_id=200,  # Different user
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        updated = UserMeeting(
            id=1,
            user_id=200,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,
            created_at=now,
        )
        mock_uow.user_meetings.update.return_value = updated

        app = create_test_app(mock_uow, mock_user_hr)
        client = TestClient(app)

        update_data = {"status": "COMPLETED"}

        # Act
        response = client.patch("/api/v1/user-meetings/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK

    async def test_update_assignment_forbidden(self, mock_uow, mock_user_employee):
        """Test non-owner/non-HR user cannot update another user's assignment."""
        # Arrange
        user = mock_user_employee(100)
        now = datetime.now(UTC)
        assignment = UserMeeting(
            id=1,
            user_id=200,  # Different user
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        update_data = {"status": "COMPLETED"}

        # Act
        response = client.patch("/api/v1/user-meetings/1", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCompleteMeeting:
    """Tests for POST /api/v1/user-meetings/{assignment_id}/complete endpoint."""

    async def test_complete_own_meeting_success(self, mock_uow, mock_user_employee):
        """Test user completing their own meeting."""
        # Arrange
        user = mock_user_employee(100)
        now = datetime.now(UTC)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=now,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        completed = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,
            feedback="Great meeting!",
            rating=5,
            created_at=now,
        )
        mock_uow.user_meetings.update.return_value = completed

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        completion_data = {
            "feedback": "Great meeting!",
            "rating": 5,
        }

        # Act
        response = client.post("/api/v1/user-meetings/1/complete", json=completion_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "COMPLETED"
        assert data["feedback"] == "Great meeting!"
        assert data["rating"] == 5

    async def test_complete_other_user_meeting_forbidden(self, mock_uow, mock_user_employee):
        """Test user completing another user's meeting."""
        # Arrange
        user = mock_user_employee(100)
        assignment = UserMeeting(
            id=1,
            user_id=200,  # Different user
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=datetime.now(UTC),
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        completion_data = {"feedback": "Good"}

        # Act
        response = client.post("/api/v1/user-meetings/1/complete", json=completion_data)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "own" in response.json()["detail"].lower()

    async def test_complete_already_completed_meeting(self, mock_uow, mock_user_employee):
        """Test completing already completed meeting."""
        # Arrange
        user = mock_user_employee(100)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,  # Already completed
            created_at=datetime.now(UTC),
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        completion_data = {"feedback": "Great!"}

        # Act
        response = client.post("/api/v1/user-meetings/1/complete", json=completion_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already completed" in response.json()["detail"]

    async def test_complete_meeting_not_found(self, mock_uow, mock_user_employee):
        """Test completing non-existent meeting."""
        # Arrange
        user = mock_user_employee(100)
        mock_uow.user_meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, user)
        client = TestClient(app)

        completion_data = {"feedback": "Great!"}

        # Act
        response = client.post("/api/v1/user-meetings/999/complete", json=completion_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteAssignment:
    """Tests for DELETE /api/v1/user-meetings/{assignment_id} endpoint."""

    async def test_delete_assignment_success(self, mock_uow, mock_user_hr):
        """Test HR deleting an assignment."""
        # Arrange
        assignment = UserMeeting(
            id=1,
            user_id=200,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            created_at=datetime.now(UTC),
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/user-meetings/1")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_uow.user_meetings.delete.assert_called_once_with(1)

    async def test_delete_assignment_not_found(self, mock_uow, mock_user_hr):
        """Test deleting non-existent assignment."""
        # Arrange
        mock_uow.user_meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        # Act
        response = client.delete("/api/v1/user-meetings/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAutoAssign:
    """Tests for POST /api/v1/user-meetings/auto-assign/{user_id} endpoint."""

    async def test_auto_assign_success(self, mock_uow, mock_user_hr):
        """Test auto-assigning meetings to a user."""
        # Arrange
        now = datetime.now(UTC)
        meetings = [
            Meeting(
                id=1,
                title="HR Meeting",
                type=MeetingType.HR,
                is_mandatory=True,
                department_id=1,
                order=0,
                deadline_days=7,
                duration_minutes=60,
                created_at=now,
            ),
            Meeting(
                id=2,
                title="Security",
                type=MeetingType.SECURITY,
                is_mandatory=True,
                department_id=1,
                order=1,
                deadline_days=7,
                duration_minutes=60,
                created_at=now,
            ),
        ]
        mock_uow.meetings.find_meetings.return_value = (meetings, 2)
        mock_uow.user_meetings.get_user_meeting.return_value = None

        created_assignments = [
            UserMeeting(id=1, user_id=300, meeting_id=1, status=MeetingStatus.SCHEDULED, created_at=now),
            UserMeeting(id=2, user_id=300, meeting_id=2, status=MeetingStatus.SCHEDULED, created_at=now),
        ]
        mock_uow.user_meetings.create.side_effect = created_assignments

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        # Act
        response = client.post("/api/v1/user-meetings/auto-assign/300?department_id=1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    async def test_auto_assign_with_position_and_level(self, mock_uow, mock_user_hr):
        """Test auto-assign with position and level filters."""
        # Arrange
        now = datetime.now(UTC)
        meetings = [
            Meeting(
                id=1,
                title="Dev Meeting",
                type=MeetingType.TEAM,
                is_mandatory=True,
                order=0,
                deadline_days=7,
                duration_minutes=60,
                created_at=now,
            ),
        ]
        mock_uow.meetings.find_meetings.return_value = (meetings, 1)
        mock_uow.user_meetings.get_user_meeting.return_value = None

        assignment = UserMeeting(id=1, user_id=300, meeting_id=1, status=MeetingStatus.SCHEDULED, created_at=now)
        mock_uow.user_meetings.create.return_value = assignment

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        # Act
        response = client.post("/api/v1/user-meetings/auto-assign/300?department_id=1&position=Developer&level=JUNIOR")

        # Assert
        assert response.status_code == status.HTTP_200_OK


class TestGetMeetingAssignments:
    """Tests for GET /api/v1/user-meetings/by-meeting/{meeting_id} endpoint."""

    async def test_get_meeting_assignments_success(self, mock_uow, mock_user_hr):
        """Test getting all assignments for a meeting."""
        # Arrange
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        mock_uow.meetings.get_by_id.return_value = meeting

        assignments = [
            UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED, created_at=now),
            UserMeeting(id=2, user_id=101, meeting_id=1, status=MeetingStatus.COMPLETED, created_at=now),
        ]
        mock_uow.user_meetings.find_by_meeting.return_value = (assignments, 2)

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/by-meeting/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_get_meeting_assignments_with_status_filter(self, mock_uow, mock_user_hr):
        """Test getting assignments filtered by status."""
        # Arrange
        now = datetime.now(UTC)
        meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
            is_mandatory=True,
            order=0,
            deadline_days=7,
            duration_minutes=60,
            created_at=now,
        )
        mock_uow.meetings.get_by_id.return_value = meeting

        assignments = [
            UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED, created_at=now),
        ]
        mock_uow.user_meetings.find_by_meeting.return_value = (assignments, 1)

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/by-meeting/1?meeting_status=SCHEDULED")

        # Assert
        assert response.status_code == status.HTTP_200_OK

    async def test_get_meeting_assignments_meeting_not_found(self, mock_uow, mock_user_hr):
        """Test getting assignments for non-existent meeting."""
        # Arrange
        mock_uow.meetings.get_by_id.return_value = None

        app = create_test_app(mock_uow, mock_user_hr, require_hr_only=True)
        client = TestClient(app)

        # Act
        response = client.get("/api/v1/user-meetings/by-meeting/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
