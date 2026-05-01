"""Invitation management service with repository pattern."""

from datetime import UTC, datetime, timedelta

from loguru import logger
from pydantic import HttpUrl

from auth_service.config import settings
from auth_service.core import (
    ConflictException,
    InvitationStatus,
    NotFoundException,
    UserRole,
    ValidationException,
    generate_invitation_token,
)
from auth_service.models import Invitation, InvitationStatusHistory
from auth_service.repositories.unit_of_work import IUnitOfWork
from auth_service.schemas import InvitationCreate, InvitationStats


class InvitationService:
    """Service for invitation management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize InvitationService with Unit of Work."""
        self._uow = uow

    async def create_invitation(self, invitation_data: InvitationCreate) -> Invitation:
        """Create new invitation."""
        logger.debug(
            "Creating invitation (email={}, employee_id={}, role={}, mentor_id={})",
            invitation_data.email,
            invitation_data.employee_id,
            invitation_data.role,
            invitation_data.mentor_id,
        )
        # Check if pending invitation already exists for email
        has_pending = await self._uow.invitations.exists_pending_for_email(invitation_data.email)
        if has_pending:
            logger.warning(
                "Create invitation conflict: pending invitation exists for email ({})",
                invitation_data.email,
            )
            msg = "Pending invitation already exists for this email"
            raise ConflictException(msg)

        # Check if user already exists
        existing_user = await self._uow.users.get_by_email(invitation_data.email)
        if existing_user:
            logger.warning(
                "Create invitation conflict: user already exists for email ({})",
                invitation_data.email,
            )
            msg = "User with this email already exists"
            raise ConflictException(msg)

        # Check if employee_id is already used
        existing_employee = await self._uow.users.get_by_employee_id(invitation_data.employee_id)
        if existing_employee:
            logger.warning(
                "Create invitation conflict: employee_id already in use ({})",
                invitation_data.employee_id,
            )
            msg = "Employee ID already in use"
            raise ConflictException(msg)

        # Check if mentor exists when specified
        if invitation_data.mentor_id is not None:
            mentor = await self._uow.users.get_by_id(invitation_data.mentor_id)
            if not mentor:
                logger.warning(
                    "Create invitation: mentor not found (mentor_id={})",
                    invitation_data.mentor_id,
                )
                msg = "Mentor not found"
                raise NotFoundException(msg)

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
        created = await self._uow.invitations.create(invitation)
        await self._uow.commit()
        logger.info(
            "Invitation created (invitation_id={}, email={}, expires_at={})",
            created.id,
            created.email,
            created.expires_at.isoformat() if created.expires_at else None,
        )
        return created

    async def get_invitation_by_id(self, invitation_id: int) -> Invitation:
        """Get invitation by ID."""
        invitation = await self._uow.invitations.get_by_id(invitation_id)
        if not invitation:
            logger.warning("Invitation not found (invitation_id={})", invitation_id)
            msg = "Invitation"
            raise NotFoundException(msg)
        return invitation

    async def get_valid_invitation(self, token: str) -> Invitation:
        """Get valid (pending and not expired) invitation by token."""
        invitation = await self._uow.invitations.get_valid_by_token(token)
        if not invitation:
            logger.warning("Invalid or expired invitation token")
            msg = "Invalid or expired invitation"
            raise ValidationException(msg)
        return invitation

    async def resend_invitation(self, invitation_id: int, changed_by: int | None = None) -> Invitation:
        """Resend invitation with new token and extended expiry."""
        invitation = await self.get_invitation_by_id(invitation_id)
        old_status = invitation.status

        if invitation.status != InvitationStatus.PENDING:
            logger.warning(
                "Resend invitation rejected: status is {} (invitation_id={})",
                invitation.status,
                invitation_id,
            )
            msg = "Can only resend pending invitations"
            raise ValidationException(msg)

        # Generate new token and extend expiry
        invitation.token = generate_invitation_token()
        invitation.expires_at = datetime.now(UTC) + timedelta(days=7)
        invitation.status = InvitationStatus.PENDING

        updated = await self._uow.invitations.update(invitation)

        # Record status change
        await self._record_status_change(
            invitation_id=invitation.id,
            old_status=old_status,
            new_status=invitation.status,
            changed_by=changed_by,
        )

        logger.info("Invitation resent (invitation_id={})", updated.id)
        return updated

    async def revoke_invitation(self, invitation_id: int, changed_by: int | None = None) -> Invitation:
        """Revoke (cancel) invitation."""
        invitation = await self.get_invitation_by_id(invitation_id)
        old_status = invitation.status

        if invitation.status != InvitationStatus.PENDING:
            logger.warning(
                "Revoke invitation rejected: status is {} (invitation_id={})",
                invitation.status,
                invitation_id,
            )
            msg = "Can only revoke pending invitations"
            raise ValidationException(msg)

        invitation.status = InvitationStatus.REVOKED

        updated = await self._uow.invitations.update(invitation)

        # Record status change
        await self._record_status_change(
            invitation_id=invitation.id,
            old_status=old_status,
            new_status=invitation.status,
            changed_by=changed_by,
        )

        logger.info("Invitation revoked (invitation_id={})", updated.id)
        return updated

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
        sort_by: str | None = None,
        sort_order: str = "desc",
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
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return list(invitations), total

    async def get_invitation_stats(self) -> InvitationStats:
        """Get invitation statistics."""
        return await self._uow.invitations.get_statistics()

    async def delete_invitation(self, invitation_id: int) -> bool:
        """Delete invitation by ID."""
        invitation = await self._uow.invitations.get_by_id(invitation_id)
        if not invitation:
            logger.warning("Delete invitation: not found (invitation_id={})", invitation_id)
            msg = "Invitation"
            raise NotFoundException(msg)
        deleted = await self._uow.invitations.delete(invitation_id)
        logger.info(
            "Invitation deleted (invitation_id={}, deleted={})", invitation_id, deleted
        )
        return deleted

    def generate_invitation_url(self, token: str) -> HttpUrl:
        """Generate invitation URL for Telegram bot."""
        return HttpUrl(f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={token}")

    async def _record_status_change(
        self,
        invitation_id: int,
        old_status: str | None,
        new_status: str,
        changed_by: int | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Record invitation status change to audit log."""
        status_change = InvitationStatusHistory(
            invitation_id=invitation_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            metadata=metadata,
        )
        await self._uow.invitation_status_history.create(status_change)
