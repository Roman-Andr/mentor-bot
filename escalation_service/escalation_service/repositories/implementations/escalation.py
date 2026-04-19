"""SQLAlchemy implementation of Escalation repository."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import Column, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from escalation_service.core.enums import EscalationStatus, EscalationType
from escalation_service.models import EscalationRequest
from escalation_service.repositories.implementations.base import SqlAlchemyBaseRepository
from escalation_service.repositories.interfaces import IEscalationRepository


class EscalationRepository(SqlAlchemyBaseRepository[EscalationRequest, int], IEscalationRepository):
    """SQLAlchemy implementation of Escalation repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize EscalationRepository with database session."""
        super().__init__(session, EscalationRequest)

    def _get_sort_column(self, sort_by: str | None) -> Column:
        """Get SQLAlchemy column for sorting."""
        column_map = {
            "type": EscalationRequest.type,
            "status": EscalationRequest.status,
            "user": EscalationRequest.user_id,
            "assignedTo": EscalationRequest.assigned_to,
            "createdAt": EscalationRequest.created_at,
            "updatedAt": EscalationRequest.updated_at,
            "resolvedAt": EscalationRequest.resolved_at,
        }
        return column_map.get(sort_by, EscalationRequest.created_at)

    async def find_requests(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
        assigned_to: int | None = None,
        escalation_type: EscalationType | None = None,
        status: EscalationStatus | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[Sequence[EscalationRequest], int]:
        """Find escalation requests with filtering and return results with total count."""
        count_stmt = select(func.count(EscalationRequest.id))
        stmt = select(EscalationRequest)

        if user_id is not None:
            stmt = stmt.where(EscalationRequest.user_id == user_id)
            count_stmt = count_stmt.where(EscalationRequest.user_id == user_id)

        if assigned_to is not None:
            stmt = stmt.where(EscalationRequest.assigned_to == assigned_to)
            count_stmt = count_stmt.where(EscalationRequest.assigned_to == assigned_to)

        if escalation_type is not None:
            stmt = stmt.where(EscalationRequest.type == escalation_type)
            count_stmt = count_stmt.where(EscalationRequest.type == escalation_type)

        if status is not None:
            stmt = stmt.where(EscalationRequest.status == status)
            count_stmt = count_stmt.where(EscalationRequest.status == status)

        if search:
            search_filter = or_(
                EscalationRequest.reason.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)
        stmt = stmt.order_by(sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        requests = result.scalars().all()

        return requests, total

    async def get_user_requests(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[EscalationRequest]:
        """Get requests created by a specific user."""
        stmt = (
            select(EscalationRequest)
            .where(EscalationRequest.user_id == user_id)
            .order_by(EscalationRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_assigned_requests(
        self, assignee_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[EscalationRequest]:
        """Get requests assigned to a specific user."""
        stmt = (
            select(EscalationRequest)
            .where(EscalationRequest.assigned_to == assignee_id)
            .order_by(EscalationRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
