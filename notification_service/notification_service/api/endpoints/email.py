"""Email sending endpoints for service-to-service communication."""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from jinja2 import BaseLoader, Environment, select_autoescape
from pydantic import BaseModel, EmailStr

from notification_service.middleware.auth import verify_service_api_key
from notification_service.services.email import EmailService

logger = logging.getLogger(__name__)

router = APIRouter()

# Load email templates
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


class EmailSendRequest(BaseModel):
    """Request to send a templated email."""

    to_email: EmailStr
    template: str  # e.g., "password_reset", "password_reset_confirmation"
    subject: str | None = None  # Optional override
    variables: dict = {}  # Template variables


class EmailSendResponse(BaseModel):
    """Response from sending an email."""

    success: bool
    message: str


def load_template(template_name: str) -> str:
    """Load an email template from file."""
    template_path = TEMPLATES_DIR / f"{template_name}.html"
    if not template_path.exists():
        # Fallback to simple text templates
        if template_name == "password_reset":
            return _get_default_password_reset_template()
        if template_name == "password_reset_confirmation":
            return _get_default_password_reset_confirmation_template()
        raise ValueError(f"Template not found: {template_name}")

    return template_path.read_text(encoding="utf-8")


def render_template(template_content: str, variables: dict) -> str:
    """Render template with Jinja2 and HTML autoescaping for XSS protection."""
    env = Environment(
        loader=BaseLoader(),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.from_string(template_content)
    return template.render(**variables)


def _get_default_password_reset_template() -> str:
    """Default plain text template for password reset."""
    return """<!DOCTYPE html>
<html>
<body>
    <h1>Password Reset Request</h1>
    <p>Hi {{ user_name }},</p>
    <p>Click the link below to reset your password:</p>
    <p><a href="{{ reset_url }}">Reset Password</a></p>
    <p>Or copy this URL: {{ reset_url }}</p>
    <p>This link expires in {{ expiry_hours }} hours.</p>
    <p>If you didn't request this, please ignore this email.</p>
</body>
</html>"""


def _get_default_password_reset_confirmation_template() -> str:
    """Default plain text template for password reset confirmation."""
    return """<!DOCTYPE html>
<html>
<body>
    <h1>Password Reset Successful</h1>
    <p>Hi {{ user_name }},</p>
    <p>Your password has been successfully reset.</p>
    <p>If you didn't make this change, please contact your administrator immediately.</p>
</body>
</html>"""


def _get_default_subject(template_name: str) -> str:
    """Get default subject line for a template."""
    subjects = {
        "password_reset": "Password Reset Request - Mentor Bot",
        "password_reset_confirmation": "Your Password Has Been Reset - Mentor Bot",
    }
    return subjects.get(template_name, "Notification from Mentor Bot")


@router.post("/send")
async def send_email(
    request: EmailSendRequest,
    x_service_api_key: Annotated[str | None, Header(alias="X-Service-Api-Key")] = None,
) -> EmailSendResponse:
    """
    Send a templated email (service-to-service endpoint).

    This endpoint is intended for inter-service communication only
    and requires a valid service API key.
    """
    # Verify service API key
    if not x_service_api_key or not verify_service_api_key(x_service_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing service API key",
        )

    try:
        # Load and render template
        template_content = load_template(request.template)
        rendered_body = render_template(template_content, request.variables)

        # Determine subject
        subject = request.subject or _get_default_subject(request.template)

        # Send email
        email_service = EmailService()
        await email_service.send_email(
            to_email=request.to_email,
            subject=subject,
            body=rendered_body,
        )

        logger.info("Email sent successfully to %s using template %s", request.to_email, request.template)
        return EmailSendResponse(success=True, message="Email sent successfully")

    except ValueError as e:
        logger.error("Template error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template error: {e!s}",
        ) from e
    except Exception as e:
        logger.exception("Failed to send email")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {e!s}",
        ) from e
