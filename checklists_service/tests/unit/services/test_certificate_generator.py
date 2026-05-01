"""Unit tests for certificate generator service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from checklists_service.models import Certificate
from checklists_service.services.certificate_generator import CertificateGenerator


class TestCertificateGeneratorInit:
    """Test CertificateGenerator initialization."""

    def test_init(self) -> None:
        """Test CertificateGenerator initialization."""
        auth_token = "test-token"
        generator = CertificateGenerator(auth_token)
        assert generator.auth_token == auth_token

    def test_init_without_token(self) -> None:
        """Test CertificateGenerator initialization without token."""
        generator = CertificateGenerator()
        assert generator.auth_token is None


class TestGetUserData:
    """Test _get_user_data method."""

    @patch("checklists_service.services.certificate_generator.auth_service_client")
    async def test_get_user_data_success(self, mock_auth_client) -> None:
        """Test successful user data retrieval."""
        user_mock = MagicMock()
        user_mock.id = 1
        user_mock.email = "user@example.com"
        user_mock.first_name = "John"
        user_mock.last_name = "Doe"
        user_mock.employee_id = "EMP001"
        user_mock.position = "Developer"
        user_mock.department_id = 1

        mock_auth_client.get_user = AsyncMock(return_value=user_mock)

        generator = CertificateGenerator("test-token")
        result = await generator._get_user_data(1)

        assert result.id == 1
        assert result.email == "user@example.com"
        mock_auth_client.get_user.assert_awaited_once_with(1, "test-token")

    @patch("checklists_service.services.certificate_generator.auth_service_client")
    async def test_get_user_data_not_found(self, mock_auth_client) -> None:
        """Test user data retrieval when user not found."""
        mock_auth_client.get_user = AsyncMock(return_value=None)

        generator = CertificateGenerator("test-token")
        result = await generator._get_user_data(999)

        assert result is None

    @patch("checklists_service.services.certificate_generator.auth_service_client")
    async def test_get_user_data_no_token(self, mock_auth_client) -> None:
        """Test user data retrieval when no auth token."""
        generator = CertificateGenerator()
        result = await generator._get_user_data(1)

        assert result is None
        mock_auth_client.get_user.assert_not_called()


class TestFormatDate:
    """Test _format_date method."""

    def test_format_date_with_date(self) -> None:
        """Test formatting a valid date."""
        generator = CertificateGenerator("test-token")
        date = datetime(2024, 1, 15, tzinfo=UTC)
        result = generator._format_date(date, "en")
        assert result == "January 15, 2024"

    def test_format_date_with_none(self) -> None:
        """Test formatting when date is None."""
        generator = CertificateGenerator("test-token")
        result = generator._format_date(None, "en")
        assert result == "-"

    def test_format_date_russian_locale(self) -> None:
        """Test formatting date with Russian locale."""
        generator = CertificateGenerator("test-token")
        date = datetime(2024, 1, 15, tzinfo=UTC)
        result = generator._format_date(date, "ru")
        assert "января" in result


class TestGetTranslations:
    """Test _get_translations method."""

    def test_get_translations_english(self) -> None:
        """Test getting English translations."""
        generator = CertificateGenerator("test-token")
        result = generator._get_translations("en")
        assert "title" in result
        assert "subtitle" in result
        assert "presentedTo" in result
        assert "achievement" in result
        assert result["title"] == "Certificate of Completion"

    def test_get_translations_russian(self) -> None:
        """Test getting Russian translations."""
        generator = CertificateGenerator("test-token")
        result = generator._get_translations("ru")
        assert "title" in result
        assert "subtitle" in result
        assert "presentedTo" in result
        assert result["title"] == "Сертификат о Завершении"

    def test_get_translations_default_english(self) -> None:
        """Test defaulting to English for unknown locale."""
        generator = CertificateGenerator("test-token")
        result = generator._get_translations("fr")
        assert "title" in result
        assert result["title"] == "Certificate of Completion"


class TestGenerateCertificatePdf:
    """Test generate_certificate_pdf method."""

    @patch("checklists_service.services.certificate_generator.HTML")
    async def test_generate_certificate_pdf_success(self, mock_html) -> None:
        """Test successful PDF generation."""
        generator = CertificateGenerator("test-token")

        certificate = MagicMock()
        certificate.id = 1

        employee_data = {"id": 1, "email": "user@example.com"}
        hr_data = {"id": 10, "email": "hr@example.com"}
        mentor_data = {"id": 2, "email": "mentor@example.com"}

        mock_html_obj = MagicMock()
        mock_html.return_value = mock_html_obj
        mock_html_obj.write_pdf.return_value = b"pdf bytes"

        result = await generator.generate_certificate_pdf(
            certificate=certificate,
            template_name="Onboarding Template",
            employee_data=employee_data,
            hr_data=hr_data,
            mentor_data=mentor_data,
            locale="en",
        )

        assert result == b"pdf bytes"
        mock_html.assert_called_once()
        mock_html_obj.write_pdf.assert_called_once()

    @patch("checklists_service.services.certificate_generator.HTML")
    async def test_generate_certificate_pdf_error(self, mock_html) -> None:
        """Test PDF generation raises Exception on error."""
        generator = CertificateGenerator("test-token")

        certificate = MagicMock()
        employee_data = {"id": 1}
        hr_data = None
        mentor_data = None

        mock_html_obj = MagicMock()
        mock_html.return_value = mock_html_obj
        mock_html_obj.write_pdf.side_effect = Exception("PDF error")

        with pytest.raises(Exception, match="PDF error"):
            await generator.generate_certificate_pdf(
                certificate=certificate,
                template_name="Template",
                employee_data=employee_data,
                hr_data=hr_data,
                mentor_data=mentor_data,
                locale="en",
            )


class TestGenerateCertificateFromChecklist:
    """Test generate_certificate_from_checklist method."""

    @patch("checklists_service.services.certificate_generator.HTML")
    @patch("checklists_service.services.certificate_generator.auth_service_client")
    async def test_generate_certificate_from_checklist_success(self, mock_auth_client, mock_html) -> None:
        """Test successful certificate generation from checklist."""
        user_mock = MagicMock()
        user_mock.id = 1
        user_mock.email = "user@example.com"
        user_mock.first_name = "John"
        user_mock.last_name = "Doe"
        user_mock.employee_id = "EMP001"
        user_mock.position = "Developer"
        mock_auth_client.get_user = AsyncMock(return_value=user_mock)

        mock_html_obj = MagicMock()
        mock_html.return_value = mock_html_obj
        mock_html_obj.write_pdf.return_value = b"pdf bytes"

        certificate = Certificate(
            id=1,
            cert_uid="test-uid",
            user_id=1,
            checklist_id=1,
            hr_id=10,
            mentor_id=2,
            issued_at=datetime.now(UTC),
        )

        generator = CertificateGenerator("test-token")
        result = await generator.generate_certificate_from_checklist(
            certificate=certificate,
            checklist_data={"template_name": "Onboarding Template"},
            locale="en",
        )

        assert result == b"pdf bytes"

    @patch("checklists_service.services.certificate_generator.auth_service_client")
    async def test_generate_certificate_from_checklist_checklist_not_found(self, mock_auth_client) -> None:
        """Test certificate generation when checklist not found."""
        mock_auth_client.get_user = AsyncMock(return_value=None)

        certificate = Certificate(
            id=1,
            cert_uid="test-uid",
            user_id=1,
            checklist_id=1,
            hr_id=10,
            mentor_id=2,
            issued_at=datetime.now(UTC),
        )

        generator = CertificateGenerator("test-token")

        with pytest.raises(ValueError, match="Employee 1 not found"):
            await generator.generate_certificate_from_checklist(
                certificate=certificate,
                checklist_data={"template_name": "Template"},
                locale="en",
            )

    @patch("checklists_service.services.certificate_generator.HTML")
    @patch("checklists_service.services.certificate_generator.auth_service_client")
    async def test_generate_certificate_from_checklist_user_not_found(self, mock_auth_client, mock_html) -> None:
        """Test certificate generation when user not found."""
        mock_auth_client.get_user = AsyncMock(return_value=None)

        mock_html_obj = MagicMock()
        mock_html.return_value = mock_html_obj
        mock_html_obj.write_pdf.return_value = b"pdf bytes"

        certificate = Certificate(
            id=1,
            cert_uid="test-uid",
            user_id=1,
            checklist_id=1,
            hr_id=10,
            mentor_id=2,
            issued_at=datetime.now(UTC),
        )

        generator = CertificateGenerator("test-token")

        with pytest.raises(ValueError, match="Employee 1 not found"):
            await generator.generate_certificate_from_checklist(
                certificate=certificate,
                checklist_data={"template_name": "Template"},
                locale="en",
            )

    @patch("checklists_service.services.certificate_generator.HTML")
    @patch("checklists_service.services.certificate_generator.auth_service_client")
    async def test_generate_certificate_from_checklist_russian_locale(self, mock_auth_client, mock_html) -> None:
        """Test certificate generation with Russian locale."""
        user_mock = MagicMock()
        user_mock.id = 1
        user_mock.email = "user@example.com"
        mock_auth_client.get_user = AsyncMock(return_value=user_mock)

        mock_html_obj = MagicMock()
        mock_html.return_value = mock_html_obj
        mock_html_obj.write_pdf.return_value = b"pdf bytes"

        certificate = Certificate(
            id=1,
            cert_uid="test-uid",
            user_id=1,
            checklist_id=1,
            hr_id=10,
            mentor_id=2,
            issued_at=datetime.now(UTC),
        )

        generator = CertificateGenerator("test-token")
        result = await generator.generate_certificate_from_checklist(
            certificate=certificate,
            checklist_data={"template_name": "Onboarding Template"},
            locale="ru",
        )

        assert result == b"pdf bytes"
