"""Internal maintenance endpoints for feedback data."""

from fastapi import APIRouter
from sqlalchemy import delete, or_, update

from feedback_service.api.deps import ServiceAuth, UOWDep
from feedback_service.models import Comment, ExperienceRating, FeedbackStatusChangeHistory, PulseSurvey

router = APIRouter()


@router.delete("/users/{user_id}")
async def cleanup_user_feedback_data(
    user_id: int,
    uow: UOWDep,
    _service_auth: ServiceAuth,
) -> dict[str, int]:
    """Remove feedback-service data that belongs or points to a deleted user."""
    session = uow._session
    if session is None:
        msg = "Session not initialized"
        raise RuntimeError(msg)

    comments = await session.execute(delete(Comment).where(Comment.user_id == user_id))
    replied_comments = await session.execute(
        update(Comment).where(Comment.replied_by == user_id).values(replied_by=None)
    )
    ratings = await session.execute(delete(ExperienceRating).where(ExperienceRating.user_id == user_id))
    pulse_surveys = await session.execute(delete(PulseSurvey).where(PulseSurvey.user_id == user_id))
    status_history = await session.execute(
        delete(FeedbackStatusChangeHistory).where(
            or_(FeedbackStatusChangeHistory.user_id == user_id, FeedbackStatusChangeHistory.changed_by == user_id)
        )
    )
    await uow.commit()
    return {
        "comments": comments.rowcount or 0,
        "experience_ratings": ratings.rowcount or 0,
        "pulse_surveys": pulse_surveys.rowcount or 0,
        "status_history": status_history.rowcount or 0,
        "updated_comments": replied_comments.rowcount or 0,
    }
