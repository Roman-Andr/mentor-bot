"""Google Calendar integration endpoints."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

from meeting_service.api.deps import DatabaseSession
from meeting_service.config import settings
from meeting_service.core import ValidationException
from meeting_service.database import AsyncSessionLocal
from meeting_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from meeting_service.services.google_calendar_service import GoogleCalendarService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/connect")
async def connect_calendar(
    state: Annotated[str, Query()],
    _db: DatabaseSession,
) -> RedirectResponse:
    """Initiate Google Calendar OAuth2 connection."""
    # Parse state to extract user_id and CSRF token
    if ":" not in state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter format")

    try:
        user_id_str, _csrf_token = state.split(":", 1)
        int(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter format") from None

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google Calendar integration not configured"
        )

    # Create OAuth flow.
    # autogenerate_code_verifier=False disables PKCE: the verifier would only
    # live on this Flow instance and the /callback handler builds a fresh Flow,
    # so Google would reject the token exchange with "Missing code verifier".
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
        autogenerate_code_verifier=False,
    )

    # Generate authorization URL with state for CSRF protection
    authorization_url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,  # Pass the original state for CSRF protection
    )

    return RedirectResponse(url=authorization_url)


@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    _db: DatabaseSession,
) -> dict[str, str]:
    """Handle Google OAuth2 callback."""
    try:
        # Parse state
        if ":" not in state:
            msg = "Invalid state parameter"
            raise ValidationException(msg)

        user_id_str, _auth_state = state.split(":", 1)
        user_id = int(user_id_str)

        # Create OAuth flow
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

        # Exchange authorization code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Save credentials
        async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
            service = GoogleCalendarService(uow)
            expiry = (
                credentials.expiry.replace(tzinfo=UTC) if credentials.expiry else datetime.now(UTC) + timedelta(hours=1)
            )
            await service.save_credentials(
                user_id=user_id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expiry=expiry,
            )

        return {
            "status": "success",
            "message": "Google Calendar account connected successfully",
            "user_id": str(user_id),
        }

    except Exception as e:
        logger.exception("OAuth callback error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to connect Google Calendar: {e!s}"
        ) from e


@router.get("/status/{user_id}")
async def get_calendar_status(
    user_id: int,
    _db: DatabaseSession,
) -> dict[str, bool]:
    """Check if user has connected Google Calendar."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        service = GoogleCalendarService(uow)
        account = await service.get_credentials(user_id)
        return {
            "connected": account is not None,
            "sync_enabled": account.sync_enabled if account else False,
        }


@router.delete("/{user_id}")
async def disconnect_calendar(
    user_id: int,
    _db: DatabaseSession,
) -> dict[str, str]:
    """Disconnect Google Calendar account."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        await uow.google_calendar_accounts.delete(user_id)
        await uow.commit()

    return {
        "status": "success",
        "message": "Google Calendar account disconnected",
    }
