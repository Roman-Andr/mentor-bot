"""Unit tests for audit endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from auth_service.api.endpoints.audit import (
    AuditResponse,
    InvitationHistoryEntry,
    LoginHistoryEntry,
    MentorAssignmentEntry,
    RoleChangeEntry,
    get_invitation_history,
    get_login_history,
    get_mentor_assignment_history,
    get_role_change_history,
    require_hr_or_admin,
)
from auth_service.core import PermissionDenied
from auth_service.models import (
    InvitationStatusHistory,
    LoginHistory,
    MentorAssignmentHistory,
    RoleChangeHistory,
)


def create_login_history(**kwargs):
    """Helper to create LoginHistory with defaults."""
    defaults = {
        "id": 1,
        "user_id": 1,
        "login_at": datetime.now(UTC),
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla",
        "success": True,
        "failure_reason": None,
        "method": "password",
    }
    defaults.update(kwargs)
    return LoginHistory(**defaults)


def create_role_change_history(**kwargs):
    """Helper to create RoleChangeHistory with defaults."""
    defaults = {
        "id": 1,
        "user_id": 1,
        "old_role": "NEWBIE",
        "new_role": "MENTOR",
        "changed_at": datetime.now(UTC),
        "changed_by": 2,
        "reason": "Promotion",
    }
    defaults.update(kwargs)
    return RoleChangeHistory(**defaults)


def create_invitation_status_history(**kwargs):
    """Helper to create InvitationStatusHistory with defaults."""
    defaults = {
        "id": 1,
        "invitation_id": 10,
        "old_status": "PENDING",
        "new_status": "ACCEPTED",
        "changed_at": datetime.now(UTC),
        "changed_by": 1,
    }
    defaults.update(kwargs)
    return InvitationStatusHistory(**defaults)


def create_mentor_assignment_history(**kwargs):
    """Helper to create MentorAssignmentHistory with defaults."""
    defaults = {
        "id": 1,
        "user_id": 1,
        "mentor_id": 2,
        "action": "ASSIGNED",
        "changed_at": datetime.now(UTC),
        "changed_by": 3,
        "reason": "Initial assignment",
    }
    defaults.update(kwargs)
    return MentorAssignmentHistory(**defaults)


class TestRequireHrOrAdmin:
    """Tests for require_hr_or_admin function."""

    def test_require_hr_or_admin_with_admin(self, admin_user):
        """Test require_hr_or_admin allows admin user."""
        # Should not raise
        require_hr_or_admin(admin_user)

    def test_require_hr_or_admin_with_hr(self, hr_user):
        """Test require_hr_or_admin allows HR user."""
        # Should not raise
        require_hr_or_admin(hr_user)

    def test_require_hr_or_admin_with_mentor(self, mentor_user):
        """Test require_hr_or_admin denies mentor user."""
        with pytest.raises(PermissionDenied) as exc_info:
            require_hr_or_admin(mentor_user)

        assert "Access denied: HR or Admin role required" in str(exc_info.value)

    def test_require_hr_or_admin_with_newbie(self, newbie_user):
        """Test require_hr_or_admin denies newbie user."""
        with pytest.raises(PermissionDenied) as exc_info:
            require_hr_or_admin(newbie_user)

        assert "Access denied: HR or Admin role required" in str(exc_info.value)


class TestGetLoginHistory:
    """Tests for get_login_history endpoint."""

    async def test_get_login_history_all_records(self, admin_user, mock_uow):
        """Test get_login_history returns all records when no user_id provided."""
        login1 = {
            "id": 1,
            "user_id": 1,
            "login_at": datetime.now(UTC),
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla",
            "success": True,
            "failure_reason": None,
            "method": "password",
        }
        login2 = {
            "id": 2,
            "user_id": 2,
            "login_at": datetime.now(UTC),
            "ip_address": "192.168.1.2",
            "user_agent": "Chrome",
            "success": True,
            "failure_reason": None,
            "method": "telegram",
        }

        mock_uow.login_history.get_all = AsyncMock(return_value=([login1, login2], 2))

        result = await get_login_history(
            current_user=admin_user, uow=mock_uow, user_id=None, from_date=None, to_date=None, limit=50, offset=0
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 2
        assert result.total == 2
        assert all(isinstance(item, LoginHistoryEntry) for item in result.items)
        mock_uow.login_history.get_all.assert_called_once_with(from_date=None, to_date=None, limit=50, offset=0)

    async def test_get_login_history_by_user_id(self, admin_user, mock_uow):
        """Test get_login_history returns records for specific user."""
        login1 = {
            "id": 1,
            "user_id": 5,
            "login_at": datetime.now(UTC),
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla",
            "success": True,
            "failure_reason": None,
            "method": "password",
        }

        mock_uow.login_history.get_by_user_id = AsyncMock(return_value=[login1])

        result = await get_login_history(
            current_user=admin_user,
            uow=mock_uow,
            user_id=5,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 1
        assert result.total == 1
        assert result.items[0].user_id == 5
        mock_uow.login_history.get_by_user_id.assert_called_once_with(user_id=5, from_date=None, to_date=None, limit=50)

    async def test_get_login_history_with_date_filters(self, admin_user, mock_uow):
        """Test get_login_history with date filtering."""
        from_date = datetime(2026, 1, 1, tzinfo=UTC)
        to_date = datetime(2026, 12, 31, tzinfo=UTC)

        mock_uow.login_history.get_all = AsyncMock(return_value=([], 0))

        await get_login_history(
            current_user=admin_user,
            uow=mock_uow,
            user_id=None,
            from_date=from_date,
            to_date=to_date,
            limit=50,
            offset=0,
        )

        mock_uow.login_history.get_all.assert_called_once_with(from_date=from_date, to_date=to_date, limit=50, offset=0)

    async def test_get_login_history_permission_denied(self, newbie_user, mock_uow):
        """Test get_login_history raises PermissionError for non-HR/Admin."""
        with pytest.raises(PermissionDenied) as exc_info:
            await get_login_history(
                current_user=newbie_user,
                uow=mock_uow,
                user_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )

        assert "Access denied: HR or Admin role required" in str(exc_info.value)


class TestGetRoleChangeHistory:
    """Tests for get_role_change_history endpoint."""

    async def test_get_role_change_history_all_records(self, admin_user, mock_uow):
        """Test get_role_change_history returns all records when no user_id provided."""
        role_change1 = {
            "id": 1,
            "user_id": 1,
            "old_role": "NEWBIE",
            "new_role": "MENTOR",
            "changed_at": datetime.now(UTC),
            "changed_by": 2,
            "reason": "Promotion",
        }
        role_change2 = {
            "id": 2,
            "user_id": 3,
            "old_role": "MENTOR",
            "new_role": "HR",
            "changed_at": datetime.now(UTC),
            "changed_by": 1,
            "reason": "Role change",
        }

        mock_uow.role_change_history.get_all = AsyncMock(return_value=([role_change1, role_change2], 2))

        result = await get_role_change_history(
            current_user=admin_user,
            uow=mock_uow,
            user_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 2
        assert result.total == 2
        assert all(isinstance(item, RoleChangeEntry) for item in result.items)

    async def test_get_role_change_history_by_user_id(self, admin_user, mock_uow):
        """Test get_role_change_history returns records for specific user."""
        role_change = {
            "id": 1,
            "user_id": 5,
            "old_role": "NEWBIE",
            "new_role": "MENTOR",
            "changed_at": datetime.now(UTC),
            "changed_by": 2,
            "reason": "Promotion",
        }

        mock_uow.role_change_history.get_by_user_id = AsyncMock(return_value=[role_change])

        result = await get_role_change_history(
            current_user=admin_user,
            uow=mock_uow,
            user_id=5,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 1
        assert result.total == 1
        assert result.items[0].user_id == 5
        mock_uow.role_change_history.get_by_user_id.assert_called_once_with(user_id=5, from_date=None, to_date=None)

    async def test_get_role_change_history_permission_denied(self, newbie_user, mock_uow):
        """Test get_role_change_history raises PermissionError for non-HR/Admin."""
        with pytest.raises(PermissionDenied) as exc_info:
            await get_role_change_history(
                current_user=newbie_user,
                uow=mock_uow,
                user_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )

        assert "Access denied: HR or Admin role required" in str(exc_info.value)


class TestGetInvitationHistory:
    """Tests for get_invitation_history endpoint."""

    async def test_get_invitation_history_all_records(self, admin_user, mock_uow):
        """Test get_invitation_history returns all records when no invitation_id provided."""
        history1 = {
            "id": 1,
            "invitation_id": 10,
            "old_status": "PENDING",
            "new_status": "ACCEPTED",
            "changed_at": datetime.now(UTC),
            "changed_by": 1,
            "meta_data": {},
        }
        history2 = {
            "id": 2,
            "invitation_id": 11,
            "old_status": "PENDING",
            "new_status": "EXPIRED",
            "changed_at": datetime.now(UTC),
            "changed_by": None,
            "meta_data": None,
        }

        mock_uow.invitation_status_history.get_all = AsyncMock(return_value=([history1, history2], 2))

        result = await get_invitation_history(
            current_user=admin_user,
            uow=mock_uow,
            invitation_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 2
        assert result.total == 2
        assert all(isinstance(item, InvitationHistoryEntry) for item in result.items)

    async def test_get_invitation_history_by_invitation_id(self, admin_user, mock_uow):
        """Test get_invitation_history returns records for specific invitation."""
        history = {
            "id": 1,
            "invitation_id": 20,
            "old_status": "PENDING",
            "new_status": "ACCEPTED",
            "changed_at": datetime.now(UTC),
            "changed_by": 1,
            "meta_data": {"auto_created": True},
        }

        mock_uow.invitation_status_history.get_by_invitation_id = AsyncMock(return_value=[history])

        result = await get_invitation_history(
            current_user=admin_user,
            uow=mock_uow,
            invitation_id=20,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 1
        assert result.total == 1
        assert result.items[0].invitation_id == 20
        mock_uow.invitation_status_history.get_by_invitation_id.assert_called_once_with(
            invitation_id=20, from_date=None, to_date=None
        )

    async def test_get_invitation_history_permission_denied(self, newbie_user, mock_uow):
        """Test get_invitation_history raises PermissionError for non-HR/Admin."""
        with pytest.raises(PermissionDenied) as exc_info:
            await get_invitation_history(
                current_user=newbie_user,
                uow=mock_uow,
                invitation_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )

        assert "Access denied: HR or Admin role required" in str(exc_info.value)


class TestGetMentorAssignmentHistory:
    """Tests for get_mentor_assignment_history endpoint."""

    async def test_get_mentor_assignment_history_all_records(self, admin_user, mock_uow):
        """Test get_mentor_assignment_history returns all records when no filters provided."""
        assignment1 = {
            "id": 1,
            "user_id": 1,
            "mentor_id": 2,
            "action": "ASSIGNED",
            "changed_at": datetime.now(UTC),
            "changed_by": 3,
            "reason": "Initial assignment",
        }
        assignment2 = {
            "id": 2,
            "user_id": 4,
            "mentor_id": 5,
            "action": "REASSIGNED",
            "changed_at": datetime.now(UTC),
            "changed_by": 3,
            "reason": "Mentor change",
        }

        mock_uow.mentor_assignment_history.get_all = AsyncMock(return_value=([assignment1, assignment2], 2))

        result = await get_mentor_assignment_history(
            current_user=admin_user,
            uow=mock_uow,
            user_id=None,
            mentor_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 2
        assert result.total == 2
        assert all(isinstance(item, MentorAssignmentEntry) for item in result.items)

    async def test_get_mentor_assignment_history_by_user_id(self, admin_user, mock_uow):
        """Test get_mentor_assignment_history returns records for specific user."""
        assignment = {
            "id": 1,
            "user_id": 10,
            "mentor_id": 2,
            "action": "ASSIGNED",
            "changed_at": datetime.now(UTC),
            "changed_by": 3,
            "reason": "Initial assignment",
        }

        mock_uow.mentor_assignment_history.get_by_user_id = AsyncMock(return_value=[assignment])

        result = await get_mentor_assignment_history(
            current_user=admin_user,
            uow=mock_uow,
            user_id=10,
            mentor_id=None,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 1
        assert result.total == 1
        assert result.items[0].user_id == 10
        mock_uow.mentor_assignment_history.get_by_user_id.assert_called_once_with(
            user_id=10, from_date=None, to_date=None
        )

    async def test_get_mentor_assignment_history_by_mentor_id(self, admin_user, mock_uow):
        """Test get_mentor_assignment_history returns records for specific mentor."""
        assignment = {
            "id": 1,
            "user_id": 1,
            "mentor_id": 20,
            "action": "ASSIGNED",
            "changed_at": datetime.now(UTC),
            "changed_by": 3,
            "reason": "Initial assignment",
        }

        mock_uow.mentor_assignment_history.get_by_mentor_id = AsyncMock(return_value=[assignment])

        result = await get_mentor_assignment_history(
            current_user=admin_user,
            uow=mock_uow,
            user_id=None,
            mentor_id=20,
            from_date=None,
            to_date=None,
            limit=50,
            offset=0,
        )

        assert isinstance(result, AuditResponse)
        assert len(result.items) == 1
        assert result.total == 1
        assert result.items[0].mentor_id == 20
        mock_uow.mentor_assignment_history.get_by_mentor_id.assert_called_once_with(
            mentor_id=20, from_date=None, to_date=None
        )

    async def test_get_mentor_assignment_history_permission_denied(self, newbie_user, mock_uow):
        """Test get_mentor_assignment_history raises PermissionError for non-HR/Admin."""
        with pytest.raises(PermissionDenied) as exc_info:
            await get_mentor_assignment_history(
                current_user=newbie_user,
                uow=mock_uow,
                user_id=None,
                mentor_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )

        assert "Access denied: HR or Admin role required" in str(exc_info.value)
