"""SQLAlchemy implementations of Template repositories."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.core.enums import TemplateStatus
from checklists_service.models import Checklist, TaskTemplate, Template
from checklists_service.repositories.implementations.base import SqlAlchemyBaseRepository
from checklists_service.repositories.interfaces.template import ITaskTemplateRepository, ITemplateRepository


class TemplateRepository(SqlAlchemyBaseRepository[Template, int], ITemplateRepository):
    """SQLAlchemy implementation of Template repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize TemplateRepository with database session."""
        super().__init__(session, Template)

    async def find_templates(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        department: str | None = None,
        status: TemplateStatus | None = None,
        is_default: bool | None = None,
    ) -> tuple[Sequence[Template], int]:
        """Find templates with filtering and return results with total count."""
        count_stmt = select(func.count(Template.id))
        stmt = select(Template)

        if department:
            stmt = stmt.where(Template.department == department)
            count_stmt = count_stmt.where(Template.department == department)

        if status:
            stmt = stmt.where(Template.status == status)
            count_stmt = count_stmt.where(Template.status == status)

        if is_default is not None:
            stmt = stmt.where(Template.is_default == is_default)
            count_stmt = count_stmt.where(Template.is_default == is_default)

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        stmt = stmt.offset(skip).limit(limit).order_by(Template.created_at.desc())
        result = await self._session.execute(stmt)
        templates = result.scalars().all()

        return templates, total

    async def get_by_name_and_department(self, name: str, department: str | None) -> Template | None:
        """Get template by name and department."""
        stmt = select(Template).where(
            Template.name == name,
            Template.department == department,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_other_defaults(self, department: str | None, exclude_id: int) -> None:
        """Clear is_default flag on other templates in the same department."""
        stmt = select(Template).where(
            Template.department == department,
            Template.is_default,
            Template.id != exclude_id,
        )
        result = await self._session.execute(stmt)
        for other in result.scalars().all():
            other.is_default = False

    async def count_tasks(self, template_id: int) -> int:
        """Count task templates for a template."""
        stmt = select(func.count(TaskTemplate.id)).where(TaskTemplate.template_id == template_id)
        result = await self._session.execute(stmt)
        return cast("int", result.scalar_one())

    async def has_checklists(self, template_id: int) -> bool:
        """Check if template has associated checklists."""
        stmt = select(func.count(Checklist.id)).where(Checklist.template_id == template_id)
        result = await self._session.execute(stmt)
        return cast("int", result.scalar_one()) > 0

    async def get_department_stats(self, user_id: int | None = None) -> dict[str, int]:
        """Get checklist count grouped by department."""
        stmt = (
            select(Template.department, func.count(Checklist.id))
            .join(Checklist, Checklist.template_id == Template.id)
            .group_by(Template.department)
        )
        if user_id is not None:
            stmt = stmt.where(Checklist.user_id == user_id)

        result = await self._session.execute(stmt)
        return dict(result.all())


class TaskTemplateRepository(SqlAlchemyBaseRepository[TaskTemplate, int], ITaskTemplateRepository):
    """SQLAlchemy implementation of TaskTemplate repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize TaskTemplateRepository with database session."""
        super().__init__(session, TaskTemplate)

    async def find_by_template(self, template_id: int) -> Sequence[TaskTemplate]:
        """Find task templates for a template, ordered by order field."""
        stmt = select(TaskTemplate).where(TaskTemplate.template_id == template_id).order_by(TaskTemplate.order)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_existing_ids(self, template_id: int, ids: list[int]) -> set[int]:
        """Find which of the given IDs exist for a template."""
        if not ids:
            return set()

        stmt = select(TaskTemplate.id).where(
            TaskTemplate.template_id == template_id,
            TaskTemplate.id.in_(ids),
        )
        result = await self._session.execute(stmt)
        return {row[0] for row in result.all()}

    async def clone_tasks(self, source_template_id: int, target_template_id: int) -> None:
        """Clone all task templates from source to target template."""
        source_tasks = await self.find_by_template(source_template_id)

        for task in source_tasks:
            new_task = TaskTemplate(
                template_id=target_template_id,
                title=task.title,
                description=task.description,
                instructions=task.instructions,
                category=task.category,
                order=task.order,
                due_days=task.due_days,
                estimated_minutes=task.estimated_minutes,
                resources=task.resources.copy(),
                required_documents=task.required_documents.copy(),
                assignee_role=task.assignee_role,
                auto_assign=task.auto_assign,
                depends_on=task.depends_on.copy(),
            )
            self._session.add(new_task)
