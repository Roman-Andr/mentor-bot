"""Pytest configuration and shared fixtures for auth_service tests."""

import os

# Clear proxy environment variables to prevent httpx errors with unsupported socks:// scheme
for proxy_var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"]:
    os.environ.pop(proxy_var, None)

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Set required environment variables BEFORE any app imports
# because config.py reads settings at import time
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only-123456")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-unit-tests-only-12345")
os.environ.setdefault("SERVICE_API_KEY", "test-service-api-key")

import pytest

from auth_service.repositories.unit_of_work import IUnitOfWork


# Import services for type hints and fixtures
@pytest.fixture
def mock_auth_service():
    """Create a mock AuthService for dependency injection testing."""
    from auth_service.services import AuthService
    return MagicMock(spec=AuthService)


@pytest.fixture
def mock_user_service():
    """Create a mock UserService for dependency injection testing."""
    from auth_service.services import UserService
    return MagicMock(spec=UserService)


@pytest.fixture
def mock_invitation_service():
    """Create a mock InvitationService for dependency injection testing."""
    from auth_service.services import InvitationService
    return MagicMock(spec=InvitationService)


@pytest.fixture
def mock_department_service():
    """Create a mock DepartmentService for dependency injection testing."""
    from auth_service.services import DepartmentService
    return MagicMock(spec=DepartmentService)


@pytest.fixture
def mock_uow():
    """Create a mock IUnitOfWork with AsyncMock repositories."""
    uow = MagicMock(spec=IUnitOfWork)

    # Mock the repositories with AsyncMock methods
    uow.users = MagicMock()
    uow.users.get_by_email = AsyncMock()
    uow.users.get_by_id = AsyncMock()
    uow.users.get_by_telegram_id = AsyncMock()
    uow.users.get_by_employee_id = AsyncMock()
    uow.users.update_last_login = AsyncMock()
    uow.users.update = AsyncMock()
    uow.users.create = AsyncMock()
    uow.users.deactivate_user = AsyncMock()
    uow.users.update_role = AsyncMock()
    uow.users.find_users = AsyncMock()

    uow.invitations = MagicMock()
    uow.invitations.get_by_id = AsyncMock()
    uow.invitations.get_valid_by_token = AsyncMock()
    uow.invitations.mark_as_used = AsyncMock()
    uow.invitations.create = AsyncMock()
    uow.invitations.update = AsyncMock()
    uow.invitations.delete = AsyncMock()
    uow.invitations.find_invitations = AsyncMock()
    uow.invitations.get_statistics = AsyncMock()
    uow.invitations.exists_pending_for_email = AsyncMock()

    uow.user_mentors = MagicMock()
    uow.user_mentors.get_active_by_user_id = AsyncMock()
    uow.user_mentors.get_by_user_id = AsyncMock()
    uow.user_mentors.get_by_mentor_id = AsyncMock()
    uow.user_mentors.get_by_user_and_mentor = AsyncMock()
    uow.user_mentors.get_by_id = AsyncMock()
    uow.user_mentors.get_all = AsyncMock()
    uow.user_mentors.create = AsyncMock()
    uow.user_mentors.update = AsyncMock()
    uow.user_mentors.delete = AsyncMock()

    uow.departments = MagicMock()
    uow.departments.get_by_id = AsyncMock()
    uow.departments.get_by_name = AsyncMock()
    uow.departments.find_departments = AsyncMock()
    uow.departments.create = AsyncMock()
    uow.departments.update = AsyncMock()
    uow.departments.delete = AsyncMock()

    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()

    return uow


@pytest.fixture(autouse=True)
def mock_init_db():
    """Mock database initialization for all tests."""
    with patch("auth_service.main.init_db", new_callable=AsyncMock):
        yield


@pytest.fixture(autouse=True)
def override_uow_dependency(mock_uow):
    """Override the UOW dependency for all API tests."""
    from auth_service.api import deps
    from auth_service.main import app

    # Store original override if any
    original_override = app.dependency_overrides.get(deps.get_uow)

    # Override with mock
    async def mock_get_uow() -> AsyncGenerator[IUnitOfWork]:
        yield mock_uow

    app.dependency_overrides[deps.get_uow] = mock_get_uow

    yield

    # Restore original override or remove
    if original_override is not None:
        app.dependency_overrides[deps.get_uow] = original_override
    else:
        app.dependency_overrides.pop(deps.get_uow, None)


@pytest.fixture(autouse=True)
def fast_bcrypt(monkeypatch):
    """
    Speed up bcrypt by using minimum rounds for all tests.

    Bcrypt default is 12 rounds which is slow. Using 4 rounds (minimum)
    makes tests ~10x faster while still testing real bcrypt functionality.
    """
    import bcrypt

    # Save original gensalt
    original_gensalt = bcrypt.gensalt

    def _fast_gensalt(rounds: int = 12, prefix: bytes = b"2b"):
        # Force minimum rounds for speed (4 is bcrypt minimum)
        return original_gensalt(rounds=4, prefix=prefix)

    # Patch bcrypt module directly
    monkeypatch.setattr(bcrypt, "gensalt", _fast_gensalt)


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    from auth_service.core.enums import UserRole
    from auth_service.models import User
    return User(
        id=1,
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        employee_id="EMP001",
        is_active=True,
        is_verified=True,
        role=UserRole.ADMIN,
    )


@pytest.fixture
def hr_user():
    """Create an HR user for testing."""
    from auth_service.core.enums import UserRole
    from auth_service.models import User
    return User(
        id=2,
        email="hr@example.com",
        first_name="HR",
        last_name="User",
        employee_id="EMP002",
        is_active=True,
        is_verified=True,
        role=UserRole.HR,
    )


@pytest.fixture
def mentor_user():
    """Create a mentor user for testing."""
    from auth_service.core.enums import UserRole
    from auth_service.models import User
    return User(
        id=3,
        email="mentor@example.com",
        first_name="Mentor",
        last_name="User",
        employee_id="EMP003",
        is_active=True,
        is_verified=True,
        role=UserRole.MENTOR,
    )


@pytest.fixture
def newbie_user():
    """Create a newbie user for testing."""
    from auth_service.core.enums import UserRole
    from auth_service.models import User
    return User(
        id=4,
        email="newbie@example.com",
        first_name="Newbie",
        last_name="User",
        employee_id="EMP004",
        is_active=True,
        is_verified=True,
        role=UserRole.NEWBIE,
    )
