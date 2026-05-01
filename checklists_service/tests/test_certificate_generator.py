"""Tests for certificate generator service."""

import pytest
from datetime import datetime, UTC

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


@pytest.mark.asyncio
async def test_generate_certificate_pdf_without_auth_token() -> None:
    """Test PDF generation fails without auth token."""
    generator = CertificateGenerator(auth_token=None)
    
    certificate = Certificate(
        id=1,
        cert_uid="test-uid",
        user_id=1,
        checklist_id=1,
        issued_at=datetime.now(UTC),
    )
    
    employee_data = {"first_name": "John", "last_name": "Doe", "position": "Developer"}
    
    with pytest.raises(ValueError, match="Employee .* not found"):
        await generator.generate_certificate_pdf(
            certificate=certificate,
            template_name="Test Program",
            employee_data=employee_data,
            hr_data=None,
            mentor_data=None,
            locale="en",
        )
