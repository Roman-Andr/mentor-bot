"""Unit tests for telegram_bot MeetingServiceClient."""

import pytest
from fastapi import status
from httpx import RequestError, Response

from telegram_bot.services.meeting_client import MeetingServiceClient


@pytest.fixture
def meeting_client():
    """Create a meeting client with test base URL."""
    return MeetingServiceClient(base_url="http://test-meeting:8006")


class TestCreateMeeting:
    """Test cases for create_meeting method."""

    async def test_create_meeting_success(self, meeting_client, monkeypatch):
        """Test successful meeting creation."""
        mock_data = {"id": 1, "status": "created", "meet_link": "https://meet.google.com/test"}

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_201_CREATED, json=mock_data)

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.create_meeting(
            user_id=1,
            title="Test Meeting",
            description="Test description",
            participant_ids=[2, 3],
            scheduled_at="2024-01-01T10:00:00",
            auth_token="test-token",
        )
        assert result is not None
        assert result["id"] == 1
        assert result["status"] == "created"

    async def test_create_meeting_with_duration(self, meeting_client, monkeypatch):
        """Test meeting creation with custom duration."""
        captured_json = {}

        async def mock_post(*args, **kwargs):
            captured_json["data"] = kwargs.get("json", {})
            return Response(status_code=status.HTTP_201_CREATED, json={"id": 1})

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.create_meeting(
            user_id=1,
            title="Test Meeting",
            description="Test",
            participant_ids=[2],
            scheduled_at="2024-01-01T10:00:00",
            auth_token="test-token",
            duration_minutes=30,
        )
        assert result is not None
        assert captured_json["data"].get("duration_minutes") == 30

    async def test_create_meeting_with_type(self, meeting_client, monkeypatch):
        """Test meeting creation with custom type."""
        captured_json = {}

        async def mock_post(*args, **kwargs):
            captured_json["data"] = kwargs.get("json", {})
            return Response(status_code=status.HTTP_201_CREATED, json={"id": 1})

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.create_meeting(
            user_id=1,
            title="Test Meeting",
            description="Test",
            participant_ids=[2],
            scheduled_at="2024-01-01T10:00:00",
            auth_token="test-token",
            meeting_type="review",
        )
        assert result is not None
        assert captured_json["data"].get("meeting_type") == "review"

    async def test_create_meeting_failure(self, meeting_client, monkeypatch):
        """Test failed meeting creation."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.create_meeting(
            user_id=1,
            title="Test",
            description="Test",
            participant_ids=[2],
            scheduled_at="2024-01-01T10:00:00",
            auth_token="test-token",
        )
        assert result is None

    async def test_create_meeting_request_error(self, meeting_client, monkeypatch):
        """Test meeting creation with request error."""

        async def mock_post(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.create_meeting(
            user_id=1,
            title="Test",
            description="Test",
            participant_ids=[2],
            scheduled_at="2024-01-01T10:00:00",
            auth_token="test-token",
        )
        assert result is None


class TestGetUserMeetings:
    """Test cases for get_user_meetings method."""

    async def test_get_user_meetings_success(self, meeting_client, monkeypatch):
        """Test successful user meetings retrieval."""
        mock_data = {"meetings": [{"id": 1, "title": "Meeting 1"}, {"id": 2, "title": "Meeting 2"}]}

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(meeting_client.client, "get", mock_get)

        result = await meeting_client.get_user_meetings(1, "test-token")
        assert len(result) == 2
        assert result[0]["id"] == 1

    async def test_get_user_meetings_empty(self, meeting_client, monkeypatch):
        """Test user meetings retrieval with empty result."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json={"meetings": []})

        monkeypatch.setattr(meeting_client.client, "get", mock_get)

        result = await meeting_client.get_user_meetings(1, "test-token")
        assert result == []

    async def test_get_user_meetings_failure(self, meeting_client, monkeypatch):
        """Test failed user meetings retrieval."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        monkeypatch.setattr(meeting_client.client, "get", mock_get)

        result = await meeting_client.get_user_meetings(1, "test-token")
        assert result == []

    async def test_get_user_meetings_request_error(self, meeting_client, monkeypatch):
        """Test user meetings retrieval with request error."""

        async def mock_get(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(meeting_client.client, "get", mock_get)

        result = await meeting_client.get_user_meetings(1, "test-token")
        assert result == []

    async def test_get_user_meetings_with_limit(self, meeting_client, monkeypatch):
        """Test user meetings retrieval with custom limit."""
        captured_params = {}

        async def mock_get(*args, **kwargs):
            captured_params["params"] = kwargs.get("params", {})
            return Response(status_code=status.HTTP_200_OK, json={"meetings": []})

        monkeypatch.setattr(meeting_client.client, "get", mock_get)

        await meeting_client.get_user_meetings(1, "test-token", limit=5)
        assert captured_params["params"].get("limit") == 5


class TestGetUpcomingMeetings:
    """Test cases for get_upcoming_meetings method."""

    async def test_get_upcoming_meetings_success(self, meeting_client, monkeypatch):
        """Test successful upcoming meetings retrieval."""
        mock_data = {"meetings": [{"id": 1, "title": "Upcoming Meeting"}]}

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(meeting_client.client, "get", mock_get)

        result = await meeting_client.get_upcoming_meetings(1, "test-token")
        assert len(result) == 1

    async def test_get_upcoming_meetings_empty(self, meeting_client, monkeypatch):
        """Test upcoming meetings retrieval with empty result."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json={"meetings": []})

        monkeypatch.setattr(meeting_client.client, "get", mock_get)

        result = await meeting_client.get_upcoming_meetings(1, "test-token")
        assert result == []

    async def test_get_upcoming_meetings_request_error(self, meeting_client, monkeypatch):
        """Test upcoming meetings retrieval with request error."""

        async def mock_get(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(meeting_client.client, "get", mock_get)

        result = await meeting_client.get_upcoming_meetings(1, "test-token")
        assert result == []


class TestConfirmMeeting:
    """Test cases for confirm_meeting method."""

    async def test_confirm_meeting_success(self, meeting_client, monkeypatch):
        """Test successful meeting confirmation."""
        mock_data = {"id": 1, "status": "confirmed"}

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.confirm_meeting(1, 1, "test-token")
        assert result is not None
        assert result["status"] == "confirmed"

    async def test_confirm_meeting_failure(self, meeting_client, monkeypatch):
        """Test failed meeting confirmation."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.confirm_meeting(1, 1, "test-token")
        assert result is None

    async def test_confirm_meeting_request_error(self, meeting_client, monkeypatch):
        """Test meeting confirmation with request error."""

        async def mock_post(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.confirm_meeting(1, 1, "test-token")
        assert result is None


class TestCancelMeeting:
    """Test cases for cancel_meeting method."""

    async def test_cancel_meeting_success(self, meeting_client, monkeypatch):
        """Test successful meeting cancellation."""
        mock_data = {"id": 1, "status": "cancelled"}

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.cancel_meeting(1, 1, "test-token")
        assert result is not None
        assert result["status"] == "cancelled"

    async def test_cancel_meeting_with_reason(self, meeting_client, monkeypatch):
        """Test meeting cancellation with reason."""
        captured_json = {}

        async def mock_post(*args, **kwargs):
            captured_json["data"] = kwargs.get("json", {})
            return Response(status_code=status.HTTP_200_OK, json={"id": 1, "status": "cancelled"})

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.cancel_meeting(1, 1, "test-token", reason="Conflict")
        assert result is not None
        assert captured_json["data"].get("reason") == "Conflict"

    async def test_cancel_meeting_failure(self, meeting_client, monkeypatch):
        """Test failed meeting cancellation."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.cancel_meeting(1, 1, "test-token")
        assert result is None

    async def test_cancel_meeting_request_error(self, meeting_client, monkeypatch):
        """Test meeting cancellation with request error."""

        async def mock_post(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(meeting_client.client, "post", mock_post)

        result = await meeting_client.cancel_meeting(1, 1, "test-token")
        assert result is None
