"""Client for interacting with Meeting Service Calendar API."""

from typing import Any

import httpx
from google_auth_oauthlib.flow import Flow
from loguru import logger

from telegram_bot.config import settings


class CalendarClient:
    """Client for Meeting Service Calendar API."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize calendar client with meeting service URL."""
        self.base_url = base_url or settings.MEETING_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT
        )

    async def check_connection_status(
        self, user_id: int, auth_token: str
    ) -> dict[str, Any]:
        """Check if user has connected Google Calendar."""
        logger.debug("Checking calendar connection status (user_id={})", user_id)
        try:
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/calendar/status/{user_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            response.raise_for_status()
            logger.debug("Calendar status checked (user_id={}, connected=True)", user_id)
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.warning("Calendar status check failed (user_id={}, status={})", user_id, e.response.status_code)
            return {"connected": False, "error": f"HTTP {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.exception("Calendar service request failed (user_id={})", user_id)
            return {"connected": False, "error": str(e)}

    async def get_connect_url(self, user_id: int, state: str) -> str:
        """Get Google Calendar connection URL."""
        logger.debug("Generating Google Calendar connect URL (user_id={})", user_id)
        # Format state as user_id:random_state for CSRF protection
        formatted_state = f"{user_id}:{state}"

        # Create OAuth flow using google_auth_oauthlib
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=settings.GOOGLE_CALENDAR_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )

        # Generate authorization URL with state for CSRF protection
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=formatted_state,
        )

        logger.debug("Google Calendar connect URL generated (user_id={})", user_id)
        return authorization_url

    async def disconnect_calendar(
        self, user_id: int, auth_token: str
    ) -> dict[str, Any]:
        """Disconnect Google Calendar account."""
        logger.info("Disconnecting Google Calendar (user_id={})", user_id)
        try:
            response = await self.client.delete(
                f"{settings.API_V1_PREFIX}/calendar/{user_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            response.raise_for_status()
            logger.info("Google Calendar disconnected (user_id={})", user_id)
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.warning("Calendar disconnect failed (user_id={}, status={})", user_id, e.response.status_code)
            return {"success": False, "error": f"HTTP {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.exception("Calendar disconnect request failed (user_id={})", user_id)
            return {"success": False, "error": str(e)}
