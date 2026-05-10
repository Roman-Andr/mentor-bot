"""Unit tests for escalation_service internal maintenance endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from escalation_service.api.internal import cleanup_user_escalation_data


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


class TestCleanupUserEscalationData:
    async def test_cleanup_with_escalations(self, mock_uow: MagicMock) -> None:
        """Returns correct counts when user owns escalations."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([1, 2]),  # escalation_ids
                make_result(3),  # status_history (by user)
                make_result(1),  # mentor_history (by user)
                make_result(2),  # status_by_escalation
                make_result(4),  # mentor_by_escalation
                make_result(2),  # escalations deleted
                make_result(1),  # updated_escalations
            ]
        )

        result = await cleanup_user_escalation_data(user_id=42, uow=mock_uow, _service_auth=None)

        assert result["escalations"] == 2
        assert result["status_history"] == 3 + 2
        assert result["mentor_history"] == 1 + 4
        assert result["updated_escalations"] == 1
        mock_uow.commit.assert_awaited_once()

    async def test_cleanup_without_escalations(self, mock_uow: MagicMock) -> None:
        """Returns zero counts when user owns no escalations."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([]),  # no escalation_ids
                make_result(0),  # status_history
                make_result(0),  # mentor_history
                make_result(0),  # updated_escalations
            ]
        )

        result = await cleanup_user_escalation_data(user_id=99, uow=mock_uow, _service_auth=None)

        assert result["escalations"] == 0
        assert result["status_history"] == 0
        assert result["mentor_history"] == 0
        mock_uow.commit.assert_awaited_once()

    async def test_cleanup_handles_none_rowcount(self, mock_uow: MagicMock) -> None:
        """Returns 0 for None rowcount values."""
        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_scalars([]),
                make_result(None),
                make_result(None),
                make_result(None),
            ]
        )

        result = await cleanup_user_escalation_data(user_id=1, uow=mock_uow, _service_auth=None)

        assert result["status_history"] == 0
        assert result["mentor_history"] == 0

    async def test_cleanup_raises_if_session_none(self) -> None:
        """Raises RuntimeError when session is not initialized."""
        mock_uow = MagicMock()
        mock_uow._session = None

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await cleanup_user_escalation_data(user_id=1, uow=mock_uow, _service_auth=None)
