"""Unit tests for notification_service/services/email.py."""

from email.message import EmailMessage
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from _pytest.logging import LogCaptureFixture
from notification_service.config import settings
from notification_service.services.email import (
    EmailService as EmailServiceClass,
)
from notification_service.services.email import (
    _sanitize_email_header,
    _validate_email_address,
)


class TestHelperFunctions:
    """Tests for helper functions _sanitize_email_header and _validate_email_address."""

    def test_sanitize_email_header_with_empty_string(self) -> None:
        """Test line 20: _sanitize_email_header returns empty string unchanged."""
        result = _sanitize_email_header("")
        assert result == ""

    def test_sanitize_email_header_removes_newlines(self) -> None:
        r"""_sanitize_email_header removes \r, \n, and \0 characters."""
        header = "test\r\nheader\0value"
        result = _sanitize_email_header(header)
        assert result == "testheadervalue"

    def test_validate_email_address_with_empty_string(self) -> None:
        """Test line 31: _validate_email_address returns False for empty string."""
        result = _validate_email_address("")
        assert result is False

    def test_validate_email_address_with_none(self) -> None:
        """_validate_email_address returns False for None."""
        result = _validate_email_address(None)
        assert result is False

    def test_validate_email_address_valid_email(self) -> None:
        """_validate_email_address returns True for valid email."""
        result = _validate_email_address("user@example.com")
        assert result is True

    def test_validate_email_address_rejects_newline(self) -> None:
        """_validate_email_address rejects email with newline."""
        result = _validate_email_address("user@example.com\n")
        assert result is False

    def test_validate_email_address_rejects_carriage_return(self) -> None:
        """_validate_email_address rejects email with carriage return."""
        result = _validate_email_address("user@example.com\r")
        assert result is False

    def test_validate_email_address_rejects_null_byte(self) -> None:
        """_validate_email_address rejects email with null byte."""
        result = _validate_email_address("user@example.com\0")
        assert result is False

    def test_validate_email_address_rejects_angle_brackets(self) -> None:
        """_validate_email_address rejects email with < or >."""
        assert _validate_email_address("<user@example.com>") is False
        assert _validate_email_address("user@example.com>") is False
        assert _validate_email_address("<user@example.com") is False

    def test_validate_email_address_with_invalid_format(self) -> None:
        """Test lines 47-48: _validate_email_address returns False for invalid format via EmailNotValidError."""
        # Email that passes dangerous_chars check but fails RFC validation
        # This triggers the EmailNotValidError exception path
        assert _validate_email_address("not-an-email") is False
        assert _validate_email_address("@nodomain.com") is False
        assert _validate_email_address("spaces in@email.com") is False


class TestEmailServiceDryRun:
    """Tests for email service dry-run mode."""

    @pytest.fixture(autouse=True)
    def reset_settings(self) -> None:
        """Reset settings after each test."""
        original_dry_run = settings.EMAIL_DRY_RUN
        original_debug = settings.DEBUG
        yield
        settings.EMAIL_DRY_RUN = original_dry_run
        settings.DEBUG = original_debug

    async def test_dry_run_mode_returns_without_sending(self) -> None:
        """Dry-run mode logs and returns without calling SMTP."""
        settings.EMAIL_DRY_RUN = True
        settings.DEBUG = False

        service = EmailServiceClass()

        with patch("notification_service.services.email.aiosmtplib.send") as mock_send:
            await service.send_email("user@example.com", "Test Subject", "Test body")
            mock_send.assert_not_called()

    async def test_dry_run_mode_logs_message(self, caplog: LogCaptureFixture) -> None:
        """Dry-run mode logs the email that would be sent."""
        settings.EMAIL_DRY_RUN = True
        settings.DEBUG = False
        caplog.set_level("INFO")

        service = EmailServiceClass()
        await service.send_email("user@example.com", "Test Subject", "Test body")

        assert "[DRY RUN]" in caplog.text
        assert "user@example.com" in caplog.text
        assert "Test Subject" in caplog.text

    async def test_debug_mode_triggers_dry_run(self) -> None:
        """DEBUG=True also triggers dry-run behavior."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = True

        service = EmailServiceClass()

        with patch("notification_service.services.email.aiosmtplib.send") as mock_send:
            await service.send_email("user@example.com", "Test Subject", "Test body")
            mock_send.assert_not_called()

    async def test_dry_run_with_custom_from_email(self, caplog: LogCaptureFixture) -> None:
        """Dry-run logs custom from_email when provided."""
        settings.EMAIL_DRY_RUN = True
        settings.DEBUG = False
        caplog.set_level("INFO")

        service = EmailServiceClass()
        await service.send_email(
            to_email="user@example.com",
            subject="Test Subject",
            body="Test body",
            from_email="custom@sender.com",
        )

        assert "custom@sender.com" in caplog.text


class TestEmailServiceSending:
    """Tests for email service actual sending."""

    @pytest.fixture(autouse=True)
    def reset_settings(self) -> None:
        """Reset settings after each test."""
        original_dry_run = settings.EMAIL_DRY_RUN
        original_debug = settings.DEBUG
        yield
        settings.EMAIL_DRY_RUN = original_dry_run
        settings.DEBUG = original_debug

    async def test_raises_value_error_for_invalid_email(self) -> None:
        """Test lines 80-81: ValueError raised when email validation fails."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False

        service = EmailServiceClass()

        with pytest.raises(ValueError, match="Invalid recipient email address"):
            await service.send_email("invalid@email\n.com", "Test Subject", "Test body")

    async def test_sends_email_via_smtp_when_not_dry_run(self) -> None:
        """When not in dry-run, email is sent via aiosmtplib."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False

        service = EmailServiceClass()
        mock_send = AsyncMock()

        with patch("notification_service.services.email.aiosmtplib.send", mock_send):
            await service.send_email("user@example.com", "Test Subject", "Test body")

        mock_send.assert_awaited_once()

    async def test_message_construction_with_subject_and_recipients(self) -> None:
        """EmailMessage is constructed with correct subject and recipients."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False

        service = EmailServiceClass()
        captured_message: EmailMessage | None = None

        async def capture_send(message: EmailMessage, **_kwargs: Any) -> None:
            nonlocal captured_message
            captured_message = message

        with patch("notification_service.services.email.aiosmtplib.send", capture_send):
            await service.send_email("user@example.com", "Test Subject", "Test body")

        assert captured_message is not None
        assert captured_message["To"] == "user@example.com"
        assert captured_message["Subject"] == "Test Subject"
        assert captured_message["From"] == settings.DEFAULT_FROM_EMAIL

    async def test_message_construction_uses_custom_from(self) -> None:
        """Custom from_email is used when provided."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False

        service = EmailServiceClass()
        captured_message: EmailMessage | None = None

        async def capture_send(message: EmailMessage, **_kwargs: Any) -> None:
            nonlocal captured_message
            captured_message = message

        with patch("notification_service.services.email.aiosmtplib.send", capture_send):
            await service.send_email(
                to_email="user@example.com",
                subject="Test",
                body="Body",
                from_email="custom@sender.com",
            )

        assert captured_message is not None
        assert captured_message["From"] == "custom@sender.com"

    async def test_message_body_is_set_as_content(self) -> None:
        """Email body is set as message content."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False

        service = EmailServiceClass()
        captured_message: EmailMessage | None = None

        async def capture_send(message: EmailMessage, **_kwargs: Any) -> None:
            nonlocal captured_message
            captured_message = message

        with patch("notification_service.services.email.aiosmtplib.send", capture_send):
            await service.send_email("user@example.com", "Test", "Plain text body", html=False)

        assert captured_message is not None
        assert captured_message.get_content() == "Plain text body\n"

    async def test_smtp_connection_uses_configured_settings(self) -> None:
        """SMTP connection uses host/port/user/password from settings."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False

        service = EmailServiceClass()
        mock_send = AsyncMock()

        with patch("notification_service.services.email.aiosmtplib.send", mock_send):
            await service.send_email("user@example.com", "Test", "Body")

        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["hostname"] == settings.SMTP_HOST
        assert call_kwargs["port"] == settings.SMTP_PORT
        assert call_kwargs["username"] == settings.SMTP_USER
        assert call_kwargs["password"] == settings.SMTP_PASSWORD
        assert call_kwargs["use_tls"] == settings.SMTP_USE_TLS

    async def test_logs_success_after_sending(self, caplog: LogCaptureFixture) -> None:
        """Successful send logs info message."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False
        caplog.set_level("INFO")

        service = EmailServiceClass()
        mock_send = AsyncMock()

        with patch("notification_service.services.email.aiosmtplib.send", mock_send):
            await service.send_email("user@example.com", "Test", "Body")

        assert "Email sent to user@example.com" in caplog.text

    async def test_raises_on_smtp_error(self) -> None:
        """SMTP errors are raised after logging."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False

        service = EmailServiceClass()
        mock_send = AsyncMock(side_effect=Exception("SMTP connection failed"))

        with (
            patch("notification_service.services.email.aiosmtplib.send", mock_send),
            pytest.raises(Exception, match="SMTP connection failed"),
        ):
            await service.send_email("user@example.com", "Test", "Body")

    async def test_logs_exception_on_smtp_error(self, caplog: LogCaptureFixture) -> None:
        """SMTP errors are logged as exceptions."""
        settings.EMAIL_DRY_RUN = False
        settings.DEBUG = False
        caplog.set_level("ERROR")

        service = EmailServiceClass()
        mock_send = AsyncMock(side_effect=Exception("SMTP failed"))

        with (
            patch("notification_service.services.email.aiosmtplib.send", mock_send),
            pytest.raises(Exception, match="SMTP failed"),
        ):
            await service.send_email("user@example.com", "Test", "Body")

        assert "Failed to send email" in caplog.text
