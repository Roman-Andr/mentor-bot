"""Meeting management service with repository pattern."""

from datetime import UTC, datetime

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


class MeetingService:
    """Service for meeting management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize MeetingService with Unit of Work."""
        self._uow = uow

    # --- Meeting templates ---
    async def create_meeting(self, meeting_data: MeetingCreate) -> Meeting:
        """Create a new meeting template."""
        meeting = Meeting(**meeting_data.model_dump())
        return await self._uow.meetings.create(meeting)

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
        department: str | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
        *,
        is_mandatory: bool | None = None,
    ) -> tuple[list[Meeting], int]:
        """Get paginated list of meeting templates with filters."""
        meetings, total = await self._uow.meetings.find_meetings(
            skip=skip,
            limit=limit,
            meeting_type=meeting_type,
            department=department,
            position=position,
            level=level,
            is_mandatory=is_mandatory,
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
        # Check if meeting exists
        await self.get_meeting(assignment_data.meeting_id)

        # Check if already assigned
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
        return await self._uow.user_meetings.create(assignment)

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
        await self._uow.user_meetings.delete(assignment.id)

    # --- Auto-assignment for new user ---
    async def assign_meetings_for_user(
        self,
        user_id: int,
        department: str | None = None,
        position: str | None = None,
        level: EmployeeLevel | None = None,
    ) -> list[UserMeeting]:
        """Automatically assign all mandatory meetings matching user's department/position/level."""
        # Find all meetings that match the user's attributes (or have null targeting)
        meetings, _ = await self._uow.meetings.find_meetings(
            is_mandatory=True,
            department=department,
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
