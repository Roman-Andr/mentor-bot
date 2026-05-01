"""SQLAlchemy implementation of Dialogue scenario change history repository."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import DialogueScenarioChangeHistory
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.dialogue_scenario_change_history import IDialogueScenarioChangeHistoryRepository


class DialogueScenarioChangeHistoryRepository(
    SqlAlchemyBaseRepository[DialogueScenarioChangeHistory, int], IDialogueScenarioChangeHistoryRepository
):
    """SQLAlchemy implementation of Dialogue scenario change history repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize DialogueScenarioChangeHistoryRepository with database session."""
        super().__init__(session, DialogueScenarioChangeHistory)

    async def create(self, entity: DialogueScenarioChangeHistory) -> DialogueScenarioChangeHistory:
        """Create dialogue scenario change history entry."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def get_by_scenario_id(
        self,
        scenario_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[DialogueScenarioChangeHistory]:
        """Get dialogue scenario change history for a scenario with optional date filtering."""
        stmt = select(DialogueScenarioChangeHistory).where(DialogueScenarioChangeHistory.scenario_id == scenario_id)

        if from_date:
            stmt = stmt.where(DialogueScenarioChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(DialogueScenarioChangeHistory.changed_at <= to_date)

        stmt = stmt.order_by(DialogueScenarioChangeHistory.changed_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[DialogueScenarioChangeHistory], int]:
        """Get all dialogue scenario change history with filtering and pagination."""
        count_stmt = select(func.count(DialogueScenarioChangeHistory.id))
        stmt = select(DialogueScenarioChangeHistory)

        if from_date:
            stmt = stmt.where(DialogueScenarioChangeHistory.changed_at >= from_date)
            count_stmt = count_stmt.where(DialogueScenarioChangeHistory.changed_at >= from_date)
        if to_date:
            stmt = stmt.where(DialogueScenarioChangeHistory.changed_at <= to_date)
            count_stmt = count_stmt.where(DialogueScenarioChangeHistory.changed_at <= to_date)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(DialogueScenarioChangeHistory.changed_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total
