"""Unit tests for telegram_bot EscalationServiceClient."""

import pytest
from fastapi import status
from httpx import RequestError, Response

from telegram_bot.services.escalation_client import EscalationServiceClient


@pytest.fixture
def escalation_client():
    """Create an escalation client with test base URL."""
    return EscalationServiceClient(base_url="http://test-escalation:8005")


class TestCreateEscalation:
    """Test cases for create_escalation method with new schema."""

    async def test_create_escalation_sends_correct_schema(self, escalation_client, monkeypatch):
        """Test that client sends correct escalation_service schema."""
        captured_payload = {}

        async def mock_post(*args, **kwargs):
            captured_payload["json"] = kwargs.get("json", {})
            return Response(
                status_code=status.HTTP_201_CREATED,
                json={"id": 1, "reason": "Test Reason", "status": "PENDING"},
            )

        monkeypatch.setattr(escalation_client.client, "post", mock_post)

        result = await escalation_client.create_escalation(
            user_id=1,
            title="Test Reason",  # Old field name
            description="Test description",
            category="HR",
            auth_token="test-token",
        )

        assert result is not None
        assert result["id"] == 1

        # Verify the payload matches escalation_service schema
        payload = captured_payload["json"]
        assert payload["user_id"] == 1
        assert payload["type"] == "HR"  # category -> type
        assert payload["source"] == "MANUAL"
        assert payload["reason"] == "Test Reason"  # title -> reason
        assert payload["context"]["description"] == "Test description"
        assert payload["assigned_to"] is None

    async def test_create_escalation_maps_categories(self, escalation_client, monkeypatch):
        """Test category to type mapping."""
        test_cases = [
            ("HR", "HR"),
            ("Mentor", "MENTOR"),
            ("Technical", "IT"),
            ("General", "GENERAL"),
            ("unknown", "GENERAL"),
        ]

        for category, expected_type in test_cases:
            captured_payload = {}

            async def mock_post(*args, **kwargs):
                captured_payload["json"] = kwargs.get("json", {})
                return Response(
                    status_code=status.HTTP_201_CREATED,
                    json={"id": 1, "reason": "Test", "status": "PENDING"},
                )

            monkeypatch.setattr(escalation_client.client, "post", mock_post)

            await escalation_client.create_escalation(
                user_id=1,
                title="Test",
                description="Test",
                category=category,
                auth_token="test-token",
            )

            assert captured_payload["json"]["type"] == expected_type

    async def test_create_escalation_success(self, escalation_client, monkeypatch):
        """Test successful escalation creation."""
        mock_data = {
            "id": 1,
            "reason": "Test Escalation",  # escalation_service uses 'reason'
            "status": "PENDING",
            "type": "HR",
        }

        async def mock_post(*args, **kwargs):
            return Response(
                status_code=status.HTTP_201_CREATED,
                json=mock_data,
            )

        monkeypatch.setattr(escalation_client.client, "post", mock_post)

        result = await escalation_client.create_escalation(
            user_id=1,
            title="Test Escalation",
            description="Test description",
            category="HR",
            auth_token="test-token",
        )
        assert result is not None
        assert result["id"] == 1
        assert result["reason"] == "Test Escalation"

    async def test_create_escalation_with_priority(self, escalation_client, monkeypatch):
        """Test escalation creation with priority stored in context."""
        captured_payload = {}

        async def mock_post(*args, **kwargs):
            captured_payload["json"] = kwargs.get("json", {})
            return Response(
                status_code=status.HTTP_201_CREATED,
                json={"id": 1, "reason": "Urgent Issue", "status": "PENDING"},
            )

        monkeypatch.setattr(escalation_client.client, "post", mock_post)

        result = await escalation_client.create_escalation(
            user_id=1,
            title="Urgent Issue",
            description="Test",
            category="HR",
            auth_token="test-token",
            priority="high",
        )
        assert result is not None
        # Priority is stored in context
        assert captured_payload["json"]["context"]["priority"] == "high"

    async def test_create_escalation_failure(self, escalation_client, monkeypatch):
        """Test failed escalation creation."""

        async def mock_post(*args, **kwargs):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        monkeypatch.setattr(escalation_client.client, "post", mock_post)

        result = await escalation_client.create_escalation(
            user_id=1,
            title="Test",
            description="Test",
            category="HR",
            auth_token="test-token",
        )
        assert result is None

    async def test_create_escalation_request_error(self, escalation_client, monkeypatch):
        """Test escalation creation with request error."""

        async def mock_post(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(escalation_client.client, "post", mock_post)

        result = await escalation_client.create_escalation(
            user_id=1,
            title="Test",
            description="Test",
            category="HR",
            auth_token="test-token",
        )
        assert result is None


class TestGetUserEscalations:
    """Test cases for get_user_escalations method."""

    async def test_get_user_escalations_success(self, escalation_client, monkeypatch):
        """Test successful user escalations retrieval."""
        mock_data = [
            {"id": 1, "reason": "Issue 1", "status": "PENDING"},  # uses 'reason'
            {"id": 2, "reason": "Issue 2", "status": "RESOLVED"},
        ]

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        result = await escalation_client.get_user_escalations(1, "test-token")
        assert len(result) == 2
        assert result[0]["id"] == 1

    async def test_get_user_escalations_wrapped_response(self, escalation_client, monkeypatch):
        """Test escalations retrieval with wrapped response format."""
        mock_data = {"escalations": [{"id": 1, "reason": "Issue", "status": "PENDING"}]}

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        result = await escalation_client.get_user_escalations(1, "test-token")
        assert len(result) == 1
        assert result[0]["id"] == 1

    async def test_get_user_escalations_empty(self, escalation_client, monkeypatch):
        """Test user escalations retrieval with empty result."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=[])

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        result = await escalation_client.get_user_escalations(1, "test-token")
        assert result == []

    async def test_get_user_escalations_failure(self, escalation_client, monkeypatch):
        """Test failed user escalations retrieval."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        result = await escalation_client.get_user_escalations(1, "test-token")
        assert result == []

    async def test_get_user_escalations_request_error(self, escalation_client, monkeypatch):
        """Test user escalations retrieval with request error."""

        async def mock_get(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        result = await escalation_client.get_user_escalations(1, "test-token")
        assert result == []

    async def test_get_user_escalations_with_limit(self, escalation_client, monkeypatch):
        """Test user escalations retrieval with custom limit."""
        captured_params = {}

        async def mock_get(*args, **kwargs):
            captured_params["params"] = kwargs.get("params", {})
            return Response(status_code=status.HTTP_200_OK, json=[])

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        await escalation_client.get_user_escalations(1, "test-token", limit=5)
        assert captured_params["params"].get("limit") == 5


class TestGetEscalationStatus:
    """Test cases for get_escalation_status method."""

    async def test_get_escalation_status_success(self, escalation_client, monkeypatch):
        """Test successful escalation status retrieval."""
        mock_data = {"id": 1, "reason": "Test", "status": "IN_PROGRESS"}

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_200_OK, json=mock_data)

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        result = await escalation_client.get_escalation_status(1, "test-token")
        assert result is not None
        assert result["id"] == 1
        assert result["status"] == "IN_PROGRESS"

    async def test_get_escalation_status_not_found(self, escalation_client, monkeypatch):
        """Test escalation status retrieval for non-existent escalation."""

        async def mock_get(*args, **kwargs):
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        result = await escalation_client.get_escalation_status(999, "test-token")
        assert result is None

    async def test_get_escalation_status_request_error(self, escalation_client, monkeypatch):
        """Test escalation status retrieval with request error."""

        async def mock_get(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(escalation_client.client, "get", mock_get)

        result = await escalation_client.get_escalation_status(1, "test-token")
        assert result is None


class TestUpdateEscalationStatus:
    """Test cases for update_escalation_status method."""

    async def test_update_escalation_status_success(self, escalation_client, monkeypatch):
        """Test successful escalation status update."""
        mock_data = {"id": 1, "status": "RESOLVED"}

        async def mock_patch(*args, **kwargs):
            return Response(status_code=200, json=mock_data)

        monkeypatch.setattr(escalation_client.client, "patch", mock_patch)

        result = await escalation_client.update_escalation_status(
            1, "RESOLVED", "test-token"
        )
        assert result is not None
        assert result["status"] == "RESOLVED"

    async def test_update_escalation_status_with_notes(self, escalation_client, monkeypatch):
        """Test escalation status update with notes."""
        captured_json = {}

        async def mock_patch(*args, **kwargs):
            captured_json["data"] = kwargs.get("json", {})
            return Response(status_code=200, json={"id": 1, "status": "RESOLVED"})

        monkeypatch.setattr(escalation_client.client, "patch", mock_patch)

        result = await escalation_client.update_escalation_status(
            1, "RESOLVED", "test-token", notes="Issue fixed"
        )
        assert result is not None
        assert captured_json["data"].get("notes") == "Issue fixed"

    async def test_update_escalation_status_failure(self, escalation_client, monkeypatch):
        """Test failed escalation status update."""

        async def mock_patch(*args, **kwargs):
            return Response(status_code=400)

        monkeypatch.setattr(escalation_client.client, "patch", mock_patch)

        result = await escalation_client.update_escalation_status(
            1, "RESOLVED", "test-token"
        )
        assert result is None

    async def test_update_escalation_status_request_error(self, escalation_client, monkeypatch):
        """Test escalation status update with request error."""

        async def mock_patch(*args, **kwargs):
            raise RequestError("Connection failed")

        monkeypatch.setattr(escalation_client.client, "patch", mock_patch)

        result = await escalation_client.update_escalation_status(
            1, "RESOLVED", "test-token"
        )
        assert result is None
