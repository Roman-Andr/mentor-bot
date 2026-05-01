"""Unit tests for notification_service/schemas/template.py."""

from datetime import UTC, datetime

import pytest
from notification_service.schemas.template import (
    TemplateBase,
    TemplateCreate,
    TemplateListResponse,
    TemplatePreviewRequest,
    TemplateRenderRequest,
    TemplateRenderResponse,
    TemplateResponse,
    TemplateUpdate,
)
from pydantic import ValidationError


class TestTemplateBase:
    """Tests for TemplateBase schema."""

    def test_valid_template_base(self) -> None:
        """Create valid TemplateBase with all fields."""
        data = {
            "name": "welcome",
            "channel": "email",
            "language": "en",
            "subject": "Welcome!",
            "body_html": "<h1>Welcome</h1>",
            "body_text": "Welcome text",
            "variables": ["user_name"],
        }

        result = TemplateBase(**data)

        assert result.name == "welcome"
        assert result.channel == "email"
        assert result.language == "en"
        assert result.subject == "Welcome!"
        assert result.body_html == "<h1>Welcome</h1>"
        assert result.body_text == "Welcome text"
        assert result.variables == ["user_name"]

    def test_channel_case_insensitive(self) -> None:
        """Channel validation is case-insensitive and lowercases result."""
        data = {
            "name": "test",
            "channel": "EMAIL",
            "body_text": "Test",
        }

        result = TemplateBase(**data)

        assert result.channel == "email"

    def test_invalid_channel_raises_error(self) -> None:
        """Invalid channel value raises ValidationError."""
        data = {
            "name": "test",
            "channel": "invalid_channel",
            "body_text": "Test",
        }

        with pytest.raises(ValidationError) as exc_info:
            TemplateBase(**data)

        assert "channel" in str(exc_info.value)
        assert "email" in str(exc_info.value)
        assert "telegram" in str(exc_info.value)

    def test_valid_channels_accepted(self) -> None:
        """All valid channels (email, telegram, sms) are accepted."""
        for channel in ["email", "telegram", "sms", "EMAIL", "Telegram", "SMS"]:
            data = {
                "name": "test",
                "channel": channel,
                "body_text": "Test content",
            }

            result = TemplateBase(**data)
            assert result.channel == channel.lower()

    def test_default_language_is_en(self) -> None:
        """Default language is 'en' when not specified."""
        data = {
            "name": "test",
            "channel": "email",
            "body_text": "Test",
        }

        result = TemplateBase(**data)

        assert result.language == "en"

    def test_body_content_validation_both_provided(self) -> None:
        """Valid when both body_text and body_html provided."""
        data = {
            "name": "test",
            "channel": "email",
            "body_text": "Text version",
            "body_html": "<p>HTML version</p>",
        }

        result = TemplateBase(**data)

        assert result.body_text == "Text version"
        assert result.body_html == "<p>HTML version</p>"

    def test_body_content_validation_only_text(self) -> None:
        """Valid when only body_text provided."""
        data = {
            "name": "test",
            "channel": "telegram",
            "body_text": "Text version only",
        }

        result = TemplateBase(**data)

        assert result.body_text == "Text version only"
        assert result.body_html is None

    def test_body_content_validation_only_html(self) -> None:
        """Valid when only body_html provided."""
        data = {
            "name": "test",
            "channel": "email",
            "body_html": "<p>HTML only</p>",
        }

        result = TemplateBase(**data)

        assert result.body_html == "<p>HTML only</p>"
        assert result.body_text is None

    def test_body_content_validation_body_html_none_with_text_set(self) -> None:
        """Valid when body_html=None explicitly but body_text is set."""
        data = {
            "name": "test",
            "channel": "telegram",
            "body_text": "Plain text content",
            "body_html": None,  # Explicitly pass None
        }

        result = TemplateBase(**data)
        assert result.body_text == "Plain text content"
        assert result.body_html is None

    def test_body_content_validation_body_text_none_with_html_set(self) -> None:
        """Valid when body_text=None explicitly but body_html is set."""
        data = {
            "name": "test",
            "channel": "email",
            "body_text": None,  # Explicitly pass None
            "body_html": "<p>HTML content</p>",
        }

        result = TemplateBase(**data)
        assert result.body_html == "<p>HTML content</p>"
        assert result.body_text is None

    def test_body_content_validation_neither_body_raises_error(self) -> None:
        """Test model_validator: error raised when neither body_text nor body_html provided."""
        data = {
            "name": "test",
            "channel": "email",
            # Neither body_text nor body_html provided
        }

        with pytest.raises(ValidationError) as exc_info:
            TemplateBase(**data)

        assert "at least one" in str(exc_info.value).lower()

    def test_body_content_validation_both_explicit_none_raises_error(self) -> None:
        """Test model_validator: error raised when both body_text and body_html are explicitly None."""
        data = {
            "name": "test",
            "channel": "email",
            "body_text": None,
            "body_html": None,
        }

        with pytest.raises(ValidationError) as exc_info:
            TemplateBase(**data)

        assert "at least one" in str(exc_info.value).lower()

    def test_empty_variables_list_default(self) -> None:
        """Default empty variables list when not provided."""
        data = {
            "name": "test",
            "channel": "email",
            "body_text": "Test",
        }

        result = TemplateBase(**data)

        assert result.variables == []

    def test_name_min_length_validation(self) -> None:
        """Name must be at least 1 character."""
        data = {
            "name": "",
            "channel": "email",
            "body_text": "Test",
        }

        with pytest.raises(ValidationError) as exc_info:
            TemplateBase(**data)

        assert "name" in str(exc_info.value)

    def test_name_max_length_validation(self) -> None:
        """Name must not exceed 100 characters."""
        data = {
            "name": "a" * 101,
            "channel": "email",
            "body_text": "Test",
        }

        with pytest.raises(ValidationError) as exc_info:
            TemplateBase(**data)

        assert "name" in str(exc_info.value)

    def test_subject_max_length_validation(self) -> None:
        """Subject must not exceed 500 characters."""
        data = {
            "name": "test",
            "channel": "email",
            "body_text": "Test",
            "subject": "a" * 501,
        }

        with pytest.raises(ValidationError) as exc_info:
            TemplateBase(**data)

        assert "subject" in str(exc_info.value)


class TestTemplateCreate:
    """Tests for TemplateCreate schema."""

    def test_template_create_inherits_base(self) -> None:
        """TemplateCreate inherits all validations from TemplateBase."""
        data = {
            "name": "new_template",
            "channel": "telegram",
            "language": "ru",
            "body_text": "Привет, {{ user_name }}!",
            "variables": ["user_name"],
        }

        result = TemplateCreate(**data)

        assert result.name == "new_template"
        assert result.channel == "telegram"
        assert result.language == "ru"


class TestTemplateUpdate:
    """Tests for TemplateUpdate schema."""

    def test_all_fields_optional(self) -> None:
        """All fields in TemplateUpdate are optional."""
        result = TemplateUpdate()

        assert result.subject is None
        assert result.body_html is None
        assert result.body_text is None
        assert result.variables is None
        assert result.is_active is None

    def test_partial_update(self) -> None:
        """Can update only specific fields."""
        data = {
            "subject": "Updated Subject",
            "is_active": False,
        }

        result = TemplateUpdate(**data)

        assert result.subject == "Updated Subject"
        assert result.is_active is False
        assert result.body_html is None
        assert result.body_text is None
        assert result.variables is None

    def test_update_body_fields(self) -> None:
        """Can update body fields."""
        data = {
            "body_html": "<h1>New HTML</h1>",
            "body_text": "New text",
        }

        result = TemplateUpdate(**data)

        assert result.body_html == "<h1>New HTML</h1>"
        assert result.body_text == "New text"

    def test_update_variables(self) -> None:
        """Can update variables list."""
        data = {
            "variables": ["user_name", "task_title"],
        }

        result = TemplateUpdate(**data)

        assert result.variables == ["user_name", "task_title"]


class TestTemplateResponse:
    """Tests for TemplateResponse schema."""

    def test_full_response(self) -> None:
        """Create complete TemplateResponse."""
        now = datetime.now(UTC)

        data = {
            "id": 1,
            "name": "welcome",
            "channel": "email",
            "language": "en",
            "subject": "Welcome!",
            "body_html": "<h1>Welcome</h1>",
            "body_text": "Welcome text",
            "variables": ["user_name"],
            "version": 2,
            "is_active": True,
            "is_default": False,
            "created_at": now,
            "updated_at": now,
            "created_by": 42,
        }

        result = TemplateResponse(**data)

        assert result.id == 1
        assert result.version == 2
        assert result.is_active is True
        assert result.is_default is False
        assert result.created_by == 42

    def test_model_validate_from_attributes(self) -> None:
        """Can validate from ORM model with from_attributes."""

        class MockOrmModel:
            id = 1
            name = "test"
            channel = "telegram"
            language = "ru"
            subject = None
            body_html = "<p>Test</p>"
            body_text = "Test text"
            variables = []
            version = 1
            is_active = True
            is_default = False
            created_at = datetime.now(UTC)
            updated_at = datetime.now(UTC)
            created_by = 1

        orm_model = MockOrmModel()
        result = TemplateResponse.model_validate(orm_model)

        assert result.id == 1
        assert result.name == "test"


class TestTemplateListResponse:
    """Tests for TemplateListResponse schema."""

    def test_list_response(self) -> None:
        """Create TemplateListResponse with templates."""
        now = datetime.now(UTC)

        templates = [
            TemplateResponse(
                id=1,
                name="welcome",
                channel="email",
                language="en",
                subject="Welcome!",
                body_text="Welcome text",
                variables=["user_name"],
                version=1,
                is_active=True,
                is_default=False,
                created_at=now,
                updated_at=now,
                created_by=1,
            ),
            TemplateResponse(
                id=2,
                name="reminder",
                channel="telegram",
                language="en",
                body_text="Reminder text",
                variables=["task"],
                version=1,
                is_active=True,
                is_default=False,
                created_at=now,
                updated_at=now,
                created_by=1,
            ),
        ]

        result = TemplateListResponse(
            total=2,
            templates=templates,
            page=1,
            size=10,
            pages=1,
        )

        assert result.total == 2
        assert len(result.templates) == 2
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 1

    def test_empty_list_response(self) -> None:
        """Create TemplateListResponse with no templates."""
        result = TemplateListResponse(
            total=0,
            templates=[],
            page=1,
            size=10,
            pages=0,
        )

        assert result.total == 0
        assert result.templates == []


class TestTemplateRenderRequest:
    """Tests for TemplateRenderRequest schema."""

    def test_valid_request(self) -> None:
        """Create valid render request."""
        data = {
            "template_name": "welcome",
            "channel": "email",
            "language": "en",
            "variables": {"user_name": "John", "task_title": "Complete setup"},
        }

        result = TemplateRenderRequest(**data)

        assert result.template_name == "welcome"
        assert result.channel == "email"
        assert result.language == "en"
        assert result.variables == {"user_name": "John", "task_title": "Complete setup"}

    def test_default_language(self) -> None:
        """Default language is 'en'."""
        data = {
            "template_name": "test",
            "channel": "telegram",
        }

        result = TemplateRenderRequest(**data)

        assert result.language == "en"

    def test_default_empty_variables(self) -> None:
        """Default empty variables dict."""
        data = {
            "template_name": "test",
            "channel": "telegram",
        }

        result = TemplateRenderRequest(**data)

        assert result.variables == {}

    def test_template_name_validation(self) -> None:
        """Template name must not be empty."""
        data = {
            "template_name": "",
            "channel": "email",
        }

        with pytest.raises(ValidationError) as exc_info:
            TemplateRenderRequest(**data)

        assert "template_name" in str(exc_info.value)


class TestTemplateRenderResponse:
    """Tests for TemplateRenderResponse schema."""

    def test_full_response(self) -> None:
        """Create complete render response."""
        data = {
            "template_name": "welcome",
            "channel": "email",
            "language": "en",
            "subject": "Welcome John!",
            "body": "<h1>Welcome John!</h1><p>Glad to have you.</p>",
            "variables_used": ["user_name"],
        }

        result = TemplateRenderResponse(**data)

        assert result.template_name == "welcome"
        assert result.channel == "email"
        assert result.language == "en"
        assert result.subject == "Welcome John!"
        assert result.body == "<h1>Welcome John!</h1><p>Glad to have you.</p>"
        assert result.variables_used == ["user_name"]

    def test_response_without_subject(self) -> None:
        """Create response without subject (for telegram)."""
        data = {
            "template_name": "reminder",
            "channel": "telegram",
            "language": "en",
            "subject": None,
            "body": "Don't forget!",
            "variables_used": [],
        }

        result = TemplateRenderResponse(**data)

        assert result.subject is None
        assert result.body == "Don't forget!"


class TestTemplatePreviewRequest:
    """Tests for TemplatePreviewRequest schema."""

    def test_all_fields_optional(self) -> None:
        """All fields are optional for preview."""
        result = TemplatePreviewRequest()

        assert result.body_text is None
        assert result.body_html is None
        assert result.subject is None
        assert result.variables == {}

    def test_preview_with_text(self) -> None:
        """Create preview request with text body."""
        data = {
            "body_text": "Hello {{ name }}!",
            "variables": {"name": "World"},
        }

        result = TemplatePreviewRequest(**data)

        assert result.body_text == "Hello {{ name }}!"
        assert result.variables == {"name": "World"}

    def test_preview_with_html(self) -> None:
        """Create preview request with HTML body."""
        data = {
            "body_html": "<h1>Hello {{ name }}</h1>",
            "subject": "Welcome {{ name }}",
            "variables": {"name": "User"},
        }

        result = TemplatePreviewRequest(**data)

        assert result.body_html == "<h1>Hello {{ name }}</h1>"
        assert result.subject == "Welcome {{ name }}"
        assert result.variables == {"name": "User"}

    def test_preview_both_bodies(self) -> None:
        """Create preview request with both text and HTML."""
        data = {
            "body_text": "Plain text",
            "body_html": "<p>HTML</p>",
            "subject": "Test",
            "variables": {"var1": "value1"},
        }

        result = TemplatePreviewRequest(**data)

        assert result.body_text == "Plain text"
        assert result.body_html == "<p>HTML</p>"
        assert result.subject == "Test"
