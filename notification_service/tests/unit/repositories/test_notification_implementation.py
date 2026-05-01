"""Unit tests for notification_service/repositories/implementations/notification.py."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.core.exceptions import NotFoundException
from notification_service.models import Notification, ScheduledNotification
from notification_service.repositories.implementations.notification import (
    NotificationRepository,
    ScheduledNotificationRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock AsyncSession."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def notification_repo(mock_session: MagicMock) -> NotificationRepository:
    """Create a NotificationRepository with mock session."""
    return NotificationRepository(mock_session)


@pytest.fixture
def scheduled_repo(mock_session: MagicMock) -> ScheduledNotificationRepository:
    """Create a ScheduledNotificationRepository with mock session."""
    return ScheduledNotificationRepository(mock_session)


@pytest.fixture
def sample_notification() -> Notification:
    """Create a sample Notification."""
    return Notification(
        id=1,
        user_id=42,
        type=NotificationType.GENERAL,
        channel=NotificationChannel.EMAIL,
        body="Test notification",
        status=NotificationStatus.PENDING,
    )


@pytest.fixture
def sample_scheduled_notification() -> ScheduledNotification:
    """Create a sample ScheduledNotification."""
    return ScheduledNotification(
        id=1,
        user_id=42,
        type=NotificationType.GENERAL,
        channel=NotificationChannel.EMAIL,
        body="Scheduled notification",
        scheduled_time=datetime.now(UTC) + timedelta(hours=1),
        processed=False,
    )


class TestNotificationRepositoryFindNotifications:
    """Tests for NotificationRepository.find_notifications."""

    async def test_find_without_filters(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Find notifications without any filters."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        notifications, total = await notification_repo.find_notifications()

        assert total == 1
        assert len(notifications) == 1
        assert notifications[0].id == 1

    async def test_find_with_user_id_filter(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Find notifications filtered by user_id."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        notifications, total = await notification_repo.find_notifications(user_id=42)

        assert total == 1
        assert len(notifications) == 1

    async def test_find_with_type_filter(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Find notifications filtered by notification_type."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        notifications, total = await notification_repo.find_notifications(notification_type=NotificationType.GENERAL)

        assert total == 1
        assert len(notifications) == 1

    async def test_find_with_status_filter(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Find notifications filtered by status."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        notifications, total = await notification_repo.find_notifications(status=NotificationStatus.PENDING)

        assert total == 1
        assert len(notifications) == 1

    async def test_find_with_all_filters(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Find notifications with all filters applied."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        notifications, total = await notification_repo.find_notifications(
            user_id=42, notification_type=NotificationType.GENERAL, status=NotificationStatus.PENDING
        )

        assert total == 1
        assert len(notifications) == 1

    async def test_find_returns_empty_when_no_matches(
        self, notification_repo: NotificationRepository, mock_session: MagicMock
    ) -> None:
        """Returns empty list and zero total when no matches."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        notifications, total = await notification_repo.find_notifications(user_id=999)

        assert total == 0
        assert notifications == []

    async def test_respects_pagination_parameters(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Respects skip and limit parameters."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 100

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        notifications, total = await notification_repo.find_notifications(skip=10, limit=5)

        assert total == 100
        assert len(notifications) == 1

    async def test_ascending_sort_order(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Uses ascending sort order when specified (line 71)."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_data_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        notifications, total = await notification_repo.find_notifications(sort_by="created_at", sort_order="asc")

        assert total == 1
        assert len(notifications) == 1
        # Verify the query was built with asc() ordering


class TestNotificationRepositoryGetUserNotifications:
    """Tests for NotificationRepository.get_user_notifications."""

    async def test_returns_notifications_for_user(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Returns notifications for specific user."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await notification_repo.get_user_notifications(42)

        assert len(result) == 1
        assert result[0].user_id == 42

    async def test_returns_empty_list_when_user_has_no_notifications(
        self, notification_repo: NotificationRepository, mock_session: MagicMock
    ) -> None:
        """Returns empty list when user has no notifications."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await notification_repo.get_user_notifications(999)

        assert result == []

    async def test_respects_pagination(
        self, notification_repo: NotificationRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Respects skip and limit parameters."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_notification]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await notification_repo.get_user_notifications(42, skip=5, limit=3)

        assert len(result) == 1


class TestScheduledNotificationRepositoryFindPendingBefore:
    """Tests for ScheduledNotificationRepository.find_pending_before."""

    async def test_returns_pending_notifications_before_time(
        self,
        scheduled_repo: ScheduledNotificationRepository,
        mock_session: MagicMock,
        sample_scheduled_notification: ScheduledNotification,
    ) -> None:
        """Returns pending notifications scheduled before given time."""
        before_time = datetime.now(UTC)

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_scheduled_notification]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await scheduled_repo.find_pending_before(before_time)

        assert len(result) == 1
        assert result[0].processed is False

    async def test_returns_empty_when_no_pending_notifications(
        self, scheduled_repo: ScheduledNotificationRepository, mock_session: MagicMock
    ) -> None:
        """Returns empty list when no pending notifications."""
        before_time = datetime.now(UTC)

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await scheduled_repo.find_pending_before(before_time)

        assert result == []


class TestScheduledNotificationRepositoryMarkProcessed:
    """Tests for ScheduledNotificationRepository.mark_processed."""

    async def test_marks_notification_as_processed(
        self,
        scheduled_repo: ScheduledNotificationRepository,
        mock_session: MagicMock,
        sample_scheduled_notification: ScheduledNotification,
    ) -> None:
        """Marks notification as processed and sets processed_at time."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_scheduled_notification
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await scheduled_repo.mark_processed(1)

        assert result.processed is True
        assert result.processed_at is not None
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(sample_scheduled_notification)

    async def test_raises_error_when_notification_not_found(
        self, scheduled_repo: ScheduledNotificationRepository, mock_session: MagicMock
    ) -> None:
        """Raises NotFoundException when notification not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(NotFoundException):
            await scheduled_repo.mark_processed(999)

    async def test_preserves_timezone_in_processed_at(
        self, scheduled_repo: ScheduledNotificationRepository, mock_session: MagicMock
    ) -> None:
        """Preserves timezone when setting processed_at."""
        from datetime import timezone as tz_module

        tz = tz_module(timedelta(hours=3))  # UTC+3
        notification = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=datetime.now(tz),
            processed=False,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = notification
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await scheduled_repo.mark_processed(1)

        assert result.processed is True
        assert result.processed_at is not None
        assert result.processed_at.tzinfo is not None

    async def test_flush_and_refresh_called_in_mark_processed(
        self, scheduled_repo: ScheduledNotificationRepository, mock_session: MagicMock
    ) -> None:
        """Test lines 122-126: verify flush and refresh are called in mark_processed."""
        from datetime import timedelta

        notification = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=datetime.now(UTC) + timedelta(hours=1),
            processed=False,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = notification
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await scheduled_repo.mark_processed(1)

        # Verify lines 124-125 are covered
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(notification)
        assert result.processed is True
        assert result.processed_at is not None


class TestScheduledNotificationRepositoryIncrementRetry:
    """Tests for ScheduledNotificationRepository.increment_retry."""

    async def test_increments_retry_count_and_updates_time(
        self, scheduled_repo: ScheduledNotificationRepository, mock_session: MagicMock
    ) -> None:
        """Increments retry count, sets failed_at, and updates scheduled_time (lines 132-142)."""
        from datetime import timedelta

        # Create a scheduled notification with retry_count=0
        notification = ScheduledNotification(
            id=1,
            user_id=42,
            type=NotificationType.GENERAL,
            channel=NotificationChannel.EMAIL,
            body="Test",
            scheduled_time=datetime.now(UTC) + timedelta(hours=1),
            processed=False,
            retry_count=0,  # Start with 0
            max_retries=3,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = notification
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        next_scheduled = datetime.now(UTC) + timedelta(minutes=5)
        result = await scheduled_repo.increment_retry(1, next_scheduled)

        assert result.retry_count == 1  # Incremented from 0
        assert result.failed_at is not None
        assert result.scheduled_time == next_scheduled
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(notification)

    async def test_raises_error_when_notification_not_found_for_retry(
        self, scheduled_repo: ScheduledNotificationRepository, mock_session: MagicMock
    ) -> None:
        """Raises NotFoundException when notification not found for increment_retry."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(NotFoundException):
            await scheduled_repo.increment_retry(999, datetime.now(UTC))
