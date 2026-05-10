"""Client for interacting with Meeting Service Calendar API."""

from typing import Any

import httpx
from loguru import logger

from telegram_bot.config import settings


class CalendarClient:
    """Client for Meeting Service Calendar API."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize calendar client with meeting service URL."""
        self.base_url = base_url or settings.MEETING_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=settings.SERVICE_TIMEOUT)

    async def check_connection_status(self, user_id: int, auth_token: str) -> dict[str, Any]:
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
        """Get Google Calendar connection URL by calling Meeting Service."""
        logger.debug("Getting Google Calendar connect URL from Meeting Service (user_id={})", user_id)
        # Format state as user_id:random_state for CSRF protection
        formatted_state = f"{user_id}:{state}"

        try:
            # Call Meeting Service /connect endpoint to generate OAuth URL
            # Meeting Service will handle PKCE and store code_verifier in its Redis DB
            response = await self.client.get(
                f"{settings.API_V1_PREFIX}/calendar/connect",
                params={"state": formatted_state},
                follow_redirects=False,
            )

            # 307 Temporary Redirect is expected - extract authorization URL from location header
            if response.status_code == 307:
                authorization_url = response.headers.get("location")
                if not authorization_url:
                    logger.error("Meeting Service returned 307 without location header (user_id={})", user_id)
                    raise ValueError("Failed to get authorization URL from Meeting Service")
                logger.debug("Google Calendar connect URL retrieved (user_id={})", user_id)
                return authorization_url

            # If not a redirect, check for other errors
            if response.status_code >= 400:
                raise httpx.HTTPStatusError(
                    f"Meeting Service returned error status {response.status_code}",
                    request=response.request,
                    response=response,
                )

        except httpx.HTTPStatusError as e:
            logger.warning(
                "Meeting Service connect request failed (user_id={}, status={})", user_id, e.response.status_code
            )
            raise
        except httpx.RequestError:
            logger.exception("Meeting Service request failed (user_id={})", user_id)
            raise

    async def disconnect_calendar(self, user_id: int, auth_token: str) -> dict[str, Any]:
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
