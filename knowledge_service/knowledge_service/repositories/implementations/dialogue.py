"""SQLAlchemy implementation of Dialogue repository."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import Column, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from knowledge_service.models import DialogueScenario, DialogueStep
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.dialogue import IDialogueScenarioRepository, IDialogueStepRepository


class DialogueScenarioRepository(SqlAlchemyBaseRepository[DialogueScenario, int], IDialogueScenarioRepository):
    """SQLAlchemy implementation of DialogueScenario repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize dialogue scenario repository."""
        super().__init__(session, DialogueScenario)

    async def create(self, entity: DialogueScenario) -> DialogueScenario:
        """Create scenario with eager-loaded steps."""
        self._session.add(entity)
        await self._session.flush()
        stmt = (
            select(DialogueScenario)
            .where(DialogueScenario.id == entity.id)
            .options(selectinload(DialogueScenario.steps))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update(self, entity: DialogueScenario) -> DialogueScenario:
        """Update scenario with eager-loaded steps."""
        await self._session.flush()
        stmt = (
            select(DialogueScenario)
            .where(DialogueScenario.id == entity.id)
            .options(selectinload(DialogueScenario.steps))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_by_id_with_steps(self, scenario_id: int) -> DialogueScenario | None:
        """Get scenario by ID with eager-loaded steps."""
        stmt = (
            select(DialogueScenario)
            .where(DialogueScenario.id == scenario_id)
            .options(selectinload(DialogueScenario.steps))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_scenarios(self, *, skip: int = 0, limit: int = 100) -> tuple[Sequence[DialogueScenario], int]:
        """Get active scenarios ordered by display_order."""
        stmt = (
            select(DialogueScenario)
            .where(DialogueScenario.is_active)
            .order_by(DialogueScenario.display_order)
            .options(selectinload(DialogueScenario.steps))
        )
        count_stmt = select(func.count(DialogueScenario.id)).where(DialogueScenario.is_active)

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def get_by_category(
        self, category: str, *, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[DialogueScenario], int]:
        """Get scenarios by category."""
        stmt = (
            select(DialogueScenario)
            .where(DialogueScenario.category == category)
            .order_by(DialogueScenario.display_order)
            .options(selectinload(DialogueScenario.steps))
        )
        count_stmt = select(func.count(DialogueScenario.id)).where(DialogueScenario.category == category)

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    def _get_sort_column(self, sort_by: str | None) -> Column:
        """Get SQLAlchemy column for sorting."""
        column_map = {
            "title": DialogueScenario.title,
            "category": DialogueScenario.category,
            "isActive": DialogueScenario.is_active,
            "displayOrder": DialogueScenario.display_order,
            "createdAt": DialogueScenario.created_at,
            "updatedAt": DialogueScenario.updated_at,
        }
        return column_map.get(sort_by, DialogueScenario.display_order)

    async def find_scenarios(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[Sequence[DialogueScenario], int]:
        """Find scenarios with filtering."""
        stmt = select(DialogueScenario).options(selectinload(DialogueScenario.steps))
        count_stmt = select(func.count(DialogueScenario.id))

        if category is not None:
            stmt = stmt.where(DialogueScenario.category == category)
            count_stmt = count_stmt.where(DialogueScenario.category == category)

        if is_active is not None:
            stmt = stmt.where(DialogueScenario.is_active == is_active)
            count_stmt = count_stmt.where(DialogueScenario.is_active == is_active)

        if search and search.strip():
            search_filter = or_(
                DialogueScenario.title.ilike(f"%{search}%"),
                DialogueScenario.description.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = cast("int", (await self._session.execute(count_stmt)).scalar_one())

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)
        stmt = stmt.order_by(sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total


class DialogueStepRepository(SqlAlchemyBaseRepository[DialogueStep, int], IDialogueStepRepository):
    """SQLAlchemy implementation of DialogueStep repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize dialogue step repository."""
        super().__init__(session, DialogueStep)

    async def get_by_scenario_id(self, scenario_id: int) -> Sequence[DialogueStep]:
        """Get all steps for a scenario ordered by step_number."""
        stmt = select(DialogueStep).where(DialogueStep.scenario_id == scenario_id).order_by(DialogueStep.step_number)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_first_step(self, scenario_id: int) -> DialogueStep | None:
        """Get the first step (step_number=1) for a scenario."""
        stmt = select(DialogueStep).where(and_(DialogueStep.scenario_id == scenario_id, DialogueStep.step_number == 1))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def reorder_steps(self, scenario_id: int, step_ids: list[int]) -> None:
        """Reorder steps by updating step_numbers."""
        for idx, step_id in enumerate(step_ids, start=1):
            stmt = select(DialogueStep).where(and_(DialogueStep.id == step_id, DialogueStep.scenario_id == scenario_id))
            result = await self._session.execute(stmt)
            step = result.scalar_one_or_none()
            if step:
                step.step_number = idx
        await self._session.flush()
