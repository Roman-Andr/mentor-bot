"""Unit tests for feedback API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from feedback_service.api.deps import get_current_active_user
from feedback_service.database import get_db
from feedback_service.main import app
from feedback_service.models import Comment, ExperienceRating, PulseSurvey

# Create test client
client = TestClient(app)


def override_get_db() -> MagicMock:
    """Override get_db dependency with mock."""
    return MagicMock()


def mock_current_user(
    user_id: int = 1,
    role: str = "USER",
    department_id: int | None = 1,
    level: str | None = "MIDDLE",
) -> MagicMock:
    """Create a mock current user for testing."""
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.role = role
    mock_user.is_active = True
    mock_user.has_role = lambda roles: role in roles
    mock_user.department_id = department_id
    mock_user.level = level
    return mock_user


app.dependency_overrides[get_db] = override_get_db


class TestSubmitPulseSurvey:
    """Tests for POST /feedback/pulse endpoint."""

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_submit_pulse_survey_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful pulse survey submission returns 201."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock()
        mock_result = MagicMock(spec=PulseSurvey)
        mock_result.id = 1
        mock_result.user_id = 1
        mock_result.is_anonymous = False
        mock_result.rating = 7
        mock_repo.create.return_value = mock_result
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post("/api/v1/feedback/pulse", json={"rating": 7, "is_anonymous": False})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == 1
        assert data["user_id"] == 1
        assert data["rating"] == 7
        assert data["is_anonymous"] is False

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_submit_pulse_survey_anonymous(self, mock_repo_class: MagicMock) -> None:
        """Test successful anonymous pulse survey submission returns 201."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock()
        mock_result = MagicMock(spec=PulseSurvey)
        mock_result.id = 1
        mock_result.user_id = None
        mock_result.is_anonymous = True
        mock_result.rating = 8
        mock_repo.create.return_value = mock_result
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post("/api/v1/feedback/pulse", json={"rating": 8, "is_anonymous": True})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == 1
        assert data["user_id"] is None
        assert data["is_anonymous"] is True
        assert data["rating"] == 8

    def test_submit_pulse_survey_invalid_rating_high(self) -> None:
        """Test pulse survey with rating > 10 returns 422."""
        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")
        response = client.post("/api/v1/feedback/pulse", json={"rating": 11, "is_anonymous": False})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_submit_pulse_survey_invalid_rating_low(self) -> None:
        """Test pulse survey with rating < 1 returns 422."""
        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")
        response = client.post("/api/v1/feedback/pulse", json={"rating": 0, "is_anonymous": False})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_submit_pulse_survey_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test pulse survey database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post("/api/v1/feedback/pulse", json={"rating": 7, "is_anonymous": False})

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "pulse survey" in response.json()["detail"].lower()


class TestSubmitExperienceRating:
    """Tests for POST /feedback/experience endpoint."""

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_submit_experience_rating_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful experience rating submission returns 201."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock()
        mock_result = MagicMock(spec=ExperienceRating)
        mock_result.id = 1
        mock_result.user_id = 1
        mock_result.is_anonymous = False
        mock_result.rating = 4
        mock_repo.create.return_value = mock_result
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post("/api/v1/feedback/experience", json={"rating": 4, "is_anonymous": False})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == 1
        assert data["user_id"] == 1
        assert data["rating"] == 4
        assert data["is_anonymous"] is False

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_submit_experience_rating_anonymous(self, mock_repo_class: MagicMock) -> None:
        """Test successful anonymous experience rating submission returns 201."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock()
        mock_result = MagicMock(spec=ExperienceRating)
        mock_result.id = 1
        mock_result.user_id = None
        mock_result.is_anonymous = True
        mock_result.rating = 5
        mock_repo.create.return_value = mock_result
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post("/api/v1/feedback/experience", json={"rating": 5, "is_anonymous": True})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == 1
        assert data["user_id"] is None
        assert data["is_anonymous"] is True
        assert data["rating"] == 5

    def test_submit_experience_rating_invalid_high(self) -> None:
        """Test experience rating with rating > 5 returns 422."""
        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")
        response = client.post("/api/v1/feedback/experience", json={"rating": 6, "is_anonymous": False})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_submit_experience_rating_invalid_low(self) -> None:
        """Test experience rating with rating < 1 returns 422."""
        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")
        response = client.post("/api/v1/feedback/experience", json={"rating": 0, "is_anonymous": False})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_submit_experience_rating_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test experience rating database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post("/api/v1/feedback/experience", json={"rating": 4, "is_anonymous": False})

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "experience rating" in response.json()["detail"].lower()


class TestSubmitComment:
    """Tests for POST /feedback/comments endpoint."""

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_submit_comment_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful comment submission returns 201."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock()
        mock_result = MagicMock(spec=Comment)
        mock_result.id = 1
        mock_result.user_id = 1
        mock_result.is_anonymous = False
        mock_result.comment = "This is a detailed feedback comment with enough length."
        mock_result.reply = None
        mock_result.replied_at = None
        mock_result.replied_by = None
        mock_result.allow_contact = False
        mock_result.contact_email = None
        mock_repo.create.return_value = mock_result
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post(
            "/api/v1/feedback/comments",
            json={"comment": "This is a detailed feedback comment with enough length.", "is_anonymous": False}
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == 1
        assert data["user_id"] == 1
        assert data["is_anonymous"] is False
        assert "detailed feedback" in data["comment"]

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_submit_comment_anonymous_with_contact(self, mock_repo_class: MagicMock) -> None:
        """Test successful anonymous comment with contact info returns 201."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock()
        mock_result = MagicMock(spec=Comment)
        mock_result.id = 1
        mock_result.user_id = None
        mock_result.is_anonymous = True
        mock_result.comment = "Anonymous feedback with contact."
        mock_result.reply = None
        mock_result.replied_at = None
        mock_result.replied_by = None
        mock_result.allow_contact = True
        mock_result.contact_email = "user@example.com"
        mock_repo.create.return_value = mock_result
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post(
            "/api/v1/feedback/comments",
            json={
                "comment": "Anonymous feedback with contact.",
                "is_anonymous": True,
                "allow_contact": True,
                "contact_email": "user@example.com"
            }
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == 1
        assert data["user_id"] is None
        assert data["is_anonymous"] is True
        assert data["allow_contact"] is True
        assert data["contact_email"] == "user@example.com"

    def test_submit_comment_too_short(self) -> None:
        """Test comment with less than 10 characters returns 422."""
        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")
        response = client.post(
            "/api/v1/feedback/comments",
            json={"comment": "Short", "is_anonymous": False}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_submit_comment_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test comment database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.post(
            "/api/v1/feedback/comments",
            json={"comment": "This is a detailed feedback comment with enough length.", "is_anonymous": False}
        )

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "comment" in response.json()["detail"].lower()


class TestGetPulseSurveys:
    """Tests for GET /feedback/pulse endpoint."""

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_surveys_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful pulse survey retrieval returns 200."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock()
        mock_survey = MagicMock(spec=PulseSurvey)
        mock_survey.id = 1
        mock_survey.user_id = 1
        mock_survey.is_anonymous = False
        mock_survey.rating = 7
        mock_survey.submitted_at = datetime.now(UTC)
        mock_repo.get_by_user.return_value = ([mock_survey], 1)
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/pulse")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["rating"] == 7
        assert data["items"][0]["is_anonymous"] is False

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_surveys_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/pulse")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "pulse surveys" in response.json()["detail"].lower()

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_surveys_with_date_filters(self, mock_repo_class: MagicMock) -> None:
        """Test pulse survey retrieval with date filters."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock()
        mock_survey = MagicMock(spec=PulseSurvey)
        mock_survey.id = 1
        mock_survey.user_id = 1
        mock_survey.is_anonymous = False
        mock_survey.rating = 7
        mock_survey.submitted_at = datetime.now(UTC)
        mock_repo.get_by_user.return_value = ([mock_survey], 1)
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/pulse?from_date=2024-01-01T00:00:00&to_date=2024-12-31T23:59:59")

        # Assert
        assert response.status_code == status.HTTP_200_OK

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_surveys_hr_can_view_all(self, mock_repo_class: MagicMock) -> None:
        """Test HR can view all pulse surveys without user_id filter."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock()
        mock_survey1 = MagicMock(spec=PulseSurvey)
        mock_survey1.id = 1
        mock_survey1.user_id = 1
        mock_survey1.rating = 7
        mock_survey1.submitted_at = datetime.now(UTC)
        mock_survey2 = MagicMock(spec=PulseSurvey)
        mock_survey2.id = 2
        mock_survey2.user_id = 2
        mock_survey2.rating = 8
        mock_survey2.submitted_at = datetime.now(UTC)
        mock_repo.get_by_user.return_value = ([mock_survey1, mock_survey2], 2)
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.get("/api/v1/feedback/pulse")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_surveys_user_cannot_view_others(self, mock_repo_class: MagicMock) -> None:
        """Test regular user cannot view another user's pulse surveys."""
        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/pulse?user_id=2")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetPulseStats:
    """Tests for GET /feedback/pulse/stats endpoint."""

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_stats_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful pulse stats retrieval returns 200."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_stats = AsyncMock()
        mock_repo.get_rating_distribution = AsyncMock()
        mock_repo.get_stats.return_value = {
            "average_rating": 7.5,
            "total_responses": 100,
            "min_rating": 1,
            "max_rating": 10,
        }
        mock_repo.get_rating_distribution.return_value = {7: 50, 8: 30, 9: 20}
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/pulse/stats")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["average_rating"] == 7.5
        assert data["total_responses"] == 100
        assert data["rating_distribution"] == {"7": 50, "8": 30, "9": 20}

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_stats_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_stats = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/pulse/stats")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "pulse stats" in response.json()["detail"].lower()

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_stats_hr_can_view_all(self, mock_repo_class: MagicMock) -> None:
        """Test HR can view stats for all users."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_stats = AsyncMock()
        mock_repo.get_rating_distribution = AsyncMock()
        mock_repo.get_stats.return_value = {
            "average_rating": 7.5,
            "total_responses": 1000,
            "min_rating": 1,
            "max_rating": 10,
        }
        mock_repo.get_rating_distribution.return_value = {5: 100, 6: 200, 7: 300, 8: 250, 9: 150}
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.get("/api/v1/feedback/pulse/stats")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_responses"] == 1000


class TestGetPulseAnonymityStats:
    """Tests for GET /feedback/pulse/anonymity-stats endpoint."""

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_anonymity_stats_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful anonymity stats retrieval returns 200."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_anonymity_stats = AsyncMock()
        mock_repo.get_anonymity_stats.return_value = {
            "anonymous": {"average_rating": 7.0, "count": 50},
            "attributed": {"average_rating": 7.8, "count": 150},
        }
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.get("/api/v1/feedback/pulse/anonymity-stats")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["anonymous"]["count"] == 50
        assert data["attributed"]["count"] == 150

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_anonymity_stats_with_department_filter(self, mock_repo_class: MagicMock) -> None:
        """Test anonymity stats with department filter."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_anonymity_stats = AsyncMock()
        mock_repo.get_anonymity_stats.return_value = {
            "anonymous": {"average_rating": 7.5, "count": 25},
            "attributed": {"average_rating": 8.0, "count": 75},
        }
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.get("/api/v1/feedback/pulse/anonymity-stats?department_id=1")

        # Assert
        assert response.status_code == status.HTTP_200_OK

    @patch("feedback_service.api.endpoints.feedback.PulseSurveyRepository")
    def test_get_pulse_anonymity_stats_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_anonymity_stats = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.get("/api/v1/feedback/pulse/anonymity-stats")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "anonymity stats" in response.json()["detail"].lower()

    def test_get_pulse_anonymity_stats_user_forbidden(self) -> None:
        """Test regular user cannot access anonymity stats."""
        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        response = client.get("/api/v1/feedback/pulse/anonymity-stats")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetExperienceRatings:
    """Tests for GET /feedback/experience endpoint."""

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_get_experience_ratings_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful experience rating retrieval returns 200."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock()
        mock_rating = MagicMock(spec=ExperienceRating)
        mock_rating.id = 1
        mock_rating.user_id = 1
        mock_rating.is_anonymous = False
        mock_rating.rating = 4
        mock_rating.submitted_at = datetime.now(UTC)
        mock_repo.get_by_user.return_value = ([mock_rating], 1)
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/experience")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["rating"] == 4
        assert data["items"][0]["is_anonymous"] is False

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_get_experience_ratings_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/experience")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "experience ratings" in response.json()["detail"].lower()

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_get_experience_ratings_with_rating_filters(self, mock_repo_class: MagicMock) -> None:
        """Test experience ratings with min/max rating filters."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock()
        mock_rating = MagicMock(spec=ExperienceRating)
        mock_rating.id = 1
        mock_rating.user_id = 1
        mock_rating.rating = 4
        mock_rating.submitted_at = datetime.now(UTC)
        mock_repo.get_by_user.return_value = ([mock_rating], 1)
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/experience?min_rating=3&max_rating=5")

        # Assert
        assert response.status_code == status.HTTP_200_OK


class TestGetExperienceStats:
    """Tests for GET /feedback/experience/stats endpoint."""

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_get_experience_stats_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful experience stats retrieval returns 200."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_stats = AsyncMock()
        mock_repo.get_rating_distribution = AsyncMock()
        mock_repo.get_stats.return_value = {
            "average_rating": 4.2,
            "total_ratings": 50,
            "min_rating": 1,
            "max_rating": 5,
        }
        mock_repo.get_rating_distribution.return_value = {4: 30, 5: 20}
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/experience/stats")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["average_rating"] == 4.2
        assert data["total_ratings"] == 50
        assert data["rating_distribution"] == {"4": 30, "5": 20}

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_get_experience_stats_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_stats = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/experience/stats")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "experience stats" in response.json()["detail"].lower()

    @patch("feedback_service.api.endpoints.feedback.ExperienceRatingRepository")
    def test_get_experience_stats_hr_can_view_all(self, mock_repo_class: MagicMock) -> None:
        """Test HR can view stats for all users."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_stats = AsyncMock()
        mock_repo.get_rating_distribution = AsyncMock()
        mock_repo.get_stats.return_value = {
            "average_rating": 4.5,
            "total_ratings": 500,
            "min_rating": 1,
            "max_rating": 5,
        }
        mock_repo.get_rating_distribution.return_value = {3: 100, 4: 200, 5: 200}
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.get("/api/v1/feedback/experience/stats")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_ratings"] == 500


class TestGetComments:
    """Tests for GET /feedback/comments endpoint."""

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_get_comments_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful comment retrieval returns 200."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock()
        mock_comment = MagicMock(spec=Comment)
        mock_comment.id = 1
        mock_comment.user_id = 1
        mock_comment.is_anonymous = False
        mock_comment.comment = "This is a test comment with enough length for validation."
        mock_comment.submitted_at = datetime.now(UTC)
        mock_comment.reply = None
        mock_comment.replied_at = None
        mock_comment.replied_by = None
        mock_comment.allow_contact = False
        mock_comment.contact_email = None
        mock_repo.get_by_user.return_value = ([mock_comment], 1)
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/comments")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert "test comment" in data["items"][0]["comment"]
        assert data["items"][0]["is_anonymous"] is False

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_get_comments_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock(side_effect=Exception("Database error"))
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/comments")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "comments" in response.json()["detail"].lower()

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_get_comments_with_search_filter(self, mock_repo_class: MagicMock) -> None:
        """Test comments with search filter."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock()
        mock_comment = MagicMock(spec=Comment)
        mock_comment.id = 1
        mock_comment.user_id = 1
        mock_comment.comment = "This is a test comment with enough length for validation."
        mock_comment.submitted_at = datetime.now(UTC)
        mock_comment.reply = None
        mock_comment.replied_at = None
        mock_comment.replied_by = None
        mock_comment.allow_contact = False
        mock_comment.contact_email = None
        mock_repo.get_by_user.return_value = ([mock_comment], 1)
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/comments?search=test")

        # Assert
        assert response.status_code == status.HTTP_200_OK

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_get_comments_with_has_reply_filter(self, mock_repo_class: MagicMock) -> None:
        """Test comments with has_reply filter."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_user = AsyncMock()
        mock_repo.get_by_user.return_value = ([], 0)
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        # Act
        response = client.get("/api/v1/feedback/comments?has_reply=true")

        # Assert
        assert response.status_code == status.HTTP_200_OK


class TestReplyToComment:
    """Tests for POST /feedback/comments/{id}/reply endpoint."""

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_reply_to_comment_success(self, mock_repo_class: MagicMock) -> None:
        """Test successful comment reply returns 200."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock()
        mock_repo.add_reply = AsyncMock()
        mock_comment = MagicMock(spec=Comment)
        mock_comment.id = 1
        mock_comment.user_id = 1
        mock_comment.is_anonymous = False
        mock_comment.comment = "Original comment"
        mock_comment.submitted_at = datetime.now(UTC)
        mock_comment.reply = "Thank you for your feedback!"
        mock_comment.replied_at = datetime.now(UTC)
        mock_comment.replied_by = 2
        mock_comment.allow_contact = False
        mock_comment.contact_email = None
        mock_repo.get_by_id.return_value = mock_comment
        mock_repo.add_reply.return_value = mock_comment
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.post(
            "/api/v1/feedback/comments/1/reply",
            json={"reply": "Thank you for your feedback!"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["reply"] == "Thank you for your feedback!"
        assert data["replied_by"] == 2

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_reply_to_anonymous_comment_with_contact(self, mock_repo_class: MagicMock) -> None:
        """Test replying to anonymous comment with contact info returns 200."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock()
        mock_repo.add_reply = AsyncMock()
        mock_comment = MagicMock(spec=Comment)
        mock_comment.id = 1
        mock_comment.user_id = None
        mock_comment.is_anonymous = True
        mock_comment.allow_contact = True
        mock_comment.contact_email = "user@example.com"
        mock_comment.comment = "Anonymous feedback"
        mock_comment.submitted_at = datetime.now(UTC)
        mock_comment.reply = None
        mock_comment.replied_at = None
        mock_comment.replied_by = None
        mock_repo.get_by_id.return_value = mock_comment
        mock_repo.add_reply.return_value = mock_comment
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.post(
            "/api/v1/feedback/comments/1/reply",
            json={"reply": "Thank you for your anonymous feedback!"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_reply_to_anonymous_comment_without_contact_fails(self, mock_repo_class: MagicMock) -> None:
        """Test replying to anonymous comment without contact info returns 403."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock()
        mock_comment = MagicMock(spec=Comment)
        mock_comment.id = 1
        mock_comment.user_id = None
        mock_comment.is_anonymous = True
        mock_comment.allow_contact = False
        mock_comment.contact_email = None
        mock_repo.get_by_id.return_value = mock_comment
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.post(
            "/api/v1/feedback/comments/1/reply",
            json={"reply": "This should fail"}
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_reply_to_comment_not_found(self, mock_repo_class: MagicMock) -> None:
        """Test reply to non-existent comment returns 404."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock()
        mock_repo.get_by_id.return_value = None
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.post(
            "/api/v1/feedback/comments/999/reply",
            json={"reply": "Thank you for your feedback!"}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_reply_to_comment_user_forbidden(self) -> None:
        """Test regular user cannot reply to comments."""
        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(1, "USER")

        response = client.post(
            "/api/v1/feedback/comments/1/reply",
            json={"reply": "Thank you for your feedback!"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("feedback_service.api.endpoints.feedback.CommentRepository")
    def test_reply_to_comment_db_error(self, mock_repo_class: MagicMock) -> None:
        """Test database error returns 500."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock()
        mock_repo.add_reply = AsyncMock(side_effect=Exception("Database error"))
        mock_comment = MagicMock(spec=Comment)
        mock_comment.id = 1
        mock_comment.user_id = 1
        mock_comment.is_anonymous = False
        mock_comment.allow_contact = False
        mock_repo.get_by_id.return_value = mock_comment
        mock_repo_class.return_value = mock_repo

        app.dependency_overrides[get_current_active_user] = lambda: mock_current_user(2, "HR")

        # Act
        response = client.post(
            "/api/v1/feedback/comments/1/reply",
            json={"reply": "Thank you for your feedback!"}
        )

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "reply" in response.json()["detail"].lower()
