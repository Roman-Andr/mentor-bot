"""Certificate repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Any

from checklists_service.models import Certificate
from checklists_service.repositories.interfaces.base import BaseRepository


class ICertificateRepository(BaseRepository["Certificate", int]):
    """Certificate repository interface with certificate-specific queries."""

    @abstractmethod
    async def get_by_checklist_id(self, checklist_id: int) -> Certificate | None:
        """Get certificate by checklist ID."""

    @abstractmethod
    async def get_by_checklist_ids(self, checklist_ids: Sequence[int]) -> Sequence[Certificate]:
        """Get certificates by multiple checklist IDs."""

    @abstractmethod
    async def get_by_user(self, user_id: int) -> Sequence[Certificate]:
        """Get all certificates for a user."""

    @abstractmethod
    async def get_by_cert_uid(self, cert_uid: str) -> Certificate | None:
        """Get certificate by public UID."""

    @abstractmethod
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
