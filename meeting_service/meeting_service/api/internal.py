"""Internal maintenance endpoints for meeting data."""

from fastapi import APIRouter
from sqlalchemy import delete, or_

from meeting_service.api.deps import ServiceAuth, UOWDep
from meeting_service.models import (
    GoogleCalendarAccount,
    MeetingParticipantHistory,
    MeetingStatusChangeHistory,
    UserMeeting,
)

router = APIRouter()


@router.delete("/users/{user_id}")
async def cleanup_user_meeting_data(
    user_id: int,
    uow: UOWDep,
    _service_auth: ServiceAuth,
) -> dict[str, int]:
    """Remove meeting-service data that belongs or points to a deleted user."""
    session = uow._session
    if session is None:
        msg = "Session not initialized"
        raise RuntimeError(msg)

    calendar_accounts = await session.execute(
        delete(GoogleCalendarAccount).where(GoogleCalendarAccount.user_id == user_id)
    )
    user_meetings = await session.execute(delete(UserMeeting).where(UserMeeting.user_id == user_id))
    participant_history = await session.execute(
        delete(MeetingParticipantHistory).where(MeetingParticipantHistory.user_id == user_id)
    )
    status_history = await session.execute(
        delete(MeetingStatusChangeHistory).where(
            or_(MeetingStatusChangeHistory.user_id == user_id, MeetingStatusChangeHistory.changed_by == user_id)
        )
    )
    await uow.commit()
    return {
        "calendar_accounts": calendar_accounts.rowcount or 0,
        "user_meetings": user_meetings.rowcount or 0,
        "participant_history": participant_history.rowcount or 0,
        "status_history": status_history.rowcount or 0,
    }
