"""Unit tests for audit endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from escalation_service.api.deps import UserInfo
from escalation_service.api.endpoints.audit import (
    AuditResponse,
    EscalationStatusEntry,
    MentorInterventionEntry,
    get_escalation_status_history,
    get_mentor_intervention_history,
    require_hr_or_admin,
)
from escalation_service.core.enums import UserRole


class TestRequireHrOrAdmin:
    """Tests for require_hr_or_admin function."""

    def test_allows_hr_user(self):
        """Test that HR users are allowed."""
        user = UserInfo({"id": 1, "role": UserRole.HR.value, "is_active": True})
        # Should not raise
        require_hr_or_admin(user)

    def test_allows_admin_user(self):
        """Test that Admin users are allowed."""
        user = UserInfo({"id": 1, "role": UserRole.ADMIN.value, "is_active": True})
        # Should not raise
        require_hr_or_admin(user)

    def test_denies_regular_user(self):
        """Test that regular users are denied."""
        user = UserInfo({"id": 1, "role": UserRole.USER.value, "is_active": True})
        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            require_hr_or_admin(user)

    def test_denies_user_with_no_role(self):
        """Test that users with no role are denied."""
        user = UserInfo({"id": 1, "role": None, "is_active": True})
        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            require_hr_or_admin(user)


class TestGetEscalationStatusHistory:
    """Tests for get_escalation_status_history endpoint."""

    @pytest.fixture
    def mock_uow(self):
        """Create a mock Unit of Work."""
        uow = MagicMock()
        uow.escalation_status_history = MagicMock()
        uow.escalation_status_history.get_by_escalation_id = AsyncMock()
        uow.escalation_status_history.get_by_user_id = AsyncMock()
        uow.escalation_status_history.get_all = AsyncMock()
        return uow

    @pytest.fixture
    def hr_user(self):
        """Create an HR user."""
        return UserInfo({"id": 1, "role": UserRole.HR.value, "is_active": True})

    @pytest.fixture
    def admin_user(self):
        """Create an Admin user."""
        return UserInfo({"id": 1, "role": UserRole.ADMIN.value, "is_active": True})

    @pytest.fixture
    def regular_user(self):
        """Create a regular user."""
        return UserInfo({"id": 1, "role": UserRole.USER.value, "is_active": True})

    @pytest.mark.asyncio
    async def test_get_by_escalation_id_with_hr(self, hr_user, mock_uow):
        """Test getting history by escalation_id with HR user."""
        # Arrange
        mock_entry = {
            "id": 1,
            "escalation_id": 10,
            "user_id": 100,
            "action": "status_change",
            "old_status": "PENDING",
            "new_status": "ASSIGNED",
            "changed_at": datetime.now(tz=UTC),
            "changed_by": 200,
            "metadata": {},
        }
        mock_uow.escalation_status_history.get_by_escalation_id.return_value = [mock_entry]

        # Act
        result = await get_escalation_status_history(
            current_user=hr_user,
            uow=mock_uow,
            escalation_id=10,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert len(result.items) == 1
        assert result.total == 1
        assert isinstance(result.items[0], EscalationStatusEntry)
        mock_uow.escalation_status_history.get_by_escalation_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_escalation_id_with_date_filters(self, hr_user, mock_uow):
        """Test getting history by escalation_id with date filters."""
        # Arrange
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 1, 31, tzinfo=UTC)

        mock_entry = {
            "id": 1,
            "escalation_id": 10,
            "user_id": 100,
            "action": "status_change",
            "old_status": "PENDING",
            "new_status": "ASSIGNED",
            "changed_at": datetime(2024, 1, 15, tzinfo=UTC),
            "changed_by": 200,
            "metadata": {},
        }
        mock_uow.escalation_status_history.get_by_escalation_id.return_value = [mock_entry]

        # Act
        result = await get_escalation_status_history(
            current_user=hr_user,
            uow=mock_uow,
            escalation_id=10,
            from_date=from_date,
            to_date=to_date,
        )

        # Assert
        assert result.total == 1
        assert len(result.items) == 1
        mock_uow.escalation_status_history.get_by_escalation_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, hr_user, mock_uow):
        """Test getting history by user_id."""
        # Arrange
        mock_entry = {
            "id": 2,
            "escalation_id": 10,
            "user_id": 100,
            "action": "status_change",
            "old_status": "ASSIGNED",
            "new_status": "IN_PROGRESS",
            "changed_at": datetime.now(tz=UTC),
            "changed_by": 200,
            "metadata": {},
        }
        mock_uow.escalation_status_history.get_by_user_id.return_value = [mock_entry]

        # Act
        result = await get_escalation_status_history(
            current_user=hr_user,
            uow=mock_uow,
            user_id=100,
            escalation_id=None,
        )

        # Assert
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].user_id == 100
        mock_uow.escalation_status_history.get_by_user_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, hr_user, mock_uow):
        """Test getting all history with pagination."""
        # Arrange
        mock_entries = [
            {
                "id": i,
                "escalation_id": 10,
                "user_id": 100,
                "action": "status_change",
                "old_status": "PENDING",
                "new_status": "ASSIGNED",
                "changed_at": datetime.now(tz=UTC),
                "changed_by": 200,
                "metadata": {},
            }
            for i in range(1, 6)
        ]
        mock_uow.escalation_status_history.get_all.return_value = (mock_entries, 100)

        # Act
        result = await get_escalation_status_history(
            current_user=hr_user,
            uow=mock_uow,
            escalation_id=None,
            user_id=None,
            limit=10,
            offset=5,
        )

        # Assert
        assert result.total == 100
        assert len(result.items) == 5
        mock_uow.escalation_status_history.get_all.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_denies_regular_user(self, regular_user, mock_uow):
        """Test that regular users are denied access."""
        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            await get_escalation_status_history(
                current_user=regular_user,
                uow=mock_uow,
            )


class TestGetMentorInterventionHistory:
    """Tests for get_mentor_intervention_history endpoint."""

    @pytest.fixture
    def mock_uow(self):
        """Create a mock Unit of Work."""
        uow = MagicMock()
        uow.mentor_intervention_history = MagicMock()
        uow.mentor_intervention_history.get_by_escalation_id = AsyncMock()
        uow.mentor_intervention_history.get_by_mentor_id = AsyncMock()
        uow.mentor_intervention_history.get_all = AsyncMock()
        return uow

    @pytest.fixture
    def hr_user(self):
        """Create an HR user."""
        return UserInfo({"id": 1, "role": UserRole.HR.value, "is_active": True})

    @pytest.fixture
    def regular_user(self):
        """Create a regular user."""
        return UserInfo({"id": 1, "role": UserRole.USER.value, "is_active": True})

    @pytest.mark.asyncio
    async def test_get_by_escalation_id(self, hr_user, mock_uow):
        """Test getting intervention history by escalation_id."""
        # Arrange
        mock_entry = {
            "id": 1,
            "escalation_id": 10,
            "mentor_id": 200,
            "intervention_type": "guidance",
            "intervention_at": datetime.now(tz=UTC),
            "notes": "Test notes",
            "outcome": "resolved",
            "escalation_resolved": True,
        }
        mock_uow.mentor_intervention_history.get_by_escalation_id.return_value = [mock_entry]

        # Act
        result = await get_mentor_intervention_history(
            current_user=hr_user,
            uow=mock_uow,
            escalation_id=10,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert len(result.items) == 1
        assert result.total == 1
        assert isinstance(result.items[0], MentorInterventionEntry)
        mock_uow.mentor_intervention_history.get_by_escalation_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_escalation_id_with_date_filters(self, hr_user, mock_uow):
        """Test getting intervention history by escalation_id with date filters."""
        # Arrange
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 1, 31, tzinfo=UTC)

        mock_entry = {
            "id": 1,
            "escalation_id": 10,
            "mentor_id": 200,
            "intervention_type": "guidance",
            "intervention_at": datetime(2024, 1, 15, tzinfo=UTC),
            "notes": "Test notes",
            "outcome": "resolved",
            "escalation_resolved": True,
        }
        mock_uow.mentor_intervention_history.get_by_escalation_id.return_value = [mock_entry]

        # Act
        result = await get_mentor_intervention_history(
            current_user=hr_user,
            uow=mock_uow,
            escalation_id=10,
            from_date=from_date,
            to_date=to_date,
        )

        # Assert
        assert result.total == 1
        assert len(result.items) == 1
        mock_uow.mentor_intervention_history.get_by_escalation_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_mentor_id(self, hr_user, mock_uow):
        """Test getting intervention history by mentor_id."""
        # Arrange
        mock_entry = {
            "id": 2,
            "escalation_id": 10,
            "mentor_id": 200,
            "intervention_type": "guidance",
            "intervention_at": datetime.now(tz=UTC),
            "notes": "Mentor notes",
            "outcome": "in_progress",
            "escalation_resolved": False,
        }
        mock_uow.mentor_intervention_history.get_by_mentor_id.return_value = [mock_entry]

        # Act
        result = await get_mentor_intervention_history(
            current_user=hr_user,
            uow=mock_uow,
            escalation_id=None,
            mentor_id=200,
        )

        # Assert
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].mentor_id == 200
        mock_uow.mentor_intervention_history.get_by_mentor_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_mentor_id_with_date_filters(self, hr_user, mock_uow):
        """Test getting intervention history by mentor_id with date filters."""
        # Arrange
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 1, 31, tzinfo=UTC)

        mock_entry = {
            "id": 3,
            "escalation_id": 10,
            "mentor_id": 200,
            "intervention_type": "guidance",
            "intervention_at": datetime(2024, 1, 15, tzinfo=UTC),
            "notes": "Filtered notes",
            "outcome": "resolved",
            "escalation_resolved": True,
        }
        mock_uow.mentor_intervention_history.get_by_mentor_id.return_value = [mock_entry]

        # Act
        result = await get_mentor_intervention_history(
            current_user=hr_user,
            uow=mock_uow,
            escalation_id=None,
            mentor_id=200,
            from_date=from_date,
            to_date=to_date,
        )

        # Assert
        assert result.total == 1
        assert len(result.items) == 1
        mock_uow.mentor_intervention_history.get_by_mentor_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, hr_user, mock_uow):
        """Test getting all intervention history with pagination."""
        # Arrange
        mock_entries = [
            {
                "id": i,
                "escalation_id": 10,
                "mentor_id": 200,
                "intervention_type": "guidance",
                "intervention_at": datetime.now(tz=UTC),
                "notes": f"Note {i}",
                "outcome": "in_progress",
                "escalation_resolved": False,
            }
            for i in range(1, 6)
        ]
        mock_uow.mentor_intervention_history.get_all.return_value = (mock_entries, 50)

        # Act
        result = await get_mentor_intervention_history(
            current_user=hr_user,
            uow=mock_uow,
            escalation_id=None,
            mentor_id=None,
            limit=10,
            offset=5,
        )

        # Assert
        assert result.total == 50
        assert len(result.items) == 5
        mock_uow.mentor_intervention_history.get_all.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_denies_regular_user(self, regular_user, mock_uow):
        """Test that regular users are denied access."""
        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            await get_mentor_intervention_history(
                current_user=regular_user,
                uow=mock_uow,
            )
