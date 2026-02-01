"""Template management service."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.core import (
    ConflictException,
    NotFoundException,
    TemplateStatus,
    ValidationException,
)
from checklists_service.models import TaskTemplate, Template
from checklists_service.schemas import TaskTemplateCreate, TemplateCreate, TemplateUpdate, TemplateWithTasks
from checklists_service.schemas.template import TaskTemplateResponse, TemplateResponse


class TemplateService:
    """Service for template management operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize template service with database session."""
        self.db = db

    async def create_template(self, template_data: TemplateCreate) -> Template:
        """Create new template."""
        stmt = select(Template).where(
            Template.name == template_data.name,
            Template.department == template_data.department,
        )
        result = await self.db.execute(stmt)
        existing_template = result.scalar_one_or_none()

        if existing_template:
            msg = "Template with this name already exists for the department"
            raise ConflictException(msg)

        template = Template(
            name=template_data.name,
            description=template_data.description,
            department=template_data.department,
            position=template_data.position,
            level=template_data.level,
            duration_days=template_data.duration_days,
            task_categories=template_data.task_categories,
            default_assignee_role=template_data.default_assignee_role,
            status=template_data.status,
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def get_template(self, template_id: int) -> Template:
        """Get template by ID."""
        stmt = select(Template).where(Template.id == template_id)
        result = await self.db.execute(stmt)
        template = result.scalar_one_or_none()

        if not template:
            msg = "Template"
            raise NotFoundException(msg)

        return template

    async def get_template_with_tasks(self, template_id: int) -> TemplateWithTasks:
        """Get template with its tasks."""
        template = await self.get_template(template_id)

        stmt = select(TaskTemplate).where(TaskTemplate.template_id == template_id).order_by(TaskTemplate.order)
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())

        return TemplateWithTasks(
            **TemplateResponse.model_validate(template).model_dump(),
            tasks=[TaskTemplateResponse.model_validate(task) for task in tasks],
        )

    async def update_template(self, template_id: int, update_data: TemplateUpdate) -> Template:
        """Update template."""
        template = await self.get_template(template_id)

        if update_data.is_default and update_data.is_default != template.is_default:
            stmt = select(Template).where(
                Template.department == template.department,
                Template.is_default,
                Template.id != template_id,
            )
            result = await self.db.execute(stmt)
            other_defaults = list(result.scalars().all())

            for other in other_defaults:
                other.is_default = False

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(template, field, value)

        template.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def delete_template(self, template_id: int) -> None:
        """Delete template."""
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ACTIVE:
            msg = "Cannot delete active template. Archive it first."
            raise ValidationException(msg)

        if template.checklists:
            msg = "Cannot delete template with associated checklists"
            raise ValidationException(msg)

        await self.db.delete(template)
        await self.db.commit()

    async def get_templates(
        self,
        skip: int = 0,
        limit: int = 50,
        department: str | None = None,
        status: str | None = None,
        *,
        is_default: bool | None = None,
    ) -> tuple[list[Template], int]:
        """Get paginated list of templates with filters."""
        stmt = select(Template)
        count_stmt = select(func.count(Template.id))

        if department:
            stmt = stmt.where(Template.department == department)
            count_stmt = count_stmt.where(Template.department == department)

        if status:
            stmt = stmt.where(Template.status == status)
            count_stmt = count_stmt.where(Template.status == status)

        if is_default is not None:
            stmt = stmt.where(Template.is_default == is_default)
            count_stmt = count_stmt.where(Template.is_default == is_default)

        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

        stmt = stmt.offset(skip).limit(limit).order_by(Template.created_at.desc())
        result = await self.db.execute(stmt)
        templates = list(result.scalars().all())

        return templates, total

    async def clone_template(self, template_id: int) -> Template:
        """Clone template with new version."""
        original = await self.get_template(template_id)

        new_template = Template(
            name=f"{original.name} (Copy)",
            description=original.description,
            department=original.department,
            position=original.position,
            level=original.level,
            duration_days=original.duration_days,
            task_categories=original.task_categories.copy(),
            default_assignee_role=original.default_assignee_role,
            status=TemplateStatus.DRAFT,
            version=original.version + 1,
        )

        self.db.add(new_template)
        await self.db.flush()

        stmt = select(TaskTemplate).where(TaskTemplate.template_id == template_id)
        result = await self.db.execute(stmt)
        original_tasks = list(result.scalars().all())

        for task in original_tasks:
            new_task = TaskTemplate(
                template_id=new_template.id,
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
            self.db.add(new_task)

        await self.db.commit()
        await self.db.refresh(new_template)

        return new_template

    async def add_task_to_template(self, template_id: int, task_data: TaskTemplateCreate) -> TaskTemplate:
        """Add task to template."""
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ARCHIVED:
            msg = "Cannot add tasks to archived template"
            raise ValidationException(msg)

        if task_data.depends_on:
            stmt = select(TaskTemplate.id).where(
                TaskTemplate.template_id == template_id,
                TaskTemplate.id.in_(task_data.depends_on),
            )
            result = await self.db.execute(stmt)
            existing_ids = {row[0] for row in result.all()}

            missing_ids = set(task_data.depends_on) - existing_ids
            if missing_ids:
                msg = f"Invalid dependency IDs: {missing_ids}"
                raise ValidationException(msg)

        task = TaskTemplate(
            template_id=template_id,
            title=task_data.title,
            description=task_data.description,
            instructions=task_data.instructions,
            category=task_data.category,
            order=task_data.order,
            due_days=task_data.due_days,
            estimated_minutes=task_data.estimated_minutes,
            resources=task_data.resources,
            required_documents=task_data.required_documents,
            assignee_role=task_data.assignee_role,
            auto_assign=task_data.auto_assign,
            depends_on=task_data.depends_on,
        )

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def publish_template(self, template_id: int) -> Template:
        """Publish template (set to active)."""
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ACTIVE:
            return template

        stmt = select(func.count(TaskTemplate.id)).where(TaskTemplate.template_id == template_id)
        result = await self.db.execute(stmt)
        task_count = result.scalar_one()

        if task_count == 0:
            msg = "Cannot publish template without tasks"
            raise ValidationException(msg)

        template.status = TemplateStatus.ACTIVE
        template.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(template)

        return template
