"""Interface for Google Calendar account repository."""

from abc import ABC, abstractmethod

from meeting_service.models.google_calendar_account import GoogleCalendarAccount


class IGoogleCalendarAccountRepository(ABC):
    """Interface for Google Calendar account repository."""

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> GoogleCalendarAccount | None:
        """Get account by user ID."""

    @abstractmethod
    async def create(self, account: GoogleCalendarAccount) -> GoogleCalendarAccount:
        """Create a new account."""

    @abstractmethod
    async def update(self, account: GoogleCalendarAccount) -> GoogleCalendarAccount:
        """Update an existing account."""

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        """Delete account by user ID."""
