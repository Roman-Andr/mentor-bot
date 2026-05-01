"""Pytest configuration and shared fixtures for notification_service tests."""

import os
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Clear proxy environment variables to avoid httpx proxy errors
# httpx doesn't support 'socks://' scheme, only 'socks5://' and 'socks5h://'
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("all_proxy", None)
os.environ.pop("ALL_PROXY", None)

# Set required environment variables BEFORE any app imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SERVICE_API_KEY", "test-api-key")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8001")
os.environ.setdefault("DEFAULT_FROM_EMAIL", "test@example.com")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("SMTP_HOST", "smtp.test.com")
os.environ.setdefault("SMTP_PORT", "587")
os.environ.setdefault("SMTP_USER", "test@test.com")
os.environ.setdefault("SMTP_PASSWORD", "testpassword")

# Now safe to import app modules
from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.models import Notification, ScheduledNotification
from notification_service.repositories.unit_of_work import IUnitOfWork
from notification_service.services.auth_client import UserPreferences


@pytest.fixture(autouse=True)
def patch_auth_client():
    """Automatically patch AuthClient in all tests to avoid HTTP calls."""
    with patch("notification_service.services.notification.AuthClient") as mock_auth_client:
        mock_client = MagicMock()
        mock_client.get_user_preferences = AsyncMock(return_value=UserPreferences())
        mock_auth_client.return_value = mock_client
        yield


@pytest.fixture
def mock_uow() -> MagicMock:
    """Create a mock Unit of Work with AsyncMock repositories."""
    uow = MagicMock(spec=IUnitOfWork)
    uow.notifications = MagicMock()
    uow.notifications.create = AsyncMock(return_value=None)
    uow.notifications.update = AsyncMock(return_value=None)
    uow.notifications.get_user_notifications = AsyncMock(return_value=[])
    uow.notifications.find_notifications = AsyncMock(return_value=([], 0))

    uow.scheduled_notifications = MagicMock()
    uow.scheduled_notifications.create = AsyncMock(return_value=None)
    uow.scheduled_notifications.find_pending_before = AsyncMock(return_value=[])
    uow.scheduled_notifications.mark_processed = AsyncMock(return_value=None)

    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()

    return uow


@pytest.fixture
def sample_notification() -> Notification:
    """Create a sample Notification model for testing."""
    return Notification(
        id=1,
        user_id=42,
        recipient_telegram_id=123456789,
        recipient_email="user@example.com",
        type=NotificationType.GENERAL,
        channel=NotificationChannel.EMAIL,
        subject="Test Subject",
        body="Test body content",
        data={},
        status=NotificationStatus.PENDING,
    )


@pytest.fixture
def sample_scheduled_notification() -> ScheduledNotification:
    """Create a sample ScheduledNotification model for testing."""
    return ScheduledNotification(
        id=1,
        user_id=42,
        recipient_telegram_id=123456789,
        recipient_email="user@example.com",
        type=NotificationType.GENERAL,
        channel=NotificationChannel.EMAIL,
        subject="Scheduled Subject",
        body="Scheduled body content",
        data={"key": "value"},
        scheduled_time=datetime.now(UTC) + timedelta(hours=1),
        processed=False,
    )


@pytest.fixture
def client() -> TestClient:
    """
    Create a FastAPI TestClient for integration tests.

    Mocks database initialization and scheduler to avoid real connections.
    """
    with (
        patch("notification_service.main.init_db", new_callable=AsyncMock),
        patch("notification_service.main.scheduler") as mock_scheduler,
        patch("notification_service.services.notification.AuthClient") as mock_auth_client,
    ):
        mock_scheduler.run = MagicMock(return_value=AsyncMock())
        mock_auth_client.return_value = MagicMock()
        mock_auth_client.return_value.get_user_preferences = AsyncMock(return_value=UserPreferences())
        from notification_service.main import app

        return TestClient(app)
