"""Pytest configuration for escalation_service tests."""

import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# Clear proxy environment variables to prevent httpx errors with unsupported socks:// scheme
for proxy_var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"]:
    os.environ.pop(proxy_var, None)

# Set required environment variables BEFORE any app imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_escalation_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/4")
os.environ.setdefault("SERVICE_API_KEY", "test_service_api_key")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")

# Now we can import from the service
from escalation_service.api.deps import UserInfo, get_current_active_user, get_uow
from escalation_service.core.enums import EscalationSource, EscalationStatus, EscalationType
from escalation_service.main import app
from escalation_service.models import EscalationRequest
from escalation_service.repositories.unit_of_work import IUnitOfWork
from escalation_service.services.escalation import EscalationService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Coroutine


@pytest.fixture
def mock_uow() -> MagicMock:
    """Create a mock Unit of Work for service layer testing."""
    uow = MagicMock(spec=IUnitOfWork)

    # Make escalations repository methods async mocks
    uow.escalations = MagicMock()
    uow.escalations.get_by_id = AsyncMock()
    uow.escalations.get_all = AsyncMock()
    uow.escalations.create = AsyncMock()
    uow.escalations.update = AsyncMock()
    uow.escalations.delete = AsyncMock()
    uow.escalations.find_requests = AsyncMock()

    # Make UoW methods async mocks
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()

    return uow


@pytest.fixture
def escalation_service(mock_uow: MagicMock) -> EscalationService:
    """Create an EscalationService with mock UoW."""
    return EscalationService(mock_uow)


@pytest.fixture
def sample_escalation_request() -> EscalationRequest:
    """Create a sample escalation request for testing."""
    return EscalationRequest(
        id=1,
        user_id=100,
        type=EscalationType.GENERAL,
        source=EscalationSource.MANUAL,
        reason="Test escalation reason",
        context={},
        status=EscalationStatus.PENDING,
        assigned_to=None,
        related_entity_type=None,
        related_entity_id=None,
    )


@pytest.fixture
def sample_assigned_request() -> EscalationRequest:
    """Create a sample assigned escalation request for testing."""
    return EscalationRequest(
        id=2,
        user_id=100,
        type=EscalationType.HR,
        source=EscalationSource.MANUAL,
        reason="HR issue",
        context={},
        status=EscalationStatus.ASSIGNED,
        assigned_to=200,
        related_entity_type=None,
        related_entity_id=None,
    )


@pytest.fixture
def sample_resolved_request() -> EscalationRequest:
    """Create a sample resolved escalation request for testing."""
    return EscalationRequest(
        id=3,
        user_id=100,
        type=EscalationType.IT,
        source=EscalationSource.MANUAL,
        reason="IT issue resolved",
        context={},
        status=EscalationStatus.RESOLVED,
        assigned_to=200,
        related_entity_type=None,
        related_entity_id=None,
        resolved_at=datetime.now(tz=UTC),
    )


# User fixtures for API testing
@pytest.fixture
def regular_user() -> UserInfo:
    """Create a regular user for testing."""
    return UserInfo({
        "id": 100,
        "email": "user@example.com",
        "role": "USER",
        "is_active": True,
        "is_verified": True,
        "first_name": "Test",
        "last_name": "User",
    })


@pytest.fixture
def hr_user() -> UserInfo:
    """Create an HR user for testing."""
    return UserInfo({
        "id": 200,
        "email": "hr@example.com",
        "role": "HR",
        "is_active": True,
        "is_verified": True,
        "first_name": "HR",
        "last_name": "Manager",
    })


@pytest.fixture
def admin_user() -> UserInfo:
    """Create an admin user for testing."""
    return UserInfo({
        "id": 300,
        "email": "admin@example.com",
        "role": "ADMIN",
        "is_active": True,
        "is_verified": True,
        "first_name": "Admin",
        "last_name": "User",
    })


@pytest.fixture
def mock_current_user(regular_user: UserInfo) -> Callable[[], Coroutine[Any, Any, UserInfo]]:
    """Override get_current_active_user to return regular user."""
    async def _get_current_user() -> UserInfo:
        return regular_user
    return _get_current_user


@pytest.fixture
def mock_current_hr(hr_user: UserInfo) -> Callable[[], Coroutine[Any, Any, UserInfo]]:
    """Override get_current_active_user to return HR user."""
    async def _get_current_user() -> UserInfo:
        return hr_user
    return _get_current_user


@pytest.fixture
def mock_current_admin(admin_user: UserInfo) -> Callable[[], Coroutine[Any, Any, UserInfo]]:
    """Override get_current_active_user to return admin user."""
    async def _get_current_user() -> UserInfo:
        return admin_user
    return _get_current_user


@pytest.fixture
def mock_uow_dependency(mock_uow: MagicMock) -> Callable[[], Coroutine[Any, Any, MagicMock]]:
    """Override get_uow to return mock UoW."""
    async def _get_mock_uow() -> MagicMock:
        return mock_uow
    return _get_mock_uow


@pytest.fixture
async def async_client_with_user(regular_user: UserInfo, mock_uow: MagicMock) -> AsyncGenerator[AsyncClient]:
    """Create an async client with regular user authenticated and mock UoW."""
    async def override_get_user() -> UserInfo:
        return regular_user

    async def override_get_uow() -> MagicMock:
        return mock_uow

    app.dependency_overrides[get_current_active_user] = override_get_user
    app.dependency_overrides[get_uow] = override_get_uow

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def async_client_with_hr(hr_user: UserInfo, mock_uow: MagicMock) -> AsyncGenerator[AsyncClient]:
    """Create an async client with HR user authenticated and mock UoW."""
    async def override_get_user() -> UserInfo:
        return hr_user

    async def override_get_uow() -> MagicMock:
        return mock_uow

    app.dependency_overrides[get_current_active_user] = override_get_user
    app.dependency_overrides[get_uow] = override_get_uow

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def async_client_with_admin(admin_user: UserInfo, mock_uow: MagicMock) -> AsyncGenerator[AsyncClient]:
    """Create an async client with admin user authenticated and mock UoW."""
    async def override_get_user() -> UserInfo:
        return admin_user

    async def override_get_uow() -> MagicMock:
        return mock_uow

    app.dependency_overrides[get_current_active_user] = override_get_user
    app.dependency_overrides[get_uow] = override_get_uow

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI TestClient with mocked database for health checks."""
    with (
        patch("escalation_service.database.engine") as mock_engine,
    ):
        # Mock the database connection for health checks
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()

        # Create a proper async context manager mock for engine.connect()
        class AsyncContextMock:
            async def __aenter__(self):
                return mock_conn
            async def __aexit__(self, *args):
                return False

        mock_engine.connect = MagicMock(return_value=AsyncContextMock())

        # Import app AFTER patching engine to ensure patched engine is used
        with patch.dict("sys.modules"):
            # Force reimport of main module to use patched engine
            import sys
            # Remove cached modules to force reimport
            mods_to_remove = [k for k in sys.modules if "escalation_service" in k]
            for m in mods_to_remove:
                del sys.modules[m]

            from escalation_service.main import app

            return TestClient(app)
