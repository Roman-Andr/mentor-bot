"""Tests for certificate generator service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from checklists_service.models import Certificate
from checklists_service.services.certificate_generator import CertificateGenerator


@pytest.mark.asyncio
async def test_format_date_english() -> None:
    """Test date formatting for English locale."""
    generator = CertificateGenerator()
    date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    formatted = generator._format_date(date, "en")
    assert formatted == "January 15, 2024"


@pytest.mark.asyncio
async def test_format_date_russian() -> None:
    """Test date formatting for Russian locale."""
    generator = CertificateGenerator()
    date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    formatted = generator._format_date(date, "ru")
    assert formatted == "15 января 2024"


@pytest.mark.asyncio
async def test_format_date_none() -> None:
    """Test date formatting with None value."""
    generator = CertificateGenerator()

    formatted = generator._format_date(None, "en")
    assert formatted == "-"


@pytest.mark.asyncio
async def test_get_translations_english() -> None:
    """Test getting English translations."""
    generator = CertificateGenerator()

    translations = generator._get_translations("en")

    assert "title" in translations
    assert translations["title"] == "Certificate of Completion"
    assert "subtitle" in translations
    assert "appName" in translations


@pytest.mark.asyncio
async def test_get_translations_russian() -> None:
    """Test getting Russian translations."""
    generator = CertificateGenerator()

    translations = generator._get_translations("ru")

    assert "title" in translations
    assert translations["title"] == "Сертификат о Завершении"
    assert "subtitle" in translations
    assert "appName" in translations


@patch("checklists_service.services.certificate_generator.HTML")
@pytest.mark.asyncio
async def test_generate_certificate_pdf_without_auth_token(mock_html) -> None:
    """Test PDF generation works without auth token when employee_data is provided."""
    generator = CertificateGenerator(auth_token=None)

    certificate = Certificate(
        id=1,
        cert_uid="test-uid",
        user_id=1,
        checklist_id=1,
        issued_at=datetime.now(UTC),
    )

    employee_data = {"first_name": "John", "last_name": "Doe", "position": "Developer"}

    mock_html_obj = MagicMock()
    mock_html.return_value = mock_html_obj
    mock_html_obj.write_pdf.return_value = b"pdf bytes"

    result = await generator.generate_certificate_pdf(
        certificate=certificate,
        template_name="Test Program",
        employee_data=employee_data,
        hr_data=None,
        mentor_data=None,
        locale="en",
    )

    assert result == b"pdf bytes"


@pytest.mark.asyncio
async def test_get_user_data_without_auth_token() -> None:
    """Test _get_user_data returns None when auth_token is not set (lines 31-36)."""
    generator = CertificateGenerator(auth_token=None)

    result = await generator._get_user_data(user_id=1)

    assert result is None


@patch("checklists_service.services.certificate_generator.HTML")
@pytest.mark.asyncio
async def test_generate_certificate_from_checklist_employee_not_found(mock_html) -> None:
    """Test generate_certificate_from_checklist raises ValueError when employee not found (lines 163-178)."""
    generator = CertificateGenerator(auth_token="test-token")

    certificate = Certificate(
        id=1,
        cert_uid="test-uid",
        user_id=1,
        checklist_id=1,
        issued_at=datetime.now(UTC),
    )

    checklist_data = {"template_name": "Test Program"}

    mock_html_obj = MagicMock()
    mock_html.return_value = mock_html_obj
    mock_html_obj.write_pdf.return_value = b"pdf bytes"

    with pytest.raises(ValueError, match="Employee 1 not found"):
        await generator.generate_certificate_from_checklist(
            certificate=certificate,
            checklist_data=checklist_data,
            locale="en",
        )


@patch("checklists_service.services.certificate_generator.HTML")
@patch("checklists_service.utils.auth_service_client")
@pytest.mark.asyncio
async def test_generate_certificate_from_checklist_with_hr_and_mentor(
    mock_auth_client, mock_html
) -> None:
    """Test generate_certificate_from_checklist with hr_id and mentor_id (lines 168-178)."""
    mock_auth_client.get_user = AsyncMock(side_effect=lambda uid, token: {
        1: {"first_name": "John", "last_name": "Doe", "position": "Developer"},
        2: {"first_name": "Jane", "last_name": "Smith", "position": "HR Manager"},
        3: {"first_name": "Bob", "last_name": "Johnson", "position": "Mentor"},
    }.get(uid))

    generator = CertificateGenerator(auth_token="test-token")

    certificate = Certificate(
        id=1,
        cert_uid="test-uid",
        user_id=1,
        checklist_id=1,
        hr_id=2,
        mentor_id=3,
        issued_at=datetime.now(UTC),
    )

    checklist_data = {"template_name": "Test Program"}

    mock_html_obj = MagicMock()
    mock_html.return_value = mock_html_obj
    mock_html_obj.write_pdf.return_value = b"pdf bytes"

    result = await generator.generate_certificate_from_checklist(
        certificate=certificate,
        checklist_data=checklist_data,
        locale="en",
    )

    assert result == b"pdf bytes"
    mock_auth_client.get_user.assert_any_call(1, "test-token")
    mock_auth_client.get_user.assert_any_call(2, "test-token")
    mock_auth_client.get_user.assert_any_call(3, "test-token")
