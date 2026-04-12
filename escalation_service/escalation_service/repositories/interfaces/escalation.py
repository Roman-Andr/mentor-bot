"""Escalation repository interface."""

from abc import abstractmethod
from collections.abc import Sequence

from escalation_service.core.enums import EscalationStatus, EscalationType
from escalation_service.models import EscalationRequest
from escalation_service.repositories.interfaces.base import BaseRepository


class IEscalationRepository(BaseRepository["EscalationRequest", int]):
    """Escalation repository interface with specific queries."""

    @abstractmethod
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
    ) -> tuple[Sequence[EscalationRequest], int]:
        """Find escalation requests with filtering and return results with total count."""

    @abstractmethod
    async def get_user_requests(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[EscalationRequest]:
        """Get requests created by a specific user."""

    @abstractmethod
    async def get_assigned_requests(
        self, assignee_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[EscalationRequest]:
        """Get requests assigned to a specific user."""
