"""Escalation status history repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from escalation_service.models import EscalationStatusHistory
from escalation_service.repositories.interfaces.base import BaseRepository


class IEscalationStatusHistoryRepository(BaseRepository["EscalationStatusHistory", int]):
    """Escalation status history repository interface."""

    @abstractmethod
    async def create(self, entity: EscalationStatusHistory) -> EscalationStatusHistory:
        """Create escalation status history entry."""

    @abstractmethod
    async def get_by_escalation_id(
        self,
        escalation_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[EscalationStatusHistory]:
        """Get escalation status history for an escalation with optional date filtering."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Sequence[EscalationStatusHistory]:
        """Get escalation status history for a user with optional date filtering."""

    @abstractmethod
    async def get_all(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[EscalationStatusHistory], int]:
        """Get all escalation status history with filtering and pagination."""
