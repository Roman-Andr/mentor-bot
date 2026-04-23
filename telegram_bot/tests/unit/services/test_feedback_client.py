"""Unit tests for telegram_bot FeedbackServiceClient."""

from typing import Never

import pytest
from fastapi import status
from httpx import RequestError, Response

from telegram_bot.services.feedback_client import FeedbackServiceClient


@pytest.fixture
def feedback_client():
    """Create a feedback client with test base URL."""
    return FeedbackServiceClient(base_url="http://test-feedback:8007")


class TestSubmitPulseSurvey:
    """Test cases for submit_pulse_survey method."""

    async def test_submit_pulse_survey_success(self, feedback_client, monkeypatch):
        """Test successful pulse survey submission."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_201_CREATED)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_pulse_survey(1, 5, "test-token")
        assert result is True

    async def test_submit_pulse_survey_failure(self, feedback_client, monkeypatch):
        """Test failed pulse survey submission."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_pulse_survey(1, 5, "test-token")
        assert result is False

    async def test_submit_pulse_survey_request_error(self, feedback_client, monkeypatch):
        """Test pulse survey submission with request error."""

        async def mock_post(*args, **kwargs) -> Never:
            msg = "Connection failed"
            raise RequestError(msg)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_pulse_survey(1, 5, "test-token")
        assert result is False


class TestSubmitExperienceRating:
    """Test cases for submit_experience_rating method."""

    async def test_submit_experience_rating_success(self, feedback_client, monkeypatch):
        """Test successful experience rating submission."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_201_CREATED)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_experience_rating(1, 4, "test-token")
        assert result is True

    async def test_submit_experience_rating_failure(self, feedback_client, monkeypatch):
        """Test failed experience rating submission."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_experience_rating(1, 4, "test-token")
        assert result is False

    async def test_submit_experience_rating_request_error(self, feedback_client, monkeypatch):
        """Test experience rating submission with request error."""

        async def mock_post(*args, **kwargs) -> Never:
            msg = "Connection failed"
            raise RequestError(msg)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_experience_rating(1, 4, "test-token")
        assert result is False


class TestSubmitComment:
    """Test cases for submit_comment method."""

    async def test_submit_comment_success(self, feedback_client, monkeypatch):
        """Test successful comment submission."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_201_CREATED)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_comment(1, "Great service!", "test-token", is_anonymous=False)
        assert result is True

    async def test_submit_comment_failure(self, feedback_client, monkeypatch):
        """Test failed comment submission."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_comment(1, "Great service!", "test-token", is_anonymous=False)
        assert result is False

    async def test_submit_comment_empty_comment(self, feedback_client, monkeypatch):
        """Test comment submission with empty comment."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_201_CREATED)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_comment(1, "", "test-token", is_anonymous=False)
        assert result is True

    async def test_submit_comment_request_error(self, feedback_client, monkeypatch):
        """Test comment submission with request error."""

        async def mock_post(*args, **kwargs) -> Never:
            msg = "Connection failed"
            raise RequestError(msg)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_comment("Test comment", "test-token", is_anonymous=False)
        assert result is False

    async def test_submit_comment_with_contact_email_anonymous(self, feedback_client, monkeypatch):
        """Test comment submission with contact_email when anonymous and allow_contact=True.

        Covers line 71: when is_anonymous=True, allow_contact=True, and contact_email is provided,
        the payload should include contact_email.
        """
        captured_payload = {}

        async def mock_post(*args, **kwargs):
            captured_payload.update(kwargs.get("json", {}))
            return Response(status_code=status.HTTP_201_CREATED)

        monkeypatch.setattr(feedback_client.client, "post", mock_post)

        result = await feedback_client.submit_comment(
            comment="Great service!",
            is_anonymous=True,
            auth_token="test-token",
            allow_contact=True,
            contact_email="user@example.com"
        )

        assert result is True
        assert captured_payload["comment"] == "Great service!"
        assert captured_payload["is_anonymous"] is True
        assert captured_payload["allow_contact"] is True
        assert captured_payload["contact_email"] == "user@example.com"
