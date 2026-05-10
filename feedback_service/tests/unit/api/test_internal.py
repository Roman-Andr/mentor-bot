"""Unit tests for feedback_service internal maintenance endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from feedback_service.api.endpoints.internal import cleanup_user_feedback_data


@pytest.fixture
def mock_uow() -> MagicMock:
    uow = MagicMock()
    uow._session = AsyncMock()
    uow.commit = AsyncMock()
    return uow


class TestCleanupUserFeedbackData:
    async def test_cleanup_returns_counts(self, mock_uow: MagicMock) -> None:
        """Returns counts of deleted/updated rows for a user."""

        def make_result(count: int) -> MagicMock:
            r = MagicMock()
            r.rowcount = count
            return r

        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_result(2),  # comments deleted
                make_result(1),  # replied_comments updated
                make_result(3),  # ratings deleted
                make_result(4),  # pulse_surveys deleted
                make_result(5),  # status_history deleted
            ]
        )

        result = await cleanup_user_feedback_data(user_id=42, uow=mock_uow, _service_auth=None)

        assert result["comments"] == 2
        assert result["experience_ratings"] == 3
        assert result["pulse_surveys"] == 4
        assert result["status_history"] == 5
        assert result["updated_comments"] == 1
        mock_uow.commit.assert_awaited_once()

    async def test_cleanup_handles_zero_rowcount(self, mock_uow: MagicMock) -> None:
        """Returns 0 for None rowcount values."""

        def make_result(count: int | None) -> MagicMock:
            r = MagicMock()
            r.rowcount = count
            return r

        mock_uow._session.execute = AsyncMock(
            side_effect=[
                make_result(None),
                make_result(None),
                make_result(None),
                make_result(None),
                make_result(None),
            ]
        )

        result = await cleanup_user_feedback_data(user_id=99, uow=mock_uow, _service_auth=None)

        assert result["comments"] == 0
        assert result["experience_ratings"] == 0
        assert result["pulse_surveys"] == 0
        assert result["status_history"] == 0
        assert result["updated_comments"] == 0

    async def test_cleanup_raises_if_session_none(self) -> None:
        """Raises RuntimeError when session is not initialized."""
        mock_uow = MagicMock()
        mock_uow._session = None

        with pytest.raises(RuntimeError, match="Session not initialized"):
            await cleanup_user_feedback_data(user_id=1, uow=mock_uow, _service_auth=None)
