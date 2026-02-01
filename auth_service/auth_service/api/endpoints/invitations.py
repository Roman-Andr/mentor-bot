"""Invitation management endpoints with repository pattern."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from auth_service.api.deps import (
    HRUser,
    InvitationServiceDep,
)
from auth_service.core import (
    ConflictException,
    InvitationStatus,
    NotFoundException,
    ValidationException,
)
from auth_service.schemas import (
    InvitationCreate,
    InvitationListResponse,
    InvitationResponse,
    InvitationStats,
)

router = APIRouter()


@router.get("/")
async def get_invitations(  # noqa: PLR0913
    invitation_service: InvitationServiceDep,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    email: Annotated[str | None, Query()] = None,
    status: Annotated[InvitationStatus | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    *,
    expired_only: Annotated[bool, Query()] = False,
) -> InvitationListResponse:
    """Get paginated list of invitations (HR/admin only)."""
    invitations, total = await invitation_service.get_invitations(
        skip=skip,
        limit=limit,
        email=email,
        status=status,
        department=department,
        expired_only=expired_only,
    )

    stats = await invitation_service.get_invitation_stats()
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return InvitationListResponse(
        total=total,
        invitations=[
            InvitationResponse(
                **invitation.__dict__,
                invitation_url=invitation_service.generate_invitation_url(invitation.token),
                is_expired=invitation.expires_at < datetime.now(UTC) and invitation.status == InvitationStatus.PENDING,
            )
            for invitation in invitations
        ],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
        stats=stats,
    )


@router.post("/")
async def create_invitation(
    invitation_data: InvitationCreate,
    invitation_service: InvitationServiceDep,
    _current_user: HRUser,
) -> InvitationResponse:
    """Create new invitation (HR/admin only)."""
    try:
        invitation = await invitation_service.create_invitation(invitation_data)
        return InvitationResponse(
            **invitation.__dict__,
            invitation_url=invitation_service.generate_invitation_url(invitation.token),
            is_expired=False,
        )
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.detail),
        ) from e


@router.get("/{invitation_id}")
async def get_invitation(
    invitation_id: int,
    invitation_service: InvitationServiceDep,
    _current_user: HRUser,
) -> InvitationResponse:
    """Get invitation by ID (HR/admin only)."""
    try:
        invitation = await invitation_service.get_invitation_by_id(invitation_id)
        return InvitationResponse(
            **invitation.__dict__,
            invitation_url=invitation_service.generate_invitation_url(invitation.token),
            is_expired=invitation.expires_at < datetime.now(UTC) and invitation.status == InvitationStatus.PENDING,
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.get("/token/{token}")
async def get_invitation_by_token(
    token: str,
    invitation_service: InvitationServiceDep,
) -> InvitationResponse:
    """Get invitation by token (public, for registration)."""
    try:
        invitation = await invitation_service.get_valid_invitation(token)
        return InvitationResponse(
            **invitation.__dict__,
            invitation_url=invitation_service.generate_invitation_url(invitation.token),
            is_expired=False,
        )
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail),
        ) from e


@router.post("/{invitation_id}/resend")
async def resend_invitation(
    invitation_id: int,
    invitation_service: InvitationServiceDep,
    _current_user: HRUser,
) -> InvitationResponse:
    """Resend invitation with new token (HR/admin only)."""
    try:
        invitation = await invitation_service.resend_invitation(invitation_id)
        return InvitationResponse(
            **invitation.__dict__,
            invitation_url=invitation_service.generate_invitation_url(invitation.token),
            is_expired=False,
        )
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.post("/{invitation_id}/revoke")
async def revoke_invitation(
    invitation_id: int,
    invitation_service: InvitationServiceDep,
    _current_user: HRUser,
) -> InvitationResponse:
    """Revoke invitation (HR/admin only)."""
    try:
        invitation = await invitation_service.revoke_invitation(invitation_id)
        return InvitationResponse(
            **invitation.__dict__,
            invitation_url=invitation_service.generate_invitation_url(invitation.token),
            is_expired=True,
        )
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
        ) from e


@router.get("/stats/summary")
async def get_invitation_stats(
    invitation_service: InvitationServiceDep,
    _current_user: HRUser,
) -> InvitationStats:
    """Get invitation statistics (HR/admin only)."""
    return await invitation_service.get_invitation_stats()
