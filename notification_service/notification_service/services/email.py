"""Email integration service using SMTP."""

import logging
from email.message import EmailMessage

import aiosmtplib

from notification_service.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self) -> None:
        """Initialize email service with SMTP settings."""
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.default_from = settings.DEFAULT_FROM_EMAIL

    async def send_email(self, to_email: str, subject: str, body: str, from_email: str | None = None) -> None:
        """Send an email using SMTP."""
        message = EmailMessage()
        message["From"] = from_email or self.default_from
        message["To"] = to_email
        message["Subject"] = subject
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
            logger.info(f"Email sent to {to_email}")
        except Exception as e:
            logger.exception(f"Failed to send email: {e}")
            raise
