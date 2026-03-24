"""SQLAlchemy implementation of Invitation repository."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import cast

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_service.core import InvitationStatus
from auth_service.models import Invitation
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.invitation import IInvitationRepository
from auth_service.schemas.invitation import InvitationStats


class InvitationRepository(SqlAlchemyBaseRepository[Invitation, int], IInvitationRepository):
    """SQLAlchemy implementation of Invitation repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize InvitationRepository with database session."""
        super().__init__(session, Invitation)

    async def get_by_id(self, entity_id: int) -> Invitation | None:
        """Get invitation by ID with department relationship."""
        stmt = select(Invitation).where(Invitation.id == entity_id).options(selectinload(Invitation.department))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> Invitation | None:
        """Get invitation by token."""
        stmt = select(Invitation).where(Invitation.token == token).options(selectinload(Invitation.department))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_valid_by_token(self, token: str) -> Invitation | None:
        """Get valid (pending and not expired) invitation by token."""
        stmt = (
            select(Invitation)
            .where(
                and_(
                    Invitation.token == token,
                    Invitation.status == InvitationStatus.PENDING,
                    Invitation.expires_at > datetime.now(UTC),
                )
            )
            .options(selectinload(Invitation.department))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Sequence[Invitation]:
        """Get all invitations for email address."""
        stmt = select(Invitation).where(Invitation.email == email).options(selectinload(Invitation.department))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_invitations(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        email: str | None = None,
        status: InvitationStatus | None = None,
        department_id: int | None = None,
        expired_only: bool = False,
    ) -> tuple[Sequence[Invitation], int]:
        """Find invitations with filtering and return results with total count."""
        count_stmt = select(func.count(Invitation.id))

        stmt = select(Invitation).options(selectinload(Invitation.department))

        if email:
            stmt = stmt.where(Invitation.email.ilike(f"%{email}%"))
            count_stmt = count_stmt.where(Invitation.email.ilike(f"%{email}%"))

        if status:
            stmt = stmt.where(Invitation.status == status)
            count_stmt = count_stmt.where(Invitation.status == status)

        if department_id is not None:
            stmt = stmt.where(Invitation.department_id == department_id)
            count_stmt = count_stmt.where(Invitation.department_id == department_id)

        if expired_only:
            expired_filter = and_(
                Invitation.expires_at < datetime.now(UTC),
                Invitation.status == InvitationStatus.PENDING,
            )
            stmt = stmt.where(expired_filter)
            count_stmt = count_stmt.where(expired_filter)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.offset(skip).limit(limit).order_by(Invitation.created_at.desc())
        result = await self._session.execute(stmt)
        invitations = result.scalars().all()

        return invitations, total

    async def create(self, entity: Invitation) -> Invitation:
        """Create invitation and reload with department relationship."""
        self._session.add(entity)
        await self._session.flush()
        return await self.get_by_id(entity.id) or entity  # type: ignore[return-value]

    async def mark_as_used(self, invitation_id: int, user_id: int) -> Invitation:
        """Mark invitation as used and link to user."""
        invitation = await self.get_by_id(invitation_id)
        if not invitation:
            msg = f"Invitation with ID {invitation_id} not found"
            raise ValueError(msg)

        if invitation.status != InvitationStatus.PENDING:
            msg = "Invitation is not pending"
            raise ValueError(msg)

        if invitation.expires_at < datetime.now(UTC):
            msg = "Invitation has expired"
            raise ValueError(msg)

        invitation.status = InvitationStatus.USED
        invitation.used_at = datetime.now(UTC)
        invitation.user_id = user_id

        await self._session.flush()
        return await self.get_by_id(invitation_id) or invitation  # type: ignore[return-value]

    async def update_status(self, invitation_id: int, status: InvitationStatus) -> Invitation:
        """Update invitation status."""
        invitation = await self.get_by_id(invitation_id)
        if not invitation:
            msg = f"Invitation with ID {invitation_id} not found"
            raise ValueError(msg)

        invitation.status = status
        await self._session.flush()
        return await self.get_by_id(invitation_id) or invitation  # type: ignore[return-value]

    async def get_statistics(self) -> InvitationStats:
        """Get invitation statistics."""
        total_stmt = select(func.count(Invitation.id))
        total_result = await self._session.execute(total_stmt)
        total = cast("int", total_result.scalar_one())

        status_stmt = select(Invitation.status, func.count(Invitation.id)).group_by(Invitation.status)
        status_result = await self._session.execute(status_stmt)
        status_counts = dict(status_result.all())

        for status in InvitationStatus:
            status_counts.setdefault(status, 0)

        expired_stmt = select(func.count(Invitation.id)).where(
            and_(
                Invitation.expires_at < datetime.now(UTC),
                Invitation.status == InvitationStatus.PENDING,
            )
        )
        expired_result = await self._session.execute(expired_stmt)
        expired = cast("int", expired_result.scalar_one())

        used_count = status_counts.get(InvitationStatus.USED, 0)
        conversion_rate = (used_count / total * 100) if total > 0 else 0.0

        recent_stmt = (
            select(func.date(Invitation.created_at).label("date"), func.count(Invitation.id).label("count"))
            .where(Invitation.created_at >= datetime.now(UTC) - timedelta(days=30))
            .group_by(func.date(Invitation.created_at))
        )
        recent_result = await self._session.execute(recent_stmt)

        recent_activity = [{"date": row.date.isoformat(), "count": row.count} for row in recent_result.all()]

        return InvitationStats(
            total=total,
            pending=status_counts.get(InvitationStatus.PENDING, 0),
            used=used_count,
            revoked=status_counts.get(InvitationStatus.REVOKED, 0),
            expired=expired,
            conversion_rate=round(conversion_rate, 2),
            by_status=status_counts,
            recent_activity=recent_activity,
        )

    async def exists_pending_for_email(self, email: str) -> bool:
        """Check if pending invitation exists for email."""
        stmt = select(func.count(Invitation.id)).where(
            and_(
                Invitation.email == email,
                Invitation.status == InvitationStatus.PENDING,
                Invitation.expires_at > datetime.now(UTC),
            )
        )
        result = await self._session.execute(stmt)
        count = cast("int", result.scalar_one())
        return count > 0
