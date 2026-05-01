"""Certificate repository implementation."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any, cast

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from checklists_service.models import Certificate
from checklists_service.repositories.implementations.base import SqlAlchemyBaseRepository


class CertificateRepository(SqlAlchemyBaseRepository[Certificate, int]):
    """SQLAlchemy implementation of Certificate repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize certificate repository."""
        super().__init__(session, Certificate)

    def _select(self) -> Select[tuple[Certificate]]:
        """Helper to create a select statement for the model."""
        return select(self._model_class)

    async def get_by_checklist_id(self, checklist_id: int) -> Certificate | None:
        """Get certificate by checklist ID."""
        stmt = self._select().where(Certificate.checklist_id == checklist_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_checklist_ids(self, checklist_ids: Sequence[int]) -> Sequence[Certificate]:
        """Get certificates by multiple checklist IDs."""
        if not checklist_ids:
            return []
        stmt = self._select().where(Certificate.checklist_id.in_(checklist_ids))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user(self, user_id: int) -> Sequence[Certificate]:
        """Get all certificates for a user."""
        stmt = select(Certificate).where(Certificate.user_id == user_id).order_by(Certificate.issued_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_cert_uid(self, cert_uid: str) -> Certificate | None:
        """Get certificate by public UID."""
        stmt = select(Certificate).where(Certificate.cert_uid == cert_uid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_certificates(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        user_id: int | None = None,
        from_date: Any | None = None,
        to_date: Any | None = None,
    ) -> tuple[Sequence[Certificate], int]:
        """Find certificates with filtering and return results with total count."""
        conditions = []

        if user_id is not None:
            conditions.append(Certificate.user_id == user_id)

        if from_date is not None:
            if isinstance(from_date, str):
                from_date = datetime.fromisoformat(from_date)
            conditions.append(Certificate.issued_at >= from_date)

        if to_date is not None:
            if isinstance(to_date, str):
                to_date = datetime.fromisoformat(to_date)
            conditions.append(Certificate.issued_at <= to_date)

        base_query: Select[tuple[Certificate]] = select(Certificate)
        count_query = select(func.count()).select_from(Certificate)

        if conditions:
            base_query = base_query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        total_result = await self._session.execute(count_query)
        total = cast(int, total_result.scalar())

        # Get paginated results
        query = base_query.order_by(Certificate.issued_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total
