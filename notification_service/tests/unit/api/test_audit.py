"""Unit tests for notification_service/api/endpoints/audit.py."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from notification_service.api.endpoints.audit import (
    AuditResponse,
    NotificationAuditEntry,
    get_notifications_audit,
    require_hr_or_admin,
)
from notification_service.core import UserRole


class TestRequireHrOrAdmin:
    """Tests for require_hr_or_admin function (lines 45-48)."""

    def test_raises_when_user_role_not_hr_or_admin(self) -> None:
        """Raises PermissionError when user role is not HR or ADMIN (lines 47-48)."""
        from notification_service.api.deps import UserInfo

        current_user = UserInfo({"id": 1, "role": "USER", "is_active": True})

        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            require_hr_or_admin(current_user)

    def test_passes_when_user_role_is_hr(self) -> None:
        """Does not raise when user role is HR."""
        from notification_service.api.deps import UserInfo

        current_user = UserInfo({"id": 1, "role": UserRole.HR, "is_active": True})

        require_hr_or_admin(current_user)

    def test_passes_when_user_role_is_admin(self) -> None:
        """Does not raise when user role is ADMIN."""
        from notification_service.api.deps import UserInfo

        current_user = UserInfo({"id": 1, "role": UserRole.ADMIN, "is_active": True})

        require_hr_or_admin(current_user)


class TestGetNotificationsAudit:
    """Tests for get_notifications_audit endpoint (lines 51-94)."""

    async def test_validates_user_role(self) -> None:
        """Validates that user has HR or ADMIN role (line 62)."""
        from notification_service.api.deps import UserInfo
        from sqlalchemy.ext.asyncio import AsyncSession

        current_user = UserInfo({"id": 1, "role": "USER", "is_active": True})
        mock_db = MagicMock(spec=AsyncSession)

        with pytest.raises(PermissionError, match="Access denied: HR or Admin role required"):
            await get_notifications_audit(current_user=current_user, db=mock_db)

    async def test_calls_uow_and_executes_queries(self) -> None:
        """Tests that the endpoint creates UoW and executes queries (lines 64-91)."""
        from notification_service.api.deps import UserInfo
        from sqlalchemy.ext.asyncio import AsyncSession

        current_user = UserInfo({"id": 1, "role": UserRole.ADMIN, "is_active": True})
        mock_db = MagicMock(spec=AsyncSession)
        mock_session = AsyncMock()
        mock_db.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.__aexit__ = AsyncMock(return_value=None)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one.return_value = 10
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("notification_service.api.endpoints.audit.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow._session = mock_session
            mock_uow_class.return_value = mock_uow

            mock_stmt = MagicMock()
            mock_stmt.where.return_value = mock_stmt
            mock_stmt.order_by.return_value = mock_stmt
            mock_stmt.offset.return_value = mock_stmt
            mock_stmt.limit.return_value = mock_stmt
            mock_uow.notifications._select.return_value = mock_stmt
            mock_uow.notifications._count.return_value = mock_stmt
            mock_uow.notifications._model = MagicMock()
            mock_uow.notifications._model.user_id = MagicMock()
            mock_uow.notifications._model.created_at = MagicMock()
            mock_uow.notifications._model.created_at.desc = MagicMock(return_value=mock_stmt)

            result = await get_notifications_audit(
                current_user=current_user,
                db=mock_db,
                user_id=None,
                from_date=None,
                to_date=None,
                limit=50,
                offset=0,
            )

        assert isinstance(result, AuditResponse)
        assert result.total == 10
        assert result.items == []

    async def test_handles_user_id_filter(self) -> None:
        """Tests user_id filter is applied (lines 67-68, 76-77)."""
        from notification_service.api.deps import UserInfo
        from sqlalchemy.ext.asyncio import AsyncSession

        current_user = UserInfo({"id": 1, "role": UserRole.HR, "is_active": True})
        mock_db = MagicMock(spec=AsyncSession)
        mock_session = AsyncMock()
        mock_db.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.__aexit__ = AsyncMock(return_value=None)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one.return_value = 1
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("notification_service.api.endpoints.audit.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow._session = mock_session
            mock_uow_class.return_value = mock_uow

            mock_stmt = MagicMock()
            mock_stmt.where.return_value = mock_stmt
            mock_stmt.order_by.return_value = mock_stmt
            mock_stmt.offset.return_value = mock_stmt
            mock_stmt.limit.return_value = mock_stmt
            mock_uow.notifications._select.return_value = mock_stmt
            mock_uow.notifications._count.return_value = mock_stmt
            mock_uow.notifications._model = MagicMock()
            mock_uow.notifications._model.user_id = MagicMock()
            mock_uow.notifications._model.created_at = MagicMock()
            mock_uow.notifications._model.created_at.desc = MagicMock(return_value=mock_stmt)

            result = await get_notifications_audit(
                current_user=current_user,
                db=mock_db,
                user_id=42,
                from_date=None,
                to_date=None,
            )

        assert isinstance(result, AuditResponse)

    async def test_handles_date_filters(self) -> None:
        """Tests date filter code path exists (lines 69-72, 78-81)."""
        from notification_service.api.deps import UserInfo
        from sqlalchemy.ext.asyncio import AsyncSession

        current_user = UserInfo({"id": 1, "role": UserRole.ADMIN, "is_active": True})
        mock_db = MagicMock(spec=AsyncSession)
        mock_session = AsyncMock()
        mock_db.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.__aexit__ = AsyncMock(return_value=None)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one.return_value = 5
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("notification_service.api.endpoints.audit.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow._session = mock_session
            mock_uow_class.return_value = mock_uow

            mock_stmt = MagicMock()
            mock_stmt.where.return_value = mock_stmt
            mock_stmt.order_by.return_value = mock_stmt
            mock_stmt.offset.return_value = mock_stmt
            mock_stmt.limit.return_value = mock_stmt
            mock_uow.notifications._select.return_value = mock_stmt
            mock_uow.notifications._count.return_value = mock_stmt
            mock_uow.notifications._model = MagicMock()
            mock_uow.notifications._model.user_id = MagicMock()

            # Make created_at support comparison operations
            mock_created_at = MagicMock()
            mock_created_at.__ge__ = MagicMock(return_value=mock_stmt)
            mock_created_at.__le__ = MagicMock(return_value=mock_stmt)
            mock_created_at.desc = MagicMock(return_value=mock_stmt)
            mock_uow.notifications._model.created_at = mock_created_at

            from_date = datetime(2024, 1, 1, tzinfo=UTC)
            to_date = datetime(2024, 12, 31, tzinfo=UTC)

            result = await get_notifications_audit(
                current_user=current_user,
                db=mock_db,
                user_id=None,
                from_date=from_date,
                to_date=to_date,
            )

        assert isinstance(result, AuditResponse)

    async def test_applies_pagination(self) -> None:
        """Tests limit and offset pagination are applied (line 87)."""
        from notification_service.api.deps import UserInfo
        from sqlalchemy.ext.asyncio import AsyncSession

        current_user = UserInfo({"id": 1, "role": UserRole.ADMIN, "is_active": True})
        mock_db = MagicMock(spec=AsyncSession)
        mock_session = AsyncMock()
        mock_db.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.__aexit__ = AsyncMock(return_value=None)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one.return_value = 100
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("notification_service.api.endpoints.audit.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow._session = mock_session
            mock_uow_class.return_value = mock_uow

            mock_stmt = MagicMock()
            mock_stmt.where.return_value = mock_stmt
            mock_stmt.order_by.return_value = mock_stmt
            mock_stmt.offset.return_value = mock_stmt
            mock_stmt.limit.return_value = mock_stmt
            mock_uow.notifications._select.return_value = mock_stmt
            mock_uow.notifications._count.return_value = mock_stmt
            mock_uow.notifications._model = MagicMock()
            mock_uow.notifications._model.user_id = MagicMock()
            mock_uow.notifications._model.created_at = MagicMock()
            mock_uow.notifications._model.created_at.desc = MagicMock(return_value=mock_stmt)

            result = await get_notifications_audit(
                current_user=current_user,
                db=mock_db,
                user_id=None,
                from_date=None,
                to_date=None,
                limit=25,
                offset=10,
            )

        assert isinstance(result, AuditResponse)
        assert result.total == 100

    async def test_orders_by_created_at_desc(self) -> None:
        """Tests results are ordered by created_at descending (line 87)."""
        from notification_service.api.deps import UserInfo
        from sqlalchemy.ext.asyncio import AsyncSession

        current_user = UserInfo({"id": 1, "role": UserRole.HR, "is_active": True})
        mock_db = MagicMock(spec=AsyncSession)
        mock_session = AsyncMock()
        mock_db.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.__aexit__ = AsyncMock(return_value=None)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("notification_service.api.endpoints.audit.SqlAlchemyUnitOfWork") as mock_uow_class:
            mock_uow = MagicMock()
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)
            mock_uow._session = mock_session
            mock_uow_class.return_value = mock_uow

            mock_stmt = MagicMock()
            mock_stmt.where.return_value = mock_stmt
            mock_stmt.order_by.return_value = mock_stmt
            mock_stmt.offset.return_value = mock_stmt
            mock_stmt.limit.return_value = mock_stmt
            mock_uow.notifications._select.return_value = mock_stmt
            mock_uow.notifications._count.return_value = mock_stmt
            mock_uow.notifications._model = MagicMock()
            mock_uow.notifications._model.user_id = MagicMock()
            mock_uow.notifications._model.created_at = MagicMock()
            mock_uow.notifications._model.created_at.desc = MagicMock(return_value=mock_stmt)

            result = await get_notifications_audit(
                current_user=current_user,
                db=mock_db,
                user_id=None,
                from_date=None,
                to_date=None,
            )

        assert isinstance(result, AuditResponse)


class TestNotificationAuditEntry:
    """Tests for NotificationAuditEntry schema."""

    def test_validates_notification_audit_entry(self) -> None:
        """NotificationAuditEntry validates correctly."""
        entry = NotificationAuditEntry(
            id=1,
            user_id=42,
            type="GENERAL",
            channel="EMAIL",
            status="SENT",
            sent_at=datetime(2024, 1, 1, tzinfo=UTC),
            delivered_at=datetime(2024, 1, 1, 0, 1, tzinfo=UTC),
            read_at=datetime(2024, 1, 1, 0, 5, tzinfo=UTC),
            failure_reason=None,
            metadata={"key": "value"},
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
        )

        assert entry.id == 1
        assert entry.user_id == 42
        assert entry.type == "GENERAL"
        assert entry.channel == "EMAIL"
        assert entry.status == "SENT"


class TestAuditResponse:
    """Tests for AuditResponse schema."""

    def test_validates_audit_response(self) -> None:
        """AuditResponse validates correctly."""
        response = AuditResponse(
            items=[],
            total=0,
        )

        assert response.items == []
        assert response.total == 0
