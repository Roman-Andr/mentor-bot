"""Certificate PDF generation service using WeasyPrint."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from checklists_service.models import Certificate

logger = logging.getLogger(__name__)

# Template directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"

# Jinja2 environment
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)


class CertificateGenerator:
    """Service for generating certificate PDFs."""

    def __init__(self, auth_token: str | None = None) -> None:
        """Initialize certificate generator."""
        self.auth_token = auth_token

    async def _get_user_data(self, user_id: int) -> dict[str, Any] | None:
        """Get user data from auth service."""
        if not self.auth_token:
            logger.warning("_get_user_data called without auth token")
            return None

        from checklists_service.utils import auth_service_client
        return await auth_service_client.get_user(user_id, self.auth_token)

    def _format_date(self, date: datetime | None, locale: str = "en") -> str:
        """Format date for certificate."""
        if not date:
            return "-"

        if locale == "ru":
            # Russian month names
            months_ru = [
                "января",
                "февраля",
                "марта",
                "апреля",
                "мая",
                "июня",
                "июля",
                "августа",
                "сентября",
                "октября",
                "ноября",
                "декабря",
            ]
            return f"{date.day} {months_ru[date.month - 1]} {date.year}"
        return date.strftime("%B %d, %Y")

    def _get_translations(self, locale: str) -> dict[str, str]:
        """Get translations for certificate based on locale."""
        if locale == "ru":
            return {
                "title": "Сертификат о Завершении",
                "subtitle": "Онбординг успешно завершён",
                "presentedTo": "Вручается",
                "achievement": 'За успешное завершение программы онбординга "{program_name}"',
                "completedOn": "Дата завершения",
                "hr_signature": "Подпись HR",
                "mentor_signature": "Подпись наставника",
                "date": "Дата",
                "certificate_id": "№ сертификата",
                "appName": "Mentor Bot",
            }
        return {
            "title": "Certificate of Completion",
            "subtitle": "Onboarding Successfully Completed",
            "presentedTo": "Presented to",
            "achievement": 'For successfully completing the "{program_name}" onboarding program',
            "completedOn": "Completed on",
            "hr_signature": "HR Signature",
            "mentor_signature": "Mentor Signature",
            "date": "Date",
            "certificate_id": "Certificate #",
            "appName": "Mentor Bot",
        }

    async def generate_certificate_pdf(
        self,
        certificate: Certificate,
        template_name: str,
        employee_data: dict[str, Any],
        hr_data: dict[str, Any] | None,
        mentor_data: dict[str, Any] | None,
        locale: str = "en",
    ) -> bytes:
        """
        Generate certificate PDF.

        Args:
            certificate: Certificate model instance
            template_name: Name of the onboarding template
            employee_data: Employee user data from auth service
            hr_data: HR user data from auth service (optional)
            mentor_data: Mentor user data from auth service (optional)
            locale: Language locale (en or ru)

        Returns:
            PDF as bytes

        """
        translations = self._get_translations(locale)

        # Prepare template context
        context = {
            "employee_name": f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}".strip(),
            "employee_position": employee_data.get("position", ""),
            "employee_department": employee_data.get("department", {}).get("name", "")
            if employee_data.get("department")
            else "",
            "program_name": template_name,
            "completion_date": self._format_date(certificate.issued_at, locale),
            "hr_name": f"{hr_data.get('first_name', '')} {hr_data.get('last_name', '')}".strip() if hr_data else "",
            "mentor_name": f"{mentor_data.get('first_name', '')} {mentor_data.get('last_name', '')}".strip()
            if mentor_data
            else "",
            "cert_uid": certificate.cert_uid,
            "cert_id": str(certificate.id).zfill(8),
            **translations,
        }

        # Load and render template
        template = jinja_env.get_template(f"certificate_{locale}.html")
        html_content = template.render(**context)

        # Generate PDF
        pdf_bytes = HTML(string=html_content).write_pdf()

        logger.info("Generated certificate PDF (cert_uid=%s)", certificate.cert_uid)
        return pdf_bytes

    async def generate_certificate_from_checklist(
        self,
        certificate: Certificate,
        checklist_data: dict[str, Any],
        locale: str = "en",
    ) -> bytes:
        """
        Generate certificate PDF from checklist data.

        Args:
            certificate: Certificate model instance
            checklist_data: Checklist data including template and assignee info
            locale: Language locale (en or ru)

        Returns:
            PDF as bytes

        """
        # Fetch user data
        employee_data = await self._get_user_data(certificate.user_id)
        if not employee_data:
            msg = f"Employee {certificate.user_id} not found"
            raise ValueError(msg)

        hr_data = None
        if certificate.hr_id:
            hr_data = await self._get_user_data(certificate.hr_id)

        mentor_data = None
        if certificate.mentor_id:
            mentor_data = await self._get_user_data(certificate.mentor_id)

        template_name = checklist_data.get("template_name", "Onboarding")

        return await self.generate_certificate_pdf(
            certificate=certificate,
            template_name=template_name,
            employee_data=employee_data,
            hr_data=hr_data,
            mentor_data=mentor_data,
            locale=locale,
        )
