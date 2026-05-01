"""Unit tests for GoogleCalendarService."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from googleapiclient.errors import HttpError  # type: ignore[import-untyped]
from meeting_service.core import NotFoundException, ValidationException
from meeting_service.models.google_calendar_account import GoogleCalendarAccount
from meeting_service.services.google_calendar_service import GoogleCalendarService


class TestGetCredentials:
    """Tests for get_credentials method."""

    async def test_get_credentials_exists(self, mock_uow):
        """Test getting existing credentials."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        expected_account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="token123",
            refresh_token="refresh456",
            token_expiry=datetime.now(UTC) + timedelta(hours=1),
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = expected_account

        # Act
        result = await service.get_credentials(100)

        # Assert
        assert result == expected_account
        assert result.access_token == "token123"
        mock_uow.google_calendar_accounts.get_by_user_id.assert_called_once_with(100)

    async def test_get_credentials_not_found(self, mock_uow):
        """Test getting credentials when none exist."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = None

        # Act
        result = await service.get_credentials(100)

        # Assert
        assert result is None


class TestSaveCredentials:
    """Tests for save_credentials method."""

    async def test_save_new_credentials(self, mock_uow):
        """Test saving new credentials for a user."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = None

        expiry = datetime.now(UTC) + timedelta(hours=1)
        new_account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="new_token",
            refresh_token="new_refresh",
            token_expiry=expiry,
            calendar_id="primary",
        )
        mock_uow.google_calendar_accounts.create.return_value = new_account

        # Act
        result = await service.save_credentials(100, "new_token", "new_refresh", expiry)

        # Assert
        assert result.access_token == "new_token"
        assert result.refresh_token == "new_refresh"
        assert result.user_id == 100
        mock_uow.google_calendar_accounts.create.assert_called_once()

    async def test_update_existing_credentials(self, mock_uow):
        """Test updating existing credentials."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        existing_account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="old_token",
            refresh_token="old_refresh",
            token_expiry=datetime.now(UTC) - timedelta(hours=1),
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = existing_account

        new_expiry = datetime.now(UTC) + timedelta(hours=1)
        updated_account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="updated_token",
            refresh_token="updated_refresh",
            token_expiry=new_expiry,
        )
        mock_uow.google_calendar_accounts.update.return_value = updated_account

        # Act
        result = await service.save_credentials(100, "updated_token", "updated_refresh", new_expiry)

        # Assert
        assert result.access_token == "updated_token"
        assert result.refresh_token == "updated_refresh"
        mock_uow.google_calendar_accounts.update.assert_called_once()


class TestRefreshCredentials:
    """Tests for refresh_credentials method."""

    async def test_refresh_valid_credentials(self, mock_uow):
        """Test refreshing valid (non-expired) credentials."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="valid_token",
            refresh_token="refresh_token",
            token_expiry=datetime.now(UTC) + timedelta(hours=1),
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account

        # Mock credentials to be valid
        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds_class.return_value = mock_creds

            # Act
            result = await service.refresh_credentials(100)

            # Assert
            assert result == account
            # Should not refresh if already valid
            assert not mock_creds.refresh.called

    async def test_refresh_expired_credentials(self, mock_uow):
        """Test refreshing expired credentials."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="expired_token",
            refresh_token="refresh_token",
            token_expiry=datetime.now(UTC) - timedelta(hours=1),
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account
        mock_uow.google_calendar_accounts.update.return_value = account

        # Mock credentials to be expired but refreshable
        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = False
            mock_creds.expired = True
            mock_creds.refresh_token = "refresh_token"
            mock_creds.token = "new_token"
            mock_creds.expiry = datetime.now(UTC) + timedelta(hours=1)
            mock_creds_class.return_value = mock_creds

            with patch("meeting_service.services.google_calendar_service.Request"):
                # Act
                result = await service.refresh_credentials(100)

                # Assert
                assert result == account
                # Update should be called with new token
                mock_uow.google_calendar_accounts.update.assert_called_once()

    async def test_refresh_no_credentials_found(self, mock_uow):
        """Test refreshing when no credentials exist."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            await service.refresh_credentials(100)
        assert "Google Calendar account not found" in str(exc_info.value.detail)

    async def test_refresh_invalid_no_refresh_token(self, mock_uow):
        """Test refreshing when credentials are invalid and no refresh token."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="expired_token",
            refresh_token=None,  # No refresh token
            token_expiry=datetime.now(UTC) - timedelta(hours=1),
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account

        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = False
            mock_creds.expired = True
            mock_creds.refresh_token = None  # No refresh token
            mock_creds_class.return_value = mock_creds

            # Act & Assert
            with pytest.raises(ValidationException) as exc_info:
                await service.refresh_credentials(100)
            assert "Invalid or expired credentials without refresh token" in str(exc_info.value.detail)


class TestCreateEvent:
    """Tests for create_event method."""

    async def test_create_event_success(self, mock_uow):
        """Test creating a calendar event successfully."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="token",
            refresh_token="refresh",
            calendar_id="primary",
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account

        event_data = {
            "summary": "Test Meeting",
            "start": {"dateTime": "2024-01-01T10:00:00Z"},
            "end": {"dateTime": "2024-01-01T11:00:00Z"},
        }
        expected_event = {"id": "event-123", "status": "confirmed"}

        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds_class.return_value = mock_creds

            with patch("meeting_service.services.google_calendar_service.build") as mock_build:
                mock_service = MagicMock()
                mock_events = MagicMock()
                mock_events.insert.return_value.execute.return_value = expected_event
                mock_service.events.return_value = mock_events
                mock_build.return_value = mock_service

                # Act
                result = await service.create_event(100, event_data)

                # Assert
                assert result == expected_event
                mock_events.insert.assert_called_once_with(
                    calendarId="primary",
                    body=event_data,
                    sendNotifications=True,
                )

    async def test_create_event_api_error(self, mock_uow):
        """Test handling API error when creating event."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="token",
            refresh_token="refresh",
            calendar_id="primary",
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account

        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds_class.return_value = mock_creds

            with patch("meeting_service.services.google_calendar_service.build") as mock_build:
                mock_service = MagicMock()
                mock_events = MagicMock()
                mock_events.insert.return_value.execute.side_effect = HttpError(
                    resp=MagicMock(status=403),
                    content=b'{"error": {"message": "Permission denied"}}',
                )
                mock_service.events.return_value = mock_events
                mock_build.return_value = mock_service

                # Act & Assert
                with pytest.raises(ValidationException) as exc_info:
                    await service.create_event(100, {"summary": "Test"})
                assert "Failed to create calendar event" in str(exc_info.value.detail)


class TestUpdateEvent:
    """Tests for update_event method."""

    async def test_update_event_success(self, mock_uow):
        """Test updating a calendar event successfully."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="token",
            refresh_token="refresh",
            calendar_id="primary",
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account

        event_data = {
            "summary": "Updated Meeting",
            "start": {"dateTime": "2024-01-01T12:00:00Z"},
            "end": {"dateTime": "2024-01-01T13:00:00Z"},
        }
        expected_event = {"id": "event-123", "status": "confirmed", "summary": "Updated Meeting"}

        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds_class.return_value = mock_creds

            with patch("meeting_service.services.google_calendar_service.build") as mock_build:
                mock_service = MagicMock()
                mock_events = MagicMock()
                mock_events.update.return_value.execute.return_value = expected_event
                mock_service.events.return_value = mock_events
                mock_build.return_value = mock_service

                # Act
                result = await service.update_event(100, "event-123", event_data)

                # Assert
                assert result == expected_event
                mock_events.update.assert_called_once_with(
                    calendarId="primary",
                    eventId="event-123",
                    body=event_data,
                    sendNotifications=True,
                )

    async def test_update_event_api_error(self, mock_uow):
        """Test handling API error when updating event."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="token",
            refresh_token="refresh",
            calendar_id="primary",
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account

        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds_class.return_value = mock_creds

            with patch("meeting_service.services.google_calendar_service.build") as mock_build:
                mock_service = MagicMock()
                mock_events = MagicMock()
                mock_events.update.return_value.execute.side_effect = HttpError(
                    resp=MagicMock(status=404),
                    content=b'{"error": {"message": "Event not found"}}',
                )
                mock_service.events.return_value = mock_events
                mock_build.return_value = mock_service

                # Act & Assert
                with pytest.raises(ValidationException) as exc_info:
                    await service.update_event(100, "event-123", {"summary": "Test"})
                assert "Failed to update calendar event" in str(exc_info.value.detail)


class TestDeleteEvent:
    """Tests for delete_event method."""

    async def test_delete_event_success(self, mock_uow):
        """Test deleting a calendar event successfully."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="token",
            refresh_token="refresh",
            calendar_id="primary",
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account

        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds_class.return_value = mock_creds

            with patch("meeting_service.services.google_calendar_service.build") as mock_build:
                mock_service = MagicMock()
                mock_events = MagicMock()
                mock_events.delete.return_value.execute.return_value = None
                mock_service.events.return_value = mock_events
                mock_build.return_value = mock_service

                # Act - should not raise
                await service.delete_event(100, "event-123")

                # Assert
                mock_events.delete.assert_called_once_with(
                    calendarId="primary",
                    eventId="event-123",
                )

    async def test_delete_event_api_error(self, mock_uow):
        """Test handling API error when deleting event."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="token",
            refresh_token="refresh",
            calendar_id="primary",
        )
        mock_uow.google_calendar_accounts.get_by_user_id.return_value = account

        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds_class.return_value = mock_creds

            with patch("meeting_service.services.google_calendar_service.build") as mock_build:
                mock_service = MagicMock()
                mock_events = MagicMock()
                mock_events.delete.return_value.execute.side_effect = HttpError(
                    resp=MagicMock(status=410),
                    content=b'{"error": {"message": "Resource has been deleted"}}',
                )
                mock_service.events.return_value = mock_events
                mock_build.return_value = mock_service

                # Act & Assert
                with pytest.raises(ValidationException) as exc_info:
                    await service.delete_event(100, "event-123")
                assert "Failed to delete calendar event" in str(exc_info.value.detail)


class TestBuildCredentials:
    """Tests for _build_credentials helper method."""

    async def test_build_credentials_with_all_fields(self, mock_uow):
        """Test building credentials from stored account data."""
        # Arrange
        service = GoogleCalendarService(mock_uow)
        account = GoogleCalendarAccount(
            id=1,
            user_id=100,
            access_token="access_token_123",
            refresh_token="refresh_token_456",
            token_expiry=datetime.now(UTC) + timedelta(hours=1),
            calendar_id="primary",
        )

        with patch("meeting_service.services.google_calendar_service.Credentials") as mock_creds_class:
            mock_creds = MagicMock()
            mock_creds_class.return_value = mock_creds

            with patch("meeting_service.services.google_calendar_service.settings") as mock_settings:
                mock_settings.GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
                mock_settings.GOOGLE_CLIENT_ID = "client_id"
                mock_settings.GOOGLE_CLIENT_SECRET = "client_secret"
                mock_settings.GOOGLE_CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]

                # Act
                service._build_credentials(account)

                # Assert
                mock_creds_class.assert_called_once_with(
                    token="access_token_123",
                    refresh_token="refresh_token_456",
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id="client_id",
                    client_secret="client_secret",
                    scopes=["https://www.googleapis.com/auth/calendar"],
                )
