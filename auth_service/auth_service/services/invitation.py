"""Invitation management service with repository pattern."""

from datetime import UTC, datetime, timedelta

from auth_service.core import (
    ConflictException,
    InvitationStatus,
    NotFoundException,
    UserRole,
    ValidationException,
    generate_invitation_token,
)
from auth_service.models.invitation import Invitation
from auth_service.repositories.unit_of_work import IUnitOfWork
from auth_service.schemas import InvitationCreate, InvitationStats


class InvitationService:
    """Service for invitation management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize InvitationService with Unit of Work."""
        self._uow = uow

    async def create_invitation(self, invitation_data: InvitationCreate) -> Invitation:
        """Create new invitation."""
        # Check if pending invitation already exists for email
        has_pending = await self._uow.invitations.exists_pending_for_email(invitation_data.email)
        if has_pending:
            msg = "Pending invitation already exists for this email"
            raise ConflictException(msg)

        # Check if user already exists
        existing_user = await self._uow.users.get_by_email(invitation_data.email)
        if existing_user:
            msg = "User with this email already exists"
            raise ConflictException(msg)

        # Check if employee_id is already used
        existing_employee = await self._uow.users.get_by_employee_id(invitation_data.employee_id)
        if existing_employee:
            msg = "Employee ID already in use"
            raise ConflictException(msg)

        # Create invitation
        invitation = Invitation(
            token=generate_invitation_token(),
            email=invitation_data.email,
            employee_id=invitation_data.employee_id,
            first_name=invitation_data.first_name,
            last_name=invitation_data.last_name,
            department_id=invitation_data.department_id,
            position=invitation_data.position,
            level=invitation_data.level,
            role=invitation_data.role,
            mentor_id=invitation_data.mentor_id,
            expires_at=datetime.now(UTC) + timedelta(days=invitation_data.expires_in_days),
            status=InvitationStatus.PENDING,
        )

        # Save invitation
        return await self._uow.invitations.create(invitation)

    async def get_invitation_by_id(self, invitation_id: int) -> Invitation:
        """Get invitation by ID."""
        invitation = await self._uow.invitations.get_by_id(invitation_id)
        if not invitation:
            msg = "Invitation"
            raise NotFoundException(msg)
        return invitation

    async def get_valid_invitation(self, token: str) -> Invitation:
        """Get valid (pending and not expired) invitation by token."""
        invitation = await self._uow.invitations.get_valid_by_token(token)
        if not invitation:
            msg = "Invalid or expired invitation"
            raise ValidationException(msg)
        return invitation

    async def resend_invitation(self, invitation_id: int) -> Invitation:
        """Resend invitation with new token and extended expiry."""
        invitation = await self.get_invitation_by_id(invitation_id)

        if invitation.status != InvitationStatus.PENDING:
            msg = "Can only resend pending invitations"
            raise ValidationException(msg)

        # Generate new token and extend expiry
        invitation.token = generate_invitation_token()
        invitation.expires_at = datetime.now(UTC) + timedelta(days=7)
        invitation.status = InvitationStatus.PENDING

        return await self._uow.invitations.update(invitation)

    async def revoke_invitation(self, invitation_id: int) -> Invitation:
        """Revoke (cancel) invitation."""
        invitation = await self.get_invitation_by_id(invitation_id)

        if invitation.status != InvitationStatus.PENDING:
            msg = "Can only revoke pending invitations"
            raise ValidationException(msg)

        invitation.status = InvitationStatus.REVOKED

        return await self._uow.invitations.update(invitation)

    async def get_invitations(
        self,
        skip: int = 0,
        limit: int = 100,
        email: str | None = None,
        role: UserRole | None = None,
        status: InvitationStatus | None = None,
        department_id: int | None = None,
        *,
        expired_only: bool = False,
    ) -> tuple[list[Invitation], int]:
        """Get paginated list of invitations with filters."""
        invitations, total = await self._uow.invitations.find_invitations(
            skip=skip,
            limit=limit,
            email=email,
            role=role,
            status=status,
            department_id=department_id,
            expired_only=expired_only,
        )
        return list(invitations), total

    async def get_invitation_stats(self) -> InvitationStats:
        """Get invitation statistics."""
        return await self._uow.invitations.get_statistics()

    async def delete_invitation(self, invitation_id: int) -> bool:
        """Delete invitation by ID."""
        invitation = await self._uow.invitations.get_by_id(invitation_id)
        if not invitation:
            msg = "Invitation"
            raise NotFoundException(msg)
        return await self._uow.invitations.delete(invitation_id)

    def generate_invitation_url(self, token: str) -> str:
        """Generate invitation URL for Telegram bot."""
        return f"https://t.me/company_hr_mentor_bot?start={token}"
