"""Template management service with repository pattern."""

from datetime import UTC, datetime

from checklists_service.core import (
    ConflictException,
    NotFoundException,
    TemplateStatus,
    ValidationException,
)
from checklists_service.models import TaskTemplate, Template
from checklists_service.repositories.unit_of_work import IUnitOfWork
from checklists_service.schemas import TaskTemplateCreate, TemplateCreate, TemplateUpdate, TemplateWithTasks
from checklists_service.schemas.template import TaskTemplateResponse, TemplateResponse


class TemplateService:
    """Service for template management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize template service with Unit of Work."""
        self._uow = uow

    async def create_template(self, template_data: TemplateCreate) -> Template:
        """Create new template."""
        existing_template = await self._uow.templates.get_by_name_and_department(
            template_data.name, template_data.department_id
        )
        if existing_template:
            msg = "Template with this name already exists for the department"
            raise ConflictException(msg)

        template = Template(
            name=template_data.name,
            description=template_data.description,
            department_id=template_data.department_id,
            position=template_data.position,
            level=template_data.level,
            duration_days=template_data.duration_days,
            task_categories=template_data.task_categories,
            default_assignee_role=template_data.default_assignee_role,
            status=template_data.status,
        )

        created = await self._uow.templates.create(template)
        return await self.get_template(created.id)

    async def get_template(self, template_id: int) -> Template:
        """Get template by ID."""
        template = await self._uow.templates.get_by_id(template_id)
        if not template:
            msg = "Template"
            raise NotFoundException(msg)
        return template

    async def get_template_with_tasks(self, template_id: int) -> TemplateWithTasks:
        """Get template with its tasks."""
        template = await self.get_template(template_id)

        tasks = list(await self._uow.task_templates.find_by_template(template_id))

        return TemplateWithTasks(
            **TemplateResponse.model_validate(template).model_dump(),
            tasks=[TaskTemplateResponse.model_validate(task) for task in tasks],
        )

    async def update_template(self, template_id: int, update_data: TemplateUpdate) -> Template:
        """Update template."""
        template = await self.get_template(template_id)

        if update_data.is_default and update_data.is_default != template.is_default:
            await self._uow.templates.clear_other_defaults(template.department_id, template_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(template, field, value)

        template.updated_at = datetime.now(UTC)
        await self._uow.templates.update(template)
        return await self.get_template(template_id)

    async def delete_template(self, template_id: int) -> None:
        """Delete template."""
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ACTIVE:
            msg = "Cannot delete active template. Archive it first."
            raise ValidationException(msg)

        has_checklists = await self._uow.templates.has_checklists(template_id)
        if has_checklists:
            msg = "Cannot delete template with associated checklists"
            raise ValidationException(msg)

        await self._uow.templates.delete(template_id)

    async def get_templates(
        self,
        skip: int = 0,
        limit: int = 50,
        department_id: int | None = None,
        status: str | None = None,
        *,
        is_default: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Template], int]:
        """Get paginated list of templates with filters."""
        status_enum = TemplateStatus(status) if status else None

        templates, total = await self._uow.templates.find_templates(
            skip=skip,
            limit=limit,
            department_id=department_id,
            status=status_enum,
            is_default=is_default,
            search=search,
        )
        return list(templates), total

    async def clone_template(self, template_id: int) -> Template:
        """Clone template with new version."""
        original = await self.get_template(template_id)

        new_template = Template(
            name=f"{original.name} (Copy)",
            description=original.description,
            department_id=original.department_id,
            position=original.position,
            level=original.level,
            duration_days=original.duration_days,
            task_categories=original.task_categories.copy(),
            default_assignee_role=original.default_assignee_role,
            status=TemplateStatus.DRAFT,
            version=original.version + 1,
        )

        new_template = await self._uow.templates.create(new_template)
        await self._uow.task_templates.clone_tasks(template_id, new_template.id)

        return await self.get_template(new_template.id)

    async def add_task_to_template(self, template_id: int, task_data: TaskTemplateCreate) -> TaskTemplate:
        """Add task to template."""
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ARCHIVED:
            msg = "Cannot add tasks to archived template"
            raise ValidationException(msg)

        if task_data.depends_on:
            existing_ids = await self._uow.task_templates.find_existing_ids(template_id, task_data.depends_on)
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

        return await self._uow.task_templates.create(task)

    async def publish_template(self, template_id: int) -> Template:
        """Publish template (set to active)."""
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ACTIVE:
            return template

        task_count = await self._uow.templates.count_tasks(template_id)
        if task_count == 0:
            msg = "Cannot publish template without tasks"
            raise ValidationException(msg)

        template.status = TemplateStatus.ACTIVE
        template.updated_at = datetime.now(UTC)

        await self._uow.templates.update(template)
        return await self.get_template(template_id)
