"""Unit tests for escalation_service/api/endpoints/escalations.py."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from escalation_service.api.deps import get_current_active_user, get_escalation_service, get_uow
from escalation_service.core.enums import EscalationSource, EscalationStatus, EscalationType
from escalation_service.main import app
from escalation_service.models import EscalationRequest
from escalation_service.services.escalation import EscalationService
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_notification_client():
    """Automatically mock NotificationClient for all API tests to prevent HTTP calls."""
    with patch("escalation_service.services.escalation.NotificationClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.notify_escalation_created = AsyncMock(return_value=True)
        mock_instance.notify_escalation_assigned = AsyncMock(return_value=True)
        mock_instance.notify_status_change = AsyncMock(return_value=True)
        mock_client.return_value = mock_instance
        yield mock_client


class MockUserInfo:
    """Mock UserInfo class for testing."""

    def __init__(self, user_id: int, role: str = "USER", **kwargs: object) -> None:
        """
        Initialize mock user with given attributes.

        Args:
            user_id: The user's ID.
            role: The user's role.
            **kwargs: Additional user attributes.

        """
        self.id = user_id
        self.email = kwargs.get("email", f"user{user_id}@test.com")
        self.role = role
        self.is_active = kwargs.get("is_active", True)
        self.is_verified = kwargs.get("is_verified", True)
        self.first_name = kwargs.get("first_name", "Test")
        self.last_name = kwargs.get("last_name", "User")
        self.employee_id = kwargs.get("employee_id")
        self.department = kwargs.get("department")
        self.position = kwargs.get("position")
        self.level = kwargs.get("level")
        self.telegram_id = kwargs.get("telegram_id")

    def has_role(self, roles: list[str]) -> bool:
        """Check if user has any of the specified roles."""
        return self.role in roles if self.role else False


def create_mock_escalation(
    escalation_id=1,
    user_id=100,
    status=EscalationStatus.PENDING,
    assigned_to=None,
    escalation_type=EscalationType.GENERAL,
):
    """Create a mock escalation request for testing using actual model attributes."""
    mock = MagicMock(spec=EscalationRequest)

    # Set all required attributes that Pydantic will validate
    mock.id = escalation_id
    mock.user_id = user_id
    mock.type = escalation_type
    mock.source = EscalationSource.MANUAL
    mock.reason = "Test reason"
    mock.context = {}
    mock.status = status
    mock.assigned_to = assigned_to
    mock.related_entity_type = None
    mock.related_entity_id = None
    mock.created_at = datetime.now(tz=UTC)
    mock.updated_at = None
    mock.resolved_at = None

    # Add model_config for Pydantic v2 compatibility with model_validate
    mock.model_config = {"from_attributes": True}

    return mock


def create_mock_uow():
    """Create a properly configured mock UoW."""
    mock_uow = MagicMock()
    mock_uow.escalations = MagicMock()
    mock_uow.escalations.get_by_id = AsyncMock()
    mock_uow.escalations.create = AsyncMock()
    mock_uow.escalations.update = AsyncMock()
    mock_uow.escalations.delete = AsyncMock()
    mock_uow.escalations.find_requests = AsyncMock()
    mock_uow.escalations.get_user_requests = AsyncMock()
    mock_uow.escalations.get_assigned_requests = AsyncMock()
    mock_uow.commit = AsyncMock()
    mock_uow.rollback = AsyncMock()
    return mock_uow


@pytest.fixture
def regular_user():
    """Create a regular user for testing."""
    return MockUserInfo(user_id=100, role="USER", email="user@example.com")


@pytest.fixture
def hr_user():
    """Create an HR user for testing."""
    return MockUserInfo(user_id=200, role="HR", email="hr@example.com")


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    return MockUserInfo(user_id=300, role="ADMIN", email="admin@example.com")


class TestGetEscalations:
    """Tests for GET /api/v1/escalations endpoint."""

    def test_get_escalations_regular_user(self, regular_user):
        """Regular users can only see their own escalation requests."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(user_id=regular_user.id)
        mock_uow.escalations.find_requests.return_value = ([mock_escalation], 1)

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["requests"]) == 1

        # Verify user_id filter was applied for regular user
        call_kwargs = mock_uow.escalations.find_requests.call_args.kwargs
        assert call_kwargs["user_id"] == regular_user.id

        app.dependency_overrides.clear()

    def test_get_escalations_regular_user_cannot_view_others(self, regular_user):
        """Regular users cannot view other users' escalation requests."""
        # Arrange
        mock_uow = create_mock_uow()

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act - try to view another user's escalations
        client = TestClient(app)
        response = client.get("/api/v1/escalations/?user_id=999")

        # Assert
        assert response.status_code == 403
        assert "Cannot view other users' requests" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_escalations_hr_can_view_all(self, hr_user):
        """HR users can view all escalation requests with filters."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(user_id=999, status=EscalationStatus.PENDING)
        mock_uow.escalations.find_requests.return_value = ([mock_escalation], 1)

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/?user_id=999&escalation_status=PENDING&type=GENERAL")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        # Verify filters were passed through for HR
        call_kwargs = mock_uow.escalations.find_requests.call_args.kwargs
        assert call_kwargs["user_id"] == 999
        assert call_kwargs["status"] == EscalationStatus.PENDING
        assert call_kwargs["escalation_type"] == EscalationType.GENERAL

        app.dependency_overrides.clear()

    def test_get_escalations_pagination(self, hr_user):
        """Test pagination parameters are passed correctly."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation()
        mock_uow.escalations.find_requests.return_value = ([mock_escalation], 100)

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/?skip=20&limit=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 3  # skip=20, limit=10 -> page 3
        assert data["size"] == 10
        assert data["pages"] == 10  # 100 total / 10 per page

        # Verify pagination params
        call_kwargs = mock_uow.escalations.find_requests.call_args.kwargs
        assert call_kwargs["skip"] == 20
        assert call_kwargs["limit"] == 10

        app.dependency_overrides.clear()

    def test_get_escalations_with_search(self, hr_user):
        """Search parameter is passed correctly."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation()
        mock_uow.escalations.find_requests.return_value = ([mock_escalation], 1)

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/?search=urgent")

        # Assert
        assert response.status_code == 200

        call_kwargs = mock_uow.escalations.find_requests.call_args.kwargs
        assert call_kwargs["search"] == "urgent"

        app.dependency_overrides.clear()


class TestCreateEscalation:
    """Tests for POST /api/v1/escalations endpoint."""

    def test_create_escalation_regular_user_own_request(self, regular_user):
        """Regular users can create escalation for themselves."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_created = create_mock_escalation(user_id=regular_user.id)
        mock_uow.escalations.create.return_value = mock_created

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        create_data = {
            "user_id": regular_user.id,
            "type": "GENERAL",
            "source": "MANUAL",
            "reason": "Need help with onboarding",
        }

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/", json=create_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == regular_user.id
        assert data["status"] == "PENDING"

        app.dependency_overrides.clear()

    def test_create_escalation_regular_user_cannot_create_for_others(self, regular_user):
        """Regular users cannot create escalations for other users."""
        # Arrange
        mock_uow = create_mock_uow()

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        create_data = {
            "user_id": 999,  # Different user
            "type": "GENERAL",
            "source": "MANUAL",
            "reason": "Need help",
        }

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/", json=create_data)

        # Assert
        assert response.status_code == 403
        assert "Cannot create requests for other users" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_create_escalation_hr_can_create_for_others(self, hr_user):
        """HR users can create escalations for other users."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_created = create_mock_escalation(user_id=999)
        mock_uow.escalations.create.return_value = mock_created

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        create_data = {
            "user_id": 999,  # Different user
            "type": "HR",
            "source": "MANUAL",
            "reason": "HR assistance needed",
        }

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/", json=create_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING"

        app.dependency_overrides.clear()

    def test_create_escalation_with_all_fields(self, regular_user):
        """Create escalation with all optional fields."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_created = create_mock_escalation(user_id=regular_user.id, escalation_type=EscalationType.IT)
        mock_uow.escalations.create.return_value = mock_created

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        create_data = {
            "user_id": regular_user.id,
            "type": "IT",
            "source": "AUTO_NO_ANSWER",
            "reason": "Technical issue",
            "context": {"device": "laptop", "issue": "screen"},
            "assigned_to": 200,
            "related_entity_type": "task",
            "related_entity_id": 42,
        }

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/", json=create_data)

        # Assert
        assert response.status_code == 200

        # Verify create was called
        mock_uow.escalations.create.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

        app.dependency_overrides.clear()


class TestGetEscalationById:
    """Tests for GET /api/v1/escalations/{id} endpoint."""

    def test_get_escalation_by_id_owner(self, regular_user):
        """User can get their own escalation."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(escalation_id=1, user_id=regular_user.id)
        mock_uow.escalations.get_by_id.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["user_id"] == regular_user.id

        app.dependency_overrides.clear()

    def test_get_escalation_by_id_assignee(self, regular_user):
        """Assignee can get the escalation they are assigned to."""
        # Arrange - regular_user is the assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(
            escalation_id=2, user_id=999, assigned_to=regular_user.id, status=EscalationStatus.ASSIGNED
        )
        mock_uow.escalations.get_by_id.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/2")

        # Assert
        assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_get_escalation_by_id_forbidden(self, regular_user):
        """User cannot get escalation they don't own or are not assigned to."""
        # Arrange - regular_user is neither owner nor assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(escalation_id=1, user_id=999, assigned_to=888)
        mock_uow.escalations.get_by_id.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/1")

        # Assert
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_escalation_by_id_hr_can_access_any(self, hr_user):
        """HR can access any escalation."""
        # Arrange - escalation owned by different user
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(escalation_id=1, user_id=999, assigned_to=888)
        mock_uow.escalations.get_by_id.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/1")

        # Assert
        assert response.status_code == 200

        app.dependency_overrides.clear()


class TestUpdateEscalation:
    """Tests for PATCH /api/v1/escalations/{id} endpoint."""

    def test_update_escalation_assignee(self, regular_user):
        """Assignee can update their escalation."""
        # Arrange - regular_user is the assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(
            escalation_id=2, assigned_to=regular_user.id, status=EscalationStatus.ASSIGNED
        )
        mock_uow.escalations.get_by_id.return_value = mock_escalation
        mock_uow.escalations.update.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        update_data = {
            "status": "IN_PROGRESS",
            "resolution_note": "Working on it",
        }

        # Act
        client = TestClient(app)
        response = client.patch("/api/v1/escalations/2", json=update_data)

        # Assert
        assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_update_escalation_hr_can_update_any(self, hr_user):
        """HR can update any escalation."""
        # Arrange - hr_user is not the assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(escalation_id=2, assigned_to=999, status=EscalationStatus.ASSIGNED)
        mock_uow.escalations.get_by_id.return_value = mock_escalation
        mock_uow.escalations.update.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        update_data = {
            "assigned_to": 300,
            "status": "ASSIGNED",
        }

        # Act
        client = TestClient(app)
        response = client.patch("/api/v1/escalations/2", json=update_data)

        # Assert
        assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_update_escalation_forbidden(self, regular_user):
        """Non-assignee, non-HR cannot update escalation."""
        # Arrange - regular_user is not the assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(escalation_id=2, assigned_to=999, user_id=888)
        mock_uow.escalations.get_by_id.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        update_data = {
            "status": "RESOLVED",
        }

        # Act
        client = TestClient(app)
        response = client.patch("/api/v1/escalations/2", json=update_data)

        # Assert
        assert response.status_code == 403
        assert "Only assignee or HR can update" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_update_escalation_not_found(self, hr_user):
        """Update non-existent escalation returns 404."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_uow.escalations.get_by_id.return_value = None

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        update_data = {
            "status": "RESOLVED",
        }

        # Act
        client = TestClient(app)
        response = client.patch("/api/v1/escalations/999", json=update_data)

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

        app.dependency_overrides.clear()


class TestAssignEscalation:
    """Tests for POST /api/v1/escalations/{id}/assign/{assignee_id} endpoint."""

    def test_assign_escalation_hr_only(self, hr_user):
        """Only HR/Admin can assign escalations."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(escalation_id=1, status=EscalationStatus.PENDING)
        mock_uow.escalations.get_by_id.return_value = mock_escalation
        mock_uow.escalations.update.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/1/assign/300")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_to"] == 300
        assert data["status"] == "ASSIGNED"

        app.dependency_overrides.clear()

    def test_assign_escalation_not_found(self, hr_user):
        """Assign non-existent escalation returns 404."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_uow.escalations.get_by_id.return_value = None

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/999/assign/300")

        # Assert
        assert response.status_code == 404

        app.dependency_overrides.clear()


class TestResolveEscalation:
    """Tests for POST /api/v1/escalations/{id}/resolve endpoint."""

    def test_resolve_escalation_assignee(self, regular_user):
        """Assignee can resolve their assigned escalation."""
        # Arrange - regular_user is the assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(
            escalation_id=2, assigned_to=regular_user.id, status=EscalationStatus.ASSIGNED
        )
        mock_uow.escalations.get_by_id.return_value = mock_escalation
        mock_uow.escalations.update.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/2/resolve")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "RESOLVED"

        app.dependency_overrides.clear()

    def test_resolve_escalation_hr_can_resolve_any(self, hr_user):
        """HR can resolve any escalation."""
        # Arrange - hr_user is not the assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(escalation_id=2, assigned_to=999, status=EscalationStatus.ASSIGNED)
        mock_uow.escalations.get_by_id.return_value = mock_escalation
        mock_uow.escalations.update.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/2/resolve")

        # Assert
        assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_resolve_escalation_forbidden(self, regular_user):
        """Non-assignee, non-HR cannot resolve escalation."""
        # Arrange - regular_user is not the assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(escalation_id=2, assigned_to=999, user_id=888)
        mock_uow.escalations.get_by_id.return_value = mock_escalation

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.post("/api/v1/escalations/2/resolve")

        # Assert
        assert response.status_code == 403
        assert "Only assignee or HR can resolve" in response.json()["detail"]

        app.dependency_overrides.clear()


class TestGetUserEscalations:
    """Tests for GET /api/v1/escalations/user/{user_id} endpoint."""

    def test_get_user_escalations_own(self, regular_user):
        """User can get their own escalations."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(user_id=regular_user.id)
        mock_uow.escalations.find_requests.return_value = ([mock_escalation], 1)

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get(f"/api/v1/escalations/user/{regular_user.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        app.dependency_overrides.clear()

    def test_get_user_escalations_forbidden(self, regular_user):
        """User cannot get other users' escalations."""
        # Arrange
        mock_uow = create_mock_uow()

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/user/999")

        # Assert
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_user_escalations_hr_can_access_any(self, hr_user):
        """HR can get any user's escalations."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(user_id=999)
        mock_uow.escalations.find_requests.return_value = ([mock_escalation], 1)

        app.dependency_overrides[get_current_active_user] = lambda: hr_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/user/999")

        # Assert
        assert response.status_code == 200

        app.dependency_overrides.clear()


class TestGetMyAssignedEscalations:
    """Tests for GET /api/v1/escalations/assigned-to-me endpoint."""

    def test_get_my_assigned_escalations(self, regular_user):
        """Get escalations assigned to current user."""
        # Arrange - regular_user is the assignee
        mock_uow = create_mock_uow()
        mock_escalation = create_mock_escalation(assigned_to=regular_user.id)
        mock_uow.escalations.find_requests.return_value = ([mock_escalation], 1)

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/assigned-to-me")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Verify correct filter was applied
        call_kwargs = mock_uow.escalations.find_requests.call_args.kwargs
        assert call_kwargs["assigned_to"] == regular_user.id

        app.dependency_overrides.clear()

    def test_get_my_assigned_pagination(self, regular_user):
        """Test pagination for assigned escalations."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_escalations = [create_mock_escalation(escalation_id=i, assigned_to=regular_user.id) for i in range(1, 6)]
        mock_uow.escalations.find_requests.return_value = (mock_escalations, 10)

        app.dependency_overrides[get_current_active_user] = lambda: regular_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.get("/api/v1/escalations/assigned-to-me?skip=5&limit=5")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        call_kwargs = mock_uow.escalations.find_requests.call_args.kwargs
        assert call_kwargs["skip"] == 5
        assert call_kwargs["limit"] == 5

        app.dependency_overrides.clear()


class TestDeleteEscalation:
    """Tests for DELETE /api/v1/escalations/{id} endpoint."""

    def test_delete_escalation_admin_only(self, admin_user):
        """Only admin can delete escalations."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_uow.escalations.delete.return_value = True

        app.dependency_overrides[get_current_active_user] = lambda: admin_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.delete("/api/v1/escalations/1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

        mock_uow.escalations.delete.assert_awaited_once_with(1)
        mock_uow.commit.assert_awaited_once()

        app.dependency_overrides.clear()

    def test_delete_escalation_not_found(self, admin_user):
        """Delete non-existent escalation returns 404."""
        # Arrange
        mock_uow = create_mock_uow()
        mock_uow.escalations.delete.return_value = False

        app.dependency_overrides[get_current_active_user] = lambda: admin_user
        app.dependency_overrides[get_uow] = lambda: mock_uow
        app.dependency_overrides[get_escalation_service] = lambda: EscalationService(mock_uow)

        # Act
        client = TestClient(app)
        response = client.delete("/api/v1/escalations/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

        app.dependency_overrides.clear()


class TestRootEndpoints:
    """Tests for root and health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns service status."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        # Mock engine.connect() for the health check test
        with patch("escalation_service.main.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()

            class AsyncContextMock:
                async def __aenter__(self):
                    return mock_conn

                async def __aexit__(self, *args):
                    return False

            mock_engine.connect = MagicMock(return_value=AsyncContextMock())

            client = TestClient(app)
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "escalation"
        assert "timestamp" in data
        assert "dependencies" in data
