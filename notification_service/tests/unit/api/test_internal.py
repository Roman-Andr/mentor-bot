"""Unit tests for notification_service internal maintenance endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from notification_service.api.internal import (
    InternalCancelScheduledRequest,
    InternalScheduleTemplateRequest,
    cancel_scheduled_notifications_internal,
    cleanup_user_notification_data,
    schedule_template_notification_internal,
)
from notification_service.core.enums import NotificationChannel, NotificationType


def make_result(count: int | None) -> MagicMock:
    r = MagicMock()
    r.rowcount = count
    return r


@pytest.fixture
def mock_db() -> MagicMock:
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    return db


class TestCleanupUserNotificationData:
    async def test_cleanup_returns_counts(self, mock_db: MagicMock) -> None:
        """Returns correct counts of deleted rows."""
        mock_db.execute = AsyncMock(
            side_effect=[
                make_result(5),  # notifications
                make_result(3),  # scheduled
                make_result(2),  # updated_templates
            ]
        )

        result = await cleanup_user_notification_data(user_id=42, db=mock_db, _service_auth=None)

        assert result["notifications"] == 5
        assert result["scheduled_notifications"] == 3
        assert result["updated_templates"] == 2
        mock_db.commit.assert_awaited_once()

    async def test_cleanup_handles_none_rowcount(self, mock_db: MagicMock) -> None:
        """Returns 0 for None rowcount values."""
        mock_db.execute = AsyncMock(
            side_effect=[
                make_result(None),
                make_result(None),
                make_result(None),
            ]
        )

        result = await cleanup_user_notification_data(user_id=1, db=mock_db, _service_auth=None)

        assert result["notifications"] == 0
        assert result["scheduled_notifications"] == 0
        assert result["updated_templates"] == 0


class TestScheduleTemplateNotificationInternal:
    async def test_schedule_template_returns_id(self, mock_db: MagicMock) -> None:
        """Returns scheduled notification id on success."""
        mock_scheduled = MagicMock()
        mock_scheduled.id = 7

        mock_service = AsyncMock()
        mock_service.schedule_template = AsyncMock(return_value=mock_scheduled)
        mock_service.cleanup = AsyncMock()

        request = InternalScheduleTemplateRequest(
            template_name="task_reminder",
            user_id=1,
            variables={"task_title": "Test"},
            channel=NotificationChannel.TELEGRAM,
            scheduled_time=datetime.now(UTC),
            recipient_telegram_id=123456,
            notification_type=NotificationType.GENERAL,
        )

        with patch("notification_service.api.internal.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = AsyncMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=False)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.internal.NotificationService", return_value=mock_service):
                result = await schedule_template_notification_internal(request=request, db=mock_db, _service_auth=None)

        assert result == {"id": 7}
        mock_service.cleanup.assert_awaited_once()


class TestCancelScheduledNotificationsInternal:
    async def test_cancel_returns_cancelled_count(self, mock_db: MagicMock) -> None:
        """Returns cancelled count on success."""
        mock_service = AsyncMock()
        mock_service.cancel_scheduled = AsyncMock(return_value=4)
        mock_service.cleanup = AsyncMock()

        request = InternalCancelScheduledRequest(
            user_id=1,
            notification_type=NotificationType.GENERAL,
            data_match={"task_id": 5},
        )

        with patch("notification_service.api.internal.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = AsyncMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=False)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.internal.NotificationService", return_value=mock_service):
                result = await cancel_scheduled_notifications_internal(request=request, db=mock_db, _service_auth=None)

        assert result == {"cancelled": 4}
        mock_service.cleanup.assert_awaited_once()
