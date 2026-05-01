"""Integration tests for templates API that execute real service code."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from checklists_service.core.enums import TemplateStatus
from checklists_service.models import Template
from checklists_service.repositories.unit_of_work import IUnitOfWork
from checklists_service.schemas import TaskTemplateCreate, TemplateCreate, TemplateUpdate
from checklists_service.services import TemplateService


@pytest.fixture
def mock_template():
    """Create a mock template."""
    now = datetime.now(UTC)
    return Template(
        id=1,
        name="Test Template",
        description="Test",
        department_id=1,
        position="Developer",
        level="JUNIOR",
        duration_days=30,
        task_categories=[],
        default_assignee_role="MENTOR",
        status=TemplateStatus.DRAFT,
        version=1,
        is_default=False,
        created_at=now,
        updated_at=None,
    )


@pytest.fixture
def integration_uow():
    """Create a Unit of Work mock for integration tests."""
    uow = MagicMock(spec=IUnitOfWork)
    uow.templates = AsyncMock()
    uow.task_templates = AsyncMock()
    uow.checklists = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.mark.asyncio
async def test_create_template_service_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that calling TemplateService.create_template executes real code including logging."""
    integration_uow.templates.get_by_name_and_department = AsyncMock(return_value=None)
    integration_uow.templates.create = AsyncMock(return_value=mock_template)
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)

    template_data = TemplateCreate(
        name="Test Template",
        description="Test",
        department_id=1,
        status=TemplateStatus.DRAFT,
    )

    service = TemplateService(integration_uow)
    result = await service.create_template(template_data)

    assert result.id == 1
    integration_uow.templates.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_template_conflict_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that create_template with conflict executes real code including warning log."""
    integration_uow.templates.get_by_name_and_department = AsyncMock(return_value=mock_template)

    template_data = TemplateCreate(
        name="Test Template",
        description="Test",
        department_id=1,
        status=TemplateStatus.DRAFT,
    )

    service = TemplateService(integration_uow)

    with pytest.raises(Exception):  # ConflictException
        await service.create_template(template_data)


@pytest.mark.asyncio
async def test_update_template_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that calling TemplateService.update_template executes real code including logging."""
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.templates.update = AsyncMock(return_value=mock_template)
    integration_uow.templates.clear_other_defaults = AsyncMock()

    update_data = TemplateUpdate(name="Updated Name", is_default=True)

    service = TemplateService(integration_uow)
    result = await service.update_template(1, update_data)

    assert result.name == "Updated Name"
    integration_uow.templates.clear_other_defaults.assert_called_once()


@pytest.mark.asyncio
async def test_get_templates_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that calling TemplateService.get_templates executes real code."""
    integration_uow.templates.find_templates = AsyncMock(return_value=([mock_template], 1))

    service = TemplateService(integration_uow)
    templates, total = await service.get_templates(
        skip=0,
        limit=50,
        department_id=1,
        status="ACTIVE",
        is_default=True,
        search="test",
        sort_by="name",
        sort_order="asc",
    )

    assert len(templates) == 1
    assert total == 1


@pytest.mark.asyncio
async def test_clone_template_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that calling TemplateService.clone_template executes real code including logging."""
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.templates.create = AsyncMock(return_value=mock_template)
    integration_uow.task_templates.clone_tasks = AsyncMock()

    service = TemplateService(integration_uow)
    result = await service.clone_template(1)

    assert result.id == 1
    integration_uow.templates.create.assert_called_once()
    integration_uow.task_templates.clone_tasks.assert_called_once()


@pytest.mark.asyncio
async def test_get_template_with_tasks_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that calling TemplateService.get_template_with_tasks executes real code."""
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.task_templates.get_by_template = AsyncMock(return_value=[])

    service = TemplateService(integration_uow)
    result = await service.get_template_with_tasks(1)

    assert result.id == 1


@pytest.mark.asyncio
async def test_delete_template_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that calling TemplateService.delete_template executes real code."""
    mock_template.status = TemplateStatus.DRAFT
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.templates.has_checklists = AsyncMock(return_value=False)
    integration_uow.templates.delete = AsyncMock()

    service = TemplateService(integration_uow)
    await service.delete_template(1)

    integration_uow.templates.delete.assert_called_once()


@pytest.mark.asyncio
async def test_add_task_to_template_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that calling TemplateService.add_task_to_template executes real code."""
    from checklists_service.core.enums import TaskCategory

    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.task_templates.find_existing_ids = AsyncMock(return_value=set())
    integration_uow.task_templates.create = AsyncMock(return_value=MagicMock(id=10))

    task_data = TaskTemplateCreate(
        template_id=1,
        title="Test Task",
        description="Test",
        category=TaskCategory.TECHNICAL,
        order=0,
        due_days=5,
        depends_on=[],
    )

    service = TemplateService(integration_uow)
    result = await service.add_task_to_template(1, task_data)

    assert result.id == 10


@pytest.mark.asyncio
async def test_publish_template_executes_real_code(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test that calling TemplateService.publish_template executes real code."""
    mock_template.status = TemplateStatus.DRAFT
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.templates.count_tasks = AsyncMock(return_value=5)
    integration_uow.templates.update = AsyncMock(return_value=mock_template)

    service = TemplateService(integration_uow)
    result = await service.publish_template(1)

    assert result.status == TemplateStatus.ACTIVE


@pytest.mark.asyncio
async def test_update_template_without_default_change(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test update_template without changing is_default."""
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.templates.update = AsyncMock(return_value=mock_template)

    update_data = TemplateUpdate(name="Updated Name")

    service = TemplateService(integration_uow)
    result = await service.update_template(1, update_data)

    assert result.name == "Updated Name"
    integration_uow.templates.clear_other_defaults.assert_not_called()


@pytest.mark.asyncio
async def test_delete_template_active_template(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test delete_template for active template."""
    mock_template.status = TemplateStatus.ACTIVE
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)

    service = TemplateService(integration_uow)

    with pytest.raises(Exception):  # ValidationException
        await service.delete_template(1)


@pytest.mark.asyncio
async def test_delete_template_with_checklists(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test delete_template when template has checklists."""
    mock_template.status = TemplateStatus.DRAFT
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.templates.has_checklists = AsyncMock(return_value=True)

    service = TemplateService(integration_uow)

    with pytest.raises(Exception):  # ValidationException
        await service.delete_template(1)


@pytest.mark.asyncio
async def test_add_task_to_archived_template(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test add_task_to_template for archived template."""
    from checklists_service.core.enums import TaskCategory

    mock_template.status = TemplateStatus.ARCHIVED
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)

    task_data = TaskTemplateCreate(
        template_id=1,
        title="Test Task",
        description="Test",
        category=TaskCategory.TECHNICAL,
        order=0,
        due_days=5,
        depends_on=[],
    )

    service = TemplateService(integration_uow)

    with pytest.raises(Exception):  # ValidationException
        await service.add_task_to_template(1, task_data)


@pytest.mark.asyncio
async def test_publish_template_without_tasks(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test publish_template when template has no tasks."""
    mock_template.status = TemplateStatus.DRAFT
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.templates.count_tasks = AsyncMock(return_value=0)

    service = TemplateService(integration_uow)

    with pytest.raises(Exception):  # ValidationException
        await service.publish_template(1)


@pytest.mark.asyncio
async def test_add_task_with_dependencies(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test add_task_to_template with dependencies."""
    from checklists_service.core.enums import TaskCategory

    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.task_templates.find_existing_ids = AsyncMock(return_value={1, 2})
    integration_uow.task_templates.create = AsyncMock(return_value=MagicMock(id=10))

    task_data = TaskTemplateCreate(
        template_id=1,
        title="Test Task",
        description="Test",
        category=TaskCategory.TECHNICAL,
        order=0,
        due_days=5,
        depends_on=[1, 2],
    )

    service = TemplateService(integration_uow)
    result = await service.add_task_to_template(1, task_data)

    assert result.id == 10


@pytest.mark.asyncio
async def test_get_template_not_found(integration_uow: MagicMock) -> None:
    """Test get_template when template not found."""
    integration_uow.templates.get_by_id = AsyncMock(return_value=None)

    service = TemplateService(integration_uow)

    with pytest.raises(Exception):  # NotFoundException
        await service.get_template(999)


@pytest.mark.asyncio
async def test_add_task_invalid_dependencies(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test add_task_to_template with invalid dependency IDs."""
    from checklists_service.core.enums import TaskCategory

    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)
    integration_uow.task_templates.find_existing_ids = AsyncMock(return_value={1})  # Missing ID 2

    task_data = TaskTemplateCreate(
        template_id=1,
        title="Test Task",
        description="Test",
        category=TaskCategory.TECHNICAL,
        order=0,
        due_days=5,
        depends_on=[1, 2],  # ID 2 doesn't exist
    )

    service = TemplateService(integration_uow)

    with pytest.raises(Exception):  # ValidationException
        await service.add_task_to_template(1, task_data)


@pytest.mark.asyncio
async def test_publish_template_already_active(integration_uow: MagicMock, mock_template: Template) -> None:
    """Test publish_template when template is already ACTIVE."""
    mock_template.status = TemplateStatus.ACTIVE
    integration_uow.templates.get_by_id = AsyncMock(return_value=mock_template)

    service = TemplateService(integration_uow)
    result = await service.publish_template(1)

    assert result.status == TemplateStatus.ACTIVE
