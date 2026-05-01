"""Dialogue scenario management service."""

from knowledge_service.core import NotFoundException
from knowledge_service.models import DialogueScenario, DialogueStep
from knowledge_service.repositories import IUnitOfWork
from knowledge_service.schemas import (
    DialogueScenarioCreate,
    DialogueScenarioUpdate,
    DialogueStepCreate,
    DialogueStepUpdate,
)


class DialogueService:
    """Service for dialogue scenario management operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize dialogue service with Unit of Work."""
        self._uow = uow

    async def create_scenario(self, scenario_data: DialogueScenarioCreate) -> DialogueScenario:
        """Create new dialogue scenario with steps."""
        scenario = DialogueScenario(
            title=scenario_data.title,
            description=scenario_data.description,
            keywords=scenario_data.keywords,
            category=scenario_data.category,
            is_active=scenario_data.is_active,
            display_order=scenario_data.display_order,
        )

        created = await self._uow.dialogue_scenarios.create(scenario)

        if scenario_data.steps:
            for step_data in scenario_data.steps:
                step = DialogueStep(
                    scenario_id=created.id,
                    step_number=step_data.step_number,
                    question=step_data.question,
                    answer_type=step_data.answer_type,
                    options=step_data.options,
                    answer_content=step_data.answer_content,
                    next_step_id=step_data.next_step_id,
                    parent_step_id=step_data.parent_step_id,
                    is_final=step_data.is_final,
                )
                await self._uow.dialogue_steps.create(step)

        await self._uow.commit()
        return await self._uow.dialogue_scenarios.get_by_id_with_steps(created.id)

    async def get_scenario_by_id(self, scenario_id: int) -> DialogueScenario:
        """Get scenario by ID with steps."""
        scenario = await self._uow.dialogue_scenarios.get_by_id_with_steps(scenario_id)
        if not scenario:
            msg = "Dialogue scenario"
            raise NotFoundException(msg)
        return scenario

    async def get_active_scenarios(self, skip: int = 0, limit: int = 100) -> tuple[list[DialogueScenario], int]:
        """Get active scenarios."""
        return await self._uow.dialogue_scenarios.get_active_scenarios(skip=skip, limit=limit)

    async def get_scenarios_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[DialogueScenario], int]:
        """Get scenarios by category."""
        return await self._uow.dialogue_scenarios.get_by_category(category, skip=skip, limit=limit)

    async def find_scenarios(
        self,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[DialogueScenario], int]:
        """Find scenarios with filters."""
        return await self._uow.dialogue_scenarios.find_scenarios(
            skip=skip,
            limit=limit,
            category=category,
            is_active=is_active,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def update_scenario(self, scenario_id: int, scenario_data: DialogueScenarioUpdate) -> DialogueScenario:
        """Update dialogue scenario."""
        scenario = await self._uow.dialogue_scenarios.get_by_id(scenario_id)
        if not scenario:
            msg = "Dialogue scenario"
            raise NotFoundException(msg)

        if scenario_data.title is not None:
            scenario.title = scenario_data.title
        if scenario_data.description is not None:
            scenario.description = scenario_data.description
        if scenario_data.keywords is not None:
            scenario.keywords = scenario_data.keywords
        if scenario_data.category is not None:
            scenario.category = scenario_data.category
        if scenario_data.is_active is not None:
            scenario.is_active = scenario_data.is_active
        if scenario_data.display_order is not None:
            scenario.display_order = scenario_data.display_order

        await self._uow.dialogue_scenarios.update(scenario)
        await self._uow.commit()
        return await self._uow.dialogue_scenarios.get_by_id_with_steps(scenario_id)

    async def delete_scenario(self, scenario_id: int) -> bool:
        """Delete dialogue scenario."""
        scenario = await self._uow.dialogue_scenarios.get_by_id(scenario_id)
        if not scenario:
            msg = "Dialogue scenario"
            raise NotFoundException(msg)
        result = await self._uow.dialogue_scenarios.delete(scenario_id)
        await self._uow.commit()
        return result

    async def add_step(self, scenario_id: int, step_data: DialogueStepCreate) -> DialogueStep:
        """Add a step to a scenario."""
        scenario = await self._uow.dialogue_scenarios.get_by_id(scenario_id)
        if not scenario:
            msg = "Dialogue scenario"
            raise NotFoundException(msg)

        step = DialogueStep(
            scenario_id=scenario_id,
            step_number=step_data.step_number,
            question=step_data.question,
            answer_type=step_data.answer_type,
            options=step_data.options,
            answer_content=step_data.answer_content,
            next_step_id=step_data.next_step_id,
            parent_step_id=step_data.parent_step_id,
            is_final=step_data.is_final,
        )
        created = await self._uow.dialogue_steps.create(step)
        await self._uow.commit()
        return created

    async def update_step(self, step_id: int, step_data: DialogueStepUpdate) -> DialogueStep:
        """Update a dialogue step."""
        step = await self._uow.dialogue_steps.get_by_id(step_id)
        if not step:
            msg = "Dialogue step"
            raise NotFoundException(msg)

        if step_data.step_number is not None:
            step.step_number = step_data.step_number
        if step_data.question is not None:
            step.question = step_data.question
        if step_data.answer_type is not None:
            step.answer_type = step_data.answer_type
        if step_data.options is not None:
            step.options = step_data.options
        if step_data.answer_content is not None:
            step.answer_content = step_data.answer_content
        if step_data.next_step_id is not None:
            step.next_step_id = step_data.next_step_id
        if step_data.parent_step_id is not None:
            step.parent_step_id = step_data.parent_step_id
        if step_data.is_final is not None:
            step.is_final = step_data.is_final

        await self._uow.dialogue_steps.update(step)
        await self._uow.commit()
        return step

    async def delete_step(self, step_id: int) -> bool:
        """Delete a dialogue step."""
        step = await self._uow.dialogue_steps.get_by_id(step_id)
        if not step:
            msg = "Dialogue step"
            raise NotFoundException(msg)
        result = await self._uow.dialogue_steps.delete(step_id)
        await self._uow.commit()
        return result

    async def reorder_steps(self, scenario_id: int, step_ids: list[int]) -> None:
        """Reorder steps in a scenario."""
        await self._uow.dialogue_steps.reorder_steps(scenario_id, step_ids)
        await self._uow.commit()

    async def get_first_step(self, scenario_id: int) -> DialogueStep | None:
        """Get the first step of a scenario."""
        return await self._uow.dialogue_steps.get_first_step(scenario_id)
