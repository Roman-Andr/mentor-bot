"""Interface for Google Calendar account repository."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime

from meeting_service.models.google_calendar_account import GoogleCalendarAccount


class IGoogleCalendarAccountRepository(ABC):
    """Interface for Google Calendar account repository."""

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> GoogleCalendarAccount | None:
        """Get account by user ID."""

    @abstractmethod
    async def get_by_account_email(self, email: str) -> GoogleCalendarAccount | None:
        """Get account by email address."""

    @abstractmethod
    async def get_active_accounts(self, limit: int = 100) -> Sequence[GoogleCalendarAccount]:
        """Get all active accounts with sync enabled."""

    @abstractmethod
    async def create(self, account: GoogleCalendarAccount) -> GoogleCalendarAccount:
        """Create a new account."""

    @abstractmethod
    async def update(self, account: GoogleCalendarAccount) -> GoogleCalendarAccount:
        """Update an existing account."""

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        """Delete account by user ID."""

    @abstractmethod
    async def update_tokens(
        self,
        account: GoogleCalendarAccount,
        *,
        access_token: str,
        refresh_token: str | None = None,
        token_expiry: datetime | None = None,
    ) -> GoogleCalendarAccount:
        """Update OAuth tokens for an account."""

    @abstractmethod
    async def mark_inactive(self, account: GoogleCalendarAccount) -> GoogleCalendarAccount:
        """Mark an account as inactive (disable sync)."""
