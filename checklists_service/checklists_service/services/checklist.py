"""Checklist management service with auth integration."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.core import NotFoundException, ValidationException
from checklists_service.core.enums import ChecklistStatus, TaskStatus, TemplateStatus
from checklists_service.models import Checklist, Task, TaskTemplate, Template
from checklists_service.schemas import ChecklistCreate, ChecklistStats, ChecklistUpdate
from checklists_service.utils import auth_service_client


class ChecklistService:
    """Service for checklist management operations."""

    def __init__(self, db: AsyncSession, auth_token: str | None = None) -> None:
        """Initialize checklist service with database session and auth token."""
        self.db = db
        self.auth_token = auth_token

    async def _validate_user(self, user_id: int) -> dict:
        """Validate user exists in auth service."""
        if not self.auth_token:
            msg = "Authentication required"
            raise ValidationException(msg)

        user_data = await auth_service_client.get_user(user_id, self.auth_token)
        if not user_data:
            msg = f"User {user_id} not found in auth service"
            raise ValidationException(msg)

        return user_data

    async def create_checklist(self, checklist_data: ChecklistCreate, auth_token: str) -> Checklist:
        """Create new checklist from template."""
        self.auth_token = auth_token

        user_data = await self._validate_user(checklist_data.user_id)

        if user_data.get("employee_id") != checklist_data.employee_id:
            msg = "Employee ID does not match user"
            raise ValidationException(msg)

        stmt = select(Template).where(
            Template.id == checklist_data.template_id,
            Template.status == TemplateStatus.ACTIVE,
        )
        result = await self.db.execute(stmt)
        template = result.scalar_one_or_none()

        if not template:
            msg = "Template not found or not active"
            raise ValidationException(msg)

        stmt = select(Checklist).where(
            Checklist.user_id == checklist_data.user_id,
            Checklist.status != ChecklistStatus.COMPLETED,
        )
        result = await self.db.execute(stmt)
        existing_checklist = result.scalar_one_or_none()

        if existing_checklist:
            msg = "User already has an active checklist"
            raise ValidationException(msg)

        if checklist_data.mentor_id:
            mentor_data = await auth_service_client.get_user(checklist_data.mentor_id, auth_token)
            if not mentor_data:
                msg = f"Mentor {checklist_data.mentor_id} not found"
                raise ValidationException(msg)
            if mentor_data.get("role") not in ["MENTOR", "HR", "ADMIN"]:
                msg = "Mentor must have MENTOR, HR or ADMIN role"
                raise ValidationException(msg)

        if checklist_data.hr_id:
            hr_data = await auth_service_client.get_user(checklist_data.hr_id, auth_token)
            if not hr_data:
                msg = f"HR {checklist_data.hr_id} not found"
                raise ValidationException(msg)
            if hr_data.get("role") not in ["HR", "ADMIN"]:
                msg = "HR must have HR or ADMIN role"
                raise ValidationException(msg)

        start_date = checklist_data.start_date or datetime.now(UTC)
        due_date = checklist_data.due_date or start_date + timedelta(days=template.duration_days)

        checklist = Checklist(
            user_id=checklist_data.user_id,
            employee_id=checklist_data.employee_id,
            template_id=checklist_data.template_id,
            start_date=start_date,
            due_date=due_date,
            mentor_id=checklist_data.mentor_id,
            hr_id=checklist_data.hr_id,
            notes=checklist_data.notes,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
        )

        self.db.add(checklist)
        await self.db.flush()

        stmt = select(TaskTemplate).where(TaskTemplate.template_id == template.id).order_by(TaskTemplate.order)
        result = await self.db.execute(stmt)
        task_templates = list(result.scalars().all())

        tasks: list[Task] = []
        for idx, task_template in enumerate(task_templates):
            task_due_date = start_date + timedelta(days=task_template.due_days)
            task_due_date = min(task_due_date, due_date)

            assignee_id = None
            if task_template.auto_assign and task_template.assignee_role:
                if task_template.assignee_role == "MENTOR" and checklist.mentor_id:
                    assignee_id = checklist.mentor_id
                elif task_template.assignee_role == "HR" and checklist.hr_id:
                    assignee_id = checklist.hr_id

            task = Task(
                checklist_id=checklist.id,
                template_task_id=task_template.id,
                title=task_template.title,
                description=task_template.description,
                category=task_template.category,
                order=idx,
                due_date=task_due_date,
                assignee_id=assignee_id,
                assignee_role=task_template.assignee_role or template.default_assignee_role,
                depends_on=task_template.depends_on.copy(),
            )
            tasks.append(task)

        task_map = {task.template_task_id: task for task in tasks if task.template_task_id}
        for task in tasks:
            if task.template_task_id and task.template_task_id in task_map:
                for dep_id in task.depends_on:
                    if dep_id in task_map:
                        task_map[dep_id].blocks.append(task.template_task_id)

        for task in tasks:
            self.db.add(task)

        checklist.total_tasks = len(tasks)

        await self.db.commit()
        await self.db.refresh(checklist)

        return checklist

    async def get_checklist(self, checklist_id: int) -> Checklist:
        """Get checklist by ID."""
        stmt = select(Checklist).where(Checklist.id == checklist_id)
        result = await self.db.execute(stmt)
        checklist = result.scalar_one_or_none()

        if not checklist:
            msg = "Checklist"
            raise NotFoundException(msg)

        return checklist

    async def update_checklist(self, checklist_id: int, update_data: ChecklistUpdate) -> Checklist:
        """Update checklist."""
        checklist = await self.get_checklist(checklist_id)

        if update_data.status == ChecklistStatus.COMPLETED and checklist.status != ChecklistStatus.COMPLETED:
            checklist.completed_at = datetime.now(UTC)

            stmt = select(Task).where(
                Task.checklist_id == checklist_id,
                Task.status != TaskStatus.COMPLETED,
            )
            result = await self.db.execute(stmt)
            pending_tasks = list(result.scalars().all())

            for task in pending_tasks:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(UTC)

        if update_data.progress_percentage is not None:
            checklist.progress_percentage = update_data.progress_percentage

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if field != "progress_percentage":
                setattr(checklist, field, value)

        await self._recalculate_progress(checklist_id)

        checklist.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(checklist)

        return checklist

    async def delete_checklist(self, checklist_id: int) -> None:
        """Delete checklist."""
        checklist = await self.get_checklist(checklist_id)

        if checklist.status == ChecklistStatus.IN_PROGRESS:
            msg = "Cannot delete in-progress checklist"
            raise ValidationException(msg)

        await self.db.delete(checklist)
        await self.db.commit()

    async def get_checklists(  # noqa: PLR0913
        self,
        skip: int = 0,
        limit: int = 50,
        user_id: int | None = None,
        status: str | None = None,
        department: str | None = None,
        overdue_only: bool = False,
    ) -> tuple[list[Checklist], int]:
        """Get paginated list of checklists with filters."""
        stmt = select(Checklist)
        count_stmt = select(func.count(Checklist.id))

        if user_id is not None:
            stmt = stmt.where(Checklist.user_id == user_id)
            count_stmt = count_stmt.where(Checklist.user_id == user_id)

        if status:
            stmt = stmt.where(Checklist.status == status)
            count_stmt = count_stmt.where(Checklist.status == status)

        if department:
            stmt = stmt.join(Template).where(Template.department == department)
            count_stmt = count_stmt.join(Template).where(Template.department == department)

        if overdue_only:
            now = datetime.now(UTC)
            stmt = stmt.where(
                and_(
                    Checklist.due_date < now,
                    Checklist.status != ChecklistStatus.COMPLETED,
                )
            )
            count_stmt = count_stmt.where(
                and_(
                    Checklist.due_date < now,
                    Checklist.status != ChecklistStatus.COMPLETED,
                )
            )

        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

        stmt = stmt.offset(skip).limit(limit).order_by(Checklist.created_at.desc())
        result = await self.db.execute(stmt)
        checklists = list(result.scalars().all())

        return checklists, total

    async def complete_checklist(self, checklist_id: int) -> Checklist:
        """Mark checklist as completed."""
        checklist = await self.get_checklist(checklist_id)

        if checklist.status == ChecklistStatus.COMPLETED:
            return checklist

        stmt = select(func.count(Task.id)).where(
            Task.checklist_id == checklist_id,
            Task.status != TaskStatus.COMPLETED,
        )
        result = await self.db.execute(stmt)
        pending_tasks = result.scalar_one()

        if pending_tasks > 0:
            msg = "Cannot complete checklist with pending tasks"
            raise ValidationException(msg)

        checklist.status = ChecklistStatus.COMPLETED
        checklist.progress_percentage = 100
        checklist.completed_at = datetime.now(UTC)
        checklist.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(checklist)

        return checklist

    async def get_checklist_progress(self, checklist_id: int) -> dict[str, Any]:
        """Get detailed progress information for checklist."""
        checklist = await self.get_checklist(checklist_id)

        stmt = select(Task.status, func.count(Task.id)).where(Task.checklist_id == checklist_id).group_by(Task.status)
        result = await self.db.execute(stmt)
        status_counts = dict(result.all())

        stmt = (
            select(Task.category, func.count(Task.id)).where(Task.checklist_id == checklist_id).group_by(Task.category)
        )
        result = await self.db.execute(stmt)
        category_counts = dict(result.all())

        now = datetime.now(UTC)
        stmt = select(func.count(Task.id)).where(
            Task.checklist_id == checklist_id,
            Task.due_date < now,
            Task.status != TaskStatus.COMPLETED,
        )
        result = await self.db.execute(stmt)
        overdue_count = result.scalar_one() or 0

        total_tasks = sum(status_counts.values())
        completed_tasks = status_counts.get("completed", 0)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        blocked_tasks = []
        if "blocked" in status_counts:
            stmt = select(Task).where(
                Task.checklist_id == checklist_id,
                Task.status == TaskStatus.BLOCKED,
            )
            result = await self.db.execute(stmt)
            blocked_tasks = [{"id": t.id, "title": t.title} for t in result.scalars().all()]

        return {
            "checklist_id": checklist_id,
            "status": checklist.status,
            "progress_percentage": checklist.progress_percentage,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "completion_rate": round(completion_rate, 2),
            "overdue_tasks": overdue_count,
            "by_status": status_counts,
            "by_category": category_counts,
            "blocked_tasks": blocked_tasks,
            "start_date": checklist.start_date.isoformat() if checklist.start_date else None,
            "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
            "days_remaining": (checklist.due_date - now).days if checklist.due_date and checklist.due_date > now else 0,
        }

    async def get_checklist_stats(
        self,
        user_id: int | None = None,
        department: str | None = None,
    ) -> ChecklistStats:
        """Get checklist statistics."""
        total_stmt = select(func.count(Checklist.id))
        completed_stmt = select(func.count(Checklist.id)).where(Checklist.status == ChecklistStatus.COMPLETED)
        in_progress_stmt = select(func.count(Checklist.id)).where(Checklist.status == ChecklistStatus.IN_PROGRESS)
        not_started_stmt = select(func.count(Checklist.id)).where(Checklist.status == ChecklistStatus.PENDING)

        now = datetime.now(UTC)
        overdue_stmt = select(func.count(Checklist.id)).where(
            and_(
                Checklist.due_date < now,
                Checklist.status != ChecklistStatus.COMPLETED,
            )
        )

        if user_id is not None:
            for st in [total_stmt, completed_stmt, in_progress_stmt, not_started_stmt, overdue_stmt]:
                st = st.where(Checklist.user_id == user_id)

        if department:
            for st in [total_stmt, completed_stmt, in_progress_stmt, not_started_stmt, overdue_stmt]:
                st = st.join(Template).where(Template.department == department)

        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar_one() or 0

        completed_result = await self.db.execute(completed_stmt)
        completed = completed_result.scalar_one() or 0

        in_progress_result = await self.db.execute(in_progress_stmt)
        in_progress = in_progress_result.scalar_one() or 0

        not_started_result = await self.db.execute(not_started_stmt)
        not_started = not_started_result.scalar_one() or 0

        overdue_result = await self.db.execute(overdue_stmt)
        overdue = overdue_result.scalar_one() or 0

        avg_stmt = select(func.avg(func.extract("epoch", Checklist.completed_at - Checklist.start_date) / 86400)).where(
            Checklist.status == ChecklistStatus.COMPLETED,
            Checklist.completed_at.is_not(None),
            Checklist.start_date.is_not(None),
        )

        if user_id is not None:
            avg_stmt = avg_stmt.where(Checklist.user_id == user_id)

        avg_result = await self.db.execute(avg_stmt)
        avg_completion_days = round(avg_result.scalar_one() or 0, 2)

        completion_rate = (completed / total * 100) if total > 0 else 0

        dept_stmt = (
            select(Template.department, func.count(Checklist.id))
            .join(Checklist, Checklist.template_id == Template.id)
            .group_by(Template.department)
        )

        if user_id is not None:
            dept_stmt = dept_stmt.where(Checklist.user_id == user_id)

        dept_result = await self.db.execute(dept_stmt)
        by_department = dict(dept_result.all())

        recent_stmt = (
            select(Checklist.id, Checklist.user_id, Checklist.completed_at, Template.name.label("template_name"))
            .join(Template, Checklist.template_id == Template.id)
            .where(
                Checklist.status == ChecklistStatus.COMPLETED,
                Checklist.completed_at.is_not(None),
            )
            .order_by(Checklist.completed_at.desc())
            .limit(10)
        )

        if user_id is not None:
            recent_stmt = recent_stmt.where(Checklist.user_id == user_id)

        recent_result = await self.db.execute(recent_stmt)
        recent_completions = [
            {
                "id": row.id,
                "user_id": row.user_id,
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                "template_name": row.template_name,
            }
            for row in recent_result.all()
        ]

        return ChecklistStats(
            total=total,
            completed=completed,
            in_progress=in_progress,
            not_started=not_started,
            overdue=overdue,
            avg_completion_days=avg_completion_days,
            completion_rate=round(completion_rate, 2),
            by_department=by_department,
            recent_completions=recent_completions,
        )

    async def _recalculate_progress(self, checklist_id: int) -> None:
        """Recalculate checklist progress based on task completion."""
        stmt = select(
            func.count(Task.id).label("total"),
            func.count(Task.id).filter(Task.status == TaskStatus.COMPLETED).label("completed"),
        ).where(Task.checklist_id == checklist_id)

        result = await self.db.execute(stmt)
        row = result.one()

        total = row.total or 0
        completed = row.completed or 0
        progress = (completed / total * 100) if total > 0 else 0

        stmt = select(Checklist).where(Checklist.id == checklist_id)
        result = await self.db.execute(stmt)
        checklist = result.scalar_one()

        checklist.completed_tasks = completed
        checklist.total_tasks = total
        checklist.progress_percentage = round(progress)

        if completed == total and total > 0:
            checklist.status = ChecklistStatus.COMPLETED
            checklist.completed_at = datetime.now(UTC)
