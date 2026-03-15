"""Google Calendar service for OAuth2 and event management."""

import logging
from datetime import UTC, datetime
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from meeting_service.config import settings
from meeting_service.core import NotFoundException, ValidationException
from meeting_service.models.google_calendar_account import GoogleCalendarAccount
from meeting_service.repositories.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service for managing Google Calendar integration."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def get_credentials(self, user_id: int) -> GoogleCalendarAccount | None:
        """Get stored credentials for a user."""
        return await self._uow.google_calendar_accounts.get_by_user_id(user_id)

    async def save_credentials(
        self, user_id: int, access_token: str, refresh_token: str, expiry: datetime
    ) -> GoogleCalendarAccount:
        """Save or update user credentials."""
        existing = await self.get_credentials(user_id)
        if existing:
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.token_expiry = expiry
            existing.updated_at = datetime.now(UTC)
            return await self._uow.google_calendar_accounts.update(existing)
        account = GoogleCalendarAccount(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=expiry,
            calendar_id="primary",
            sync_enabled=True,
        )
        return await self._uow.google_calendar_accounts.create(account)

    def _build_credentials(self, token_data: GoogleCalendarAccount) -> Credentials:
        """Build Google Credentials object from stored token data."""
        return Credentials(
            token=token_data.access_token,
            refresh_token=token_data.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=settings.GOOGLE_CALENDAR_SCOPES,
        )

    async def refresh_credentials(self, user_id: int) -> GoogleCalendarAccount:
        """Refresh expired access token."""
        account = await self.get_credentials(user_id)
        if not account:
            msg = "Google Calendar account not found"
            raise NotFoundException(msg)

        creds = self._build_credentials(account)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update stored credentials
                account.access_token = creds.token
                account.token_expiry = creds.expiry
                account.updated_at = datetime.now(UTC)
                return await self._uow.google_calendar_accounts.update(account)
            msg = "Invalid or expired credentials without refresh token"
            raise ValidationException(msg)
        return account

    async def create_event(self, user_id: int, event_data: dict[str, Any]) -> dict[str, Any]:
        """Create a Google Calendar event for a user meeting."""
        account = await self.refresh_credentials(user_id)
        creds = self._build_credentials(account)

        try:
            service = build("calendar", "v3", credentials=creds)
            return (
                service.events()
                .insert(calendarId=account.calendar_id, body=event_data, sendNotifications=True)
                .execute()
            )
        except HttpError as error:
            logger.exception(f"Google Calendar API error: {error}")
            msg = f"Failed to create calendar event: {error}"
            raise ValidationException(msg)

    async def update_event(self, user_id: int, event_id: str, event_data: dict[str, Any]) -> dict[str, Any]:
        """Update a Google Calendar event."""
        account = await self.refresh_credentials(user_id)
        creds = self._build_credentials(account)

        try:
            service = build("calendar", "v3", credentials=creds)
            return (
                service.events()
                .update(calendarId=account.calendar_id, eventId=event_id, body=event_data, sendNotifications=True)
                .execute()
            )
        except HttpError as error:
            logger.exception(f"Google Calendar API error: {error}")
            msg = f"Failed to update calendar event: {error}"
            raise ValidationException(msg)

    async def delete_event(self, user_id: int, event_id: str) -> None:
        """Delete a Google Calendar event."""
        account = await self.refresh_credentials(user_id)
        creds = self._build_credentials(account)

        try:
            service = build("calendar", "v3", credentials=creds)
            service.events().delete(calendarId=account.calendar_id, eventId=event_id).execute()
        except HttpError as error:
            logger.exception(f"Google Calendar API error: {error}")
            msg = f"Failed to delete calendar event: {error}"
            raise ValidationException(msg)
