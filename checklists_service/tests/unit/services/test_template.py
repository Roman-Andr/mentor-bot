"""Unit tests for template service."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from checklists_service.core import ConflictException, NotFoundException, ValidationException
from checklists_service.core.enums import TemplateStatus
from checklists_service.models import TaskTemplate, Template
from checklists_service.schemas import TaskTemplateCreate, TemplateCreate, TemplateUpdate
from checklists_service.services import TemplateService


class TestTemplateServiceCreate:
    """Test template creation."""

    async def test_create_template_success(
        self, mock_uow: MagicMock, sample_datetime: datetime
    ) -> None:
        """Test successful template creation."""
        mock_uow.templates.get_by_name_and_department.return_value = None
        mock_uow.templates.create.return_value = Template(
            id=1,
            name="New Template",
            description="A new test template",
            department_id=1,
            position="Developer",
            duration_days=30,
            task_categories=[],
            default_assignee_role="MENTOR",
            status=TemplateStatus.DRAFT,
            version=1,
            is_default=False,
            created_at=sample_datetime,
            updated_at=None,
        )
        mock_uow.templates.get_by_id.return_value = mock_uow.templates.create.return_value

        template_data = TemplateCreate(
            name="New Template",
            description="A new test template",
            department_id=1,
            position="Developer",
            duration_days=30,
            task_categories=[],
            default_assignee_role="MENTOR",
            status=TemplateStatus.DRAFT,
        )

        service = TemplateService(mock_uow)
        result = await service.create_template(template_data)

        assert result.id == 1
        assert result.name == "New Template"
        assert result.status == TemplateStatus.DRAFT
        mock_uow.templates.create.assert_called_once()

    async def test_create_template_duplicate_name_fails(
        self, mock_uow: MagicMock, sample_template: Template
    ) -> None:
        """Test template creation fails with duplicate name in same department."""
        mock_uow.templates.get_by_name_and_department.return_value = sample_template

        template_data = TemplateCreate(
            name="Onboarding Template",
            description="Duplicate template",
            department_id=1,
            status=TemplateStatus.DRAFT,
        )

        service = TemplateService(mock_uow)

        with pytest.raises(ConflictException, match="Template with this name already exists"):
            await service.create_template(template_data)


class TestTemplateServiceGet:
    """Test template retrieval."""

    async def test_get_template_success(self, mock_uow: MagicMock, sample_template: Template) -> None:
        """Test successful template retrieval."""
        mock_uow.templates.get_by_id.return_value = sample_template

        service = TemplateService(mock_uow)
        result = await service.get_template(1)

        assert result.id == 1
        assert result.name == "Onboarding Template"

    async def test_get_template_not_found(self, mock_uow: MagicMock) -> None:
        """Test template retrieval fails when not found."""
        mock_uow.templates.get_by_id.return_value = None

        service = TemplateService(mock_uow)

        with pytest.raises(NotFoundException, match="Template"):
            await service.get_template(999)

    async def test_get_template_with_tasks(
        self,
        mock_uow: MagicMock,
        sample_template: Template,
        sample_task_template: TaskTemplate,
    ) -> None:
        """Test getting template with its tasks."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.task_templates.find_by_template.return_value = [sample_task_template]

        service = TemplateService(mock_uow)
        result = await service.get_template_with_tasks(1)

        assert result.id == 1
        assert len(result.tasks) == 1
        assert result.tasks[0].title == "Complete Documentation"


class TestTemplateServiceUpdate:
    """Test template updates."""

    async def test_update_template_success(
        self, mock_uow: MagicMock, sample_template: Template
    ) -> None:
        """Test successful template update."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.templates.update.return_value = sample_template
        mock_uow.templates.clear_other_defaults.return_value = None
        mock_uow.templates.get_by_id.return_value = sample_template

        update_data = TemplateUpdate(name="Updated Name", description="Updated description")

        service = TemplateService(mock_uow)
        result = await service.update_template(1, update_data)

        assert result.name == "Updated Name"
        assert result.description == "Updated description"

    async def test_update_template_set_default(
        self, mock_uow: MagicMock, sample_template: Template
    ) -> None:
        """Test setting template as default clears others."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.templates.clear_other_defaults.return_value = None
        mock_uow.templates.update.return_value = sample_template

        update_data = TemplateUpdate(is_default=True)

        service = TemplateService(mock_uow)
        await service.update_template(1, update_data)

        mock_uow.templates.clear_other_defaults.assert_called_once_with(1, 1)

    async def test_update_template_not_found(self, mock_uow: MagicMock) -> None:
        """Test update fails when template not found."""
        mock_uow.templates.get_by_id.return_value = None

        service = TemplateService(mock_uow)

        with pytest.raises(NotFoundException, match="Template"):
            await service.update_template(999, TemplateUpdate(name="Test"))


class TestTemplateServiceDelete:
    """Test template deletion."""

    async def test_delete_template_success(
        self, mock_uow: MagicMock, sample_template_draft: Template
    ) -> None:
        """Test successful template deletion."""
        mock_uow.templates.get_by_id.return_value = sample_template_draft
        mock_uow.templates.has_checklists.return_value = False

        service = TemplateService(mock_uow)
        await service.delete_template(2)

        mock_uow.templates.delete.assert_called_once_with(2)

    async def test_delete_template_active_fails(
        self, mock_uow: MagicMock, sample_template: Template
    ) -> None:
        """Test deletion fails for active template."""
        mock_uow.templates.get_by_id.return_value = sample_template

        service = TemplateService(mock_uow)

        with pytest.raises(ValidationException, match="Cannot delete active template"):
            await service.delete_template(1)

    async def test_delete_template_with_checklists_fails(
        self, mock_uow: MagicMock, sample_template_draft: Template
    ) -> None:
        """Test deletion fails for template with associated checklists."""
        mock_uow.templates.get_by_id.return_value = sample_template_draft
        mock_uow.templates.has_checklists.return_value = True

        service = TemplateService(mock_uow)

        with pytest.raises(ValidationException, match="Cannot delete template with associated checklists"):
            await service.delete_template(2)

    async def test_delete_template_not_found(self, mock_uow: MagicMock) -> None:
        """Test deletion fails when template not found."""
        mock_uow.templates.get_by_id.return_value = None

        service = TemplateService(mock_uow)

        with pytest.raises(NotFoundException, match="Template"):
            await service.delete_template(999)


class TestTemplateServiceList:
    """Test listing templates."""

    async def test_get_templates(self, mock_uow: MagicMock, sample_template: Template) -> None:
        """Test getting list of templates."""
        mock_uow.templates.find_templates.return_value = ([sample_template], 1)

        service = TemplateService(mock_uow)
        templates, total = await service.get_templates(skip=0, limit=50)

        assert len(templates) == 1
        assert total == 1

    async def test_get_templates_with_filters(
        self, mock_uow: MagicMock, sample_template: Template
    ) -> None:
        """Test getting templates with filters."""
        mock_uow.templates.find_templates.return_value = ([sample_template], 1)

        service = TemplateService(mock_uow)
        templates, _total = await service.get_templates(
            skip=0,
            limit=50,
            department_id=1,
            status="ACTIVE",  # Use enum value name
            is_default=False,
            search="onboarding",
        )

        assert len(templates) == 1
        mock_uow.templates.find_templates.assert_called_once()


class TestTemplateServiceClone:
    """Test template cloning."""

    async def test_clone_template_success(
        self,
        mock_uow: MagicMock,
        sample_template: Template,
        sample_datetime: datetime,
    ) -> None:
        """Test successful template cloning."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.templates.create.return_value = Template(
            id=3,
            name="Onboarding Template (Copy)",
            description=sample_template.description,
            department_id=sample_template.department_id,
            position=sample_template.position,
            duration_days=sample_template.duration_days,
            task_categories=sample_template.task_categories.copy(),
            default_assignee_role=sample_template.default_assignee_role,
            status=TemplateStatus.DRAFT,
            version=2,
            is_default=False,
            created_at=sample_datetime,
            updated_at=None,
        )
        mock_uow.templates.get_by_id.return_value = mock_uow.templates.create.return_value

        service = TemplateService(mock_uow)
        result = await service.clone_template(1)

        assert result.name == "Onboarding Template (Copy)"
        assert result.status == TemplateStatus.DRAFT
        assert result.version == 2
        mock_uow.task_templates.clone_tasks.assert_called_once_with(1, 3)

    async def test_clone_template_not_found(self, mock_uow: MagicMock) -> None:
        """Test cloning fails when template not found."""
        mock_uow.templates.get_by_id.return_value = None

        service = TemplateService(mock_uow)

        with pytest.raises(NotFoundException, match="Template"):
            await service.clone_template(999)


class TestTemplateServiceAddTask:
    """Test adding tasks to templates."""

    async def test_add_task_to_template_success(
        self,
        mock_uow: MagicMock,
        sample_template: Template,
        sample_datetime: datetime,
    ) -> None:
        """Test successful task addition to template."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.task_templates.find_existing_ids.return_value = {1, 2}
        mock_uow.task_templates.create.return_value = TaskTemplate(
            id=10,
            template_id=1,
            title="New Task",
            description="Task description",
            category="DOCUMENTATION",
            order=5,
            due_days=3,
            depends_on=[1, 2],
            created_at=sample_datetime,
            updated_at=None,
        )

        task_data = TaskTemplateCreate(
            template_id=1,
            title="New Task",
            description="Task description",
            category="DOCUMENTATION",
            order=5,
            due_days=3,
            depends_on=[1, 2],
        )

        service = TemplateService(mock_uow)
        result = await service.add_task_to_template(1, task_data)

        assert result.template_id == 1
        assert result.title == "New Task"
        assert result.depends_on == [1, 2]

    async def test_add_task_to_archived_template_fails(
        self, mock_uow: MagicMock, sample_template: Template
    ) -> None:
        """Test adding task to archived template fails."""
        sample_template.status = TemplateStatus.ARCHIVED
        mock_uow.templates.get_by_id.return_value = sample_template

        task_data = TaskTemplateCreate(
            template_id=1,
            title="New Task",
            description="Task description",
            category="DOCUMENTATION",
            order=0,
            due_days=1,
        )

        service = TemplateService(mock_uow)

        with pytest.raises(ValidationException, match="Cannot add tasks to archived template"):
            await service.add_task_to_template(1, task_data)

    async def test_add_task_with_invalid_dependencies_fails(
        self, mock_uow: MagicMock, sample_template: Template
    ) -> None:
        """Test adding task with invalid dependency IDs fails."""
        mock_uow.templates.get_by_id.return_value = sample_template
        mock_uow.task_templates.find_existing_ids.return_value = {1}  # Missing ID 999

        task_data = TaskTemplateCreate(
            template_id=1,
            title="New Task",
            description="Task description",
            category="DOCUMENTATION",
            order=0,
            due_days=1,
            depends_on=[1, 999],
        )

        service = TemplateService(mock_uow)

        with pytest.raises(ValidationException, match="Invalid dependency IDs"):
            await service.add_task_to_template(1, task_data)


class TestTemplateServicePublish:
    """Test template publishing."""

    async def test_publish_template_success(
        self, mock_uow: MagicMock, sample_template_draft: Template
    ) -> None:
        """Test successful template publishing."""
        mock_uow.templates.get_by_id.return_value = sample_template_draft
        mock_uow.templates.count_tasks.return_value = 5
        mock_uow.templates.update.return_value = sample_template_draft
        mock_uow.templates.get_by_id.return_value = sample_template_draft

        service = TemplateService(mock_uow)
        result = await service.publish_template(2)

        assert result.status == TemplateStatus.ACTIVE

    async def test_publish_already_active_template(
        self, mock_uow: MagicMock, sample_template: Template
    ) -> None:
        """Test publishing already active template returns as-is."""
        mock_uow.templates.get_by_id.return_value = sample_template

        service = TemplateService(mock_uow)
        result = await service.publish_template(1)

        assert result.status == TemplateStatus.ACTIVE
        mock_uow.templates.update.assert_not_called()

    async def test_publish_template_no_tasks_fails(
        self, mock_uow: MagicMock, sample_template_draft: Template
    ) -> None:
        """Test publishing template without tasks fails."""
        mock_uow.templates.get_by_id.return_value = sample_template_draft
        mock_uow.templates.count_tasks.return_value = 0

        service = TemplateService(mock_uow)

        with pytest.raises(ValidationException, match="Cannot publish template without tasks"):
            await service.publish_template(2)

    async def test_publish_template_not_found(self, mock_uow: MagicMock) -> None:
        """Test publishing fails when template not found."""
        mock_uow.templates.get_by_id.return_value = None

        service = TemplateService(mock_uow)

        with pytest.raises(NotFoundException, match="Template"):
            await service.publish_template(999)
