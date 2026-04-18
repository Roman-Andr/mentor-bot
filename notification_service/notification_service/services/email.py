"""Email integration service using SMTP."""

import logging
import re
from email.message import EmailMessage

import aiosmtplib

from notification_service.config import settings

logger = logging.getLogger(__name__)


def _sanitize_email_header(value: str) -> str:
    """Sanitize email header to prevent header injection attacks.

    Removes newlines and null bytes that could be used for header injection.
    """
    if not value:
        return value
    # Remove any newline characters and null bytes
    return value.replace("\r", "").replace("\n", "").replace("\0", "")


def _validate_email_address(email: str) -> bool:
    """Basic email validation to prevent header injection.

    Checks that email doesn't contain characters that could be used for header injection.
    """
    if not email:
        return False
    # Check for dangerous characters in email
    dangerous_chars = ["\r", "\n", "\0", "<", ">"]
    return not any(char in email for char in dangerous_chars)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self) -> None:
        """Initialize email service with settings."""
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.default_from = settings.DEFAULT_FROM_EMAIL

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str | None = None,
        html: bool = True,
    ) -> None:
        """Send an email using SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            from_email: Sender email address (defaults to DEFAULT_FROM_EMAIL)
            html: Whether body is HTML (default True)
        """
        # Check if in dry-run mode (log only, don't send)
        is_dry_run = settings.EMAIL_DRY_RUN or settings.DEBUG
        if is_dry_run:
            logger.info(
                "[DRY RUN] Email would be sent to %s | Subject: %s | From: %s | HTML: %s",
                to_email,
                subject,
                from_email or self.default_from,
                html,
            )
            return

        # Validate and sanitize email headers to prevent header injection
        if not _validate_email_address(to_email):
            msg = f"Invalid recipient email address: {to_email}"
            raise ValueError(msg)

        sanitized_to = _sanitize_email_header(to_email)
        sanitized_subject = _sanitize_email_header(subject)
        sanitized_from = _sanitize_email_header(from_email or self.default_from)

        message = EmailMessage()
        message["From"] = sanitized_from
        message["To"] = sanitized_to
        message["Subject"] = sanitized_subject

        if html:
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                use_tls=self.use_tls,
            )
            logger.info("Email sent to %s", to_email)
        except Exception:
            logger.exception("Failed to send email")
            raise
