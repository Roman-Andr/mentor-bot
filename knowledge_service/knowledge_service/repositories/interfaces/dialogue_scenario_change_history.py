"""Dialogue scenario change history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from knowledge_service.models import DialogueScenarioChangeHistory
from knowledge_service.repositories.interfaces.base import BaseRepository


class IDialogueScenarioChangeHistoryRepository(BaseRepository["DialogueScenarioChangeHistory", int]):
    """Dialogue scenario change history repository interface."""

    @abstractmethod
    async def create(self, entity: DialogueScenarioChangeHistory) -> DialogueScenarioChangeHistory:
        """Create dialogue scenario change history entry."""

    @abstractmethod
    async def get_by_scenario_id(
        self,
        scenario_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[DialogueScenarioChangeHistory]:
        """Get dialogue scenario change history for a scenario with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[DialogueScenarioChangeHistory], int]:
        """Get all dialogue scenario change history with filtering and pagination."""
