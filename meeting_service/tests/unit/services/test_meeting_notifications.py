"""Unit tests for MeetingService notification/reminder functionality."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from meeting_service.core.enums import MeetingStatus, MeetingType
from meeting_service.models import Meeting, UserMeeting
from meeting_service.schemas import UserMeetingCreate
from meeting_service.services.meeting import MeetingService


class TestUserName:
    """Tests for MeetingService._user_name static method."""

    def test_user_name_none_returns_there(self):
        """_user_name with None returns 'there'."""
        assert MeetingService._user_name(None) == "there"

    def test_user_name_with_first_and_last(self):
        """_user_name with first and last name returns full name."""
        data = {"first_name": "Alice", "last_name": "Smith"}
        assert MeetingService._user_name(data) == "Alice Smith"

    def test_user_name_first_name_only(self):
        """_user_name with only first name returns first name."""
        data = {"first_name": "Bob", "last_name": ""}
        assert MeetingService._user_name(data) == "Bob"

    def test_user_name_empty_names_falls_back_to_email(self):
        """_user_name with empty names falls back to email."""
        data = {"first_name": "", "last_name": "", "email": "user@example.com"}
        assert MeetingService._user_name(data) == "user@example.com"

    def test_user_name_empty_names_no_email_returns_there(self):
        """_user_name with empty names and no email returns 'there'."""
        data = {"first_name": "", "last_name": ""}
        assert MeetingService._user_name(data) == "there"

    def test_user_name_empty_dict_returns_there(self):
        """_user_name with empty dict returns 'there'."""
        assert MeetingService._user_name({}) == "there"


class TestUserLanguage:
    """Tests for MeetingService._user_language static method."""

    def test_user_language_none_returns_en(self):
        """_user_language with None returns 'en'."""
        assert MeetingService._user_language(None) == "en"

    def test_user_language_with_language(self):
        """_user_language with language set returns it."""
        data = {"language": "ru"}
        assert MeetingService._user_language(data) == "ru"

    def test_user_language_missing_key_returns_en(self):
        """_user_language with missing language key returns 'en'."""
        data = {"email": "user@example.com"}
        assert MeetingService._user_language(data) == "en"

    def test_user_language_none_value_returns_en(self):
        """_user_language with None language value returns 'en'."""
        data = {"language": None}
        assert MeetingService._user_language(data) == "en"

    def test_user_language_empty_dict_returns_en(self):
        """_user_language with empty dict returns 'en'."""
        assert MeetingService._user_language({}) == "en"


class TestCancelMeetingReminders:
    """Tests for MeetingService._cancel_meeting_reminders."""

    @pytest.mark.asyncio
    async def test_cancel_reminders_disabled_returns_early(self, mock_uow):
        """When notifications disabled, cancel_reminders returns early without calling service."""
        service = MeetingService(mock_uow, notifications_enabled=False)
        assignment = UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED)

        mock_client = AsyncMock()
        with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
            await service._cancel_meeting_reminders(assignment)

        mock_client.cancel_scheduled_notifications.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancel_reminders_enabled_calls_service(self, mock_uow):
        """When notifications enabled, cancel_reminders calls notification service."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        assignment = UserMeeting(id=5, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED)

        mock_client = MagicMock()
        mock_client.cancel_scheduled_notifications = AsyncMock(return_value=2)

        with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
            await service._cancel_meeting_reminders(assignment)

        mock_client.cancel_scheduled_notifications.assert_awaited_once_with(
            user_id=100,
            notification_type="MEETING_REMINDER",
            data_match={
                "source_service": "meeting_service",
                "assignment_id": 5,
            },
        )

    @pytest.mark.asyncio
    async def test_cancel_reminders_exception_is_swallowed(self, mock_uow):
        """When notification service raises, exception is caught and swallowed."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        assignment = UserMeeting(id=5, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED)

        mock_client = MagicMock()
        mock_client.cancel_scheduled_notifications = AsyncMock(side_effect=RuntimeError("Connection refused"))

        with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
            # Should not raise
            await service._cancel_meeting_reminders(assignment)


class TestScheduleMeetingReminders:
    """Tests for MeetingService._schedule_meeting_reminders."""

    @pytest.mark.asyncio
    async def test_schedule_reminders_disabled_returns_early(self, mock_uow):
        """When notifications disabled, schedule_reminders returns early."""
        service = MeetingService(mock_uow, notifications_enabled=False)
        assignment = UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED)
        meeting = Meeting(id=1, title="Test", type=MeetingType.HR, duration_minutes=60)

        mock_client = AsyncMock()
        with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
            await service._schedule_meeting_reminders(assignment, meeting, {"email": "u@example.com"})

        mock_client.schedule_template_notification.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedule_reminders_no_user_data_skips(self, mock_uow):
        """When user_data is None, schedule_reminders skips."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        assignment = UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED)
        meeting = Meeting(id=1, title="Test", type=MeetingType.HR, duration_minutes=60)

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock()

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, None)

        mock_cancel.assert_not_called()
        mock_client.schedule_template_notification.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedule_reminders_no_scheduled_at_skips(self, mock_uow):
        """When assignment has no scheduled_at, reminder scheduling is skipped after cancel."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        assignment = UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED, scheduled_at=None)
        meeting = Meeting(id=1, title="Test", type=MeetingType.HR, duration_minutes=60)
        user_data = {"email": "u@example.com"}

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock()

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, user_data)

        mock_cancel.assert_awaited_once_with(assignment)
        mock_client.schedule_template_notification.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedule_reminders_completed_meeting_skips(self, mock_uow):
        """When assignment is COMPLETED, reminder scheduling is skipped after cancel."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        future_time = datetime.now(UTC) + timedelta(hours=2)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,
            scheduled_at=future_time,
        )
        meeting = Meeting(id=1, title="Test", type=MeetingType.HR, duration_minutes=60)
        user_data = {"email": "u@example.com"}

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock()

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, user_data)

        mock_cancel.assert_awaited_once()
        mock_client.schedule_template_notification.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedule_reminders_no_contacts_skips(self, mock_uow):
        """When user has no telegram_id or email, reminder scheduling is skipped."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        future_time = datetime.now(UTC) + timedelta(hours=2)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            scheduled_at=future_time,
        )
        meeting = Meeting(id=1, title="Test", type=MeetingType.HR, duration_minutes=60)
        user_data = {"first_name": "Alice"}  # No email, no telegram_id

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock()

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, user_data)

        mock_client.schedule_template_notification.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedule_reminders_with_email_schedules_notifications(self, mock_uow):
        """When user has email, reminders are scheduled via notification service."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        future_time = datetime.now(UTC) + timedelta(hours=2)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            scheduled_at=future_time,
        )
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        user_data = {"email": "user@example.com", "first_name": "Alice"}

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock(return_value={"id": "notif-1"})

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, user_data)

        # Both 15-min and 5-min reminders should be scheduled via email
        assert mock_client.schedule_template_notification.call_count == 2
        calls = mock_client.schedule_template_notification.call_args_list
        channels = [c.kwargs["channel"] for c in calls]
        assert all(ch == "EMAIL" for ch in channels)
        minutes = [c.kwargs["variables"]["minutes_until"] for c in calls]
        assert set(minutes) == {5, 15}

    @pytest.mark.asyncio
    async def test_schedule_reminders_with_telegram_schedules_notifications(self, mock_uow):
        """When user has telegram_id, reminders are scheduled via telegram."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        future_time = datetime.now(UTC) + timedelta(hours=2)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            scheduled_at=future_time,
        )
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        user_data = {"telegram_id": 12345, "first_name": "Alice"}

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock(return_value={"id": "notif-1"})

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, user_data)

        # Both 15-min and 5-min reminders should be scheduled via telegram
        assert mock_client.schedule_template_notification.call_count == 2
        calls = mock_client.schedule_template_notification.call_args_list
        channels = [c.kwargs["channel"] for c in calls]
        assert all(ch == "TELEGRAM" for ch in channels)

    @pytest.mark.asyncio
    async def test_schedule_reminders_with_both_email_and_telegram(self, mock_uow):
        """When user has both email and telegram_id, all 4 reminders are scheduled."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        future_time = datetime.now(UTC) + timedelta(hours=2)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            scheduled_at=future_time,
        )
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        user_data = {"email": "user@example.com", "telegram_id": 12345}

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock(return_value={"id": "notif-1"})

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, user_data)

        # 2 channels x 2 time intervals = 4 calls
        assert mock_client.schedule_template_notification.call_count == 4

    @pytest.mark.asyncio
    async def test_schedule_reminders_past_reminder_times_skipped(self, mock_uow):
        """When reminder times are in the past, they are skipped."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        # Meeting is only 3 minutes away, so both 15-min and 5-min reminders are in the past
        close_future_time = datetime.now(UTC) + timedelta(minutes=3)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            scheduled_at=close_future_time,
        )
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        user_data = {"email": "user@example.com"}

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock()

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, user_data)

        # All reminder times are in the past, none scheduled
        mock_client.schedule_template_notification.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedule_reminders_naive_datetime_gets_utc(self, mock_uow):
        """When scheduled_at lacks timezone info, UTC is assumed."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        # Naive datetime (no tzinfo)
        naive_future = datetime.now() + timedelta(hours=2)
        assert naive_future.tzinfo is None

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            scheduled_at=naive_future,
        )
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR, duration_minutes=60)
        user_data = {"email": "user@example.com"}

        mock_cancel = AsyncMock()
        mock_client = MagicMock()
        mock_client.schedule_template_notification = AsyncMock(return_value={"id": "notif-1"})

        with patch.object(service, "_cancel_meeting_reminders", mock_cancel):
            with patch("meeting_service.utils.integrations.notification_service_client", mock_client):
                await service._schedule_meeting_reminders(assignment, meeting, user_data)

        # Should succeed without errors
        assert mock_client.schedule_template_notification.call_count == 2


class TestAssignMeetingWithNotifications:
    """Tests for assign_meeting with notifications enabled."""

    @pytest.mark.asyncio
    async def test_assign_meeting_schedules_reminders_when_enabled(self, mock_uow):
        """When notifications enabled and scheduled_at set, reminders are scheduled."""
        service = MeetingService(mock_uow, notifications_enabled=True)
        meeting = Meeting(id=1, title="Test Meeting", description="Desc", type=MeetingType.HR, duration_minutes=60)
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.user_meetings.get_user_meeting.return_value = None

        scheduled_time = datetime.now(UTC) + timedelta(hours=2)
        assignment_data = UserMeetingCreate(
            user_id=100,
            meeting_id=1,
            scheduled_at=scheduled_time,
        )

        created_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=scheduled_time,
            status=MeetingStatus.SCHEDULED,
        )
        mock_uow.user_meetings.create.return_value = created_assignment

        mock_schedule = AsyncMock()

        with patch("meeting_service.services.meeting.GoogleCalendarService") as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.create_event = AsyncMock(return_value={"id": "event-123"})
            mock_gc_class.return_value = mock_gc_instance

            with patch.object(service, "_schedule_meeting_reminders", mock_schedule):
                result = await service.assign_meeting(assignment_data, user_data={"email": "u@example.com"})

        assert result == created_assignment
        mock_schedule.assert_awaited_once()
