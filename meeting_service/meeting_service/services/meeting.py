"""Meeting management service with repository pattern."""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError

from meeting_service.core import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from meeting_service.core.enums import EmployeeLevel, MeetingStatus, MeetingType
from meeting_service.models import Meeting, MeetingMaterial, UserMeeting
from meeting_service.repositories.unit_of_work import IUnitOfWork
from meeting_service.schemas import (
    MaterialCreate,
    MeetingCreate,
    MeetingUpdate,
    UserMeetingComplete,
    UserMeetingCreate,
    UserMeetingUpdate,
)
from meeting_service.services.google_calendar_service import GoogleCalendarService

logger = logging.getLogger(__name__)


class MeetingService:
    """Service for meeting management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize MeetingService with Unit of Work."""
        self._uow = uow

    # --- Meeting templates ---
    async def create_meeting(self, meeting_data: MeetingCreate) -> Meeting:
        """Create a new meeting template."""
        meeting = Meeting(**meeting_data.model_dump())
        created = await self._uow.meetings.create(meeting)
        await self._uow.commit()
        return created

    async def get_meeting(self, meeting_id: int) -> Meeting:
        """Get meeting template by ID."""
        meeting = await self._uow.meetings.get_by_id(meeting_id)
        if not meeting:
            msg = "Meeting"
            raise NotFoundException(msg)
        return meeting

    async def update_meeting(self, meeting_id: int, meeting_data: MeetingUpdate) -> Meeting:
        """Update meeting template."""
        meeting = await self.get_meeting(meeting_id)
        update_data = meeting_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meeting, field, value)
        meeting.updated_at = datetime.now(UTC)
        return await self._uow.meetings.update(meeting)

    async def delete_meeting(self, meeting_id: int) -> None:
        """Delete meeting template (and all related materials, assignments)."""
        meeting = await self.get_meeting(meeting_id)
        await self._uow.meetings.delete(meeting.id)

    async def get_meetings(
        self,
        skip: int = 0,
        limit: int = 100,
        meeting_type: MeetingType | None = None,
        department_id: int | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
        *,
        is_mandatory: bool | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[Meeting], int]:
        """Get paginated list of meeting templates with filters."""
        meetings, total = await self._uow.meetings.find_meetings(
            skip=skip,
            limit=limit,
            meeting_type=meeting_type,
            department_id=department_id,
            position=position,
            level=level,
            is_mandatory=is_mandatory,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return list(meetings), total

    # --- Materials ---
    async def add_material(self, meeting_id: int, material_data: MaterialCreate) -> MeetingMaterial:
        """Add a material to a meeting template."""
        await self.get_meeting(meeting_id)  # ensure meeting exists
        material = MeetingMaterial(meeting_id=meeting_id, **material_data.model_dump())
        return await self._uow.materials.create(material)

    async def get_materials(self, meeting_id: int) -> list[MeetingMaterial]:
        """Get all materials for a meeting."""
        materials = await self._uow.materials.get_by_meeting(meeting_id)
        return list(materials)

    async def delete_material(self, material_id: int) -> None:
        """Delete a material."""
        material = await self._uow.materials.get_by_id(material_id)
        if not material:
            msg = "Material"
            raise NotFoundException(msg)
        await self._uow.materials.delete(material.id)

    # --- User assignments ---
    async def assign_meeting(self, assignment_data: UserMeetingCreate) -> UserMeeting:
        """Assign a meeting template to a user."""
        # Validate scheduled_at is in the future if provided
        if assignment_data.scheduled_at:
            # Handle both timezone-aware and naive datetimes
            scheduled_at = assignment_data.scheduled_at
            now = datetime.now(UTC)
            if scheduled_at.tzinfo is None:
                # Treat naive datetime as UTC
                scheduled_at = scheduled_at.replace(tzinfo=UTC)
            if scheduled_at < now:
                msg = "Meeting time must be in the future"
                raise ValidationException(msg)

        # Check if meeting exists
        meeting = await self.get_meeting(assignment_data.meeting_id)

        # Check if already assigned (early check to avoid unnecessary DB operations)
        existing = await self._uow.user_meetings.get_user_meeting(assignment_data.user_id, assignment_data.meeting_id)
        if existing:
            msg = "Meeting already assigned to this user"
            raise ConflictException(msg)

        assignment = UserMeeting(
            user_id=assignment_data.user_id,
            meeting_id=assignment_data.meeting_id,
            scheduled_at=assignment_data.scheduled_at,
            status=MeetingStatus.SCHEDULED,
        )
        try:
            created_assignment = await self._uow.user_meetings.create(assignment)
        except IntegrityError as e:
            # Database unique constraint violated - race condition protection
            msg = "Meeting already assigned to this user"
            raise ConflictException(msg) from e

        # Try to create Google Calendar event if scheduled_at is provided
        if assignment_data.scheduled_at:
            try:
                gc_service = GoogleCalendarService(self._uow)
                event_data = {
                    "summary": meeting.title,
                    "description": meeting.description,
                    "start": {
                        "dateTime": assignment_data.scheduled_at.isoformat(),
                        "timeZone": "UTC",
                    },
                    "end": {
                        "dateTime": (assignment_data.scheduled_at + timedelta(minutes=meeting.duration_minutes)).isoformat(),
                        "timeZone": "UTC",
                    },
                }
                event = await gc_service.create_event(assignment_data.user_id, event_data)
                created_assignment.google_calendar_event_id = event["id"]
                await self._uow.user_meetings.update(created_assignment)
                logger.info("Created Google Calendar event %s for user %s", event["id"], assignment_data.user_id)
            except (ValidationException, NotFoundException) as e:
                # Don't fail the assignment if calendar sync fails
                logger.warning("Failed to create Google Calendar event: %s", e)

        await self._uow.commit()
        return created_assignment

    async def get_user_meetings(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: MeetingStatus | None = None,
    ) -> tuple[list[UserMeeting], int]:
        """Get meetings assigned to a specific user."""
        items, total = await self._uow.user_meetings.find_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        return list(items), total

    async def get_meeting_assignments(
        self,
        meeting_id: int,
        skip: int = 0,
        limit: int = 100,
        status: MeetingStatus | None = None,
    ) -> tuple[list[UserMeeting], int]:
        """Get all user assignments for a specific meeting template."""
        await self.get_meeting(meeting_id)  # ensure meeting exists
        items, total = await self._uow.user_meetings.find_by_meeting(
            meeting_id=meeting_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        return list(items), total

    async def get_assignment(self, assignment_id: int) -> UserMeeting:
        """Get a specific user meeting assignment by its ID."""
        item = await self._uow.user_meetings.get_by_id(assignment_id)
        if not item:
            msg = "User meeting assignment"
            raise NotFoundException(msg)
        return item

    async def update_assignment(self, assignment_id: int, update_data: UserMeetingUpdate) -> UserMeeting:
        """Update a user meeting assignment (status, scheduled_at)."""
        assignment = await self.get_assignment(assignment_id)
        update_dict = update_data.model_dump(exclude_unset=True)

        # Handle Google Calendar sync if scheduled_at changes
        if "scheduled_at" in update_dict:
            new_scheduled_at = update_dict["scheduled_at"]
            old_scheduled_at = assignment.scheduled_at

            # Validate new scheduled_at is in the future if provided
            if new_scheduled_at and new_scheduled_at < datetime.now(UTC):
                msg = "Meeting time must be in the future"
                raise ValidationException(msg)

            # Only proceed if the time actually changed
            if new_scheduled_at != old_scheduled_at:
                gc_service = GoogleCalendarService(self._uow)

                if new_scheduled_at is None:
                    # Delete event if scheduled_at is removed
                    if assignment.google_calendar_event_id:
                        try:
                            await gc_service.delete_event(assignment.user_id, assignment.google_calendar_event_id)
                            logger.info(
                                "Deleted Google Calendar event %s due to unscheduling",
                                assignment.google_calendar_event_id,
                            )
                            assignment.google_calendar_event_id = None
                        except (ValidationException, NotFoundException) as e:
                            logger.warning("Failed to delete Google Calendar event: %s", e)
                else:
                    # Need meeting details for event data
                    meeting = await self.get_meeting(assignment.meeting_id)
                    event_data = {
                        "summary": meeting.title,
                        "description": meeting.description,
                        "start": {
                            "dateTime": new_scheduled_at.isoformat(),
                            "timeZone": "UTC",
                        },
                        "end": {
                            "dateTime": (new_scheduled_at + timedelta(minutes=meeting.duration_minutes)).isoformat(),
                            "timeZone": "UTC",
                        },
                    }

                    if assignment.google_calendar_event_id:
                        # Update existing event
                        try:
                            await gc_service.update_event(
                                assignment.user_id, assignment.google_calendar_event_id, event_data
                            )
                            logger.info("Updated Google Calendar event %s", assignment.google_calendar_event_id)
                        except (ValidationException, NotFoundException) as e:
                            logger.warning("Failed to update Google Calendar event: %s", e)
                    else:
                        # Create new event
                        try:
                            event = await gc_service.create_event(assignment.user_id, event_data)
                            assignment.google_calendar_event_id = event["id"]
                            logger.info("Created Google Calendar event %s for user %s", event["id"], assignment.user_id)
                        except (ValidationException, NotFoundException) as e:
                            logger.warning("Failed to create Google Calendar event: %s", e)

        for field, value in update_dict.items():
            setattr(assignment, field, value)
        assignment.updated_at = datetime.now(UTC)
        return await self._uow.user_meetings.update(assignment)

    async def complete_meeting(self, assignment_id: int, completion: UserMeetingComplete) -> UserMeeting:
        """Mark a user meeting as completed with feedback and rating."""
        assignment = await self.get_assignment(assignment_id)
        if assignment.status == MeetingStatus.COMPLETED:
            msg = "Meeting already completed"
            raise ValidationException(msg)

        assignment.status = MeetingStatus.COMPLETED
        assignment.completed_at = datetime.now(UTC)
        assignment.feedback = completion.feedback
        assignment.rating = completion.rating
        assignment.updated_at = datetime.now(UTC)
        return await self._uow.user_meetings.update(assignment)

    async def delete_assignment(self, assignment_id: int) -> None:
        """Delete a user meeting assignment (e.g., cancel)."""
        assignment = await self.get_assignment(assignment_id)

        # Delete Google Calendar event if it exists
        if assignment.google_calendar_event_id:
            try:
                gc_service = GoogleCalendarService(self._uow)
                await gc_service.delete_event(assignment.user_id, assignment.google_calendar_event_id)
                logger.info(
                    "Deleted Google Calendar event %s for user %s",
                    assignment.google_calendar_event_id,
                    assignment.user_id,
                )
            except (ValidationException, NotFoundException) as e:
                logger.warning("Failed to delete Google Calendar event: %s", e)

        await self._uow.user_meetings.delete(assignment.id)

    # --- Auto-assignment for new user ---
    async def assign_meetings_for_user(
        self,
        user_id: int,
        department_id: int | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
    ) -> list[UserMeeting]:
        """Automatically assign all mandatory meetings matching user's department/position/level."""
        # Find all meetings that match the user's attributes (or have null targeting)
        meetings, _ = await self._uow.meetings.find_meetings(
            is_mandatory=True,
            department_id=department_id,
            position=position,
            level=level,
        )
        created = []
        for meeting in meetings:
            # Avoid duplicate assignment
            existing = await self._uow.user_meetings.get_user_meeting(user_id, meeting.id)
            if not existing:
                assignment = UserMeeting(
                    user_id=user_id,
                    meeting_id=meeting.id,
                    scheduled_at=None,  # can be set later by HR
                    status=MeetingStatus.SCHEDULED,
                )
                created.append(await self._uow.user_meetings.create(assignment))
        return created
