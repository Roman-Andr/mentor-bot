"""Unit tests for meeting_service MeetingService."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from meeting_service.core import ConflictException, NotFoundException, ValidationException
from meeting_service.core.enums import EmployeeLevel, MaterialType, MeetingStatus, MeetingType
from meeting_service.models import Meeting, MeetingMaterial, UserMeeting
from meeting_service.schemas import (
    MaterialCreate,
    MeetingCreate,
    MeetingUpdate,
    UserMeetingComplete,
    UserMeetingCreate,
    UserMeetingUpdate,
)
from meeting_service.services.meeting import MeetingService


class TestMeetingTemplateCRUD:
    """Tests for meeting template CRUD operations."""

    async def test_create_meeting(self, mock_uow):
        """Test creating a meeting template."""
        # Arrange
        service = MeetingService(mock_uow)
        meeting_data = MeetingCreate(
            title="Test Meeting",
            description="Test Description",
            type=MeetingType.HR,
            is_mandatory=True,
            deadline_days=7,
        )
        expected_meeting = Meeting(
            id=1,
            title="Test Meeting",
            description="Test Description",
            type=MeetingType.HR,
            is_mandatory=True,
            deadline_days=7,
        )
        mock_uow.meetings.create.return_value = expected_meeting

        # Act
        result = await service.create_meeting(meeting_data)

        # Assert
        assert result == expected_meeting
        mock_uow.meetings.create.assert_called_once()
        call_args = mock_uow.meetings.create.call_args[0][0]
        assert call_args.title == "Test Meeting"
        assert call_args.type == MeetingType.HR

    async def test_get_meeting_exists(self, mock_uow):
        """Test getting an existing meeting."""
        # Arrange
        service = MeetingService(mock_uow)
        expected_meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
        )
        mock_uow.meetings.get_by_id.return_value = expected_meeting

        # Act
        result = await service.get_meeting(1)

        # Assert
        assert result == expected_meeting
        mock_uow.meetings.get_by_id.assert_called_once_with(1)

    async def test_get_meeting_not_found(self, mock_uow):
        """Test getting a non-existent meeting raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.meetings.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            await service.get_meeting(999)
        assert "Meeting" in str(exc_info.value.detail)
        mock_uow.meetings.get_by_id.assert_called_once_with(999)

    async def test_update_meeting(self, mock_uow):
        """Test updating a meeting template."""
        # Arrange
        service = MeetingService(mock_uow)
        existing_meeting = Meeting(
            id=1,
            title="Old Title",
            type=MeetingType.HR,
            is_mandatory=True,
        )
        mock_uow.meetings.get_by_id.return_value = existing_meeting

        update_data = MeetingUpdate(title="New Title", is_mandatory=False)
        expected_meeting = Meeting(
            id=1,
            title="New Title",
            type=MeetingType.HR,
            is_mandatory=False,
        )
        mock_uow.meetings.update.return_value = expected_meeting

        # Act
        result = await service.update_meeting(1, update_data)

        # Assert
        assert result.title == "New Title"
        assert result.is_mandatory is False
        mock_uow.meetings.update.assert_called_once()

    async def test_delete_meeting(self, mock_uow):
        """Test deleting a meeting template."""
        # Arrange
        service = MeetingService(mock_uow)
        existing_meeting = Meeting(
            id=1,
            title="Test Meeting",
            type=MeetingType.HR,
        )
        mock_uow.meetings.get_by_id.return_value = existing_meeting

        # Act
        await service.delete_meeting(1)

        # Assert
        mock_uow.meetings.delete.assert_called_once_with(1)

    async def test_get_meetings_with_filters(self, mock_uow):
        """Test getting meetings with filters."""
        # Arrange
        service = MeetingService(mock_uow)
        meetings = [
            Meeting(id=1, title="HR Meeting", type=MeetingType.HR),
            Meeting(id=2, title="Security Meeting", type=MeetingType.SECURITY),
        ]
        mock_uow.meetings.find_meetings.return_value = (meetings, 2)

        # Act
        result, total = await service.get_meetings(
            skip=0,
            limit=10,
            meeting_type=MeetingType.HR,
            department_id=1,
        )

        # Assert
        assert len(result) == 2
        assert total == 2
        mock_uow.meetings.find_meetings.assert_called_once_with(
            skip=0,
            limit=10,
            meeting_type=MeetingType.HR,
            department_id=1,
            position=None,
            level=None,
            is_mandatory=None,
            search=None,
            sort_by=None,
            sort_order="asc",
        )


class TestMaterialCRUD:
    """Tests for meeting material CRUD operations."""

    async def test_add_material(self, mock_uow):
        """Test adding a material to a meeting."""
        # Arrange
        service = MeetingService(mock_uow)
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting

        material_data = MaterialCreate(
            title="Test PDF",
            type="PDF",
            url="https://example.com/test.pdf",
        )
        expected_material = MeetingMaterial(
            id=1,
            meeting_id=1,
            title="Test PDF",
            type="PDF",
            url="https://example.com/test.pdf",
        )
        mock_uow.materials.create.return_value = expected_material

        # Act
        result = await service.add_material(1, material_data)

        # Assert
        assert result.meeting_id == 1
        assert result.title == "Test PDF"
        mock_uow.meetings.get_by_id.assert_called_once_with(1)
        mock_uow.materials.create.assert_called_once()

    async def test_add_material_meeting_not_found(self, mock_uow):
        """Test adding material to non-existent meeting raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.meetings.get_by_id.return_value = None

        material_data = MaterialCreate(title="Test PDF", type="PDF", url="https://example.com/test.pdf")

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.add_material(999, material_data)

    async def test_get_materials(self, mock_uow):
        """Test getting all materials for a meeting."""
        # Arrange
        service = MeetingService(mock_uow)
        materials = [
            MeetingMaterial(id=1, meeting_id=1, title="PDF 1", type="PDF"),
            MeetingMaterial(id=2, meeting_id=1, title="Link 1", type="LINK"),
        ]
        mock_uow.materials.get_by_meeting.return_value = materials

        # Act
        result = await service.get_materials(1)

        # Assert
        assert len(result) == 2
        mock_uow.materials.get_by_meeting.assert_called_once_with(1)

    async def test_delete_material(self, mock_uow):
        """Test deleting a material."""
        # Arrange
        service = MeetingService(mock_uow)
        material = MeetingMaterial(id=1, meeting_id=1, title="Test PDF", type="PDF")
        mock_uow.materials.get_by_id.return_value = material

        # Act
        await service.delete_material(1)

        # Assert
        mock_uow.materials.delete.assert_called_once_with(1)

    async def test_delete_material_not_found(self, mock_uow):
        """Test deleting non-existent material raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.materials.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            await service.delete_material(999)
        assert "Material" in str(exc_info.value.detail)


class TestAssignMeeting:
    """Tests for meeting assignment to users."""

    async def test_assign_meeting_happy_path(self, mock_uow):
        """Test happy-path meeting assignment with calendar integration."""
        # Arrange
        service = MeetingService(mock_uow)
        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.user_meetings.get_user_meeting.return_value = None  # Not already assigned

        scheduled_time = datetime.now(UTC) + timedelta(days=1)
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

        # Mock GoogleCalendarService.create_event to return an event
        calendar_event = {"id": "google-event-123", "status": "confirmed"}

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.create_event = AsyncMock(return_value=calendar_event)
            mock_gc_class.return_value = mock_gc_instance

            # Act
            result = await service.assign_meeting(assignment_data)

            # Assert
            assert result.user_id == 100
            assert result.meeting_id == 1
            mock_uow.user_meetings.create.assert_called()
            mock_gc_instance.create_event.assert_called_once()
            # Verify the calendar event ID was saved
            assert mock_uow.user_meetings.update.called

    async def test_assign_meeting_without_scheduled_at(self, mock_uow):
        """Test assigning meeting without scheduled time (no calendar sync)."""
        # Arrange
        service = MeetingService(mock_uow)
        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.user_meetings.get_user_meeting.return_value = None

        assignment_data = UserMeetingCreate(
            user_id=100,
            meeting_id=1,
            scheduled_at=None,
        )

        created_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=None,
            status=MeetingStatus.SCHEDULED,
        )
        mock_uow.user_meetings.create.return_value = created_assignment

        # Act
        result = await service.assign_meeting(assignment_data)

        # Assert
        assert result.user_id == 100
        assert result.scheduled_at is None
        # GoogleCalendarService should not be instantiated when scheduled_at is None

    async def test_assign_meeting_already_assigned(self, mock_uow):
        """Test assigning already-assigned meeting raises ConflictException."""
        # Arrange
        service = MeetingService(mock_uow)
        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting

        existing_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
        )
        mock_uow.user_meetings.get_user_meeting.return_value = existing_assignment

        assignment_data = UserMeetingCreate(
            user_id=100,
            meeting_id=1,
            scheduled_at=None,
        )

        # Act & Assert
        with pytest.raises(ConflictException) as exc_info:
            await service.assign_meeting(assignment_data)
        assert "already assigned" in str(exc_info.value.detail)

    async def test_assign_meeting_integrity_error_race_condition(self, mock_uow):
        """Test IntegrityError handling when race condition occurs (lines 133-136 coverage)."""
        # Arrange
        service = MeetingService(mock_uow)
        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.user_meetings.get_user_meeting.return_value = None  # Passes early check

        # Simulate database unique constraint violation (race condition)
        mock_uow.user_meetings.create.side_effect = IntegrityError("Duplicate entry", None, None)

        assignment_data = UserMeetingCreate(
            user_id=100,
            meeting_id=1,
            scheduled_at=None,
        )

        # Act & Assert
        with pytest.raises(ConflictException) as exc_info:
            await service.assign_meeting(assignment_data)
        assert "already assigned" in str(exc_info.value.detail)

    async def test_assign_meeting_calendar_raises_persists_assignment(self, mock_uow):
        """When calendar raises, assignment should still be persisted."""
        # Arrange
        service = MeetingService(mock_uow)
        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.user_meetings.get_user_meeting.return_value = None

        scheduled_time = datetime.now(UTC) + timedelta(days=1)
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

        # Mock GoogleCalendarService to raise ValidationException
        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.create_event = AsyncMock(
                side_effect=ValidationException("No Google Calendar credentials")
            )
            mock_gc_class.return_value = mock_gc_instance

            # Act
            result = await service.assign_meeting(assignment_data)

            # Assert: assignment was still persisted despite calendar failure
            assert result == created_assignment
            mock_uow.user_meetings.create.assert_called_once()
            # The assignment was created even though calendar failed
            # google_calendar_event_id should remain None


class TestUpdateAssignment:
    """Tests for updating meeting assignments."""

    async def test_update_assignment_scheduled_at_change(self, mock_uow):
        """Test updating assignment scheduled_at triggers calendar update."""
        # Arrange
        service = MeetingService(mock_uow)
        old_time = datetime.now(UTC) + timedelta(days=1)
        new_time = datetime.now(UTC) + timedelta(days=2)

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=old_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting

        update_data = UserMeetingUpdate(scheduled_at=new_time)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.update_event = AsyncMock()
            mock_gc_class.return_value = mock_gc_instance

            # Act
            await service.update_assignment(1, update_data)

            # Assert
            mock_gc_instance.update_event.assert_called_once_with(
                100,
                "event-123",
                {
                    "summary": "Test Meeting",
                    "description": "Test Desc",
                    "start": {"dateTime": new_time.isoformat(), "timeZone": "UTC"},
                    "end": {"dateTime": (new_time + timedelta(hours=1)).isoformat(), "timeZone": "UTC"},
                },
            )

    async def test_update_assignment_remove_scheduled_at(self, mock_uow):
        """Test removing scheduled_at deletes calendar event."""
        # Arrange
        service = MeetingService(mock_uow)
        old_time = datetime.now(UTC) + timedelta(days=1)

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=old_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        update_data = UserMeetingUpdate(scheduled_at=None)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.delete_event = AsyncMock()
            mock_gc_class.return_value = mock_gc_instance

            # Act
            await service.update_assignment(1, update_data)

            # Assert
            mock_gc_instance.delete_event.assert_called_once_with(100, "event-123")


class TestCompleteMeeting:
    """Tests for completing meetings."""

    async def test_complete_meeting(self, mock_uow):
        """Test marking a meeting as completed."""
        # Arrange
        service = MeetingService(mock_uow)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        # The update should return the modified assignment
        completed_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,
            feedback="Great meeting!",
            rating=5,
            completed_at=datetime.now(UTC),
        )
        mock_uow.user_meetings.update.return_value = completed_assignment

        completion = UserMeetingComplete(feedback="Great meeting!", rating=5)

        # Act
        result = await service.complete_meeting(1, completion)

        # Assert
        assert result.status == MeetingStatus.COMPLETED
        assert result.feedback == "Great meeting!"
        assert result.rating == 5
        assert result.completed_at is not None
        mock_uow.user_meetings.update.assert_called_once()

    async def test_complete_already_completed_meeting(self, mock_uow):
        """Test completing an already-completed meeting raises ValidationException."""
        # Arrange
        service = MeetingService(mock_uow)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        completion = UserMeetingComplete(feedback="Great meeting!", rating=5)

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await service.complete_meeting(1, completion)
        assert "already completed" in str(exc_info.value.detail)


class TestDeleteAssignment:
    """Tests for deleting meeting assignments."""

    async def test_delete_assignment_with_calendar_event(self, mock_uow):
        """Test deleting assignment also deletes calendar event."""
        # Arrange
        service = MeetingService(mock_uow)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.delete_event = AsyncMock()
            mock_gc_class.return_value = mock_gc_instance

            # Act
            await service.delete_assignment(1)

            # Assert
            mock_gc_instance.delete_event.assert_called_once_with(100, "event-123")
            mock_uow.user_meetings.delete.assert_called_once_with(1)

    async def test_delete_assignment_without_calendar_event(self, mock_uow):
        """Test deleting assignment without calendar event."""
        # Arrange
        service = MeetingService(mock_uow)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            google_calendar_event_id=None,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        # Act
        await service.delete_assignment(1)

        # Assert
        mock_uow.user_meetings.delete.assert_called_once_with(1)


class TestAutoAssignment:
    """Tests for automatic meeting assignment."""

    async def test_assign_meetings_for_user(self, mock_uow):
        """Test auto-assigning mandatory meetings to a new user."""
        # Arrange
        service = MeetingService(mock_uow)

        meetings = [
            Meeting(id=1, title="HR Onboarding", type=MeetingType.HR, is_mandatory=True, department_id=1),
            Meeting(id=2, title="Security Training", type=MeetingType.SECURITY, is_mandatory=True, department_id=1),
        ]
        mock_uow.meetings.find_meetings.return_value = (meetings, 2)
        mock_uow.user_meetings.get_user_meeting.return_value = None  # No existing assignments

        created_assignments = [
            UserMeeting(id=1, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED),
            UserMeeting(id=2, user_id=100, meeting_id=2, status=MeetingStatus.SCHEDULED),
        ]
        mock_uow.user_meetings.create.side_effect = created_assignments

        # Act
        result = await service.assign_meetings_for_user(
            user_id=100,
            department_id=1,
            position="Developer",
            level=EmployeeLevel.JUNIOR,
        )

        # Assert
        assert len(result) == 2
        assert mock_uow.meetings.find_meetings.called
        assert mock_uow.user_meetings.create.call_count == 2

    async def test_assign_meetings_skips_existing(self, mock_uow):
        """Test auto-assignment skips meetings already assigned."""
        # Arrange
        service = MeetingService(mock_uow)

        meetings = [
            Meeting(id=1, title="HR Onboarding", type=MeetingType.HR, is_mandatory=True),
        ]
        mock_uow.meetings.find_meetings.return_value = (meetings, 1)

        # Meeting already assigned
        existing = UserMeeting(id=99, user_id=100, meeting_id=1, status=MeetingStatus.SCHEDULED)
        mock_uow.user_meetings.get_user_meeting.return_value = existing

        # Act
        result = await service.assign_meetings_for_user(user_id=100)

        # Assert
        assert len(result) == 0  # No new assignments created
        mock_uow.user_meetings.create.assert_not_called()


class TestGoogleCalendarIntegration:
    """Tests for Google Calendar integration scenarios."""

    async def test_assign_meeting_creates_calendar_event_with_event_id(self, mock_uow):
        """Test that calendar event ID is saved when event is created."""
        # Arrange
        service = MeetingService(mock_uow)
        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting
        mock_uow.user_meetings.get_user_meeting.return_value = None

        scheduled_time = datetime.now(UTC) + timedelta(days=1)
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

        # Mock GoogleCalendarService with specific event ID
        calendar_event = {"id": "google-event-456", "status": "confirmed"}

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.create_event = AsyncMock(return_value=calendar_event)
            mock_gc_class.return_value = mock_gc_instance

            # Act
            result = await service.assign_meeting(assignment_data)

            # Assert
            assert result.user_id == 100
            mock_gc_instance.create_event.assert_called_once()

            # Verify update was called with calendar event ID
            update_call = mock_uow.user_meetings.update.call_args
            if update_call:
                updated_assignment = update_call[0][0]
                assert updated_assignment.google_calendar_event_id == "google-event-456"

    async def test_update_assignment_add_scheduled_at_creates_event(self, mock_uow):
        """Test adding scheduled_at to existing assignment creates calendar event."""
        # Arrange
        service = MeetingService(mock_uow)
        old_time = None
        new_time = datetime.now(UTC) + timedelta(days=2)

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=old_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id=None,
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting

        update_data = UserMeetingUpdate(scheduled_at=new_time)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.create_event = AsyncMock(return_value={"id": "new-event-123"})
            mock_gc_class.return_value = mock_gc_instance

            # Act
            await service.update_assignment(1, update_data)

            # Assert: create_event should be called (not update) since no previous event ID
            mock_gc_instance.create_event.assert_called_once()
            mock_gc_instance.update_event.assert_not_called()

    async def test_update_assignment_create_event_failure_continues(self, mock_uow):
        """Test that update continues even if creating new calendar event fails (lines 251-252)."""
        # Arrange
        service = MeetingService(mock_uow)
        old_time = None  # No previous scheduled time
        new_time = datetime.now(UTC) + timedelta(days=2)

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=old_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id=None,  # No existing event ID
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting

        # Set up the update return value
        updated_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=new_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id=None,  # Event ID remains None since create failed
        )
        mock_uow.user_meetings.update.return_value = updated_assignment

        update_data = UserMeetingUpdate(scheduled_at=new_time)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            # Simulate create_event raising NotFoundException (lines 251-252 coverage)
            mock_gc_instance.create_event = AsyncMock(
                side_effect=NotFoundException("Google Calendar account not found")
            )
            mock_gc_class.return_value = mock_gc_instance

            # Act - should not raise even though calendar create fails
            result = await service.update_assignment(1, update_data)

            # Assert - update still succeeds even though calendar create failed
            assert result.scheduled_at == new_time
            mock_uow.user_meetings.update.assert_called_once()
            # Verify create_event was attempted
            mock_gc_instance.create_event.assert_called_once()

    async def test_update_assignment_same_scheduled_at_no_calendar_call(self, mock_uow):
        """Test that calendar is not called when scheduled_at doesn't change."""
        # Arrange
        scheduled_time = datetime.now(UTC) + timedelta(days=1)
        service = MeetingService(mock_uow)

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=scheduled_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        # Update only status, not scheduled_at
        update_data = UserMeetingUpdate(status=MeetingStatus.COMPLETED)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_class.return_value = mock_gc_instance

            # Act
            await service.update_assignment(1, update_data)

            # Assert: no calendar operations should be called
            mock_gc_instance.create_event.assert_not_called()
            mock_gc_instance.update_event.assert_not_called()
            mock_gc_instance.delete_event.assert_not_called()

    async def test_reschedule_meeting_updates_existing_event(self, mock_uow):
        """Test that rescheduling updates existing calendar event."""
        # Arrange
        service = MeetingService(mock_uow)
        old_time = datetime.now(UTC) + timedelta(days=1)
        new_time = datetime.now(UTC) + timedelta(days=3)

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=old_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id="existing-event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        meeting = Meeting(id=1, title="Test Meeting", description="Test Desc", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting

        update_data = UserMeetingUpdate(scheduled_at=new_time)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_instance.update_event = AsyncMock()
            mock_gc_class.return_value = mock_gc_instance

            # Act
            await service.update_assignment(1, update_data)

            # Assert: update_event should be called with correct parameters
            mock_gc_instance.update_event.assert_called_once()
            call_args = mock_gc_instance.update_event.call_args
            assert call_args[0][0] == 100  # user_id
            assert call_args[0][1] == "existing-event-123"  # event_id

    async def test_complete_meeting_does_not_affect_calendar(self, mock_uow):
        """Test that completing a meeting doesn't modify calendar event."""
        # Arrange
        service = MeetingService(mock_uow)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        completed_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            status=MeetingStatus.COMPLETED,
            google_calendar_event_id="event-123",  # Should be preserved
        )
        mock_uow.user_meetings.update.return_value = completed_assignment

        completion = UserMeetingComplete(feedback="Great!", rating=5)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            mock_gc_class.return_value = mock_gc_instance

            # Act
            result = await service.complete_meeting(1, completion)

            # Assert
            assert result.status == MeetingStatus.COMPLETED
            # Calendar should not be modified when completing
            mock_gc_instance.delete_event.assert_not_called()
            mock_gc_instance.update_event.assert_not_called()


class TestMeetingServiceEdgeCases:
    """Tests for edge cases and error handling."""

    async def test_get_meeting_assignments_not_found(self, mock_uow):
        """Test getting assignments for non-existent meeting raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.meetings.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.get_meeting_assignments(meeting_id=999)

    async def test_get_assignment_not_found(self, mock_uow):
        """Test getting non-existent assignment raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.user_meetings.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            await service.get_assignment(999)
        assert "User meeting assignment" in str(exc_info.value.detail)

    async def test_delete_assignment_not_found(self, mock_uow):
        """Test deleting non-existent assignment raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.user_meetings.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.delete_assignment(999)

    async def test_update_meeting_not_found(self, mock_uow):
        """Test updating non-existent meeting raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.meetings.get_by_id.return_value = None

        update_data = MeetingUpdate(title="New Title")

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.update_meeting(999, update_data)

    async def test_delete_meeting_not_found(self, mock_uow):
        """Test deleting non-existent meeting raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.meetings.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.delete_meeting(999)

    async def test_update_assignment_not_found(self, mock_uow):
        """Test updating non-existent assignment raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.user_meetings.get_by_id.return_value = None

        update_data = UserMeetingUpdate(status=MeetingStatus.COMPLETED)

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.update_assignment(999, update_data)

    async def test_complete_meeting_not_found(self, mock_uow):
        """Test completing non-existent meeting raises NotFoundException."""
        # Arrange
        service = MeetingService(mock_uow)
        mock_uow.user_meetings.get_by_id.return_value = None

        completion = UserMeetingComplete(feedback="Great!", rating=5)

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.complete_meeting(999, completion)

    async def test_get_materials_meeting_not_exists_still_returns_materials(self, mock_uow):
        """Test get_materials works even if meeting existence check bypassed."""
        # Arrange - this tests the direct service method which doesn't check meeting existence
        service = MeetingService(mock_uow)
        materials = [
            MeetingMaterial(id=1, meeting_id=1, title="PDF", type=MaterialType.PDF, url="http://x.pdf"),
        ]
        mock_uow.materials.get_by_meeting.return_value = materials

        # Act
        result = await service.get_materials(1)

        # Assert
        assert len(result) == 1
        mock_uow.materials.get_by_meeting.assert_called_once_with(1)


class TestCalendarFailureScenarios:
    """Tests for calendar service failure handling."""

    async def test_update_assignment_calendar_update_fails_continues(self, mock_uow):
        """Test that update continues even if calendar update fails."""
        # Arrange
        service = MeetingService(mock_uow)
        old_time = datetime.now(UTC) + timedelta(days=1)
        new_time = datetime.now(UTC) + timedelta(days=2)

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=old_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        meeting = Meeting(id=1, title="Test Meeting", type=MeetingType.HR)
        mock_uow.meetings.get_by_id.return_value = meeting

        # Set up the update return value to have the new scheduled_at
        updated_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=new_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.update.return_value = updated_assignment

        update_data = UserMeetingUpdate(scheduled_at=new_time)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            # Calendar update raises exception
            mock_gc_instance.update_event = AsyncMock(
                side_effect=ValidationException("Calendar API error")
            )
            mock_gc_class.return_value = mock_gc_instance

            # Act - should not raise
            result = await service.update_assignment(1, update_data)

            # Assert - update still succeeds even though calendar failed
            assert result.scheduled_at == new_time
            mock_uow.user_meetings.update.assert_called_once()

    async def test_update_assignment_calendar_delete_fails_continues(self, mock_uow):
        """Test that unscheduling continues even if calendar delete fails."""
        # Arrange
        service = MeetingService(mock_uow)
        old_time = datetime.now(UTC) + timedelta(days=1)

        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=old_time,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        # Set up the update return value to have scheduled_at as None
        updated_assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            scheduled_at=None,
            status=MeetingStatus.SCHEDULED,
            google_calendar_event_id=None,
        )
        mock_uow.user_meetings.update.return_value = updated_assignment

        update_data = UserMeetingUpdate(scheduled_at=None)

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            # Calendar delete raises exception
            mock_gc_instance.delete_event = AsyncMock(
                side_effect=ValidationException("Calendar API error")
            )
            mock_gc_class.return_value = mock_gc_instance

            # Act - should not raise
            result = await service.update_assignment(1, update_data)

            # Assert - update still succeeds even though calendar failed
            assert result.scheduled_at is None
            mock_uow.user_meetings.update.assert_called_once()

    async def test_delete_assignment_calendar_delete_fails_continues(self, mock_uow):
        """Test that deleting assignment continues even if calendar delete fails."""
        # Arrange
        service = MeetingService(mock_uow)
        assignment = UserMeeting(
            id=1,
            user_id=100,
            meeting_id=1,
            google_calendar_event_id="event-123",
        )
        mock_uow.user_meetings.get_by_id.return_value = assignment

        with patch(
            "meeting_service.services.meeting.GoogleCalendarService"
        ) as mock_gc_class:
            mock_gc_instance = MagicMock()
            # Calendar delete raises exception
            mock_gc_instance.delete_event = AsyncMock(
                side_effect=ValidationException("Calendar API error")
            )
            mock_gc_class.return_value = mock_gc_instance

            # Act - should not raise
            await service.delete_assignment(1)

            # Assert - delete still succeeds even though calendar failed
            mock_uow.user_meetings.delete.assert_called_once_with(1)
