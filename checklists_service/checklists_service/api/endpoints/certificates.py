"""Certificate management endpoints."""

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel

from checklists_service.api.deps import AuthToken, CurrentUser, HRUser, ServiceAuth, UOWDep
from checklists_service.core import NotFoundException, PermissionDenied, ValidationException
from checklists_service.models import Certificate
from checklists_service.services import CertificateGenerator

logger = logging.getLogger(__name__)


class IssueCertificateRequest(BaseModel):
    """Request body for issuing a certificate."""

    checklist_id: int


router = APIRouter()


@router.get("/my")
async def get_my_certificates(
    uow: UOWDep,
    current_user: CurrentUser,
) -> list[dict]:
    """Get certificates for the current user."""
    certificates = await uow.certificates.get_by_user(current_user.id)
    return [
        {
            "cert_uid": cert.cert_uid,
            "checklist_id": cert.checklist_id,
            "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
        }
        for cert in certificates
    ]


@router.get("/{cert_uid}/download")
async def download_certificate(
    cert_uid: str,
    uow: UOWDep,
    current_user: CurrentUser,
    auth_token: AuthToken,
    locale: Annotated[str, Query()] = "en",
) -> Response:
    """Download certificate PDF by UID."""
    certificate = await uow.certificates.get_by_cert_uid(cert_uid)
    if not certificate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")

    # Check permission: owner or HR/Admin
    if certificate.user_id != current_user.id and current_user.role not in ["HR", "ADMIN"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Get checklist data
    checklist = await uow.checklists.get_by_id(certificate.checklist_id)
    if not checklist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    # Get template data
    template = await uow.templates.get_by_id(checklist.template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    # Generate PDF
    generator = CertificateGenerator(auth_token=auth_token)
    checklist_data = {
        "template_name": template.name,
    }
    
    try:
        pdf_bytes = await generator.generate_certificate_from_checklist(
            certificate=certificate,
            checklist_data=checklist_data,
            locale=locale,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("Failed to generate certificate PDF: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to generate certificate PDF"
        ) from e

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="certificate_{cert_uid}.pdf"',
        },
    )


@router.post("/issue")
async def issue_certificate(
    request: IssueCertificateRequest,
    uow: UOWDep,
    _current_user: HRUser,
) -> dict:
    """Manually issue certificate for a completed checklist (HR/admin only)."""
    # Check if checklist exists and is completed
    checklist = await uow.checklists.get_by_id(request.checklist_id)
    if not checklist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    from checklists_service.core.enums import ChecklistStatus

    if checklist.status != ChecklistStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Checklist must be completed to issue certificate"
        )

    # Check if certificate already exists
    existing = await uow.certificates.get_by_checklist_id(request.checklist_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificate already issued")

    # Create certificate
    import uuid

    certificate = Certificate(
        cert_uid=str(uuid.uuid4()),
        user_id=checklist.user_id,
        checklist_id=checklist.id,
        hr_id=checklist.hr_id,
        mentor_id=checklist.mentor_id,
    )
    await uow.certificates.create(certificate)
    await uow.commit()

    return {
        "cert_uid": certificate.cert_uid,
        "message": "Certificate issued successfully",
    }


@router.get("/list")
async def list_certificates(
    uow: UOWDep,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    user_id: Annotated[int | None, Query()] = None,
    from_date: Annotated[str | None, Query()] = None,
    to_date: Annotated[str | None, Query()] = None,
) -> dict:
    """List certificates with filters (HR/admin only)."""
    certificates, total = await uow.certificates.find_certificates(
        skip=skip,
        limit=limit,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
    )

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "total": total,
        "certificates": [
            {
                "id": cert.id,
                "cert_uid": cert.cert_uid,
                "user_id": cert.user_id,
                "checklist_id": cert.checklist_id,
                "hr_id": cert.hr_id,
                "mentor_id": cert.mentor_id,
                "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
            }
            for cert in certificates
        ],
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages,
    }
