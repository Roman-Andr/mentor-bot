"""Template management service with repository pattern."""

from datetime import UTC, datetime

from loguru import logger

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
        logger.debug(
            "Creating template (name={}, department_id={})",
            template_data.name,
            template_data.department_id,
        )
        existing_template = await self._uow.templates.get_by_name_and_department(
            template_data.name, template_data.department_id
        )
        if existing_template:
            logger.warning(
                "Create template conflict (name={}, department_id={})",
                template_data.name,
                template_data.department_id,
            )
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
        logger.info("Template created (template_id={}, name={})", created.id, created.name)
        return await self.get_template(created.id)

    async def get_template(self, template_id: int) -> Template:
        """Get template by ID."""
        template = await self._uow.templates.get_by_id(template_id)
        if not template:
            logger.warning("Template not found (template_id={})", template_id)
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
        logger.debug("Updating template (template_id={})", template_id)
        template = await self.get_template(template_id)

        if update_data.is_default and update_data.is_default != template.is_default:
            await self._uow.templates.clear_other_defaults(template.department_id, template_id)
            logger.info(
                "Cleared other default templates (department_id={}, new_default_template_id={})",
                template.department_id,
                template_id,
            )

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(template, field, value)

        template.updated_at = datetime.now(UTC)
        await self._uow.templates.update(template)
        logger.info("Template updated (template_id={})", template_id)
        return await self.get_template(template_id)

    async def delete_template(self, template_id: int) -> None:
        """Delete template."""
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ACTIVE:
            logger.warning("Delete rejected: template is ACTIVE (template_id={})", template_id)
            msg = "Cannot delete active template. Archive it first."
            raise ValidationException(msg)

        has_checklists = await self._uow.templates.has_checklists(template_id)
        if has_checklists:
            logger.warning(
                "Delete rejected: template has associated checklists (template_id={})",
                template_id,
            )
            msg = "Cannot delete template with associated checklists"
            raise ValidationException(msg)

        await self._uow.templates.delete(template_id)
        logger.info("Template deleted (template_id={})", template_id)

    async def get_templates(
        self,
        skip: int = 0,
        limit: int = 50,
        department_id: int | None = None,
        status: str | None = None,
        *,
        is_default: bool | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
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
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return list(templates), total

    async def clone_template(self, template_id: int) -> Template:
        """Clone template with new version."""
        logger.info("Cloning template (template_id={})", template_id)
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
        logger.info(
            "Template cloned (source_template_id={}, new_template_id={})",
            template_id,
            new_template.id,
        )

        return await self.get_template(new_template.id)

    async def add_task_to_template(self, template_id: int, task_data: TaskTemplateCreate) -> TaskTemplate:
        """Add task to template."""
        logger.debug(
            "Adding task to template (template_id={}, title={})",
            template_id,
            task_data.title,
        )
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ARCHIVED:
            logger.warning("Cannot add task: template archived (template_id={})", template_id)
            msg = "Cannot add tasks to archived template"
            raise ValidationException(msg)

        if task_data.depends_on:
            existing_ids = await self._uow.task_templates.find_existing_ids(template_id, task_data.depends_on)
            missing_ids = set(task_data.depends_on) - existing_ids
            if missing_ids:
                logger.warning(
                    "Add task: invalid dependency IDs (template_id={}, missing={})",
                    template_id,
                    missing_ids,
                )
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

        created = await self._uow.task_templates.create(task)
        logger.info(
            "Task added to template (template_id={}, task_template_id={})",
            template_id,
            created.id,
        )
        return created

    async def publish_template(self, template_id: int) -> Template:
        """Publish template (set to active)."""
        template = await self.get_template(template_id)

        if template.status == TemplateStatus.ACTIVE:
            logger.debug("publish_template: already ACTIVE (template_id={})", template_id)
            return template

        task_count = await self._uow.templates.count_tasks(template_id)
        if task_count == 0:
            logger.warning("Cannot publish template without tasks (template_id={})", template_id)
            msg = "Cannot publish template without tasks"
            raise ValidationException(msg)

        template.status = TemplateStatus.ACTIVE
        template.updated_at = datetime.now(UTC)

        await self._uow.templates.update(template)
        logger.info("Template published (template_id={})", template_id)
        return await self.get_template(template_id)
