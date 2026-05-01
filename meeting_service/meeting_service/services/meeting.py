"""Meeting management service with repository pattern."""

from datetime import UTC, datetime, timedelta

from loguru import logger
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


class MeetingService:
    """Service for meeting management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize MeetingService with Unit of Work."""
        self._uow = uow

    # --- Meeting templates ---
    async def create_meeting(self, meeting_data: MeetingCreate) -> Meeting:
        """Create a new meeting template."""
        logger.debug(
            "Creating meeting (title={}, type={}, department_id={}, position={})",
            meeting_data.title,
            meeting_data.type,
            meeting_data.department_id,
            meeting_data.position,
        )
        meeting = Meeting(**meeting_data.model_dump())
        created = await self._uow.meetings.create(meeting)
        await self._uow.commit()
        logger.info("Meeting created (meeting_id={}, title={})", created.id, created.title)
        return created

    async def get_meeting(self, meeting_id: int) -> Meeting:
        """Get meeting template by ID."""
        logger.debug("Fetching meeting (meeting_id={})", meeting_id)
        meeting = await self._uow.meetings.get_by_id(meeting_id)
        if not meeting:
            logger.warning("Meeting not found (meeting_id={})", meeting_id)
            msg = "Meeting"
            raise NotFoundException(msg)
        return meeting

    async def update_meeting(self, meeting_id: int, meeting_data: MeetingUpdate) -> Meeting:
        """Update meeting template."""
        logger.debug("Updating meeting (meeting_id={})", meeting_id)
        meeting = await self.get_meeting(meeting_id)
        update_data = meeting_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meeting, field, value)
        meeting.updated_at = datetime.now(UTC)
        updated = await self._uow.meetings.update(meeting)
        logger.info("Meeting updated (meeting_id={})", updated.id)
        return updated

    async def delete_meeting(self, meeting_id: int) -> None:
        """Delete meeting template (and all related materials, assignments)."""
        logger.debug("Deleting meeting (meeting_id={})", meeting_id)
        meeting = await self.get_meeting(meeting_id)
        await self._uow.meetings.delete(meeting.id)
        logger.info("Meeting deleted (meeting_id={})", meeting_id)

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
        logger.debug(
            "Listing meetings (skip={}, limit={}, type={}, department_id={}, search_present={})",
            skip,
            limit,
            meeting_type,
            department_id,
            bool(search),
        )
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
        logger.debug("Meetings listed (count={}, total={})", len(list(meetings)), total)
        return list(meetings), total

    # --- Materials ---
    async def add_material(self, meeting_id: int, material_data: MaterialCreate) -> MeetingMaterial:
        """Add a material to a meeting template."""
        logger.debug("Adding material to meeting (meeting_id={}, title={})", meeting_id, material_data.title)
        await self.get_meeting(meeting_id)  # ensure meeting exists
        material = MeetingMaterial(meeting_id=meeting_id, **material_data.model_dump())
        created = await self._uow.materials.create(material)
        logger.info("Material added (material_id={}, meeting_id={})", created.id, meeting_id)
        return created

    async def get_materials(self, meeting_id: int) -> list[MeetingMaterial]:
        """Get all materials for a meeting."""
        logger.debug("Fetching materials for meeting (meeting_id={})", meeting_id)
        materials = await self._uow.materials.get_by_meeting(meeting_id)
        logger.debug("Materials fetched (meeting_id={}, count={})", meeting_id, len(list(materials)))
        return list(materials)

    async def delete_material(self, material_id: int) -> None:
        """Delete a material."""
        logger.debug("Deleting material (material_id={})", material_id)
        material = await self._uow.materials.get_by_id(material_id)
        if not material:
            logger.warning("Material not found (material_id={})", material_id)
            msg = "Material"
            raise NotFoundException(msg)
        await self._uow.materials.delete(material.id)
        logger.info("Material deleted (material_id={})", material_id)

    # --- User assignments ---
    async def assign_meeting(self, assignment_data: UserMeetingCreate) -> UserMeeting:
        """Assign a meeting template to a user."""
        logger.debug(
            "Assigning meeting (user_id={}, meeting_id={}, scheduled_at={})",
            assignment_data.user_id,
            assignment_data.meeting_id,
            assignment_data.scheduled_at,
        )
        # Validate scheduled_at is in the future if provided
        if assignment_data.scheduled_at:
            # Handle both timezone-aware and naive datetimes
            scheduled_at = assignment_data.scheduled_at
            now = datetime.now(UTC)
            if scheduled_at.tzinfo is None:
                # Treat naive datetime as UTC
                scheduled_at = scheduled_at.replace(tzinfo=UTC)
            if scheduled_at < now:
                logger.warning(
                    "Assignment failed: scheduled_at in the past (user_id={}, meeting_id={}, scheduled_at={})",
                    assignment_data.user_id,
                    assignment_data.meeting_id,
                    scheduled_at,
                )
                msg = "Meeting time must be in the future"
                raise ValidationException(msg)

        # Check if meeting exists
        meeting = await self.get_meeting(assignment_data.meeting_id)

        # Check if already assigned (early check to avoid unnecessary DB operations)
        existing = await self._uow.user_meetings.get_user_meeting(assignment_data.user_id, assignment_data.meeting_id)
        if existing:
            logger.warning(
                "Assignment conflict: already assigned (user_id={}, meeting_id={})",
                assignment_data.user_id,
                assignment_data.meeting_id,
            )
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
            logger.warning(
                "Assignment conflict: database integrity error (user_id={}, meeting_id={})",
                assignment_data.user_id,
                assignment_data.meeting_id,
            )
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
                        "dateTime": (
                            assignment_data.scheduled_at + timedelta(minutes=meeting.duration_minutes)
                        ).isoformat(),
                        "timeZone": "UTC",
                    },
                }
                event = await gc_service.create_event(assignment_data.user_id, event_data)
                created_assignment.google_calendar_event_id = event["id"]
                await self._uow.user_meetings.update(created_assignment)
                logger.info("Created Google Calendar event %s for user %s", event["id"], assignment_data.user_id)
            except (ValidationException, NotFoundException) as e:
                # Don't fail the assignment if calendar sync fails
                logger.debug("Skipped Google Calendar sync: %s", e)

        await self._uow.commit()
        logger.info(
            "Meeting assigned (assignment_id={}, user_id={}, meeting_id={})",
            created_assignment.id,
            assignment_data.user_id,
            assignment_data.meeting_id,
        )
        return created_assignment

    async def get_user_meetings(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: MeetingStatus | None = None,
    ) -> tuple[list[UserMeeting], int]:
        """Get meetings assigned to a specific user."""
        logger.debug("Fetching user meetings (user_id={}, status={})", user_id, status)
        items, total = await self._uow.user_meetings.find_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        logger.debug("User meetings fetched (user_id={}, count={}, total={})", user_id, len(list(items)), total)
        return list(items), total

    async def get_meeting_assignments(
        self,
        meeting_id: int,
        skip: int = 0,
        limit: int = 100,
        status: MeetingStatus | None = None,
    ) -> tuple[list[UserMeeting], int]:
        """Get all user assignments for a specific meeting template."""
        logger.debug("Fetching meeting assignments (meeting_id={}, status={})", meeting_id, status)
        await self.get_meeting(meeting_id)  # ensure meeting exists
        items, total = await self._uow.user_meetings.find_by_meeting(
            meeting_id=meeting_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        logger.debug(
            "Meeting assignments fetched (meeting_id={}, count={}, total={})", meeting_id, len(list(items)), total
        )
        return list(items), total

    async def get_assignment(self, assignment_id: int) -> UserMeeting:
        """Get a specific user meeting assignment by its ID."""
        logger.debug("Fetching assignment (assignment_id={})", assignment_id)
        item = await self._uow.user_meetings.get_by_id(assignment_id)
        if not item:
            logger.warning("Assignment not found (assignment_id={})", assignment_id)
            msg = "User meeting assignment"
            raise NotFoundException(msg)
        return item

    async def update_assignment(self, assignment_id: int, update_data: UserMeetingUpdate) -> UserMeeting:
        """Update a user meeting assignment (status, scheduled_at)."""
        logger.debug("Updating assignment (assignment_id={})", assignment_id)
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
                            logger.debug("Skipped Google Calendar sync: %s", e)
                    else:
                        # Create new event
                        try:
                            event = await gc_service.create_event(assignment.user_id, event_data)
                            assignment.google_calendar_event_id = event["id"]
                            logger.info("Created Google Calendar event %s for user %s", event["id"], assignment.user_id)
                        except (ValidationException, NotFoundException) as e:
                            logger.debug("Skipped Google Calendar sync: %s", e)

        for field, value in update_dict.items():
            setattr(assignment, field, value)
        assignment.updated_at = datetime.now(UTC)
        updated = await self._uow.user_meetings.update(assignment)
        logger.info("Assignment updated (assignment_id={})", updated.id)
        return updated

    async def complete_meeting(self, assignment_id: int, completion: UserMeetingComplete) -> UserMeeting:
        """Mark a user meeting as completed with feedback and rating."""
        logger.debug("Completing meeting (assignment_id={})", assignment_id)
        assignment = await self.get_assignment(assignment_id)
        if assignment.status == MeetingStatus.COMPLETED:
            logger.warning("Complete meeting failed: already completed (assignment_id={})", assignment_id)
            msg = "Meeting already completed"
            raise ValidationException(msg)

        assignment.status = MeetingStatus.COMPLETED
        assignment.completed_at = datetime.now(UTC)
        assignment.feedback = completion.feedback
        assignment.rating = completion.rating
        assignment.updated_at = datetime.now(UTC)
        updated = await self._uow.user_meetings.update(assignment)
        logger.info("Meeting completed (assignment_id={})", updated.id)
        return updated

    async def delete_assignment(self, assignment_id: int) -> None:
        """Delete a user meeting assignment (e.g., cancel)."""
        logger.debug("Deleting assignment (assignment_id={})", assignment_id)
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
        logger.info("Assignment deleted (assignment_id={})", assignment_id)

    # --- Auto-assignment for new user ---
    async def assign_meetings_for_user(
        self,
        user_id: int,
        department_id: int | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
    ) -> list[UserMeeting]:
        """Automatically assign all mandatory meetings matching user's department/position/level."""
        logger.info(
            "Auto-assigning meetings for user (user_id={}, department_id={}, position={}, level={})",
            user_id,
            department_id,
            position,
            level,
        )
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
                logger.debug("Auto-assigned meeting (user_id={}, meeting_id={})", user_id, meeting.id)
        logger.info("Auto-assign meetings completed (user_id={}, created_count={})", user_id, len(created))
        return created
