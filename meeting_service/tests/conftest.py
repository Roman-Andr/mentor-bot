"""Pytest configuration and fixtures for meeting_service tests."""

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set required environment variables BEFORE any app imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_meeting_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SERVICE_API_KEY", "test-service-api-key")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-google-client-secret")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost:8000/callback")

# Now safe to import app code
from meeting_service.core.enums import MeetingStatus, MeetingType
from meeting_service.repositories.unit_of_work import IUnitOfWork
from meeting_service.services.google_calendar_service import GoogleCalendarService


@pytest.fixture
def mock_uow() -> MagicMock:
    """Create a mock Unit of Work with AsyncMock repositories."""
    uow = MagicMock(spec=IUnitOfWork)

    # Mock all repositories with AsyncMock methods
    uow.meetings = MagicMock()
    uow.meetings.create = AsyncMock()
    uow.meetings.get_by_id = AsyncMock()
    uow.meetings.update = AsyncMock()
    uow.meetings.delete = AsyncMock()
    uow.meetings.find_meetings = AsyncMock()

    uow.materials = MagicMock()
    uow.materials.create = AsyncMock()
    uow.materials.get_by_id = AsyncMock()
    uow.materials.get_by_meeting = AsyncMock()
    uow.materials.delete = AsyncMock()

    uow.user_meetings = MagicMock()
    uow.user_meetings.create = AsyncMock()
    uow.user_meetings.get_by_id = AsyncMock()
    uow.user_meetings.get_user_meeting = AsyncMock()
    uow.user_meetings.update = AsyncMock()
    uow.user_meetings.delete = AsyncMock()
    uow.user_meetings.find_by_user = AsyncMock()
    uow.user_meetings.find_by_meeting = AsyncMock()

    uow.google_calendar_accounts = MagicMock()
    uow.google_calendar_accounts.get_by_user_id = AsyncMock()
    uow.google_calendar_accounts.create = AsyncMock()
    uow.google_calendar_accounts.update = AsyncMock()

    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()

    return uow


@pytest.fixture
def mock_google_calendar_service() -> MagicMock:
    """Create a mock GoogleCalendarService with AsyncMock methods."""
    mock_service = MagicMock(spec=GoogleCalendarService)
    mock_service.create_event = AsyncMock()
    mock_service.update_event = AsyncMock()
    mock_service.delete_event = AsyncMock()
    mock_service.get_credentials = AsyncMock()
    mock_service.save_credentials = AsyncMock()
    mock_service.refresh_credentials = AsyncMock()
    return mock_service


@pytest.fixture
def sample_meeting_data() -> dict[str, Any]:
    """Return sample meeting data for testing."""
    return {
        "id": 1,
        "title": "Test Meeting",
        "description": "Test Description",
        "type": MeetingType.HR,
        "department_id": 1,
        "position": "Developer",
        "level": None,
        "is_mandatory": True,
        "order": 0,
        "deadline_days": 7,
    }


@pytest.fixture
def sample_user_meeting_data() -> dict[str, Any]:
    """Return sample user meeting assignment data."""
    return {
        "id": 1,
        "user_id": 100,
        "meeting_id": 1,
        "scheduled_at": None,
        "status": MeetingStatus.SCHEDULED,
        "completed_at": None,
        "feedback": None,
        "rating": None,
        "google_calendar_event_id": None,
    }
