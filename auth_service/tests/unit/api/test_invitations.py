"""Unit tests for invitations API endpoints."""

from datetime import UTC, datetime, timedelta
from typing import get_args
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from auth_service.api import deps
from auth_service.api.deps import HRUser
from auth_service.core.enums import InvitationStatus, UserRole
from auth_service.core.security import create_access_token
from auth_service.main import app
from auth_service.models import Invitation, User
from fastapi.testclient import TestClient

# Get the actual HRUser dependency callable used by FastAPI
# So get_args returns (User, Depends(...)) and the Depends is at index 1
_hr_user_dependency = get_args(HRUser)[1].dependency


@pytest.fixture
def mock_invitation_service():
    """Create a mock invitation service."""
    return MagicMock()


@pytest.fixture(autouse=True)
def mock_lifespan_db_operations():
    """Patch DB operations during app lifespan to avoid connection errors."""
    with patch("auth_service.main.init_db"), patch("auth_service.main.create_default_admin_user"):
        yield


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
        level=None,
        role=UserRole.NEWBIE,
        mentor_id=None,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        status=InvitationStatus.PENDING,
        created_at=datetime.now(UTC),
        used_at=None,
        user_id=None,
    )


class TestGetInvitations:
    """Tests for GET /api/v1/invitations/ endpoint."""

    def test_get_invitations_success(self, hr_user, mock_invitation_service, sample_invitation):
        """Test getting list of invitations as HR."""
        mock_invitation_service.get_invitations = AsyncMock(return_value=([sample_invitation], 1))
        mock_invitation_service.get_invitation_stats = AsyncMock(
            return_value={
                "total": 1,
                "pending": 1,
                "used": 0,
                "revoked": 0,
                "expired": 0,
                "conversion_rate": 0.0,
                "by_status": {},
                "recent_activity": [],
            }
        )
        mock_invitation_service.generate_invitation_url = MagicMock(
            return_value="https://t.me/bot?start=invite-token-123"
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["invitations"]) == 1
        assert data["invitations"][0]["email"] == "invited@example.com"

    def test_get_invitations_with_email_filter(self, hr_user, mock_invitation_service, sample_invitation):
        """Test getting invitations with email filter."""
        mock_invitation_service.get_invitations = AsyncMock(return_value=([sample_invitation], 1))
        mock_invitation_service.get_invitation_stats = AsyncMock(
            return_value={
                "total": 1,
                "pending": 1,
                "used": 0,
                "revoked": 0,
                "expired": 0,
                "conversion_rate": 0.0,
                "by_status": {},
                "recent_activity": [],
            }
        )
        mock_invitation_service.generate_invitation_url = MagicMock(
            return_value="https://t.me/bot?start=invite-token-123"
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/?email=invited@example.com",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200

    def test_get_invitations_with_status_filter(self, hr_user, mock_invitation_service, sample_invitation):
        """Test getting invitations with status filter."""
        mock_invitation_service.get_invitations = AsyncMock(return_value=([sample_invitation], 1))
        mock_invitation_service.get_invitation_stats = AsyncMock(
            return_value={
                "total": 1,
                "pending": 1,
                "used": 0,
                "revoked": 0,
                "expired": 0,
                "conversion_rate": 0.0,
                "by_status": {},
                "recent_activity": [],
            }
        )
        mock_invitation_service.generate_invitation_url = MagicMock(
            return_value="https://t.me/bot?start=invite-token-123"
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/?status=PENDING",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200


class TestCreateInvitation:
    """Tests for POST /api/v1/invitations/ endpoint."""

    def test_create_invitation_success(self, hr_user, mock_invitation_service, sample_invitation):
        """Test creating a new invitation."""
        mock_invitation_service.create_invitation = AsyncMock(return_value=sample_invitation)
        mock_invitation_service.generate_invitation_url = MagicMock(
            return_value="https://t.me/bot?start=invite-token-123"
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

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
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "invited@example.com"
        assert data["token"] == "invite-token-123"

    def test_create_invitation_conflict(self, hr_user, mock_invitation_service):
        """Test creating invitation with duplicate email returns 409."""
        from auth_service.core import ConflictException

        mock_invitation_service.create_invitation = AsyncMock(
            side_effect=ConflictException("Invitation already exists")
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

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
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 409


class TestGetInvitationById:
    """Tests for GET /api/v1/invitations/{invitation_id} endpoint."""

    def test_get_invitation_by_id_success(self, hr_user, mock_invitation_service, sample_invitation):
        """Test getting invitation by ID."""
        mock_invitation_service.get_invitation_by_id = AsyncMock(return_value=sample_invitation)
        mock_invitation_service.generate_invitation_url = MagicMock(
            return_value="https://t.me/bot?start=invite-token-123"
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/1",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "invited@example.com"

    def test_get_invitation_by_id_not_found(self, hr_user, mock_invitation_service):
        """Test getting non-existent invitation returns 404."""
        from auth_service.core import NotFoundException

        mock_invitation_service.get_invitation_by_id = AsyncMock(side_effect=NotFoundException("Invitation not found"))

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/999",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 404


class TestGetInvitationByToken:
    """Tests for GET /api/v1/invitations/token/{token} endpoint."""

    def test_get_invitation_by_token_success(self, mock_invitation_service, sample_invitation):
        """Test getting valid invitation by token (public endpoint)."""
        mock_invitation_service.get_valid_invitation = AsyncMock(return_value=sample_invitation)
        mock_invitation_service.generate_invitation_url = MagicMock(
            return_value="https://t.me/bot?start=invite-token-123"
        )
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/invitations/token/invite-token-123")

            assert response.status_code == 200
            data = response.json()
            assert data["token"] == "invite-token-123"
        finally:
            app.dependency_overrides.pop(deps.get_invitation_service, None)

    def test_get_invitation_by_token_invalid(self, mock_invitation_service):
        """Test getting invalid/expired invitation returns 404."""
        from auth_service.core import NotFoundException

        mock_invitation_service.get_valid_invitation = AsyncMock(side_effect=NotFoundException("Invalid token"))
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/invitations/token/invalid-token")

            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(deps.get_invitation_service, None)


class TestResendInvitation:
    """Tests for POST /api/v1/invitations/{invitation_id}/resend endpoint."""

    def test_resend_invitation_success(self, hr_user, mock_invitation_service, sample_invitation):
        """Test resending an invitation."""
        new_invitation = Invitation(
            id=sample_invitation.id,
            token="new-token-456",
            email=sample_invitation.email,
            employee_id=sample_invitation.employee_id,
            first_name=sample_invitation.first_name,
            last_name=sample_invitation.last_name,
            department_id=sample_invitation.department_id,
            position=sample_invitation.position,
            level=sample_invitation.level,
            role=sample_invitation.role,
            mentor_id=sample_invitation.mentor_id,
            expires_at=datetime.now(UTC) + timedelta(days=7),
            status=InvitationStatus.PENDING,
            created_at=sample_invitation.created_at,
            used_at=sample_invitation.used_at,
            user_id=sample_invitation.user_id,
        )
        mock_invitation_service.resend_invitation = AsyncMock(return_value=new_invitation)
        mock_invitation_service.generate_invitation_url = MagicMock(return_value="https://t.me/bot?start=new-token-456")

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/1/resend",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200

    def test_resend_non_pending_invitation(self, hr_user, mock_invitation_service):
        """Test resending non-pending invitation returns 400."""
        from auth_service.core import ValidationException

        mock_invitation_service.resend_invitation = AsyncMock(
            side_effect=ValidationException("Cannot resend non-pending invitation")
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/1/resend",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 400


class TestRevokeInvitation:
    """Tests for POST /api/v1/invitations/{invitation_id}/revoke endpoint."""

    def test_revoke_invitation_success(self, hr_user, mock_invitation_service, sample_invitation):
        """Test revoking an invitation."""
        sample_invitation.status = InvitationStatus.REVOKED
        mock_invitation_service.revoke_invitation = AsyncMock(return_value=sample_invitation)
        mock_invitation_service.generate_invitation_url = MagicMock(
            return_value="https://t.me/bot?start=invite-token-123"
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/1/revoke",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REVOKED"

    def test_revoke_invitation_not_found(self, hr_user, mock_invitation_service):
        """Test revoking non-existent invitation returns 400."""
        from auth_service.core import NotFoundException

        mock_invitation_service.revoke_invitation = AsyncMock(side_effect=NotFoundException("Invitation not found"))

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/999/revoke",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_revoke_invitation_validation_error(self, hr_user, mock_invitation_service):
        """Test revoking already used invitation returns 400."""
        from auth_service.core import ValidationException

        mock_invitation_service.revoke_invitation = AsyncMock(
            side_effect=ValidationException("Cannot revoke used invitation")
        )

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/invitations/1/revoke",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 400
        assert "cannot revoke" in response.json()["detail"].lower()


class TestGetInvitationStats:
    """Tests for GET /api/v1/invitations/stats/summary endpoint."""

    def test_get_invitation_stats_success(self, hr_user, mock_invitation_service):
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
        mock_invitation_service.get_invitation_stats = AsyncMock(return_value=stats)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/invitations/stats/summary",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10
        assert data["conversion_rate"] == 30.0


class TestDeleteInvitation:
    """Tests for DELETE /api/v1/invitations/{invitation_id} endpoint."""

    def test_delete_invitation_success(self, hr_user, mock_invitation_service):
        """Test deleting an invitation."""
        mock_invitation_service.delete_invitation = AsyncMock(return_value=True)

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.delete(
                "/api/v1/invitations/1",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    def test_delete_invitation_not_found(self, hr_user, mock_invitation_service):
        """Test deleting non-existent invitation returns 404."""
        from auth_service.core import NotFoundException

        mock_invitation_service.delete_invitation = AsyncMock(side_effect=NotFoundException("Invitation not found"))

        async def mock_require_hr() -> User:
            return hr_user

        app.dependency_overrides[_hr_user_dependency] = mock_require_hr
        app.dependency_overrides[deps.get_invitation_service] = lambda: mock_invitation_service

        with TestClient(app) as client:
            response = client.delete(
                "/api/v1/invitations/999",
                headers=create_auth_headers(hr_user.id, hr_user.role),
            )

        app.dependency_overrides.pop(_hr_user_dependency, None)
        app.dependency_overrides.pop(deps.get_invitation_service, None)

        assert response.status_code == 404
