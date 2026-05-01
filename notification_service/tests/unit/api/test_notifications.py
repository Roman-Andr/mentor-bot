"""Unit tests for notification_service/api/endpoints/notifications.py."""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from notification_service.api.endpoints.notifications import (
    get_notification_history,
    get_user_notification_history,
    schedule_notification,
    send_notification,
)
from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.schemas import (
    NotificationCreate,
    NotificationResponse,
    ScheduledNotificationCreate,
    ScheduledNotificationResponse,
)


@pytest.fixture
def mock_db() -> MagicMock:
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def hr_user() -> MagicMock:
    """Create a mock HR user."""
    user = MagicMock()
    user.id = 1
    user.role = "HR"
    user.email = "hr@example.com"
    user.is_active = True
    return user


@pytest.fixture
def admin_user() -> MagicMock:
    """Create a mock admin user."""
    user = MagicMock()
    user.id = 2
    user.role = "ADMIN"
    user.email = "admin@example.com"
    user.is_active = True
    return user


@pytest.fixture
def regular_user() -> MagicMock:
    """Create a mock regular user."""
    user = MagicMock()
    user.id = 42
    user.role = "USER"
    user.email = "user@example.com"
    user.is_active = True
    return user


@pytest.fixture
def sample_notification_create() -> NotificationCreate:
    """Create a sample notification create schema."""
    return NotificationCreate(
        user_id=42,
        recipient_telegram_id=123456789,
        recipient_email="user@example.com",
        type=NotificationType.GENERAL,
        channel=NotificationChannel.EMAIL,
        subject="Test Subject",
        body="Test body content",
        data={"key": "value"},
    )


@pytest.fixture
def sample_scheduled_create() -> ScheduledNotificationCreate:
    """Create a sample scheduled notification create schema."""
    return ScheduledNotificationCreate(
        user_id=42,
        recipient_telegram_id=123456789,
        recipient_email="user@example.com",
        type=NotificationType.MEETING_REMINDER,
        channel=NotificationChannel.TELEGRAM,
        subject="Meeting Reminder",
        body="You have a meeting in 30 minutes",
        data={"meeting_id": 123},
        scheduled_time=datetime.now(UTC),
    )


def create_mock_notification_response(user_id: int, **kwargs: Any) -> MagicMock:
    """Create a mock that passes as NotificationResponse."""
    mock = MagicMock()
    mock.id = kwargs.get("id", 1)
    mock.user_id = user_id
    mock.recipient_telegram_id = kwargs.get("recipient_telegram_id", 123456789)
    mock.recipient_email = kwargs.get("recipient_email", "user@example.com")
    mock.type = kwargs.get("type", NotificationType.GENERAL)
    mock.channel = kwargs.get("channel", NotificationChannel.EMAIL)
    mock.subject = kwargs.get("subject", "Test Subject")
    mock.body = kwargs.get("body", "Test body")
    mock.data = kwargs.get("data", {})
    mock.status = kwargs.get("status", NotificationStatus.SENT)
    mock.error_message = kwargs.get("error_message")
    mock.created_at = kwargs.get("created_at", datetime.now(UTC))
    mock.scheduled_for = kwargs.get("scheduled_for")
    mock.sent_at = kwargs.get("sent_at", datetime.now(UTC))
    # Make model_validate return the mock itself
    mock.model_validate = classmethod(lambda _cls, _obj: mock)
    return mock


def create_mock_scheduled_response(user_id: int, **kwargs: Any) -> MagicMock:
    """Create a mock that passes as ScheduledNotificationResponse."""
    mock = MagicMock()
    mock.id = kwargs.get("id", 1)
    mock.user_id = user_id
    mock.recipient_telegram_id = kwargs.get("recipient_telegram_id", 123456789)
    mock.recipient_email = kwargs.get("recipient_email", "user@example.com")
    mock.type = kwargs.get("type", NotificationType.GENERAL)
    mock.channel = kwargs.get("channel", NotificationChannel.EMAIL)
    mock.subject = kwargs.get("subject", "Test Subject")
    mock.body = kwargs.get("body", "Test body")
    mock.data = kwargs.get("data", {})
    mock.scheduled_time = kwargs.get("scheduled_time", datetime.now(UTC))
    mock.processed = kwargs.get("processed", False)
    mock.processed_at = kwargs.get("processed_at")
    mock.created_at = kwargs.get("created_at", datetime.now(UTC))
    mock.model_validate = classmethod(lambda _cls, _obj: mock)
    return mock


class TestSendNotification:
    """Tests for the send_notification endpoint."""

    async def test_send_notification_as_owner_succeeds(
        self,
        mock_db: MagicMock,
        regular_user: MagicMock,
        sample_notification_create: NotificationCreate,
    ) -> None:
        """User can send notification to themselves."""
        # Set the user_id to match the regular_user
        sample_notification_create.user_id = regular_user.id

        mock_response = create_mock_notification_response(regular_user.id)

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_immediate = AsyncMock(return_value=mock_response)
                mock_service_cls.return_value = mock_service

                with patch.object(NotificationResponse, "model_validate", return_value=mock_response):
                    result = await send_notification(sample_notification_create, mock_db, regular_user)

                    assert result.user_id == regular_user.id
                    mock_service.send_immediate.assert_awaited_once_with(sample_notification_create)

    async def test_send_notification_as_hr_for_other_user_succeeds(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
        sample_notification_create: NotificationCreate,
    ) -> None:
        """HR can send notification on behalf of another user."""
        # HR sending to a different user
        sample_notification_create.user_id = 99  # Different from HR user

        mock_response = create_mock_notification_response(99)

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_immediate = AsyncMock(return_value=mock_response)
                mock_service_cls.return_value = mock_service

                with patch.object(NotificationResponse, "model_validate", return_value=mock_response):
                    result = await send_notification(sample_notification_create, mock_db, hr_user)

                    assert result.user_id == 99
                    mock_service.send_immediate.assert_awaited_once()

    async def test_send_notification_as_admin_for_other_user_succeeds(
        self,
        mock_db: MagicMock,
        admin_user: MagicMock,
        sample_notification_create: NotificationCreate,
    ) -> None:
        """Admin can send notification on behalf of another user."""
        sample_notification_create.user_id = 99  # Different from admin user

        mock_response = create_mock_notification_response(99)

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_immediate = AsyncMock(return_value=mock_response)
                mock_service_cls.return_value = mock_service

                with patch.object(NotificationResponse, "model_validate", return_value=mock_response):
                    result = await send_notification(sample_notification_create, mock_db, admin_user)
                    assert result.user_id == 99

    async def test_send_notification_for_other_user_as_regular_user_fails(
        self,
        mock_db: MagicMock,
        regular_user: MagicMock,
        sample_notification_create: NotificationCreate,
    ) -> None:
        """Regular user cannot send notification on behalf of another user."""
        sample_notification_create.user_id = 99  # Different from regular_user.id

        with pytest.raises(HTTPException) as exc_info:
            await send_notification(sample_notification_create, mock_db, regular_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot send notifications on behalf of another user" in exc_info.value.detail


class TestScheduleNotification:
    """Tests for the schedule_notification endpoint."""

    async def test_schedule_notification_as_owner_succeeds(
        self,
        mock_db: MagicMock,
        regular_user: MagicMock,
        sample_scheduled_create: ScheduledNotificationCreate,
    ) -> None:
        """User can schedule notification for themselves."""
        sample_scheduled_create.user_id = regular_user.id

        mock_response = create_mock_scheduled_response(regular_user.id)

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.schedule = AsyncMock(return_value=mock_response)
                mock_service_cls.return_value = mock_service

                with patch.object(ScheduledNotificationResponse, "model_validate", return_value=mock_response):
                    result = await schedule_notification(sample_scheduled_create, mock_db, regular_user)

                    assert result.user_id == regular_user.id
                    mock_service.schedule.assert_awaited_once_with(sample_scheduled_create)

    async def test_schedule_notification_as_hr_for_other_user_succeeds(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
        sample_scheduled_create: ScheduledNotificationCreate,
    ) -> None:
        """HR can schedule notification on behalf of another user."""
        sample_scheduled_create.user_id = 99

        mock_response = create_mock_scheduled_response(99)

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.schedule = AsyncMock(return_value=mock_response)
                mock_service_cls.return_value = mock_service

                with patch.object(ScheduledNotificationResponse, "model_validate", return_value=mock_response):
                    result = await schedule_notification(sample_scheduled_create, mock_db, hr_user)
                    assert result.user_id == 99

    async def test_schedule_notification_for_other_user_as_regular_user_fails(
        self,
        mock_db: MagicMock,
        regular_user: MagicMock,
        sample_scheduled_create: ScheduledNotificationCreate,
    ) -> None:
        """Regular user cannot schedule notification for another user."""
        sample_scheduled_create.user_id = 99

        with pytest.raises(HTTPException) as exc_info:
            await schedule_notification(sample_scheduled_create, mock_db, regular_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot schedule notifications on behalf of another user" in exc_info.value.detail


class TestGetNotificationHistory:
    """Tests for the get_notification_history endpoint."""

    async def test_get_own_notification_history(
        self,
        mock_db: MagicMock,
        regular_user: MagicMock,
    ) -> None:
        """User can retrieve their own notification history."""
        mock_notifications = [
            create_mock_notification_response(
                regular_user.id,
                id=1,
                status=NotificationStatus.SENT,
            ),
            create_mock_notification_response(
                regular_user.id,
                id=2,
                status=NotificationStatus.FAILED,
                channel=NotificationChannel.TELEGRAM,
                type=NotificationType.MEETING_REMINDER,
            ),
        ]

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.find_notifications = AsyncMock(return_value=(mock_notifications, len(mock_notifications)))
                mock_service_cls.return_value = mock_service

                with patch.object(NotificationResponse, "model_validate", side_effect=lambda x: x):
                    result = await get_notification_history(mock_db, regular_user, skip=0, limit=50)

                    assert len(result) == 2
                    mock_service.find_notifications.assert_awaited_once_with(
                        skip=0, limit=50, user_id=regular_user.id, sort_by=None, sort_order="desc"
                    )

    async def test_pagination_with_skip_and_limit(
        self,
        mock_db: MagicMock,
        regular_user: MagicMock,
    ) -> None:
        """Pagination parameters are passed correctly to service."""
        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.find_notifications = AsyncMock(return_value=([], 0))
                mock_service_cls.return_value = mock_service

                with patch.object(NotificationResponse, "model_validate", side_effect=lambda x: x):
                    await get_notification_history(mock_db, regular_user, skip=10, limit=25)

                    mock_service.find_notifications.assert_awaited_once_with(
                        skip=10, limit=25, user_id=regular_user.id, sort_by=None, sort_order="desc"
                    )


class TestGetUserNotificationHistory:
    """Tests for the get_user_notification_history endpoint (HR/Admin only)."""

    async def test_hr_can_get_other_user_history(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
    ) -> None:
        """HR user can retrieve notification history for any user."""
        target_user_id = 99
        mock_notifications = [
            create_mock_notification_response(
                target_user_id,
                id=1,
                status=NotificationStatus.SENT,
            ),
        ]

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.find_notifications = AsyncMock(return_value=(mock_notifications, len(mock_notifications)))
                mock_service_cls.return_value = mock_service

                # HR user is passed as _current_user (dependency injected)
                with patch.object(NotificationResponse, "model_validate", side_effect=lambda x: x):
                    result = await get_user_notification_history(target_user_id, mock_db, hr_user, skip=0, limit=50)

                    assert len(result) == 1
                    assert result[0].user_id == target_user_id
                    mock_service.find_notifications.assert_awaited_once_with(
                        skip=0, limit=50, user_id=target_user_id, sort_by=None, sort_order="desc"
                    )

    async def test_admin_can_get_other_user_history(
        self,
        mock_db: MagicMock,
        admin_user: MagicMock,
    ) -> None:
        """Admin user can retrieve notification history for any user."""
        target_user_id = 99

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.find_notifications = AsyncMock(return_value=([], 0))
                mock_service_cls.return_value = mock_service

                with patch.object(NotificationResponse, "model_validate", side_effect=lambda x: x):
                    await get_user_notification_history(target_user_id, mock_db, admin_user, skip=0, limit=50)

                    mock_service.find_notifications.assert_awaited_once_with(
                        skip=0, limit=50, user_id=target_user_id, sort_by=None, sort_order="desc"
                    )


class TestListNotifications:
    """Tests for the list_notifications endpoint (lines 128-141)."""

    async def test_list_notifications_as_hr(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
    ) -> None:
        """HR can list all notifications with filters."""
        from notification_service.api.endpoints.notifications import list_notifications

        mock_notifications = [
            create_mock_notification_response(42, id=1, status=NotificationStatus.SENT),
            create_mock_notification_response(43, id=2, status=NotificationStatus.PENDING),
        ]

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.find_notifications = AsyncMock(return_value=(mock_notifications, 2))
                mock_service_cls.return_value = mock_service

                with patch.object(NotificationResponse, "model_validate", side_effect=lambda x: x):
                    result = await list_notifications(
                        mock_db,
                        hr_user,
                        skip=0,
                        limit=50,
                        user_id=42,
                        notification_type=NotificationType.GENERAL,
                        status=NotificationStatus.SENT,
                        sort_by="created_at",
                        sort_order="desc",
                    )

                    assert result.total == 2
                    assert len(result.notifications) == 2
                    mock_service.find_notifications.assert_awaited_once_with(
                        skip=0,
                        limit=50,
                        user_id=42,
                        notification_type=NotificationType.GENERAL,
                        status=NotificationStatus.SENT,
                        sort_by="created_at",
                        sort_order="desc",
                    )

    async def test_list_notifications_pagination(
        self,
        mock_db: MagicMock,
        admin_user: MagicMock,
    ) -> None:
        """List notifications with pagination."""
        from notification_service.api.endpoints.notifications import list_notifications

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.find_notifications = AsyncMock(return_value=([], 0))
                mock_service_cls.return_value = mock_service

                result = await list_notifications(mock_db, admin_user, skip=10, limit=25)

                assert result.page == 1  # 10 // 25 + 1
                assert result.size == 25
                assert result.pages == 0  # (0 + 25 - 1) // 25


class TestSendTemplateNotification:
    """Tests for send_template_notification endpoint (lines 164-189)."""

    async def test_send_template_notification_success(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
    ) -> None:
        """Send template notification successfully."""
        from notification_service.api.endpoints.notifications import send_template_notification

        mock_notification = create_mock_notification_response(
            42, id=1, status=NotificationStatus.SENT, channel=NotificationChannel.EMAIL
        )

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_template = AsyncMock(return_value=mock_notification)
                mock_service_cls.return_value = mock_service

                with patch.object(NotificationResponse, "model_validate", return_value=mock_notification):
                    result = await send_template_notification(
                        template_name="welcome",
                        user_id=42,
                        variables={"user_name": "John"},
                        channel=NotificationChannel.EMAIL,
                        db=mock_db,
                        current_user=hr_user,
                        recipient_telegram_id=None,
                        recipient_email="user@example.com",
                        notification_type=NotificationType.GENERAL,
                        language="en",
                    )

                    assert result is mock_notification
                    mock_service.send_template.assert_awaited_once_with(
                        template_name="welcome",
                        user_id=42,
                        recipient_telegram_id=None,
                        recipient_email="user@example.com",
                        variables={"user_name": "John"},
                        channel=NotificationChannel.EMAIL,
                        notification_type=NotificationType.GENERAL,
                        language="en",
                    )

    async def test_send_template_notification_not_found(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
    ) -> None:
        """Returns 404 when template not found."""
        from notification_service.api.endpoints.notifications import send_template_notification
        from notification_service.services.template import TemplateNotFoundError

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_template = AsyncMock(side_effect=TemplateNotFoundError("missing", "email", "en"))
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await send_template_notification(
                        template_name="missing",
                        user_id=42,
                        variables={},
                        channel=NotificationChannel.EMAIL,
                        db=mock_db,
                        current_user=hr_user,
                    )

                assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_send_template_notification_missing_variables(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
    ) -> None:
        """Returns 400 when template variables missing."""
        from notification_service.api.endpoints.notifications import send_template_notification
        from notification_service.services.template import MissingTemplateVariablesError

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_template = AsyncMock(side_effect=MissingTemplateVariablesError({"user_name"}))
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await send_template_notification(
                        template_name="welcome",
                        user_id=42,
                        variables={},
                        channel=NotificationChannel.EMAIL,
                        db=mock_db,
                        current_user=hr_user,
                    )

                assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestScheduleTemplateNotification:
    """Tests for schedule_template_notification endpoint (lines 207-233)."""

    async def test_schedule_template_notification_success(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
    ) -> None:
        """Schedule template notification successfully."""
        from datetime import UTC, datetime

        from notification_service.api.endpoints.notifications import schedule_template_notification

        mock_scheduled = create_mock_scheduled_response(42, id=1, processed=False)

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.schedule_template = AsyncMock(return_value=mock_scheduled)
                mock_service_cls.return_value = mock_service

                with patch.object(ScheduledNotificationResponse, "model_validate", return_value=mock_scheduled):
                    scheduled_time = datetime.now(UTC)
                    result = await schedule_template_notification(
                        template_name="meeting_reminder",
                        user_id=42,
                        variables={"meeting_title": "Team Sync"},
                        channel=NotificationChannel.TELEGRAM,
                        scheduled_time=scheduled_time,
                        db=mock_db,
                        current_user=hr_user,
                        recipient_telegram_id=123456789,
                        recipient_email=None,
                        notification_type=NotificationType.MEETING_REMINDER,
                        language="en",
                    )

                    assert result is mock_scheduled
                    mock_service.schedule_template.assert_awaited_once_with(
                        template_name="meeting_reminder",
                        user_id=42,
                        recipient_telegram_id=123456789,
                        recipient_email=None,
                        variables={"meeting_title": "Team Sync"},
                        channel=NotificationChannel.TELEGRAM,
                        scheduled_time=scheduled_time,
                        notification_type=NotificationType.MEETING_REMINDER,
                        language="en",
                    )

    async def test_schedule_template_notification_not_found(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
    ) -> None:
        """Returns 404 when template not found for scheduling."""
        from datetime import UTC, datetime

        from notification_service.api.endpoints.notifications import schedule_template_notification
        from notification_service.services.template import TemplateNotFoundError

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.schedule_template = AsyncMock(
                    side_effect=TemplateNotFoundError("missing", "telegram", "en")
                )
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await schedule_template_notification(
                        template_name="missing",
                        user_id=42,
                        variables={},
                        channel=NotificationChannel.TELEGRAM,
                        scheduled_time=datetime.now(UTC),
                        db=mock_db,
                        current_user=hr_user,
                    )

                assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_schedule_template_notification_missing_variables(
        self,
        mock_db: MagicMock,
        hr_user: MagicMock,
    ) -> None:
        """Returns 400 when template variables missing for scheduling."""
        from datetime import UTC, datetime

        from notification_service.api.endpoints.notifications import schedule_template_notification
        from notification_service.services.template import MissingTemplateVariablesError

        with patch("notification_service.api.endpoints.notifications.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.endpoints.notifications.NotificationService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.schedule_template = AsyncMock(side_effect=MissingTemplateVariablesError({"due_date"}))
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await schedule_template_notification(
                        template_name="task_reminder",
                        user_id=42,
                        variables={},
                        channel=NotificationChannel.TELEGRAM,
                        scheduled_time=datetime.now(UTC),
                        db=mock_db,
                        current_user=hr_user,
                    )

                assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
