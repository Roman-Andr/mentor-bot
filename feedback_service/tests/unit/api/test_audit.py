"""Unit tests for audit endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from feedback_service.api.endpoints.audit import (
    AuditResponse,
    FeedbackStatusChangeEntry,
    get_feedback_status_change_history,
    require_hr_or_admin,
)
from feedback_service.core import UserRole


class TestRequireHrOrAdmin:
    """Tests for require_hr_or_admin function."""

    async def test_hr_role_allowed(self) -> None:
        """HR role should be allowed."""
        # Arrange
        current_user = MagicMock()
        current_user.role = UserRole.HR

        # Act & Assert - should not raise
        require_hr_or_admin(current_user)

    async def test_admin_role_allowed(self) -> None:
        """Admin role should be allowed."""
        # Arrange
        current_user = MagicMock()
        current_user.role = UserRole.ADMIN

        # Act & Assert - should not raise
        require_hr_or_admin(current_user)

    async def test_newbie_role_denied(self) -> None:
        """Newbie role should be denied."""
        # Arrange
        current_user = MagicMock()
        current_user.role = UserRole.NEWBIE

        # Act & Assert
        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            require_hr_or_admin(current_user)

    async def test_mentor_role_denied(self) -> None:
        """Mentor role should be denied."""
        # Arrange
        current_user = MagicMock()
        current_user.role = UserRole.MENTOR

        # Act & Assert
        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            require_hr_or_admin(current_user)


class TestGetFeedbackStatusChangeHistory:
    """Tests for get_feedback_status_change_history endpoint."""

    async def test_get_by_feedback_id(self) -> None:
        """Test getting history by feedback_id."""
        # Arrange
        current_user = MagicMock()
        current_user.role = UserRole.ADMIN

        mock_uow = MagicMock()
        mock_history = {
            "id": 1,
            "feedback_id": 100,
            "user_id": 1,
            "action": "status_change",
            "old_status": "pending",
            "new_status": "approved",
            "changed_at": datetime.now(UTC),
            "changed_by": 2,
            "metadata": {"reason": "valid"},
        }
        mock_uow.feedback_status_change_history.get_by_feedback_id = AsyncMock(return_value=[mock_history])

        # Act
        result = await get_feedback_status_change_history(
            current_user=current_user,
            uow=mock_uow,
            feedback_id=100,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 1
        assert len(result.items) == 1
        assert isinstance(result.items[0], FeedbackStatusChangeEntry)
        mock_uow.feedback_status_change_history.get_by_feedback_id.assert_called_once()

    async def test_get_all_without_feedback_id(self) -> None:
        """Test getting all history without feedback_id filter."""
        # Arrange
        current_user = MagicMock()
        current_user.role = UserRole.HR

        mock_history = {
            "id": 1,
            "feedback_id": 100,
            "user_id": 1,
            "action": "status_change",
            "old_status": "pending",
            "new_status": "approved",
            "changed_at": datetime.now(UTC),
            "changed_by": 2,
            "metadata": None,
        }

        mock_uow = MagicMock()
        mock_uow.feedback_status_change_history.get_all = AsyncMock(return_value=([mock_history], 1))

        # Act
        result = await get_feedback_status_change_history(
            current_user=current_user,
            uow=mock_uow,
            feedback_id=None,
            limit=10,
            offset=0,
        )

        # Assert
        assert isinstance(result, AuditResponse)
        assert result.total == 1
        assert len(result.items) == 1
        mock_uow.feedback_status_change_history.get_all.assert_called_once()

    async def test_get_with_date_filters(self) -> None:
        """Test getting history with date filters."""
        # Arrange
        current_user = MagicMock()
        current_user.role = UserRole.ADMIN

        from_date = datetime(2026, 1, 1, tzinfo=UTC)
        to_date = datetime(2026, 1, 31, tzinfo=UTC)

        mock_uow = MagicMock()
        mock_uow.feedback_status_change_history.get_by_feedback_id = AsyncMock(return_value=[])

        # Act
        result = await get_feedback_status_change_history(
            current_user=current_user,
            uow=mock_uow,
            feedback_id=100,
            from_date=from_date,
            to_date=to_date,
        )

        # Assert
        mock_uow.feedback_status_change_history.get_by_feedback_id.assert_called_once()

    async def test_unauthorized_access_denied(self) -> None:
        """Test that non-HR/Admin users are denied access."""
        # Arrange
        current_user = MagicMock()
        current_user.role = UserRole.MENTOR

        mock_uow = MagicMock()

        # Act & Assert
        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            await get_feedback_status_change_history(
                current_user=current_user,
                uow=mock_uow,
            )
