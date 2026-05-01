"""Unit tests for certificates API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from checklists_service.api.deps import UserInfo
from checklists_service.api.endpoints import certificates
from checklists_service.api.endpoints import certificates as cert_module
from checklists_service.core.enums import ChecklistStatus
from checklists_service.models import Certificate
from fastapi import HTTPException, status


@pytest.fixture
def sample_user():
    """Create sample user."""
    return UserInfo(
        {"id": 1, "email": "user@example.com", "role": "EMPLOYEE", "is_active": True, "employee_id": "EMP001"}
    )


@pytest.fixture
def sample_hr_user():
    """Create sample HR user."""
    return UserInfo({"id": 10, "email": "hr@example.com", "role": "HR", "is_active": True, "employee_id": "HR001"})


@pytest.fixture
def sample_certificate():
    """Create sample certificate."""
    now = datetime.now(UTC)
    return Certificate(
        id=1,
        cert_uid="test-cert-uid",
        user_id=1,
        checklist_id=1,
        hr_id=10,
        mentor_id=2,
        issued_at=now,
    )


class TestGetMyCertificates:
    """Test GET /certificates/my endpoint."""

    async def test_get_my_certificates_empty(self, sample_user) -> None:
        """Test getting my certificates when none exist."""
        uow = MagicMock()
        uow.certificates.get_by_user = AsyncMock(return_value=[])

        result = await certificates.get_my_certificates(
            uow=uow,
            current_user=sample_user,
        )

        assert result == []
        uow.certificates.get_by_user.assert_awaited_once_with(sample_user.id)

    async def test_get_my_certificates_with_certificates(self, sample_user, sample_certificate) -> None:
        """Test getting my certificates when they exist."""
        uow = MagicMock()
        uow.certificates.get_by_user = AsyncMock(return_value=[sample_certificate])

        result = await certificates.get_my_certificates(
            uow=uow,
            current_user=sample_user,
        )

        assert len(result) == 1
        assert result[0]["cert_uid"] == "test-cert-uid"
        assert result[0]["checklist_id"] == 1
        assert result[0]["issued_at"] is not None
        uow.certificates.get_by_user.assert_awaited_once_with(sample_user.id)

    async def test_get_my_certificates_without_issued_at(self, sample_user) -> None:
        """Test getting my certificates with None issued_at."""
        uow = MagicMock()
        cert_no_date = Certificate(
            id=1,
            cert_uid="test-cert-uid",
            user_id=1,
            checklist_id=1,
            issued_at=None,
        )
        uow.certificates.get_by_user = AsyncMock(return_value=[cert_no_date])

        result = await certificates.get_my_certificates(
            uow=uow,
            current_user=sample_user,
        )

        assert len(result) == 1
        assert result[0]["issued_at"] is None


class TestDownloadCertificate:
    """Test GET /certificates/{cert_uid}/download endpoint."""

    async def test_download_certificate_success(self, sample_user, sample_certificate) -> None:
        """Test successful certificate download by owner."""
        uow = MagicMock()
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=sample_certificate)

        checklist_mock = MagicMock()
        checklist_mock.template_id = 1
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)

        template_mock = MagicMock()
        template_mock.name = "Onboarding Template"
        uow.templates.get_by_id = AsyncMock(return_value=template_mock)

        pdf_bytes = b"fake pdf content"
        with patch("checklists_service.api.endpoints.certificates.CertificateGenerator") as mock_gen_cls:
            mock_gen = MagicMock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.generate_certificate_from_checklist = AsyncMock(return_value=pdf_bytes)

            result = await certificates.download_certificate(
                cert_uid="test-cert-uid",
                uow=uow,
                current_user=sample_user,
                auth_token="test-token",
                locale="en",
            )

            assert result.media_type == "application/pdf"
            assert result.body == pdf_bytes
            assert "attachment" in result.headers["Content-Disposition"]

    async def test_download_certificate_by_hr(self, sample_hr_user, sample_certificate) -> None:
        """Test certificate download by HR user."""
        uow = MagicMock()
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=sample_certificate)

        checklist_mock = MagicMock()
        checklist_mock.template_id = 1
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)

        template_mock = MagicMock()
        template_mock.name = "Onboarding Template"
        uow.templates.get_by_id = AsyncMock(return_value=template_mock)

        pdf_bytes = b"fake pdf content"
        with patch("checklists_service.api.endpoints.certificates.CertificateGenerator") as mock_gen_cls:
            mock_gen = MagicMock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.generate_certificate_from_checklist = AsyncMock(return_value=pdf_bytes)

            result = await certificates.download_certificate(
                cert_uid="test-cert-uid",
                uow=uow,
                current_user=sample_hr_user,
                auth_token="test-token",
                locale="en",
            )

            assert result.media_type == "application/pdf"

    async def test_download_certificate_not_found(self, sample_user) -> None:
        """Test download fails when certificate not found."""
        uow = MagicMock()
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await certificates.download_certificate(
                cert_uid="nonexistent",
                uow=uow,
                current_user=sample_user,
                auth_token="test-token",
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Certificate not found" in exc_info.value.detail

    async def test_download_certificate_permission_denied(self, sample_user) -> None:
        """Test download fails when user doesn't own certificate."""
        uow = MagicMock()
        cert = Certificate(
            id=1,
            cert_uid="test-cert-uid",
            user_id=999,  # Different user
            checklist_id=1,
        )
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=cert)

        with pytest.raises(HTTPException) as exc_info:
            await certificates.download_certificate(
                cert_uid="test-cert-uid",
                uow=uow,
                current_user=sample_user,
                auth_token="test-token",
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail

    async def test_download_certificate_checklist_not_found(self, sample_user, sample_certificate) -> None:
        """Test download fails when checklist not found."""
        uow = MagicMock()
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=sample_certificate)
        uow.checklists.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await certificates.download_certificate(
                cert_uid="test-cert-uid",
                uow=uow,
                current_user=sample_user,
                auth_token="test-token",
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Checklist not found" in exc_info.value.detail

    async def test_download_certificate_template_not_found(self, sample_user, sample_certificate) -> None:
        """Test download fails when template not found."""
        uow = MagicMock()
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=sample_certificate)

        checklist_mock = MagicMock()
        checklist_mock.template_id = 1
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)
        uow.templates.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await certificates.download_certificate(
                cert_uid="test-cert-uid",
                uow=uow,
                current_user=sample_user,
                auth_token="test-token",
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Template not found" in exc_info.value.detail

    async def test_download_certificate_generation_error(self, sample_user, sample_certificate) -> None:
        """Test download fails when PDF generation raises ValueError."""
        uow = MagicMock()
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=sample_certificate)

        checklist_mock = MagicMock()
        checklist_mock.template_id = 1
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)

        template_mock = MagicMock()
        template_mock.name = "Onboarding Template"
        uow.templates.get_by_id = AsyncMock(return_value=template_mock)

        with patch("checklists_service.api.endpoints.certificates.CertificateGenerator") as mock_gen_cls:
            mock_gen = MagicMock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.generate_certificate_from_checklist = AsyncMock(side_effect=ValueError("Invalid data"))

            with pytest.raises(HTTPException) as exc_info:
                await certificates.download_certificate(
                    cert_uid="test-cert-uid",
                    uow=uow,
                    current_user=sample_user,
                    auth_token="test-token",
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_download_certificate_generation_exception(self, sample_user, sample_certificate) -> None:
        """Test download fails when PDF generation raises generic exception."""
        uow = MagicMock()
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=sample_certificate)

        checklist_mock = MagicMock()
        checklist_mock.template_id = 1
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)

        template_mock = MagicMock()
        template_mock.name = "Onboarding Template"
        uow.templates.get_by_id = AsyncMock(return_value=template_mock)

        with patch("checklists_service.api.endpoints.certificates.CertificateGenerator") as mock_gen_cls:
            mock_gen = MagicMock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.generate_certificate_from_checklist = AsyncMock(side_effect=RuntimeError("Unexpected error"))

            with patch.object(cert_module, "logger") as mock_logger:
                with pytest.raises(HTTPException) as exc_info:
                    await certificates.download_certificate(
                        cert_uid="test-cert-uid",
                        uow=uow,
                        current_user=sample_user,
                        auth_token="test-token",
                    )

                assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                mock_logger.exception.assert_called_once()

    async def test_download_certificate_russian_locale(self, sample_user, sample_certificate) -> None:
        """Test certificate download with Russian locale."""
        uow = MagicMock()
        uow.certificates.get_by_cert_uid = AsyncMock(return_value=sample_certificate)

        checklist_mock = MagicMock()
        checklist_mock.template_id = 1
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)

        template_mock = MagicMock()
        template_mock.name = "Onboarding Template"
        uow.templates.get_by_id = AsyncMock(return_value=template_mock)

        pdf_bytes = b"fake pdf content"
        with patch("checklists_service.api.endpoints.certificates.CertificateGenerator") as mock_gen_cls:
            mock_gen = MagicMock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.generate_certificate_from_checklist = AsyncMock(return_value=pdf_bytes)

            result = await certificates.download_certificate(
                cert_uid="test-cert-uid",
                uow=uow,
                current_user=sample_user,
                auth_token="test-token",
                locale="ru",
            )

            assert result.media_type == "application/pdf"
            mock_gen.generate_certificate_from_checklist.assert_awaited_once_with(
                certificate=sample_certificate,
                checklist_data={"template_name": "Onboarding Template"},
                locale="ru",
            )


class TestIssueCertificate:
    """Test POST /certificates/issue endpoint."""

    async def test_issue_certificate_success(self, sample_hr_user) -> None:
        """Test successful certificate issuance."""
        uow = MagicMock()

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.user_id = 1
        checklist_mock.hr_id = 10
        checklist_mock.mentor_id = 2
        checklist_mock.status = ChecklistStatus.COMPLETED
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)

        uow.certificates.get_by_checklist_id = AsyncMock(return_value=None)
        uow.certificates.create = AsyncMock()
        uow.commit = AsyncMock()

        request = MagicMock()
        request.checklist_id = 1

        result = await certificates.issue_certificate(
            request=request,
            uow=uow,
            _current_user=sample_hr_user,
        )

        assert "cert_uid" in result
        assert "message" in result
        assert result["message"] == "Certificate issued successfully"
        uow.certificates.create.assert_awaited_once()
        uow.commit.assert_awaited_once()

    async def test_issue_certificate_checklist_not_found(self, sample_hr_user) -> None:
        """Test issue fails when checklist not found."""
        uow = MagicMock()
        uow.checklists.get_by_id = AsyncMock(return_value=None)

        request = MagicMock()
        request.checklist_id = 999

        with pytest.raises(HTTPException) as exc_info:
            await certificates.issue_certificate(
                request=request,
                uow=uow,
                _current_user=sample_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Checklist not found" in exc_info.value.detail

    async def test_issue_certificate_not_completed(self, sample_hr_user) -> None:
        """Test issue fails when checklist is not completed."""
        uow = MagicMock()

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.status = ChecklistStatus.IN_PROGRESS
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)

        request = MagicMock()
        request.checklist_id = 1

        with pytest.raises(HTTPException) as exc_info:
            await certificates.issue_certificate(
                request=request,
                uow=uow,
                _current_user=sample_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Checklist must be completed" in exc_info.value.detail

    async def test_issue_certificate_already_exists(self, sample_hr_user) -> None:
        """Test issue fails when certificate already exists."""
        uow = MagicMock()

        checklist_mock = MagicMock()
        checklist_mock.id = 1
        checklist_mock.status = ChecklistStatus.COMPLETED
        uow.checklists.get_by_id = AsyncMock(return_value=checklist_mock)

        existing_cert = MagicMock()
        uow.certificates.get_by_checklist_id = AsyncMock(return_value=existing_cert)

        request = MagicMock()
        request.checklist_id = 1

        with pytest.raises(HTTPException) as exc_info:
            await certificates.issue_certificate(
                request=request,
                uow=uow,
                _current_user=sample_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Certificate already issued" in exc_info.value.detail


class TestListCertificates:
    """Test GET /certificates/list endpoint."""

    async def test_list_certificates_success(self, sample_hr_user) -> None:
        """Test successful certificate listing."""
        uow = MagicMock()

        now = datetime.now(UTC)
        cert_mock = MagicMock()
        cert_mock.id = 1
        cert_mock.cert_uid = "cert-uid-1"
        cert_mock.user_id = 1
        cert_mock.checklist_id = 1
        cert_mock.hr_id = 10
        cert_mock.mentor_id = 2
        cert_mock.issued_at = now

        uow.certificates.find_certificates = AsyncMock(return_value=([cert_mock], 1))

        result = await certificates.list_certificates(
            uow=uow,
            _current_user=sample_hr_user,
            skip=0,
            limit=50,
        )

        assert result["total"] == 1
        assert len(result["certificates"]) == 1
        assert result["page"] == 1
        assert result["size"] == 50
        assert result["pages"] == 1
        assert result["certificates"][0]["cert_uid"] == "cert-uid-1"

    async def test_list_certificates_with_filters(self, sample_hr_user) -> None:
        """Test certificate listing with filters."""
        uow = MagicMock()

        uow.certificates.find_certificates = AsyncMock(return_value=([], 0))

        result = await certificates.list_certificates(
            uow=uow,
            _current_user=sample_hr_user,
            skip=10,
            limit=25,
            user_id=1,
            from_date="2024-01-01",
            to_date="2024-12-31",
        )

        assert result["total"] == 0
        assert len(result["certificates"]) == 0
        uow.certificates.find_certificates.assert_awaited_once_with(
            skip=10,
            limit=25,
            user_id=1,
            from_date="2024-01-01",
            to_date="2024-12-31",
        )

    async def test_list_certificates_pagination_calculation(self, sample_hr_user) -> None:
        """Test certificate listing pagination calculation."""
        uow = MagicMock()

        uow.certificates.find_certificates = AsyncMock(return_value=([], 100))

        result = await certificates.list_certificates(
            uow=uow,
            _current_user=sample_hr_user,
            skip=0,
            limit=25,
        )

        assert result["total"] == 100
        assert result["pages"] == 4  # (100 + 25 - 1) // 25 = 4
        assert result["page"] == 1

    async def test_list_certificates_without_issued_at(self, sample_hr_user) -> None:
        """Test certificate listing with None issued_at."""
        uow = MagicMock()

        cert_mock = MagicMock()
        cert_mock.id = 1
        cert_mock.cert_uid = "cert-uid-1"
        cert_mock.user_id = 1
        cert_mock.checklist_id = 1
        cert_mock.hr_id = 10
        cert_mock.mentor_id = 2
        cert_mock.issued_at = None

        uow.certificates.find_certificates = AsyncMock(return_value=([cert_mock], 1))

        result = await certificates.list_certificates(
            uow=uow,
            _current_user=sample_hr_user,
        )

        assert result["certificates"][0]["issued_at"] is None
