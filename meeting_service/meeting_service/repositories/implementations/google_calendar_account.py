"""SQLAlchemy implementation for Google Calendar account repository."""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models.google_calendar_account import GoogleCalendarAccount
from meeting_service.repositories.interfaces.google_calendar_account import IGoogleCalendarAccountRepository


class SQLAlchemyGoogleCalendarAccountRepository(IGoogleCalendarAccountRepository):
    """SQLAlchemy implementation of IGoogleCalendarAccountRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def get_by_user_id(self, user_id: int) -> GoogleCalendarAccount | None:
        """Get account by user ID."""
        stmt = select(GoogleCalendarAccount).where(GoogleCalendarAccount.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, account: GoogleCalendarAccount) -> GoogleCalendarAccount:
        """Create a new account."""
        self._session.add(account)
        await self._session.commit()
        await self._session.refresh(account)
        return account

    async def update(self, account: GoogleCalendarAccount) -> GoogleCalendarAccount:
        """Update an existing account."""
        await self._session.commit()
        await self._session.refresh(account)
        return account

    async def delete(self, user_id: int) -> None:
        """Delete account by user ID."""
        account = await self.get_by_user_id(user_id)
        if account:
            await self._session.delete(account)
            await self._session.commit()
