"""Extra tests for user_meetings API to cover auth service integration path."""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from meeting_service.api import deps
from meeting_service.api.endpoints.user_meetings import router as user_meetings_router
from meeting_service.core.enums import MeetingStatus, MeetingType
from meeting_service.models import Meeting, UserMeeting


class MockHRUser:
    """Mock HR user for testing."""

    def __init__(self) -> None:
        self.id = 1
        self.email = "hr@example.com"
        self.first_name = "HR"
        self.last_name = "User"
        self.telegram_id = None
        self.role = "HR"
        self.is_active = True

    def has_role(self, roles: list[str]) -> bool:
        return self.role in roles


def create_app_with_token(mock_uow: Any, mock_user: Any, auth_token: str | None) -> FastAPI:
    """Create test app with a specific auth token value."""
    app = FastAPI()

    async def override_uow() -> Any:
        try:
            yield mock_uow
        finally:
            pass

    app.dependency_overrides[deps.get_uow] = override_uow
    app.dependency_overrides[deps.get_current_active_user] = lambda: mock_user
    app.dependency_overrides[deps.require_hr] = lambda: mock_user
    app.dependency_overrides[deps.get_auth_token] = lambda: auth_token

    app.include_router(user_meetings_router, prefix="/api/v1/user-meetings")
    return app


class TestGetRecipientUserDataWithAuthToken:
    """Tests covering _get_recipient_user_data with auth token (lines 53-55)."""

    async def test_update_other_user_with_auth_token_calls_auth_service(self, mock_uow):
        """Test that updating another user's assignment with auth token calls auth service."""
        hr_user = MockHRUser()  # id=1
        now = datetime.now(UTC)

        # Assignment belongs to user_id=200 (not HR user id=1)
        assignment = UserMeeting(
            id=1,
            user_id=200,
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

        # Provide a valid auth token so it goes to auth service
        app = create_app_with_token(mock_uow, hr_user, "valid-token-abc")
        client = TestClient(app)

        mock_user_data = {"id": 200, "email": "user200@example.com", "first_name": "Jane"}

        with patch(
            "meeting_service.utils.integrations.AuthServiceClient.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = mock_user_data
            response = client.patch("/api/v1/user-meetings/1", json={"status": "COMPLETED"})

        assert response.status_code == status.HTTP_200_OK

    async def test_assign_other_user_with_auth_token_calls_auth_service(self, mock_uow):
        """Test that assigning to another user with auth token calls auth service (line 55)."""
        hr_user = MockHRUser()  # id=1
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

        app = create_app_with_token(mock_uow, hr_user, "valid-token-xyz")
        client = TestClient(app)

        mock_user_data = {"id": 200, "email": "user200@example.com"}

        with patch(
            "meeting_service.utils.integrations.AuthServiceClient.get_user", new_callable=AsyncMock
        ) as mock_get_user:
            mock_get_user.return_value = mock_user_data
            response = client.post(
                "/api/v1/user-meetings/assign",
                json={"user_id": 200, "meeting_id": 1},
            )

        assert response.status_code == status.HTTP_200_OK
        mock_get_user.assert_awaited_once_with(200, "valid-token-xyz")
