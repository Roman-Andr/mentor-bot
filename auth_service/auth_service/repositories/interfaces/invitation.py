"""Invitation repository interface."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from auth_service.core import InvitationStatus
from auth_service.repositories.interfaces.base import BaseRepository
from auth_service.schemas.invitation import InvitationStats

if TYPE_CHECKING:
    from auth_service.models import Invitation


class IInvitationRepository(BaseRepository["Invitation", int]):
    """Invitation repository interface with invitation-specific queries."""

    @abstractmethod
    async def get_by_token(self, token: str) -> "Invitation" | None:
        """Get invitation by token."""

    @abstractmethod
    async def get_valid_by_token(self, token: str) -> "Invitation" | None:
        """Get valid (pending and not expired) invitation by token."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Sequence["Invitation"]:
        """Get all invitations for email address."""

    @abstractmethod
    async def find_invitations(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        email: str | None = None,
        status: InvitationStatus | None = None,
        department: str | None = None,
        expired_only: bool = False,
    ) -> tuple[Sequence["Invitation"], int]:
        """Find invitations with filtering and return results with total count."""

    @abstractmethod
    async def mark_as_used(self, invitation_id: int, user_id: int) -> "Invitation":
        """Mark invitation as used and link to user."""

    @abstractmethod
    async def update_status(self, invitation_id: int, status: InvitationStatus) -> "Invitation":
        """Update invitation status."""

    @abstractmethod
    async def get_statistics(self) -> InvitationStats:
        """Get invitation statistics."""

    @abstractmethod
    async def exists_pending_for_email(self, email: str) -> bool:
        """Check if pending invitation exists for email."""
