"""Unit tests for audit API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from meeting_service.api.endpoints.audit import (
    AuditResponse,
    MeetingParticipantEntry,
    MeetingStatusChangeEntry,
    get_meeting_participant_history,
    get_meeting_status_change_history,
    require_hr_or_admin,
)
from meeting_service.core import PermissionDenied, UserRole


class TestRequireHrOrAdmin:
    """Tests for require_hr_or_admin function."""

    def test_require_hr_or_admin_with_hr_role(self):
        """Test that HR role passes the check."""
        mock_user = MagicMock()
        mock_user.role = UserRole.HR

        # Act & Assert - should not raise
        require_hr_or_admin(mock_user)

    def test_require_hr_or_admin_with_admin_role(self):
        """Test that Admin role passes the check."""
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN

        # Act & Assert - should not raise
        require_hr_or_admin(mock_user)

    def test_require_hr_or_admin_with_employee_role_raises(self):
        """Test that Employee role raises PermissionDenied."""
        mock_user = MagicMock()
        mock_user.role = UserRole.EMPLOYEE

        # Act & Assert
        with pytest.raises(PermissionDenied, match="Access denied: HR or Admin role required"):
            require_hr_or_admin(mock_user)


class TestGetMeetingStatusChangeHistory:
    """Tests for get_meeting_status_change_history endpoint function."""

    @pytest.mark.asyncio
    async def test_get_history_with_meeting_id(self):
        """Test getting history by meeting_id."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.HR

        mock_uow = MagicMock()
        mock_uow.meeting_status_change_history = MagicMock()
        mock_uow.meeting_status_change_history.get_by_meeting_id = AsyncMock()

        history_entry = MagicMock()
        history_entry.id = 1
        history_entry.meeting_id = 5
        history_entry.user_id = 100
        history_entry.action = "status_changed"
        history_entry.old_status = "SCHEDULED"
        history_entry.new_status = "COMPLETED"
        history_entry.changed_at = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        history_entry.changed_by = 100
        history_entry.meta_data = None

        mock_uow.meeting_status_change_history.get_by_meeting_id.return_value = [history_entry]

        # Act
        result = await get_meeting_status_change_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=5,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 1
        assert len(result.items) == 1
        assert isinstance(result.items[0], MeetingStatusChangeEntry)
        assert result.items[0].meeting_id == 5
        mock_uow.meeting_status_change_history.get_by_meeting_id.assert_called_once_with(
            meeting_id=5, from_date=None, to_date=None
        )

    @pytest.mark.asyncio
    async def test_get_history_without_meeting_id(self):
        """Test getting all history without meeting_id."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN

        mock_uow = MagicMock()
        mock_uow.meeting_status_change_history = MagicMock()
        mock_uow.meeting_status_change_history.get_all = AsyncMock()

        history_entry = MagicMock()
        history_entry.id = 1
        history_entry.meeting_id = 5
        history_entry.user_id = 100
        history_entry.action = "status_changed"
        history_entry.old_status = "SCHEDULED"
        history_entry.new_status = "COMPLETED"
        history_entry.changed_at = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        history_entry.changed_by = 100
        history_entry.meta_data = None

        mock_uow.meeting_status_change_history.get_all.return_value = ([history_entry], 1)

        # Act
        result = await get_meeting_status_change_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 1
        assert len(result.items) == 1
        mock_uow.meeting_status_change_history.get_all.assert_called_once_with(
            from_date=None, to_date=None, limit=50, offset=0
        )

    @pytest.mark.asyncio
    async def test_get_history_with_date_filters(self):
        """Test getting history with date filters."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.HR

        mock_uow = MagicMock()
        mock_uow.meeting_status_change_history = MagicMock()
        mock_uow.meeting_status_change_history.get_all = AsyncMock()
        mock_uow.meeting_status_change_history.get_all.return_value = ([], 0)

        from_date = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, 23, 59, tzinfo=UTC)

        # Act
        result = await get_meeting_status_change_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=None,
            from_date=from_date,
            to_date=to_date,
            limit=50,
            offset=0,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 0
        assert len(result.items) == 0
        mock_uow.meeting_status_change_history.get_all.assert_called_once_with(
            from_date=from_date, to_date=to_date, limit=50, offset=0
        )

    @pytest.mark.asyncio
    async def test_get_history_with_pagination(self):
        """Test getting history with pagination."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.HR

        mock_uow = MagicMock()
        mock_uow.meeting_status_change_history = MagicMock()
        mock_uow.meeting_status_change_history.get_all = AsyncMock()
        mock_uow.meeting_status_change_history.get_all.return_value = ([], 50)

        # Act
        result = await get_meeting_status_change_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=None,
            from_date=None,
            to_date=None,
            limit=5,
            offset=10,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 50
        assert len(result.items) == 0
        mock_uow.meeting_status_change_history.get_all.assert_called_once_with(
            from_date=None, to_date=None, limit=5, offset=10
        )

    @pytest.mark.asyncio
    async def test_get_history_employee_role_forbidden(self):
        """Test that Employee role raises PermissionDenied."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.EMPLOYEE

        mock_uow = MagicMock()

        # Act & Assert
        with pytest.raises(PermissionDenied, match="Access denied: HR or Admin role required"):
            await get_meeting_status_change_history(
                current_user=mock_user,
                uow=mock_uow,
                meeting_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )


class TestGetMeetingParticipantHistory:
    """Tests for get_meeting_participant_history endpoint function."""

    @pytest.mark.asyncio
    async def test_get_participant_history_with_meeting_id(self):
        """Test getting participant history by meeting_id."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.HR

        mock_uow = MagicMock()
        mock_uow.meeting_participant_history = MagicMock()
        mock_uow.meeting_participant_history.get_by_meeting_id = AsyncMock()

        history_entry = MagicMock()
        history_entry.id = 1
        history_entry.meeting_id = 5
        history_entry.user_id = 100
        history_entry.action = "joined"
        history_entry.joined_at = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        history_entry.left_at = None
        history_entry.meta_data = None

        mock_uow.meeting_participant_history.get_by_meeting_id.return_value = [history_entry]

        # Act
        result = await get_meeting_participant_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=5,
            user_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 1
        assert len(result.items) == 1
        assert isinstance(result.items[0], MeetingParticipantEntry)
        assert result.items[0].meeting_id == 5
        mock_uow.meeting_participant_history.get_by_meeting_id.assert_called_once_with(
            meeting_id=5, from_date=None, to_date=None
        )

    @pytest.mark.asyncio
    async def test_get_participant_history_with_user_id(self):
        """Test getting participant history by user_id."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN

        mock_uow = MagicMock()
        mock_uow.meeting_participant_history = MagicMock()
        mock_uow.meeting_participant_history.get_by_user_id = AsyncMock()

        history_entry = MagicMock()
        history_entry.id = 1
        history_entry.meeting_id = 5
        history_entry.user_id = 100
        history_entry.action = "joined"
        history_entry.joined_at = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        history_entry.left_at = None
        history_entry.meta_data = None

        mock_uow.meeting_participant_history.get_by_user_id.return_value = [history_entry]

        # Act
        result = await get_meeting_participant_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=None,
            user_id=100,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 1
        assert len(result.items) == 1
        mock_uow.meeting_participant_history.get_by_user_id.assert_called_once_with(
            user_id=100, from_date=None, to_date=None
        )

    @pytest.mark.asyncio
    async def test_get_participant_history_without_filters(self):
        """Test getting all participant history without filters."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.HR

        mock_uow = MagicMock()
        mock_uow.meeting_participant_history = MagicMock()
        mock_uow.meeting_participant_history.get_all = AsyncMock()

        history_entry = MagicMock()
        history_entry.id = 1
        history_entry.meeting_id = 5
        history_entry.user_id = 100
        history_entry.action = "joined"
        history_entry.joined_at = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        history_entry.left_at = None
        history_entry.meta_data = None

        mock_uow.meeting_participant_history.get_all.return_value = ([history_entry], 1)

        # Act
        result = await get_meeting_participant_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=None,
            user_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 1
        assert len(result.items) == 1
        mock_uow.meeting_participant_history.get_all.assert_called_once_with(
            from_date=None, to_date=None, limit=50, offset=0
        )

    @pytest.mark.asyncio
    async def test_get_participant_history_with_date_filters(self):
        """Test getting participant history with date filters."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.HR

        mock_uow = MagicMock()
        mock_uow.meeting_participant_history = MagicMock()
        mock_uow.meeting_participant_history.get_all = AsyncMock()
        mock_uow.meeting_participant_history.get_all.return_value = ([], 0)

        from_date = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, 23, 59, tzinfo=UTC)

        # Act
        result = await get_meeting_participant_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=None,
            user_id=None,
            from_date=from_date,
            to_date=to_date,
            limit=50,
            offset=0,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 0
        assert len(result.items) == 0
        mock_uow.meeting_participant_history.get_all.assert_called_once_with(
            from_date=from_date, to_date=to_date, limit=50, offset=0
        )

    @pytest.mark.asyncio
    async def test_get_participant_history_with_pagination(self):
        """Test getting participant history with pagination."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.HR

        mock_uow = MagicMock()
        mock_uow.meeting_participant_history = MagicMock()
        mock_uow.meeting_participant_history.get_all = AsyncMock()
        mock_uow.meeting_participant_history.get_all.return_value = ([], 50)

        # Act
        result = await get_meeting_participant_history(
            current_user=mock_user,
            uow=mock_uow,
            meeting_id=None,
            user_id=None,
            from_date=None,
            to_date=None,
            limit=5,
            offset=10,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 50
        assert len(result.items) == 0
        mock_uow.meeting_participant_history.get_all.assert_called_once_with(
            from_date=None, to_date=None, limit=5, offset=10
        )

    @pytest.mark.asyncio
    async def test_get_participant_history_employee_role_forbidden(self):
        """Test that Employee role raises PermissionDenied."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.EMPLOYEE

        mock_uow = MagicMock()

        # Act & Assert
        with pytest.raises(PermissionDenied, match="Access denied: HR or Admin role required"):
            await get_meeting_participant_history(
                current_user=mock_user,
                uow=mock_uow,
                meeting_id=None,
                user_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )
