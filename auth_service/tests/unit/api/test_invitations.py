"""Unit tests for invitations API endpoints."""

from datetime import UTC, datetime, timedelta
from typing import get_args
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from auth_service.api import deps
from auth_service.api.deps import HRUser
from auth_service.core.enums import InvitationStatus, UserRole
from auth_service.core.security import create_access_token
from auth_service.main import app
from auth_service.models import Invitation, User

# Get the actual HRUser dependency callable used by FastAPI
# So get_args returns (User, Depends(...)) and the Depends is at index 1
_hr_user_dependency = get_args(HRUser)[1].dependency


def create_auth_headers(user_id: int = 1, role: UserRole = UserRole.HR) -> dict:
    """Create authorization headers with JWT token."""
    token = create_access_token({"sub": str(user_id), "user_id": user_id, "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def hr_user():
    """Create an HR user."""
    return User(
        id=1,
        email="hr@example.com",
        first_name="HR",
        last_name="User",
        employee_id="EMP001",
        is_active=True,
        is_verified=True,
        role=UserRole.HR,
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User(
        id=2,
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        employee_id="EMP002",
        is_active=True,
        is_verified=True,
        role=UserRole.ADMIN,
    )


@pytest.fixture
def mock_invitation_service():
    """Create a mock invitation service."""
    return MagicMock()


@pytest.fixture
def sample_invitation():
    """Create a sample invitation."""
    return Invitation(
        id=1,
        token="invite-token-123",
        email="invited@example.com",
        employee_id="EMP003",
        first_name="Invited",
        last_name="User",
        department_id=1,
        position="Developer",
        role=UserRole.NEWBIE,
        mentor_id=None,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        status=InvitationStatus.PENDING,
        created_at=datetime.now(UTC),
    )


class TestGetInvitations:
    """Tests for GET /api/v1/invitations/ endpoint."""

    def test_get_invitations_success(self, hr_user, mock_uow, sample_invitation):
        """Test getting list of invitations as HR."""
        # Configure UOW mocks to return proper tuples
        mock_uow.invitations.find_invitations = AsyncMock(return_value=([sample_invitation], 1))
        mock_uow.invitations.get_statistics = AsyncMock(return_value={
            "total": 1, "pending": 1, "used": 0, "revoked": 0, "expired": 0,
            "conversion_rate": 0.0, "by_status": {}, "recent_activity": []
        })

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["invitations"]) == 1
        assert data["invitations"][0]["email"] == "invited@example.com"

    def test_get_invitations_with_email_filter(self, hr_user, mock_uow, sample_invitation):
        """Test getting invitations with email filter."""
        mock_uow.invitations.find_invitations = AsyncMock(return_value=([sample_invitation], 1))
        mock_uow.invitations.get_statistics = AsyncMock(return_value={
            "total": 1, "pending": 1, "used": 0, "revoked": 0, "expired": 0,
            "conversion_rate": 0.0, "by_status": {}, "recent_activity": []
        })

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/?email=invited@example.com",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200
        call_kwargs = mock_uow.invitations.find_invitations.call_args.kwargs
        assert call_kwargs.get("email") == "invited@example.com"

    def test_get_invitations_with_status_filter(self, hr_user, mock_uow, sample_invitation):
        """Test getting invitations with status filter."""
        mock_uow.invitations.find_invitations = AsyncMock(return_value=([sample_invitation], 1))
        mock_uow.invitations.get_statistics = AsyncMock(return_value={
            "total": 1, "pending": 1, "used": 0, "revoked": 0, "expired": 0,
            "conversion_rate": 0.0, "by_status": {}, "recent_activity": []
        })

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/?status=PENDING",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200
        call_kwargs = mock_uow.invitations.find_invitations.call_args.kwargs
        assert call_kwargs.get("status") == InvitationStatus.PENDING


class TestCreateInvitation:
    """Tests for POST /api/v1/invitations/ endpoint."""

    def test_create_invitation_success(self, hr_user, mock_uow, sample_invitation):
        """Test creating a new invitation."""
        mock_uow.invitations.create = AsyncMock(return_value=sample_invitation)
        mock_uow.invitations.exists_pending_for_email = AsyncMock(return_value=False)
        # Mock that no user exists with this email or employee_id
        mock_uow.users.get_by_email = AsyncMock(return_value=None)
        mock_uow.users.get_by_employee_id = AsyncMock(return_value=None)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
                json={
                    "email": "new@example.com",
                    "employee_id": "EMP004",
                    "first_name": "New",
                    "last_name": "User",
                    "department_id": 1,
                    "position": "Developer",
                    "role": "NEWBIE",
                    "expires_in_days": 7,
                },
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "invited@example.com"
        assert data["token"] == "invite-token-123"

    def test_create_invitation_conflict(self, hr_user, mock_uow):
        """Test creating invitation with duplicate email returns 409."""
        mock_uow.invitations.exists_pending_for_email = AsyncMock(return_value=True)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
                json={
                    "email": "duplicate@example.com",
                    "employee_id": "EMP005",
                    "first_name": "Duplicate",
                },
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 409


class TestGetInvitationById:
    """Tests for GET /api/v1/invitations/{invitation_id} endpoint."""

    def test_get_invitation_by_id_success(self, hr_user, mock_uow, sample_invitation):
        """Test getting invitation by ID."""
        mock_uow.invitations.get_by_id = AsyncMock(return_value=sample_invitation)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/1",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "invited@example.com"

    def test_get_invitation_by_id_not_found(self, hr_user, mock_uow):
        """Test getting non-existent invitation returns 404."""
        mock_uow.invitations.get_by_id = AsyncMock(return_value=None)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/999",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 404


class TestGetInvitationByToken:
    """Tests for GET /api/v1/invitations/token/{token} endpoint."""

    def test_get_invitation_by_token_success(self, mock_uow, sample_invitation):
        """Test getting valid invitation by token (public endpoint)."""
        mock_uow.invitations.get_valid_by_token = AsyncMock(return_value=sample_invitation)

        with TestClient(app) as client:
            response = client.get("/api/v1/invitations/token/invite-token-123")

        assert response.status_code == 200
        data = response.json()
        assert data["token"] == "invite-token-123"

    def test_get_invitation_by_token_invalid(self, mock_uow):
        """Test getting invalid/expired invitation returns 404."""
        mock_uow.invitations.get_valid_by_token = AsyncMock(return_value=None)

        with TestClient(app) as client:
            response = client.get("/api/v1/invitations/token/invalid-token")

        assert response.status_code == 404


class TestResendInvitation:
    """Tests for POST /api/v1/invitations/{invitation_id}/resend endpoint."""

    def test_resend_invitation_success(self, hr_user, mock_uow, sample_invitation):
        """Test resending an invitation."""
        from datetime import UTC
        new_invitation = Invitation(
            id=sample_invitation.id,
            token="new-token-456",  # New token
            email=sample_invitation.email,
            employee_id=sample_invitation.employee_id,
            first_name=sample_invitation.first_name,
            last_name=sample_invitation.last_name,
            expires_at=datetime.now(UTC) + timedelta(days=7),
            status=InvitationStatus.PENDING,
            created_at=sample_invitation.created_at,
        )
        # Simulate resend by returning the original invitation (update will modify it)
        mock_uow.invitations.get_by_id = AsyncMock(return_value=sample_invitation)
        mock_uow.invitations.update = AsyncMock(return_value=new_invitation)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/1/resend",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200

    def test_resend_non_pending_invitation(self, hr_user, mock_uow):
        """Test resending non-pending invitation returns 400."""
        from datetime import UTC
        # Create a non-pending invitation
        used_invitation = Invitation(
            id=1,
            token="used-token",
            email="used@example.com",
            employee_id="EMP001",
            first_name="Used",
            last_name="Invitation",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            status=InvitationStatus.USED,  # Not PENDING
            created_at=datetime.now(UTC),
        )
        mock_uow.invitations.get_by_id = AsyncMock(return_value=used_invitation)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/1/resend",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 400


class TestRevokeInvitation:
    """Tests for POST /api/v1/invitations/{invitation_id}/revoke endpoint."""

    def test_revoke_invitation_success(self, hr_user, mock_uow, sample_invitation):
        """Test revoking an invitation."""
        # Set up the mock to return the pending invitation
        mock_uow.invitations.get_by_id = AsyncMock(return_value=sample_invitation)
        # Update will modify the invitation in place and return it
        mock_uow.invitations.update = AsyncMock(return_value=sample_invitation)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/1/revoke",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REVOKED"

    def test_revoke_invitation_not_found(self, hr_user, mock_uow):
        """Test revoking non-existent invitation returns 400 (covers lines 173-174)."""
        from auth_service.core import NotFoundException
        from auth_service.services import InvitationService

        # Create a mock invitation service that raises NotFoundException
        mock_service = MagicMock(spec=InvitationService)
        mock_service.revoke_invitation = AsyncMock(
            side_effect=NotFoundException("Invitation not found")
        )

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_invitation_service():
            return mock_service

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = mock_get_invitation_service

        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/invitations/999/revoke",
                    headers=create_auth_headers(hr_user.id, hr_user.role),
                )

            assert response.status_code == 400
            assert "not found" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(_hr_user_dependency, None)
            app.dependency_overrides.pop(deps.get_invitation_service, None)

    def test_revoke_invitation_validation_error(self, hr_user, mock_uow):
        """Test revoking already used invitation returns 400 (covers lines 173-174)."""
        from auth_service.core import ValidationException
        from auth_service.services import InvitationService

        # Create a mock invitation service that raises ValidationException
        mock_service = MagicMock(spec=InvitationService)
        mock_service.revoke_invitation = AsyncMock(
            side_effect=ValidationException("Cannot revoke used invitation")
        )

        async def mock_require_hr() -> User:
            return hr_user

        async def mock_get_invitation_service():
            return mock_service

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = mock_get_invitation_service

        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/invitations/1/revoke",
                    headers=create_auth_headers(hr_user.id, hr_user.role),
                )

            assert response.status_code == 400
            assert "cannot revoke" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(_hr_user_dependency, None)
            app.dependency_overrides.pop(deps.get_invitation_service, None)


class TestGetInvitationStats:
    """Tests for GET /api/v1/invitations/stats/summary endpoint."""

    def test_get_invitation_stats_success(self, hr_user, mock_uow):
        """Test getting invitation statistics."""
        stats = {
            "total": 10,
            "pending": 5,
            "used": 3,
            "revoked": 1,
            "expired": 1,
            "conversion_rate": 30.0,
            "by_status": {"PENDING": 5, "USED": 3, "REVOKED": 1},
            "recent_activity": [],
        }
        mock_uow.invitations.get_statistics = AsyncMock(return_value=stats)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/stats/summary",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10
        assert data["conversion_rate"] == 30.0


class TestDeleteInvitation:
    """Tests for DELETE /api/v1/invitations/{invitation_id} endpoint."""

    def test_delete_invitation_success(self, hr_user, mock_uow):
        """Test deleting an invitation."""
        mock_uow.invitations.delete = AsyncMock(return_value=True)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.delete(
                "/api/v1/invitations/1",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    def test_delete_invitation_not_found(self, hr_user, mock_uow):
        """Test deleting non-existent invitation returns 404."""
        # First get_by_id is called, if it returns None, we get 404
        mock_uow.invitations.get_by_id = AsyncMock(return_value=None)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr

        with TestClient(app) as client:
            response = client.delete(
                "/api/v1/invitations/999",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)

        assert response.status_code == 404
