"""Dialogue scenario repository interface."""

from abc import abstractmethod
from collections.abc import Sequence

from knowledge_service.models import DialogueScenario, DialogueStep
from knowledge_service.repositories.interfaces.base import BaseRepository


class IDialogueScenarioRepository(BaseRepository[DialogueScenario, int]):
    """Dialogue scenario repository interface."""

    @abstractmethod
    async def get_by_id_with_steps(self, scenario_id: int) -> DialogueScenario | None:
        """Get scenario by ID with eager-loaded steps."""

    @abstractmethod
    async def get_active_scenarios(self, *, skip: int = 0, limit: int = 100) -> tuple[Sequence[DialogueScenario], int]:
        """Get active scenarios ordered by display_order."""

    @abstractmethod
    async def get_by_category(
        self, category: str, *, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[DialogueScenario], int]:
        """Get scenarios by category."""

    @abstractmethod
    async def find_scenarios(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[Sequence[DialogueScenario], int]:
        """Find scenarios with filtering, return results + total count."""


class IDialogueStepRepository(BaseRepository[DialogueStep, int]):
    """Dialogue step repository interface."""

    @abstractmethod
    async def get_by_scenario_id(self, scenario_id: int) -> Sequence[DialogueStep]:
        """Get all steps for a scenario ordered by step_number."""

    @abstractmethod
    async def get_first_step(self, scenario_id: int) -> DialogueStep | None:
        """Get the first step (step_number=1) for a scenario."""

    @abstractmethod
    async def reorder_steps(self, scenario_id: int, step_ids: list[int]) -> None:
        """Reorder steps by updating step_numbers according to provided order."""
