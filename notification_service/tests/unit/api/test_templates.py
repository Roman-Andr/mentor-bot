"""Unit tests for notification_service/api/templates.py."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status

from notification_service.api.templates import (
    create_template,
    delete_template,
    get_template,
    get_template_by_name,
    list_templates,
    preview_template,
    render_template,
    update_template,
)
from notification_service.schemas.template import (
    TemplateCreate,
    TemplatePreviewRequest,
    TemplateRenderRequest,
    TemplateResponse,
    TemplateUpdate,
)


@pytest.fixture
def mock_db() -> MagicMock:
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def hr_user() -> MagicMock:
    """Create a mock HR user."""
    user = MagicMock()
    user.id = 1
    user.role = "HR"
    user.email = "hr@example.com"
    user.is_active = True
    return user


@pytest.fixture
def admin_user() -> MagicMock:
    """Create a mock admin user."""
    user = MagicMock()
    user.id = 2
    user.role = "ADMIN"
    user.email = "admin@example.com"
    user.is_active = True
    return user


@pytest.fixture
def sample_template_response() -> MagicMock:
    """Create a mock template response."""
    mock = MagicMock()
    mock.id = 1
    mock.name = "welcome"
    mock.channel = "telegram"
    mock.language = "en"
    mock.subject = None
    mock.body_text = "Welcome, {{ user_name }}!"
    mock.body_html = "<p>Welcome, {{ user_name }}!</p>"  # Need both for validation
    mock.variables = ["user_name"]
    mock.version = 1
    mock.is_active = True
    mock.is_default = False
    mock.created_at = datetime.now(UTC)
    mock.updated_at = datetime.now(UTC)
    mock.created_by = 1
    mock.model_validate = classmethod(lambda _cls, _obj: mock)
    return mock


@pytest.fixture
def sample_db_template() -> MagicMock:
    """Create a mock database template."""
    mock = MagicMock()
    mock.id = 1
    mock.name = "welcome"
    mock.channel = "telegram"
    mock.language = "en"
    mock.subject = None
    mock.body_text = "Welcome, {{ user_name }}!"
    mock.body_html = "<p>Welcome, {{ user_name }}!</p>"  # Need both for validation
    mock.variables = ["user_name"]
    mock.version = 1
    mock.is_active = True
    mock.is_default = False
    mock.created_by = 1
    return mock


class TestListTemplates:
    """Tests for the list_templates endpoint."""

    async def test_list_templates_basic(
        self, mock_db: MagicMock, hr_user: MagicMock, sample_template_response: MagicMock
    ) -> None:
        """List templates with default parameters."""
        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.find_templates = AsyncMock(return_value=([sample_template_response], 1))
            mock_uow_cls.return_value = mock_uow

            with patch.object(TemplateResponse, "model_validate", return_value=sample_template_response):
                result = await list_templates(mock_db, hr_user)

                assert result.total == 1
                assert len(result.templates) == 1
                assert result.page == 1
                assert result.size == 50
                assert result.pages == 1

    async def test_list_templates_with_filters(
        self, mock_db: MagicMock, hr_user: MagicMock, sample_template_response: MagicMock
    ) -> None:
        """List templates with filters applied."""
        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.find_templates = AsyncMock(return_value=([sample_template_response], 1))
            mock_uow_cls.return_value = mock_uow

            with patch.object(TemplateResponse, "model_validate", return_value=sample_template_response):
                result = await list_templates(
                    mock_db, hr_user, skip=10, limit=25, name="welcome", channel="telegram", language="en", is_active=True
                )

                mock_uow.templates.find_templates.assert_awaited_once_with(
                    skip=10, limit=25, name="welcome", channel="telegram", language="en", is_active=True
                )

    async def test_list_templates_empty(
        self, mock_db: MagicMock, hr_user: MagicMock
    ) -> None:
        """List templates returns empty list when none found."""
        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.find_templates = AsyncMock(return_value=([], 0))
            mock_uow_cls.return_value = mock_uow

            result = await list_templates(mock_db, hr_user)

            assert result.total == 0
            assert result.templates == []
            assert result.pages == 0


class TestGetTemplate:
    """Tests for the get_template endpoint."""

    async def test_get_template_by_id_success(
        self, mock_db: MagicMock, hr_user: MagicMock, sample_db_template: MagicMock
    ) -> None:
        """Get template by ID returns template."""
        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_id = AsyncMock(return_value=sample_db_template)
            mock_uow_cls.return_value = mock_uow

            with patch.object(TemplateResponse, "model_validate", return_value=sample_db_template):
                result = await get_template(1, mock_db, hr_user)

                assert result is sample_db_template

    async def test_get_template_by_id_not_found(
        self, mock_db: MagicMock, hr_user: MagicMock
    ) -> None:
        """Get template by ID raises 404 when not found."""
        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_id = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with pytest.raises(HTTPException) as exc_info:
                await get_template(999, mock_db, hr_user)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "999" in exc_info.value.detail


class TestGetTemplateByName:
    """Tests for the get_template_by_name endpoint."""

    async def test_get_template_by_name_from_db(
        self, mock_db: MagicMock, hr_user: MagicMock, sample_db_template: MagicMock
    ) -> None:
        """Get template by name from database."""
        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_name_channel_language = AsyncMock(return_value=sample_db_template)
            mock_uow_cls.return_value = mock_uow

            with patch.object(TemplateResponse, "model_validate", return_value=sample_db_template):
                result = await get_template_by_name("welcome", mock_db, hr_user)

                assert result is sample_db_template

    async def test_get_template_by_name_from_defaults(
        self, mock_db: MagicMock, hr_user: MagicMock
    ) -> None:
        """Get template by name falls back to defaults."""
        from notification_service.models import NotificationTemplate

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_name_channel_language = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            # Default template from TemplateService
            default_template = NotificationTemplate(
                id=0,
                name="welcome",
                channel="telegram",
                language="en",
                body_text="Welcome, {{ user_name }}!",
                version=1,
                is_active=True,
                is_default=True,
                variables=["user_name"],
            )

            with patch("notification_service.api.templates.TemplateService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service._get_default_template = MagicMock(return_value=default_template)
                mock_service_cls.return_value = mock_service

                with patch.object(TemplateResponse, "model_validate", return_value=default_template):
                    result = await get_template_by_name("welcome", mock_db, hr_user, channel="telegram", language="en")

                    assert result is default_template

    async def test_get_template_by_name_not_found(
        self, mock_db: MagicMock, hr_user: MagicMock
    ) -> None:
        """Get template by name raises 404 when not in DB or defaults."""
        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_name_channel_language = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.templates.TemplateService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service._get_default_template = MagicMock(return_value=None)
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await get_template_by_name("nonexistent", mock_db, hr_user)

                assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestCreateTemplate:
    """Tests for the create_template endpoint."""

    async def test_create_template_success(
        self, mock_db: MagicMock, admin_user: MagicMock, sample_db_template: MagicMock
    ) -> None:
        """Admin can create new template."""
        template_data = TemplateCreate(
            name="new_template",
            channel="telegram",
            language="en",
            body_text="Hello {{ name }}!",
            variables=["name"],
        )

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_name_channel_language = AsyncMock(return_value=None)
            mock_uow.templates.create = AsyncMock(return_value=sample_db_template)
            mock_uow.commit = AsyncMock()
            mock_uow_cls.return_value = mock_uow

            with patch.object(TemplateResponse, "model_validate", return_value=sample_db_template):
                result = await create_template(template_data, mock_db, admin_user)

                assert result is sample_db_template
                mock_uow.templates.create.assert_awaited_once()
                mock_uow.commit.assert_awaited_once()

    async def test_create_template_conflict_with_existing(
        self, mock_db: MagicMock, admin_user: MagicMock, sample_db_template: MagicMock
    ) -> None:
        """Cannot create template if active one already exists."""
        template_data = TemplateCreate(
            name="welcome",
            channel="telegram",
            language="en",
            body_text="Test",
        )

        # Existing non-default template
        sample_db_template.is_default = False

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_name_channel_language = AsyncMock(return_value=sample_db_template)
            mock_uow_cls.return_value = mock_uow

            with pytest.raises(HTTPException) as exc_info:
                await create_template(template_data, mock_db, admin_user)

            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert "already exists" in exc_info.value.detail


class TestUpdateTemplate:
    """Tests for the update_template endpoint."""

    async def test_update_template_success(
        self, mock_db: MagicMock, admin_user: MagicMock
    ) -> None:
        """Admin can update template (creates new version)."""
        from notification_service.models import NotificationTemplate

        update_data = TemplateUpdate(
            subject="Updated Subject",
            body_text="Updated body",
        )

        existing_template = NotificationTemplate(
            id=1,
            name="welcome",
            channel="telegram",
            language="en",
            body_text="Old body",
            version=1,
            is_active=True,
            is_default=False,
            created_by=1,
        )

        new_version = NotificationTemplate(
            id=2,
            name="welcome",
            channel="telegram",
            language="en",
            subject="Updated Subject",
            body_text="Updated body",
            version=2,
            is_active=True,
            is_default=False,
            created_by=admin_user.id,
        )

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_id = AsyncMock(return_value=existing_template)
            mock_uow.templates.update = AsyncMock()
            mock_uow.templates.create = AsyncMock(return_value=new_version)
            mock_uow.commit = AsyncMock()
            mock_uow_cls.return_value = mock_uow

            with patch.object(TemplateResponse, "model_validate", return_value=new_version):
                result = await update_template(1, update_data, mock_db, admin_user)

                assert result is new_version
                mock_uow.templates.update.assert_awaited_once_with(existing_template)
                mock_uow.commit.assert_awaited_once()

    async def test_update_template_not_found(
        self, mock_db: MagicMock, admin_user: MagicMock
    ) -> None:
        """Update raises 404 when template not found."""
        update_data = TemplateUpdate(subject="New Subject")

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_id = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with pytest.raises(HTTPException) as exc_info:
                await update_template(999, update_data, mock_db, admin_user)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_default_template_forbidden(
        self, mock_db: MagicMock, admin_user: MagicMock
    ) -> None:
        """Cannot update default templates."""
        from notification_service.models import NotificationTemplate

        update_data = TemplateUpdate(subject="New Subject")

        default_template = NotificationTemplate(
            id=1,
            name="welcome",
            channel="telegram",
            language="en",
            body_text="Default body",
            version=1,
            is_active=True,
            is_default=True,  # This is a default template
            created_by=None,
        )

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_id = AsyncMock(return_value=default_template)
            mock_uow_cls.return_value = mock_uow

            with pytest.raises(HTTPException) as exc_info:
                await update_template(1, update_data, mock_db, admin_user)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "default templates" in exc_info.value.detail.lower()


class TestDeleteTemplate:
    """Tests for the delete_template endpoint."""

    async def test_delete_template_success(
        self, mock_db: MagicMock, admin_user: MagicMock
    ) -> None:
        """Admin can delete non-default template."""
        from notification_service.models import NotificationTemplate

        template_to_delete = NotificationTemplate(
            id=1,
            name="test",
            channel="telegram",
            language="en",
            body_text="Test",
            is_default=False,
        )

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_id = AsyncMock(return_value=template_to_delete)
            mock_uow.templates.delete = AsyncMock()
            mock_uow.commit = AsyncMock()
            mock_uow_cls.return_value = mock_uow

            result = await delete_template(1, mock_db, admin_user)

            assert result == {"message": "Template 1 deleted successfully"}
            mock_uow.templates.delete.assert_awaited_once_with(1)
            mock_uow.commit.assert_awaited_once()

    async def test_delete_template_not_found(
        self, mock_db: MagicMock, admin_user: MagicMock
    ) -> None:
        """Delete raises 404 when template not found."""
        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_id = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with pytest.raises(HTTPException) as exc_info:
                await delete_template(999, mock_db, admin_user)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_default_template_forbidden(
        self, mock_db: MagicMock, admin_user: MagicMock
    ) -> None:
        """Cannot delete default templates."""
        from notification_service.models import NotificationTemplate

        default_template = NotificationTemplate(
            id=1,
            name="welcome",
            channel="telegram",
            language="en",
            body_text="Default",
            is_default=True,
        )

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow.templates = MagicMock()
            mock_uow.templates.get_by_id = AsyncMock(return_value=default_template)
            mock_uow_cls.return_value = mock_uow

            with pytest.raises(HTTPException) as exc_info:
                await delete_template(1, mock_db, admin_user)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "default templates" in exc_info.value.detail.lower()


class TestRenderTemplate:
    """Tests for the render_template endpoint."""

    async def test_render_template_success(
        self, mock_db: MagicMock, hr_user: MagicMock
    ) -> None:
        """Render template with variables."""
        render_request = TemplateRenderRequest(
            template_name="welcome",
            channel="telegram",
            language="en",
            variables={"user_name": "John"},
        )

        rendered_result = MagicMock()
        rendered_result.subject = None
        rendered_result.body = "Welcome, John!"
        rendered_result.variables_used = ["user_name"]

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.templates.TemplateService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.render = AsyncMock(return_value=rendered_result)
                mock_service_cls.return_value = mock_service

                result = await render_template(render_request, mock_db, hr_user)

                assert result.template_name == "welcome"
                assert result.subject is None
                assert result.body == "Welcome, John!"
                assert result.variables_used == ["user_name"]

    async def test_render_template_not_found(
        self, mock_db: MagicMock, hr_user: MagicMock
    ) -> None:
        """Render raises 404 when template not found."""
        from notification_service.services.template import TemplateNotFoundError

        render_request = TemplateRenderRequest(
            template_name="nonexistent",
            channel="telegram",
            language="en",
            variables={},
        )

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.templates.TemplateService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.render = AsyncMock(side_effect=TemplateNotFoundError("nonexistent", "telegram", "en"))
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await render_template(render_request, mock_db, hr_user)

                assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_render_template_missing_variables(
        self, mock_db: MagicMock, hr_user: MagicMock
    ) -> None:
        """Render raises 400 when variables missing."""
        from notification_service.services.template import MissingTemplateVariablesError

        render_request = TemplateRenderRequest(
            template_name="welcome",
            channel="telegram",
            language="en",
            variables={},
        )

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.templates.TemplateService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.render = AsyncMock(side_effect=MissingTemplateVariablesError({"user_name"}))
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await render_template(render_request, mock_db, hr_user)

                assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_render_template_render_error(
        self, mock_db: MagicMock, hr_user: MagicMock
    ) -> None:
        """Render raises 500 on TemplateRenderError (lines 250-251)."""
        from notification_service.services.template import TemplateRenderError

        render_request = TemplateRenderRequest(
            template_name="broken",
            channel="email",
            language="en",
            variables={"user_name": "Test"},
        )

        with patch("notification_service.api.templates.SqlAlchemyUnitOfWork") as mock_uow_cls:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow_cls.return_value = mock_uow

            with patch("notification_service.api.templates.TemplateService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.render = AsyncMock(side_effect=TemplateRenderError("Template parsing failed"))
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await render_template(render_request, mock_db, hr_user)

                assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert "Template parsing failed" in exc_info.value.detail


class TestPreviewTemplate:
    """Tests for the preview_template endpoint."""

    async def test_preview_template_with_text(
        self, hr_user: MagicMock
    ) -> None:
        """Preview template body with text."""
        preview_request = TemplatePreviewRequest(
            body_text="Hello {{ name }}!",
            subject="Welcome {{ name }}",
            variables={"name": "World"},
        )

        result = await preview_template(preview_request, hr_user)

        assert result.template_name == "preview"
        assert result.channel == "preview"
        assert result.subject == "Welcome World"
        assert result.body == "Hello World!"
        assert result.variables_used == ["name"]

    async def test_preview_template_with_html(
        self, hr_user: MagicMock
    ) -> None:
        """Preview template body with HTML."""
        preview_request = TemplatePreviewRequest(
            body_html="<h1>Hello {{ name }}</h1>",
            variables={"name": "User"},
        )

        result = await preview_template(preview_request, hr_user)

        assert result.body == "<h1>Hello User</h1>"
        assert result.subject is None

    async def test_preview_template_empty_body(
        self, hr_user: MagicMock
    ) -> None:
        """Preview with empty body renders empty string."""
        preview_request = TemplatePreviewRequest()

        result = await preview_template(preview_request, hr_user)

        assert result.body == ""

    async def test_preview_template_render_error(
        self, hr_user: MagicMock
    ) -> None:
        """Preview raises 400 on template error."""
        preview_request = TemplatePreviewRequest(
            body_text="Hello {% invalid %}",
            variables={},
        )

        with pytest.raises(HTTPException) as exc_info:
            await preview_template(preview_request, hr_user)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
