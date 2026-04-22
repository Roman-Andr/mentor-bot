"""Unit tests for templates API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from checklists_service.api.deps import UserInfo
from checklists_service.api.endpoints import templates
from checklists_service.core import ConflictException, NotFoundException
from checklists_service.core.enums import TemplateStatus
from checklists_service.schemas import (
    TaskTemplateCreate,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)


@pytest.fixture
def sample_hr_user():
    """Create sample HR user."""
    return UserInfo({
        "id": 10, "email": "hr@example.com", "role": "HR",
        "is_active": True, "employee_id": "HR001"
    })


@pytest.fixture
def sample_admin_user():
    """Create sample admin user."""
    return UserInfo({
        "id": 11, "email": "admin@example.com", "role": "ADMIN",
        "is_active": True, "employee_id": "ADM001"
    })


@pytest.fixture
def sample_template():
    """Create sample template."""
    now = datetime.now(UTC)
    return MagicMock(
        id=1,
        name="Onboarding Template",
        description="Standard onboarding template",
        department_id=1,
        position="Developer",
        level="JUNIOR",
        duration_days=30,
        task_categories=["DOCUMENTATION", "TRAINING"],
        default_assignee_role="MENTOR",
        status=TemplateStatus.ACTIVE,
        version=1,
        is_default=False,
        department=MagicMock(id=1, name="Engineering"),
        created_at=now,
        updated_at=None,
    )


@pytest.fixture
def sample_task_template():
    """Create sample task template."""
    now = datetime.now(UTC)
    return MagicMock(
        id=1,
        template_id=1,
        title="Complete Documentation",
        description="Read and sign documentation",
        instructions="Follow the guide",
        category="DOCUMENTATION",
        order=0,
        due_days=3,
        estimated_minutes=60,
        resources=[{"title": "Guide", "url": "https://example.com/guide"}],
        required_documents=["signed_contract"],
        assignee_role="MENTOR",
        auto_assign=True,
        depends_on=[],
        created_at=now,
        updated_at=None,
    )


class TestGetTemplates:
    """Test GET /templates endpoint."""

    async def test_get_templates(self, sample_hr_user) -> None:
        """Test getting list of templates."""
        uow = MagicMock()

        now = datetime.now(UTC)

        # Create proper TemplateResponse
        template_response = TemplateResponse(
            id=1,
            name="Onboarding Template",
            description="Test",
            department_id=1,
            position="Developer",
            level="JUNIOR",
            duration_days=30,
            task_categories=[],
            default_assignee_role="MENTOR",
            status=TemplateStatus.ACTIVE,
            version=1,
            is_default=False,
            department=None,
            created_at=now,
            updated_at=None,
        )

        mock_template = MagicMock()
        mock_template.id = 1
        mock_template.name = "Onboarding Template"

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_templates = AsyncMock(return_value=([mock_template], 1))

            # Mock the model_validate for the template
            with patch(
                "checklists_service.schemas.template.TemplateResponse.model_validate",
                return_value=template_response,
            ):
                result = await templates.get_templates(
                    uow=uow,
                    _current_user=sample_hr_user,
                )

                # Should return list of TemplateResponse objects
                assert len(result) == 1

    async def test_get_templates_with_filters(self, sample_hr_user) -> None:
        """Test getting templates with filters."""
        uow = MagicMock()

        now = datetime.now(UTC)

        # Create proper TemplateResponse
        template_response = TemplateResponse(
            id=1,
            name="Onboarding Template",
            description="Test",
            department_id=1,
            position="Developer",
            level="JUNIOR",
            duration_days=30,
            task_categories=[],
            default_assignee_role="MENTOR",
            status=TemplateStatus.ACTIVE,
            version=1,
            is_default=False,
            department=None,
            created_at=now,
            updated_at=None,
        )

        mock_template = MagicMock()
        mock_template.id = 1
        mock_template.name = "Onboarding Template"

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_templates = AsyncMock(return_value=([mock_template], 1))

            with patch(
                "checklists_service.schemas.template.TemplateResponse.model_validate",
                return_value=template_response,
            ):
                result = await templates.get_templates(
                    uow=uow,
                    _current_user=sample_hr_user,
                    skip=0,
                    limit=50,
                    department_id=1,
                    status="ACTIVE",
                    is_default=False,
                    search="onboarding",
                )

                assert len(result) == 1


class TestCreateTemplate:
    """Test POST /templates endpoint."""

    async def test_create_template_success(self, sample_admin_user) -> None:
        """Test successful template creation."""
        uow = MagicMock()
        now = datetime.now(UTC)

        # Create proper TemplateResponse
        template_response = TemplateResponse(
            id=2,
            name="New Template",
            description="A new test template",
            department_id=1,
            position="Developer",
            level="JUNIOR",
            duration_days=30,
            task_categories=[],
            default_assignee_role="MENTOR",
            status=TemplateStatus.DRAFT,
            version=1,
            is_default=False,
            department=None,
            created_at=now,
            updated_at=None,
        )

        template_data = TemplateCreate(
            name="New Template",
            description="A new test template",
            department_id=1,
            position="Developer",
            level="JUNIOR",
            duration_days=30,
            task_categories=["DOCUMENTATION", "TRAINING"],
            default_assignee_role="MENTOR",
            status=TemplateStatus.DRAFT,
        )

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.create_template = AsyncMock(return_value=template_response)
            uow.commit = AsyncMock()

            result = await templates.create_template(
                template_data=template_data,
                uow=uow,
                _current_user=sample_admin_user,
            )

            assert result.name == "New Template"
            assert result.status == TemplateStatus.DRAFT
            uow.commit.assert_awaited_once()

    async def test_create_template_conflict(self, sample_admin_user) -> None:
        """Test template creation fails with duplicate name."""
        uow = MagicMock()
        template_data = TemplateCreate(
            name="Existing Template",
            description="Duplicate template",
            status=TemplateStatus.DRAFT,
        )

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.create_template = AsyncMock(
                side_effect=ConflictException("Template with this name already exists")
            )

            with pytest.raises(HTTPException) as exc_info:
                await templates.create_template(
                    template_data=template_data,
                    uow=uow,
                    _current_user=sample_admin_user,
                )

            assert exc_info.value.status_code == 409


class TestGetTemplate:
    """Test GET /templates/{template_id} endpoint."""

    async def test_get_template_with_tasks(
        self, sample_hr_user, sample_template, sample_task_template  # noqa: ARG002
    ) -> None:
        """Test getting template with its tasks."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_template_with_tasks = AsyncMock(return_value=MagicMock(
                id=1, name="Onboarding Template", tasks=[sample_task_template]
            ))

            result = await templates.get_template(
                template_id=1,
                uow=uow,
                _current_user=sample_hr_user,
            )

            assert result.id == 1

    async def test_get_template_not_found(self, sample_hr_user) -> None:
        """Test getting non-existent template returns 404."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_template_with_tasks = AsyncMock(side_effect=NotFoundException("Template"))

            with pytest.raises(HTTPException) as exc_info:
                await templates.get_template(
                    template_id=999,
                    uow=uow,
                    _current_user=sample_hr_user,
                )

            assert exc_info.value.status_code == 404


class TestUpdateTemplateNotFound:
    """Test update_template NotFoundException handling."""

    async def test_update_template_not_found(self, sample_admin_user) -> None:
        """Test updating non-existent template raises 404."""
        uow = MagicMock()

        update_data = TemplateUpdate(name="Updated Name")

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.update_template = AsyncMock(side_effect=NotFoundException("Template"))

            with pytest.raises(HTTPException) as exc_info:
                await templates.update_template(
                    template_id=999,
                    template_data=update_data,
                    uow=uow,
                    _current_user=sample_admin_user,
                )

            assert exc_info.value.status_code == 404


class TestDeleteTemplateNotFound:
    """Test delete_template NotFoundException handling."""

    async def test_delete_template_not_found(self, sample_admin_user) -> None:
        """Test deleting non-existent template raises 404."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.delete_template = AsyncMock(side_effect=NotFoundException("Template"))

            with pytest.raises(HTTPException) as exc_info:
                await templates.delete_template(
                    template_id=999,
                    uow=uow,
                    _current_user=sample_admin_user,
                )

            assert exc_info.value.status_code == 404


class TestCloneTemplateNotFound:
    """Test clone_template NotFoundException handling."""

    async def test_clone_template_not_found(self, sample_admin_user) -> None:
        """Test cloning non-existent template raises 404."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.clone_template = AsyncMock(side_effect=NotFoundException("Template"))

            with pytest.raises(HTTPException) as exc_info:
                await templates.clone_template(
                    template_id=999,
                    uow=uow,
                    _current_user=sample_admin_user,
                )

            assert exc_info.value.status_code == 404


class TestAddTaskToTemplateNotFound:
    """Test add_task_to_template NotFoundException handling."""

    async def test_add_task_to_template_not_found(self, sample_admin_user) -> None:
        """Test adding task to non-existent template raises 404."""
        uow = MagicMock()

        task_data = TaskTemplateCreate(
            template_id=999,
            title="New Task",
            description="Task description",
            category="TECHNICAL",
            order=0,
            due_days=5,
            depends_on=[],
        )

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.add_task_to_template = AsyncMock(side_effect=NotFoundException("Template"))

            with pytest.raises(HTTPException) as exc_info:
                await templates.add_task_to_template(
                    template_id=999,
                    task_data=task_data,
                    uow=uow,
                    _current_user=sample_admin_user,
                )

            assert exc_info.value.status_code == 404


class TestPublishTemplateNotFound:
    """Test publish_template NotFoundException handling."""

    async def test_publish_template_not_found(self, sample_admin_user) -> None:
        """Test publishing non-existent template raises 404."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.publish_template = AsyncMock(side_effect=NotFoundException("Template"))

            with pytest.raises(HTTPException) as exc_info:
                await templates.publish_template(
                    template_id=999,
                    uow=uow,
                    _current_user=sample_admin_user,
                )

            assert exc_info.value.status_code == 404


class TestUpdateTemplate:
    """Test PUT /templates/{template_id} endpoint."""

    async def test_update_template_success(self, sample_admin_user) -> None:
        """Test successful template update."""
        uow = MagicMock()
        now = datetime.now(UTC)
        update_data = TemplateUpdate(name="Updated Name", description="Updated description")

        # Return proper TemplateResponse
        template_response = TemplateResponse(
            id=1,
            name="Updated Name",
            description="Updated description",
            department_id=1,
            position="Developer",
            level="JUNIOR",
            duration_days=30,
            task_categories=[],
            default_assignee_role="MENTOR",
            status=TemplateStatus.ACTIVE,
            version=1,
            is_default=False,
            department=None,
            created_at=now,
            updated_at=now,
        )

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.update_template = AsyncMock(return_value=template_response)
            uow.commit = AsyncMock()

            result = await templates.update_template(
                template_id=1,
                template_data=update_data,
                uow=uow,
                _current_user=sample_admin_user,
            )

            assert result.name == "Updated Name"
            uow.commit.assert_awaited_once()


class TestDeleteTemplate:
    """Test DELETE /templates/{template_id} endpoint."""

    async def test_delete_template_success(self, sample_admin_user) -> None:
        """Test successful template deletion."""
        uow = MagicMock()
        uow.commit = AsyncMock()

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.delete_template = AsyncMock(return_value=None)

            result = await templates.delete_template(
                template_id=1,
                uow=uow,
                _current_user=sample_admin_user,
            )

            assert "deleted" in result.message.lower()
            uow.commit.assert_awaited_once()


class TestCloneTemplate:
    """Test POST /templates/{template_id}/clone endpoint."""

    async def test_clone_template_success(self, sample_admin_user) -> None:
        """Test successful template cloning."""
        uow = MagicMock()
        now = datetime.now(UTC)

        # Return proper TemplateResponse
        template_response = TemplateResponse(
            id=3,
            name="Onboarding Template (Copy)",
            description="Cloned template",
            department_id=1,
            position="Developer",
            level="JUNIOR",
            duration_days=30,
            task_categories=[],
            default_assignee_role="MENTOR",
            status=TemplateStatus.DRAFT,
            version=2,
            is_default=False,
            department=None,
            created_at=now,
            updated_at=None,
        )

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.clone_template = AsyncMock(return_value=template_response)
            uow.commit = AsyncMock()

            result = await templates.clone_template(
                template_id=1,
                uow=uow,
                _current_user=sample_admin_user,
            )

            assert result.name == "Onboarding Template (Copy)"
            assert result.version == 2
            uow.commit.assert_awaited_once()


class TestAddTaskToTemplate:
    """Test POST /templates/{template_id}/tasks endpoint."""

    async def test_add_task_to_template_success(self, sample_admin_user, sample_task_template) -> None:
        """Test successful task addition to template."""
        uow = MagicMock()

        task_data = TaskTemplateCreate(
            template_id=1,
            title="New Task",
            description="Task description",
            category="TECHNICAL",
            order=0,
            due_days=5,
            depends_on=[],
        )

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.add_task_to_template = AsyncMock(return_value=sample_task_template)
            uow.commit = AsyncMock()

            result = await templates.add_task_to_template(
                template_id=1,
                task_data=task_data,
                uow=uow,
                _current_user=sample_admin_user,
            )

            assert result.template_id == 1
            uow.commit.assert_awaited_once()


class TestPublishTemplate:
    """Test POST /templates/{template_id}/publish endpoint."""

    async def test_publish_template_success(self, sample_admin_user) -> None:
        """Test successful template publishing."""
        uow = MagicMock()
        now = datetime.now(UTC)

        # Return proper TemplateResponse
        template_response = TemplateResponse(
            id=1,
            name="Onboarding Template",
            description="Active template",
            department_id=1,
            position="Developer",
            level="JUNIOR",
            duration_days=30,
            task_categories=[],
            default_assignee_role="MENTOR",
            status=TemplateStatus.ACTIVE,
            version=1,
            is_default=False,
            department=None,
            created_at=now,
            updated_at=now,
        )

        with patch("checklists_service.api.endpoints.templates.TemplateService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.publish_template = AsyncMock(return_value=template_response)
            uow.commit = AsyncMock()

            result = await templates.publish_template(
                template_id=1,
                uow=uow,
                _current_user=sample_admin_user,
            )

            assert result.status == TemplateStatus.ACTIVE
            uow.commit.assert_awaited_once()
