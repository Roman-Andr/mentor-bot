"""Internal maintenance endpoints for checklist data."""

from fastapi import APIRouter
from sqlalchemy import delete, or_, select, update

from checklists_service.api.deps import ServiceAuth, UOWDep
from checklists_service.models import Certificate, Checklist, ChecklistStatusHistory, Task, TaskCompletionHistory

router = APIRouter()


@router.delete("/users/{user_id}")
async def cleanup_user_checklist_data(
    user_id: int,
    uow: UOWDep,
    _service_auth: ServiceAuth,
) -> dict[str, int]:
    """Remove checklist-service data that belongs or points to a deleted user."""
    session = uow._session
    if session is None:
        msg = "Session not initialized"
        raise RuntimeError(msg)

    checklist_ids = list((await session.execute(select(Checklist.id).where(Checklist.user_id == user_id))).scalars())

    direct_task_history = await session.execute(
        delete(TaskCompletionHistory).where(
            or_(TaskCompletionHistory.user_id == user_id, TaskCompletionHistory.completed_by == user_id)
        )
    )
    direct_status_history = await session.execute(
        delete(ChecklistStatusHistory).where(
            or_(ChecklistStatusHistory.user_id == user_id, ChecklistStatusHistory.changed_by == user_id)
        )
    )

    checklist_task_history_count = 0
    checklist_status_history_count = 0
    owned_certificate_count = 0
    task_count = 0
    checklist_count = 0
    if checklist_ids:
        checklist_task_history = await session.execute(
            delete(TaskCompletionHistory).where(TaskCompletionHistory.checklist_id.in_(checklist_ids))
        )
        checklist_status_history = await session.execute(
            delete(ChecklistStatusHistory).where(ChecklistStatusHistory.checklist_id.in_(checklist_ids))
        )
        owned_certificates = await session.execute(
            delete(Certificate).where(Certificate.checklist_id.in_(checklist_ids))
        )
        tasks = await session.execute(delete(Task).where(Task.checklist_id.in_(checklist_ids)))
        checklists = await session.execute(delete(Checklist).where(Checklist.id.in_(checklist_ids)))
        checklist_task_history_count = checklist_task_history.rowcount or 0
        checklist_status_history_count = checklist_status_history.rowcount or 0
        owned_certificate_count = owned_certificates.rowcount or 0
        task_count = tasks.rowcount or 0
        checklist_count = checklists.rowcount or 0

    updated_certificates = await session.execute(
        update(Certificate)
        .where(or_(Certificate.mentor_id == user_id, Certificate.hr_id == user_id))
        .values(mentor_id=None, hr_id=None)
    )
    updated_checklists = await session.execute(
        update(Checklist)
        .where(or_(Checklist.mentor_id == user_id, Checklist.hr_id == user_id))
        .values(mentor_id=None, hr_id=None)
    )
    await uow.commit()
    return {
        "checklists": checklist_count,
        "tasks": task_count,
        "task_history": (direct_task_history.rowcount or 0) + checklist_task_history_count,
        "status_history": (direct_status_history.rowcount or 0) + checklist_status_history_count,
        "certificates": owned_certificate_count,
        "updated_certificates": updated_certificates.rowcount or 0,
        "updated_checklists": updated_checklists.rowcount or 0,
    }
