"""SQLAlchemy implementation for Google Calendar account repository."""

from collections.abc import Sequence
from datetime import datetime

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

    async def get_by_account_email(self, email: str) -> GoogleCalendarAccount | None:
        """Get account by email address."""
        # Note: This assumes calendar_id stores the email for primary calendars
        # or we may need to add an account_email field to the model
        stmt = select(GoogleCalendarAccount).where(GoogleCalendarAccount.calendar_id == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_accounts(self, limit: int = 100) -> Sequence[GoogleCalendarAccount]:
        """Get all active accounts with sync enabled."""
        stmt = (
            select(GoogleCalendarAccount)
            .where(GoogleCalendarAccount.sync_enabled == True)  # noqa: E712
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

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

    async def update_tokens(
        self,
        account: GoogleCalendarAccount,
        *,
        access_token: str,
        refresh_token: str | None = None,
        token_expiry: datetime | None = None,
    ) -> GoogleCalendarAccount:
        """Update OAuth tokens for an account."""
        account.access_token = access_token
        if refresh_token is not None:
            account.refresh_token = refresh_token
        if token_expiry is not None:
            account.token_expiry = token_expiry
        await self._session.commit()
        await self._session.refresh(account)
        return account

    async def mark_inactive(self, account: GoogleCalendarAccount) -> GoogleCalendarAccount:
        """Mark an account as inactive (disable sync)."""
        account.sync_enabled = False
        await self._session.commit()
        await self._session.refresh(account)
        return account
