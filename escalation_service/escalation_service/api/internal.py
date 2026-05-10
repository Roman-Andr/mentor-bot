"""Internal maintenance endpoints for escalation data."""

from fastapi import APIRouter
from sqlalchemy import delete, or_, select, update

from escalation_service.api.deps import ServiceAuth, UOWDep
from escalation_service.models import EscalationRequest, EscalationStatusHistory, MentorInterventionHistory

router = APIRouter()


@router.delete("/users/{user_id}")
async def cleanup_user_escalation_data(
    user_id: int,
    uow: UOWDep,
    _service_auth: ServiceAuth,
) -> dict[str, int]:
    """Remove escalation-service data that belongs or points to a deleted user."""
    session = uow._session
    if session is None:
        msg = "Session not initialized"
        raise RuntimeError(msg)

    escalation_ids = list(
        (await session.execute(select(EscalationRequest.id).where(EscalationRequest.user_id == user_id))).scalars()
    )

    status_history = await session.execute(
        delete(EscalationStatusHistory).where(
            or_(EscalationStatusHistory.user_id == user_id, EscalationStatusHistory.changed_by == user_id)
        )
    )
    mentor_history = await session.execute(
        delete(MentorInterventionHistory).where(MentorInterventionHistory.mentor_id == user_id)
    )

    status_by_escalation = 0
    mentor_by_escalation = 0
    escalation_count = 0
    if escalation_ids:
        status_by_escalation_result = await session.execute(
            delete(EscalationStatusHistory).where(EscalationStatusHistory.escalation_id.in_(escalation_ids))
        )
        mentor_by_escalation_result = await session.execute(
            delete(MentorInterventionHistory).where(MentorInterventionHistory.escalation_id.in_(escalation_ids))
        )
        escalations = await session.execute(delete(EscalationRequest).where(EscalationRequest.id.in_(escalation_ids)))
        status_by_escalation = status_by_escalation_result.rowcount or 0
        mentor_by_escalation = mentor_by_escalation_result.rowcount or 0
        escalation_count = escalations.rowcount or 0

    updated_escalations = await session.execute(
        update(EscalationRequest).where(EscalationRequest.assigned_to == user_id).values(assigned_to=None)
    )
    await uow.commit()
    return {
        "escalations": escalation_count,
        "status_history": (status_history.rowcount or 0) + status_by_escalation,
        "mentor_history": (mentor_history.rowcount or 0) + mentor_by_escalation,
        "updated_escalations": updated_escalations.rowcount or 0,
    }
