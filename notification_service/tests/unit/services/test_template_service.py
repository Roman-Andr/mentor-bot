"""Unit tests for notification_service/services/template.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jinja2 import TemplateError
from notification_service.models import NotificationTemplate
from notification_service.services.template import (
    MissingTemplateVariablesError,
    RenderedNotification,
    TemplateNotFoundError,
    TemplateRenderError,
    TemplateService,
)


@pytest.fixture
def mock_uow() -> MagicMock:
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.templates = MagicMock()
    uow.templates.get_by_name_channel_language = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def template_service(mock_uow: MagicMock) -> TemplateService:
    """Create a TemplateService with mock UoW."""
    return TemplateService(mock_uow)


@pytest.fixture
def sample_db_template() -> NotificationTemplate:
    """Create a sample database template."""
    return NotificationTemplate(
        id=1,
        name="welcome",
        channel="telegram",
        language="en",
        subject=None,
        body_text="Welcome, {{ user_name }}!",
        body_html=None,
        version=1,
        is_active=True,
        is_default=False,
        variables=["user_name"],
        created_by=1,
    )


class TestTemplateServiceGetTemplate:
    """Tests for TemplateService.get_template."""

    async def test_get_template_from_database(
        self, template_service: TemplateService, mock_uow: MagicMock, sample_db_template: NotificationTemplate
    ) -> None:
        """Get template from database when available."""
        mock_uow.templates.get_by_name_channel_language.return_value = sample_db_template

        result = await template_service.get_template("welcome", "telegram", "en")

        assert result is not None
        assert result.name == "welcome"
        assert result.id == 1
        mock_uow.templates.get_by_name_channel_language.assert_awaited_once_with("welcome", "telegram", "en")

    async def test_get_template_falls_back_to_defaults(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Fall back to default templates when not in database."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        result = await template_service.get_template("welcome", "telegram", "en")

        assert result is not None
        assert result.name == "welcome"
        assert result.is_default is True
        assert result.id == 0

    async def test_get_template_falls_back_to_english_when_language_not_found(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Fall back to English when specific language not found."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        result = await template_service.get_template("welcome", "telegram", "de")

        assert result is not None
        assert result.language == "de"  # The template language is set to the requested language
        assert "Welcome" in result.body_text or "{{ user_name }}" in (result.body_text or "")

    async def test_get_template_returns_none_when_not_found(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Returns None when template not in DB and no default exists."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        result = await template_service.get_template("nonexistent", "sms", "en")

        assert result is None


class TestTemplateServiceGetDefaultTemplate:
    """Tests for TemplateService._get_default_template."""

    async def test_get_default_template_exact_match(self, template_service: TemplateService) -> None:
        """Get default template with exact match."""
        result = template_service._get_default_template("welcome", "telegram", "en")

        assert result is not None
        assert result.name == "welcome"
        assert result.channel == "telegram"
        assert result.language == "en"

    async def test_get_default_template_falls_back_to_english(self, template_service: TemplateService) -> None:
        """Fall back to English when specific language not in defaults."""
        result = template_service._get_default_template("welcome", "telegram", "fr")

        assert result is not None
        assert result.language == "fr"  # Returns the requested language but with English content

    async def test_get_default_template_returns_none_for_unknown(self, template_service: TemplateService) -> None:
        """Returns None for unknown template."""
        result = template_service._get_default_template("unknown_template", "telegram", "en")

        assert result is None


class TestTemplateServiceValidateVariables:
    """Tests for TemplateService.validate_variables."""

    async def test_validate_all_variables_present(
        self, template_service: TemplateService, sample_db_template: NotificationTemplate
    ) -> None:
        """Returns empty set when all required variables provided."""
        variables = {"user_name": "John"}

        result = template_service.validate_variables(sample_db_template, variables)

        assert result == set()

    async def test_validate_missing_variables(
        self, template_service: TemplateService, sample_db_template: NotificationTemplate
    ) -> None:
        """Returns set of missing variable names."""
        variables = {}  # user_name is missing

        result = template_service.validate_variables(sample_db_template, variables)

        assert result == {"user_name"}

    async def test_validate_partial_variables(self, template_service: TemplateService) -> None:
        """Returns only the missing variables when some are provided."""
        template = NotificationTemplate(
            id=1,
            name="test",
            channel="email",
            language="en",
            variables=["user_name", "task_title", "due_date"],
        )
        variables = {"user_name": "John", "due_date": "2024-01-01"}

        result = template_service.validate_variables(template, variables)

        assert result == {"task_title"}

    async def test_validate_no_variables_required(self, template_service: TemplateService) -> None:
        """Returns empty set when template requires no variables."""
        template = NotificationTemplate(
            id=1,
            name="test",
            channel="telegram",
            language="en",
            variables=[],
        )
        variables = {}

        result = template_service.validate_variables(template, variables)

        assert result == set()


class TestTemplateServiceRender:
    """Tests for TemplateService.render."""

    async def test_render_telegram_template(self, template_service: TemplateService, mock_uow: MagicMock) -> None:
        """Render a telegram template successfully."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        result = await template_service.render(
            template_name="welcome",
            channel="telegram",
            language="en",
            variables={"user_name": "John"},
        )

        assert isinstance(result, RenderedNotification)
        assert result.subject is None
        assert "John" in result.body
        assert result.channel == "telegram"
        assert "user_name" in result.variables_used

    async def test_render_email_template_with_subject(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Render an email template with subject."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        result = await template_service.render(
            template_name="welcome",
            channel="email",
            language="en",
            variables={"user_name": "Jane"},
        )

        assert isinstance(result, RenderedNotification)
        assert result.subject is not None
        assert "Jane" in result.subject
        assert "Jane" in result.body

    async def test_render_raises_template_not_found(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Raises TemplateNotFoundError when template not found."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        with pytest.raises(TemplateNotFoundError) as exc_info:
            await template_service.render(
                template_name="nonexistent",
                channel="telegram",
                language="en",
                variables={},
            )

        assert "nonexistent" in str(exc_info.value)
        assert "telegram" in str(exc_info.value)

    async def test_render_raises_missing_variables(
        self, template_service: TemplateService, mock_uow: MagicMock, sample_db_template: NotificationTemplate
    ) -> None:
        """Raises MissingTemplateVariablesError when variables missing."""
        mock_uow.templates.get_by_name_channel_language.return_value = sample_db_template

        with pytest.raises(MissingTemplateVariablesError) as exc_info:
            await template_service.render(
                template_name="welcome",
                channel="telegram",
                language="en",
                variables={},  # user_name is missing
            )

        assert "user_name" in str(exc_info.value)

    async def test_render_without_validation(
        self, template_service: TemplateService, mock_uow: MagicMock, sample_db_template: NotificationTemplate
    ) -> None:
        """Render without validation when validate=False."""
        mock_uow.templates.get_by_name_channel_language.return_value = sample_db_template

        result = await template_service.render(
            template_name="welcome",
            channel="telegram",
            language="en",
            variables={},  # user_name missing but validation skipped
            validate=False,
        )

        assert isinstance(result, RenderedNotification)
        # Should render with empty string for missing variable
        assert "{{ user_name }}" not in result.body  # Jinja2 renders missing vars as empty

    async def test_render_raises_when_no_body_content(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Raises TemplateRenderError when template has no body content."""
        template = NotificationTemplate(
            id=1,
            name="empty",
            channel="telegram",
            language="en",
            body_text=None,
            body_html=None,
            variables=[],
        )
        mock_uow.templates.get_by_name_channel_language.return_value = template

        with pytest.raises(TemplateRenderError) as exc_info:
            await template_service.render(
                template_name="empty",
                channel="telegram",
                language="en",
                variables={},
                validate=False,
            )

        assert "no content" in str(exc_info.value).lower()

    async def test_render_raises_on_template_error(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Raises TemplateRenderError on Jinja2 template error."""
        template = NotificationTemplate(
            id=1,
            name="broken",
            channel="telegram",
            language="en",
            body_text="Hello {% if undefined_loop %}{{ user_name }}{% endif %}",
            variables=["user_name"],
        )
        mock_uow.templates.get_by_name_channel_language.return_value = template

        with patch.object(template_service._env, "from_string", side_effect=TemplateError("Syntax error")):
            with pytest.raises(TemplateRenderError) as exc_info:
                await template_service.render(
                    template_name="broken",
                    channel="telegram",
                    language="en",
                    variables={"user_name": "John"},
                    validate=False,
                )

            assert "rendering failed" in str(exc_info.value).lower()


class TestTemplateServiceRenderForUser:
    """Tests for TemplateService.render_for_user."""

    async def test_render_for_user_with_preferences(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Render template using user's preferences."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        class MockUser:
            first_name = "Alice"
            language = "en"
            preferred_channel = "email"

        user = MockUser()

        result = await template_service.render_for_user(
            template_name="welcome",
            user=user,
            variables={},
        )

        assert isinstance(result, RenderedNotification)
        assert "Alice" in result.body
        assert result.channel == "email"

    async def test_render_for_user_with_default_values(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Render with default values when user attributes missing."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        class MockUser:
            pass

        user = MockUser()

        result = await template_service.render_for_user(
            template_name="welcome",
            user=user,
            variables={},
        )

        assert isinstance(result, RenderedNotification)
        assert "User" in result.body  # Default user_name

    async def test_render_for_user_overrides_channel(
        self, template_service: TemplateService, mock_uow: MagicMock
    ) -> None:
        """Override user's preferred channel when specified."""
        mock_uow.templates.get_by_name_channel_language.return_value = None

        class MockUser:
            first_name = "Bob"
            language = "en"
            preferred_channel = "email"

        user = MockUser()

        result = await template_service.render_for_user(
            template_name="welcome",
            user=user,
            variables={},
            channel="telegram",
        )

        assert result.channel == "telegram"


class TestTemplateExceptions:
    """Tests for template-related exceptions."""

    def test_template_not_found_error(self) -> None:
        """TemplateNotFoundError stores template info."""
        exc = TemplateNotFoundError("my_template", "email", "ru")

        assert exc.template_name == "my_template"
        assert exc.channel == "email"
        assert exc.language == "ru"
        assert "my_template" in str(exc)
        assert "email" in str(exc)
        assert "ru" in str(exc)

    def test_missing_template_variables_error(self) -> None:
        """MissingTemplateVariablesError stores missing variables."""
        exc = MissingTemplateVariablesError({"var1", "var2"})

        assert exc.missing_variables == {"var1", "var2"}
        assert "var1" in str(exc)
        assert "var2" in str(exc)

    def test_template_render_error(self) -> None:
        """TemplateRenderError stores error message."""
        exc = TemplateRenderError("Something went wrong")

        assert "Something went wrong" in str(exc)
        assert "rendering failed" in str(exc).lower()


class TestRenderedNotification:
    """Tests for RenderedNotification dataclass."""

    def test_rendered_notification_creation(self) -> None:
        """Create RenderedNotification with all fields."""
        result = RenderedNotification(
            subject="Test Subject",
            body="Test body content",
            channel="email",
            variables_used=["user_name", "task_title"],
        )

        assert result.subject == "Test Subject"
        assert result.body == "Test body content"
        assert result.channel == "email"
        assert result.variables_used == ["user_name", "task_title"]

    def test_rendered_notification_no_subject(self) -> None:
        """Create RenderedNotification without subject (for telegram)."""
        result = RenderedNotification(
            subject=None,
            body="Test body content",
            channel="telegram",
            variables_used=["user_name"],
        )

        assert result.subject is None
        assert result.channel == "telegram"
