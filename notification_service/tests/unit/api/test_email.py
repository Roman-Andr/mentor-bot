"""Unit tests for notification_service/api/endpoints/email.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from notification_service.api.endpoints.email import (
    EmailSendRequest,
    _get_default_password_reset_confirmation_template,
    _get_default_password_reset_template,
    _get_default_subject,
    load_template,
    render_template,
    send_email,
)


class TestLoadTemplate:
    """Tests for load_template function."""

    def test_load_existing_template(self, tmp_path) -> None:
        """Load template from file system."""
        from notification_service.api.endpoints import email

        # Create a temporary templates directory and file
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "test_template.html"
        template_file.write_text("<html><body>Test</body></html>")

        # Patch the TEMPLATES_DIR
        with patch.object(email, "TEMPLATES_DIR", template_dir):
            result = load_template("test_template")
            assert result == "<html><body>Test</body></html>"

    def test_load_nonexistent_template_raises_error(self) -> None:
        """Raises ValueError when template file not found and no default exists."""
        with pytest.raises(ValueError, match="Template not found"):
            load_template("nonexistent_template_xyz")

    def test_load_password_reset_default(self) -> None:
        """Returns default template for password_reset when file not found."""
        result = load_template("password_reset")

        assert "Password Reset Request" in result
        assert "{{ user_name }}" in result
        assert "{{ reset_url }}" in result

    def test_load_password_reset_confirmation_default(self) -> None:
        """Returns default template for password_reset_confirmation when file not found."""
        result = load_template("password_reset_confirmation")

        assert "Password Reset Successful" in result
        assert "{{ user_name }}" in result

    def test_load_password_reset_first_fallback(self) -> None:
        """Test password_reset is checked first in fallback chain (line 41)."""
        from notification_service.api.endpoints import email

        with patch.object(email, "TEMPLATES_DIR", email.Path("/nonexistent")):
            # This specifically covers line 41 - the password_reset check
            result = load_template("password_reset")
            assert "Password Reset Request" in result
            assert "{{ reset_url }}" in result

    def test_load_password_reset_confirmation_second_fallback(self) -> None:
        """Test password_reset_confirmation is checked second in fallback chain (line 43)."""
        from notification_service.api.endpoints import email

        with patch.object(email, "TEMPLATES_DIR", email.Path("/nonexistent")):
            # This specifically covers line 43 - the password_reset_confirmation check
            result = load_template("password_reset_confirmation")
            assert "Password Reset Successful" in result
            assert "successfully reset" in result


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_render_simple_variables(self) -> None:
        """Render template with simple variable substitution."""
        template = "Hello {{ name }}, your code is {{ code }}"
        variables = {"name": "John", "code": "12345"}

        result = render_template(template, variables)

        assert result == "Hello John, your code is 12345"

    def test_render_no_variables(self) -> None:
        """Render template without variables returns unchanged."""
        template = "Hello World"
        variables = {}

        result = render_template(template, variables)

        assert result == "Hello World"

    def test_render_missing_variables_as_empty(self) -> None:
        """Missing variables render as empty strings (Jinja2 default behavior)."""
        template = "Hello {{ name }}, welcome to {{ place }}"
        variables = {"name": "John"}  # place is missing

        result = render_template(template, variables)

        assert result == "Hello John, welcome to "

    def test_render_converts_values_to_strings(self) -> None:
        """Non-string values are converted to strings."""
        template = "Count: {{ count }}, Active: {{ active }}"
        variables = {"count": 42, "active": True}

        result = render_template(template, variables)

        assert result == "Count: 42, Active: True"

    def test_render_escapes_html_prevents_xss(self) -> None:
        """HTML in variables is escaped to prevent XSS attacks."""
        template = "Hello {{ name }}"
        variables = {"name": "<script>alert('xss')</script>"}

        result = render_template(template, variables)

        assert "<script>" not in result
        assert "&lt;script&gt;" in result
        assert result == "Hello &lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;"


class TestGetDefaultPasswordResetTemplate:
    """Tests for _get_default_password_reset_template function."""

    def test_contains_required_placeholders(self) -> None:
        """Template contains required placeholders."""
        result = _get_default_password_reset_template()

        assert "{{ user_name }}" in result
        assert "{{ reset_url }}" in result
        assert "{{ expiry_hours }}" in result

    def test_is_valid_html(self) -> None:
        """Template is valid HTML."""
        result = _get_default_password_reset_template()

        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "</html>" in result


class TestGetDefaultPasswordResetConfirmationTemplate:
    """Tests for _get_default_password_reset_confirmation_template function."""

    def test_contains_required_placeholders(self) -> None:
        """Template contains required placeholders."""
        result = _get_default_password_reset_confirmation_template()

        assert "{{ user_name }}" in result

    def test_is_valid_html(self) -> None:
        """Template is valid HTML."""
        result = _get_default_password_reset_confirmation_template()

        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "</html>" in result


class TestGetDefaultSubject:
    """Tests for _get_default_subject function."""

    def test_password_reset_subject(self) -> None:
        """Returns correct subject for password_reset."""
        result = _get_default_subject("password_reset")

        assert "Password Reset Request" in result
        assert "Mentor Bot" in result

    def test_password_reset_confirmation_subject(self) -> None:
        """Returns correct subject for password_reset_confirmation."""
        result = _get_default_subject("password_reset_confirmation")

        assert "Password Has Been Reset" in result
        assert "Mentor Bot" in result

    def test_unknown_template_default_subject(self) -> None:
        """Returns generic subject for unknown template."""
        result = _get_default_subject("unknown_template")

        assert result == "Notification from Mentor Bot"


class TestSendEmail:
    """Tests for send_email endpoint."""

    async def test_send_email_success(self) -> None:
        """Send email with valid API key."""
        request = EmailSendRequest(
            to_email="user@example.com",
            template="password_reset",
            subject=None,
            variables={"user_name": "John", "reset_url": "https://example.com/reset", "expiry_hours": "24"},
        )

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.SERVICE_API_KEY = "valid-api-key"

            with patch("notification_service.api.endpoints.email.EmailService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_email = AsyncMock()
                mock_service_cls.return_value = mock_service

                result = await send_email(request, x_service_api_key="valid-api-key")

                assert result.success is True
                assert result.message == "Email sent successfully"
                mock_service.send_email.assert_awaited_once()

    async def test_send_email_with_custom_subject(self) -> None:
        """Send email with custom subject override."""
        request = EmailSendRequest(
            to_email="user@example.com",
            template="password_reset",
            subject="Custom Subject",
            variables={"user_name": "John", "reset_url": "https://example.com/reset", "expiry_hours": "24"},
        )

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.SERVICE_API_KEY = "valid-api-key"

            with patch("notification_service.api.endpoints.email.EmailService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_email = AsyncMock()
                mock_service_cls.return_value = mock_service

                result = await send_email(request, x_service_api_key="valid-api-key")

                # Verify custom subject was used
                call_args = mock_service.send_email.call_args
                assert call_args.kwargs["subject"] == "Custom Subject"

    async def test_send_email_missing_api_key(self) -> None:
        """Reject request without API key."""
        request = EmailSendRequest(
            to_email="user@example.com",
            template="password_reset",
            variables={},
        )

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.SERVICE_API_KEY = "valid-api-key"

            with pytest.raises(HTTPException) as exc_info:
                await send_email(request, x_service_api_key=None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "api key" in exc_info.value.detail.lower()

    async def test_send_email_invalid_api_key(self) -> None:
        """Reject request with invalid API key."""
        request = EmailSendRequest(
            to_email="user@example.com",
            template="password_reset",
            variables={},
        )

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.SERVICE_API_KEY = "valid-api-key"

            with pytest.raises(HTTPException) as exc_info:
                await send_email(request, x_service_api_key="invalid-key")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_send_email_template_error(self) -> None:
        """Handle template error gracefully."""
        request = EmailSendRequest(
            to_email="user@example.com",
            template="nonexistent_template_xyz",  # No default exists
            variables={},
        )

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.SERVICE_API_KEY = "valid-api-key"

            with pytest.raises(HTTPException) as exc_info:
                await send_email(request, x_service_api_key="valid-api-key")

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Template error" in exc_info.value.detail

    async def test_send_email_service_error(self) -> None:
        """Handle email service error gracefully."""
        request = EmailSendRequest(
            to_email="user@example.com",
            template="password_reset",
            variables={"user_name": "John", "reset_url": "https://example.com/reset", "expiry_hours": "24"},
        )

        with patch("notification_service.middleware.auth.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.SERVICE_API_KEY = "valid-api-key"

            with patch("notification_service.api.endpoints.email.EmailService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.send_email = AsyncMock(side_effect=Exception("SMTP connection failed"))
                mock_service_cls.return_value = mock_service

                with pytest.raises(HTTPException) as exc_info:
                    await send_email(request, x_service_api_key="valid-api-key")

                assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert "Failed to send email" in exc_info.value.detail
