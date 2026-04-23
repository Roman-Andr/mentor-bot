"""SQLAlchemy implementation of Checklist repository."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import Column, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.core.enums import ChecklistStatus, TaskStatus
from checklists_service.models import Checklist, Task, Template
from checklists_service.repositories.implementations.base import SqlAlchemyBaseRepository
from checklists_service.repositories.interfaces.checklist import IChecklistRepository


class ChecklistRepository(SqlAlchemyBaseRepository[Checklist, int], IChecklistRepository):
    """SQLAlchemy implementation of Checklist repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ChecklistRepository with database session."""
        super().__init__(session, Checklist)

    def _get_sort_column(self, sort_by: str | None) -> Column[Any]:  # type: ignore[type-arg]
        """Get SQLAlchemy column for sorting."""
        column_map: dict[str, Column[Any]] = {  # type: ignore[type-arg]
            "employeeId": Checklist.employee_id,
            "employee_id": Checklist.employee_id,
            "employee": Checklist.employee_id,
            "status": Checklist.status,
            "progress": Checklist.progress_percentage,
            "progress_percentage": Checklist.progress_percentage,
            "startDate": Checklist.start_date,
            "start_date": Checklist.start_date,
            "dueDate": Checklist.due_date,
            "due_date": Checklist.due_date,
            "completedAt": Checklist.completed_at,
            "completed_at": Checklist.completed_at,
            "createdAt": Checklist.created_at,
            "created_at": Checklist.created_at,
            "tasks": Checklist.total_tasks,
        }
        return column_map.get(sort_by, Checklist.created_at)  # type: ignore[return-value]

    async def find_checklists(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
        status: ChecklistStatus | None = None,
        department_id: int | None = None,
        search: str | None = None,
        overdue_only: bool = False,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[Sequence[Checklist], int]:
        """Find checklists with filtering and return results with total count."""
        count_stmt = select(func.count(Checklist.id))
        stmt = select(Checklist)

        if user_id is not None:
            stmt = stmt.where(Checklist.user_id == user_id)
            count_stmt = count_stmt.where(Checklist.user_id == user_id)

        if status:
            stmt = stmt.where(Checklist.status == status)
            count_stmt = count_stmt.where(Checklist.status == status)

        if department_id is not None:
            stmt = stmt.join(Template).where(Template.department_id == department_id)
            count_stmt = count_stmt.join(Template).where(Template.department_id == department_id)

        if search:
            search_filter = Checklist.employee_id.ilike(f"%{search}%")
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if overdue_only:
            now = datetime.now(UTC)
            overdue_filter = and_(
                Checklist.due_date < now,
                Checklist.status != ChecklistStatus.COMPLETED,
            )
            stmt = stmt.where(overdue_filter)
            count_stmt = count_stmt.where(overdue_filter)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)
        stmt = stmt.order_by(sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        checklists = result.scalars().all()

        return checklists, total

    async def get_active_by_user(self, user_id: int) -> Checklist | None:
        """Get active (non-completed) checklist for a user."""
        stmt = select(Checklist).where(
            Checklist.user_id == user_id,
            Checklist.status != ChecklistStatus.COMPLETED,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_progress(self, checklist_id: int) -> dict[str, Any]:
        """Get detailed progress information for checklist."""
        checklist = await self.get_by_id(checklist_id)
        if not checklist:
            return {}

        status_stmt = (
            select(Task.status, func.count(Task.id)).where(Task.checklist_id == checklist_id).group_by(Task.status)
        )
        result = await self._session.execute(status_stmt)
        status_counts: dict[str, int] = {str(k): v for k, v in result.all()}

        category_stmt = (
            select(Task.category, func.count(Task.id)).where(Task.checklist_id == checklist_id).group_by(Task.category)
        )
        result = await self._session.execute(category_stmt)
        category_counts: dict[str, int] = {str(k): v for k, v in result.all()}

        now = datetime.now(UTC)
        overdue_stmt = select(func.count(Task.id)).where(
            Task.checklist_id == checklist_id,
            Task.due_date < now,
            Task.status != TaskStatus.COMPLETED,
        )
        result = await self._session.execute(overdue_stmt)
        overdue_count = result.scalar_one() or 0

        total_tasks = sum(status_counts.values())
        completed_tasks = status_counts.get("completed", 0)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        blocked_tasks = []
        if "blocked" in status_counts:
            blocked_stmt = select(Task).where(
                Task.checklist_id == checklist_id,
                Task.status == TaskStatus.BLOCKED,
            )
            result = await self._session.execute(blocked_stmt)
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

    async def get_statistics(
        self,
        user_id: int | None = None,
        department_id: int | None = None,
    ) -> dict[str, Any]:
        """Get checklist statistics."""
        now = datetime.now(UTC)

        total_stmt = select(func.count(Checklist.id))
        completed_stmt = select(func.count(Checklist.id)).where(Checklist.status == ChecklistStatus.COMPLETED)
        in_progress_stmt = select(func.count(Checklist.id)).where(Checklist.status == ChecklistStatus.IN_PROGRESS)
        not_started_stmt = select(func.count(Checklist.id)).where(Checklist.status == ChecklistStatus.PENDING)
        overdue_stmt = select(func.count(Checklist.id)).where(
            and_(
                Checklist.due_date < now,
                Checklist.status != ChecklistStatus.COMPLETED,
            )
        )

        if user_id is not None:
            (total_stmt, completed_stmt, in_progress_stmt, not_started_stmt, overdue_stmt) = [
                st.where(Checklist.user_id == user_id)
                for st in (total_stmt, completed_stmt, in_progress_stmt, not_started_stmt, overdue_stmt)
            ]

        if department_id is not None:
            (total_stmt, completed_stmt, in_progress_stmt, not_started_stmt, overdue_stmt) = [
                st.join(Template).where(Template.department_id == department_id)
                for st in (total_stmt, completed_stmt, in_progress_stmt, not_started_stmt, overdue_stmt)
            ]

        total = cast("int", (await self._session.execute(total_stmt)).scalar_one() or 0)
        completed = cast("int", (await self._session.execute(completed_stmt)).scalar_one() or 0)
        in_progress = cast("int", (await self._session.execute(in_progress_stmt)).scalar_one() or 0)
        not_started = cast("int", (await self._session.execute(not_started_stmt)).scalar_one() or 0)
        overdue = cast("int", (await self._session.execute(overdue_stmt)).scalar_one() or 0)

        avg_stmt = select(func.avg(func.extract("epoch", Checklist.completed_at - Checklist.start_date) / 86400)).where(
            Checklist.status == ChecklistStatus.COMPLETED,
            Checklist.completed_at.is_not(None),
            Checklist.start_date.is_not(None),
        )
        if user_id is not None:
            avg_stmt = avg_stmt.where(Checklist.user_id == user_id)

        avg_completion_days = round(cast("float", (await self._session.execute(avg_stmt)).scalar_one() or 0), 2)
        completion_rate = (completed / total * 100) if total > 0 else 0

        dept_stmt = (
            select(Template.department_id, func.count(Checklist.id))
            .join(Checklist, Checklist.template_id == Template.id)
            .group_by(Template.department_id)
        )
        if user_id is not None:
            dept_stmt = dept_stmt.where(Checklist.user_id == user_id)

        by_department = {str(k): v for k, v in (await self._session.execute(dept_stmt)).all()}

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

        recent_result = await self._session.execute(recent_stmt)
        recent_completions = [
            {
                "id": row.id,
                "user_id": row.user_id,
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                "template_name": row.template_name,
            }
            for row in recent_result.all()
        ]

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "overdue": overdue,
            "avg_completion_days": avg_completion_days,
            "completion_rate": round(completion_rate, 2),
            "by_department": by_department,
            "recent_completions": recent_completions,
        }

    async def recalculate_progress(self, checklist_id: int) -> None:
        """Recalculate checklist progress based on task completion."""
        stmt = select(
            func.count(Task.id).label("total"),
            func.count(Task.id).filter(Task.status == TaskStatus.COMPLETED).label("completed"),
        ).where(Task.checklist_id == checklist_id)

        result = await self._session.execute(stmt)
        row = result.one()

        total = row.total or 0
        completed = row.completed or 0
        progress = (completed / total * 100) if total > 0 else 0

        checklist = await self.get_by_id(checklist_id)
        if not checklist:
            return

        checklist.completed_tasks = completed
        checklist.total_tasks = total
        checklist.progress_percentage = round(progress)

        if completed == total and total > 0:
            checklist.status = ChecklistStatus.COMPLETED
            checklist.completed_at = datetime.now(UTC)

    async def get_by_user_and_template(self, user_id: int, template_id: int) -> Checklist | None:
        """Get checklist by user and template ID."""
        stmt = select(Checklist).where(
            Checklist.user_id == user_id,
            Checklist.template_id == template_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_monthly_stats(self, months: int = 6) -> list[dict[str, Any]]:
        """Get monthly statistics for the last N months."""
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        results = []
        now = datetime.now(UTC)

        for i in range(months - 1, -1, -1):
            target_month = now.month - i
            target_year = now.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1

            month_start = datetime(target_year, target_month, 1, tzinfo=UTC)

            next_month = target_month + 1
            next_year = target_year
            if next_month > 12:
                next_month = 1
                next_year += 1
            month_end = datetime(next_year, next_month, 1, tzinfo=UTC)

            new_stmt = select(func.count(Checklist.id)).where(
                Checklist.start_date >= month_start,
                Checklist.start_date < month_end,
            )
            new_count = cast("int", (await self._session.execute(new_stmt)).scalar_one() or 0)

            completed_stmt = select(func.count(Checklist.id)).where(
                Checklist.status == ChecklistStatus.COMPLETED,
                Checklist.completed_at >= month_start,
                Checklist.completed_at < month_end,
            )
            completed_count = cast("int", (await self._session.execute(completed_stmt)).scalar_one() or 0)

            results.append(
                {
                    "month": month_names[month_start.month - 1],
                    "new_checklists": new_count,
                    "completed": completed_count,
                }
            )

        return results

    async def get_completion_time_distribution(self) -> list[dict[str, Any]]:
        """Get completion time distribution (in days)."""
        ranges = [
            ("1-7 days", 1, 7),
            ("8-14 days", 8, 14),
            ("15-21 days", 15, 21),
            ("22-30 days", 22, 30),
            (">30 days", 31, 9999),
        ]

        results = []
        for label, min_days, max_days in ranges:
            stmt = select(func.count(Checklist.id)).where(
                Checklist.status == ChecklistStatus.COMPLETED,
                Checklist.completed_at.is_not(None),
                Checklist.start_date.is_not(None),
                func.extract("epoch", Checklist.completed_at - Checklist.start_date) / 86400 >= min_days,
                func.extract("epoch", Checklist.completed_at - Checklist.start_date) / 86400 <= max_days,
            )
            count = cast("int", (await self._session.execute(stmt)).scalar_one() or 0)
            results.append({"range": label, "count": count})

        return results
