"""Pytest configuration and shared fixtures for feedback_service tests."""

import os
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# Clear proxy environment variables to prevent httpx errors with unsupported socks:// scheme
for proxy_var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"]:
    os.environ.pop(proxy_var, None)

# Set required environment variables BEFORE any app imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_feedback_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SERVICE_API_KEY", "test-service-api-key")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")
os.environ.setdefault("NOTIFICATION_SERVICE_URL", "http://localhost:8004")

# Now we can import from the application
from feedback_service.models import Comment, ExperienceRating, PulseSurvey
from feedback_service.repositories import CommentRepository, ExperienceRatingRepository, PulseSurveyRepository


@pytest.fixture
def mock_db() -> MagicMock:
    """Create a mock AsyncSession."""
    session = MagicMock(spec=AsyncSession)
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def pulse_survey_repo(mock_db: MagicMock) -> PulseSurveyRepository:
    """Create a PulseSurveyRepository with mocked session."""
    return PulseSurveyRepository(mock_db)


@pytest.fixture
def experience_rating_repo(mock_db: MagicMock) -> ExperienceRatingRepository:
    """Create an ExperienceRatingRepository with mocked session."""
    return ExperienceRatingRepository(mock_db)


@pytest.fixture
def comment_repo(mock_db: MagicMock) -> CommentRepository:
    """Create a CommentRepository with mocked session."""
    return CommentRepository(mock_db)


@pytest.fixture
def sample_pulse_create() -> dict[str, Any]:
    """Return valid PulseSurveyCreate data."""
    return {"user_id": 1, "rating": 7}


@pytest.fixture
def sample_experience_create() -> dict[str, Any]:
    """Return valid ExperienceRatingCreate data."""
    return {"user_id": 1, "rating": 4}


@pytest.fixture
def sample_comment_create() -> dict[str, Any]:
    """Return valid CommentCreate data."""
    return {"user_id": 1, "comment": "This is a detailed feedback comment with enough length."}


@pytest.fixture
def mock_pulse_survey() -> MagicMock:
    """Return a mocked PulseSurvey model instance."""
    survey = MagicMock(spec=PulseSurvey)
    survey.id = 1
    survey.user_id = 1
    survey.rating = 7
    survey.submitted_at = datetime.now(tz=UTC)
    return survey


@pytest.fixture
def mock_experience_rating() -> MagicMock:
    """Return a mocked ExperienceRating model instance."""
    rating = MagicMock(spec=ExperienceRating)
    rating.id = 1
    rating.user_id = 1
    rating.rating = 4
    rating.submitted_at = datetime.now(tz=UTC)
    return rating


@pytest.fixture
def mock_comment() -> MagicMock:
    """Return a mocked Comment model instance."""
    comment = MagicMock(spec=Comment)
    comment.id = 1
    comment.user_id = 1
    comment.comment = "This is a detailed feedback comment with enough length."
    comment.submitted_at = datetime.now(tz=UTC)
    return comment


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI TestClient with mocked database for health checks."""
    with (
        patch("feedback_service.main.init_db", new_callable=AsyncMock),
        patch("feedback_service.main.engine") as mock_engine,
    ):
        # Mock the database connection for health checks
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=False)

        from feedback_service.main import app

        return TestClient(app)
