"""Unit tests for checklists_service internal maintenance endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from checklists_service.api.internal import cleanup_user_checklist_data


def make_scalars(ids: list) -> MagicMock:
    r = MagicMock()
    r.scalars.return_value = ids
    return r


def make_result(count: int | None) -> MagicMock:
    r = MagicMock()
    r.rowcount = count
    return r


@pytest.fixture
def mock_uow() -> MagicMock:
    uow = MagicMock()
    uow._session = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestCleanupUserChecklistData:
    async def test_cleanup_with_checklists(self, mock_uow: MagicMock) -> None:
        """Returns correct counts when user owns checklists."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([1, 2]),  # checklist_ids
                make_result(3),  # direct_task_history
                make_result(2),  # direct_status_history
                make_result(4),  # checklist_task_history
                make_result(1),  # checklist_status_history
                make_result(2),  # owned_certificates
                make_result(5),  # tasks
                make_result(2),  # checklists
                make_result(1),  # updated_certificates
                make_result(1),  # updated_checklists
            ]
        )

        result = await cleanup_user_checklist_data(user_id=42, uow=mock_uow, _service_auth=None)

        assert result["checklists"] == 2
        assert result["tasks"] == 5
        assert result["task_history"] == 3 + 4
        assert result["status_history"] == 2 + 1
        assert result["certificates"] == 2
        assert result["updated_certificates"] == 1
        assert result["updated_checklists"] == 1
        mock_uow.commit.assert_awaited_once()

    async def test_cleanup_without_checklists(self, mock_uow: MagicMock) -> None:
        """Returns zero for checklist-related counts when user owns no checklists."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([]),  # no checklist_ids
                make_result(0),  # direct_task_history
                make_result(0),  # direct_status_history
                make_result(0),  # updated_certificates
                make_result(0),  # updated_checklists
            ]
        )

        result = await cleanup_user_checklist_data(user_id=99, uow=mock_uow, _service_auth=None)

        assert result["checklists"] == 0
        assert result["tasks"] == 0
        assert result["certificates"] == 0
        mock_uow.commit.assert_awaited_once()

    async def test_cleanup_handles_none_rowcount(self, mock_uow: MagicMock) -> None:
        """Returns 0 for None rowcount values."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([]),
                make_result(None),
                make_result(None),
                make_result(None),
                make_result(None),
            ]
        )

        result = await cleanup_user_checklist_data(user_id=1, uow=mock_uow, _service_auth=None)

        assert result["task_history"] == 0
        assert result["status_history"] == 0

    async def test_cleanup_raises_if_session_none(self) -> None:
        """Raises RuntimeError when session is not initialized."""
        mock_uow = MagicMock()
        mock_uow._session = None

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await cleanup_user_checklist_data(user_id=1, uow=mock_uow, _service_auth=None)
