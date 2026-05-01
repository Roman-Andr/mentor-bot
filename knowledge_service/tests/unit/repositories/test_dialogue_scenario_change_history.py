"""Tests for DialogueScenarioChangeHistory repository implementation."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import DialogueScenarioChangeHistory
from knowledge_service.repositories.implementations.dialogue_scenario_change_history import (
    DialogueScenarioChangeHistoryRepository,
)


class TestDialogueScenarioChangeHistoryRepository:
    """Test DialogueScenarioChangeHistory repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_change_history(self):
        """Create a sample change history entry."""
        return DialogueScenarioChangeHistory(
            id=1,
            scenario_id=1,
            user_id=1,
            action="update",
            old_name="Old Title",
            new_name="New Title",
            changed_at=datetime.now(UTC),
        )

    @pytest.fixture
    def sample_change_histories(self):
        """Create sample change history entries."""
        return [
            DialogueScenarioChangeHistory(
                id=1,
                scenario_id=1,
                user_id=1,
                action="create",
                old_name=None,
                new_name="Scenario",
                changed_at=datetime.now(UTC) - timedelta(hours=2),
            ),
            DialogueScenarioChangeHistory(
                id=2,
                scenario_id=1,
                user_id=2,
                action="update",
                old_name="Old Title",
                new_name="New Title",
                changed_at=datetime.now(UTC) - timedelta(hours=1),
            ),
            DialogueScenarioChangeHistory(
                id=3,
                scenario_id=1,
                user_id=1,
                action="delete",
                old_name="New Title",
                new_name=None,
                changed_at=datetime.now(UTC),
            ),
        ]

    async def test_create(self, mock_session, sample_change_history):
        """Test creating a change history entry."""
        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        result = await repo.create(sample_change_history)

        assert result == sample_change_history
        mock_session.add.assert_called_once_with(sample_change_history)
        mock_session.flush.assert_called_once()

    async def test_get_by_scenario_id(self, mock_session, sample_change_histories):
        """Test getting change history by scenario ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_change_histories
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        result = await repo.get_by_scenario_id(1)

        assert len(result) == 3
        mock_session.execute.assert_called_once()

    async def test_get_by_scenario_id_with_date_filter(
        self, mock_session, sample_change_histories
    ):
        """Test getting change history with date filtering."""
        filtered_histories = [sample_change_histories[1], sample_change_histories[2]]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered_histories
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(hours=1, minutes=30)
        result = await repo.get_by_scenario_id(1, from_date=from_date)

        assert len(result) == 2
        assert result[0].scenario_id == 1
        assert result[0].action == "update"
        assert result[1].action == "delete"
        mock_session.execute.assert_called_once()

    async def test_get_by_scenario_id_with_to_date(self, mock_session, sample_change_histories):
        """Test getting change history with to_date filter."""
        filtered_histories = [sample_change_histories[0]]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered_histories
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        to_date = datetime.now(UTC) - timedelta(hours=1, minutes=30)
        result = await repo.get_by_scenario_id(1, to_date=to_date)

        assert len(result) == 1
        assert result[0].scenario_id == 1
        assert result[0].action == "create"
        assert result[0].new_name == "Scenario"
        mock_session.execute.assert_called_once()

    async def test_get_by_scenario_id_with_date_range(
        self, mock_session, sample_change_histories
    ):
        """Test getting change history with date range."""
        filtered_histories = [sample_change_histories[1]]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered_histories
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(hours=1, minutes=30)
        to_date = datetime.now(UTC) - timedelta(minutes=30)
        result = await repo.get_by_scenario_id(1, from_date=from_date, to_date=to_date)

        assert len(result) == 1
        assert result[0] == sample_change_histories[1]
        assert result[0].scenario_id == 1
        assert result[0].user_id == 2
        mock_session.execute.assert_called_once()

    async def test_get_by_scenario_id_empty(self, mock_session):
        """Test getting change history when no entries exist."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        result = await repo.get_by_scenario_id(999)

        assert len(result) == 0

    async def test_get_all(self, mock_session, sample_change_histories):
        """Test getting all change history entries."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_change_histories
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 3
        mock_session.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        result, total = await repo.get_all()

        assert len(result) == 3
        assert total == 3

    async def test_get_all_with_pagination(self, mock_session, sample_change_histories):
        """Test getting all change history with pagination."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_change_histories[0]]
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 3
        mock_session.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        result, total = await repo.get_all(limit=1, offset=0)

        assert len(result) == 1
        assert total == 3

    async def test_get_all_with_date_filter(self, mock_session, sample_change_histories):
        """Test getting all change history with date filter."""
        filtered_histories = [sample_change_histories[1], sample_change_histories[2]]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered_histories
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 2
        mock_session.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(hours=1, minutes=30)
        result, total = await repo.get_all(from_date=from_date)

        assert len(result) == 2
        assert total == 2
        assert result[0].scenario_id == 1
        assert result[0].action == "update"
        assert result[1].action == "delete"

    async def test_get_all_with_date_range(self, mock_session, sample_change_histories):
        """Test getting all change history with date range."""
        filtered_histories = [sample_change_histories[1]]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered_histories
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1
        mock_session.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        from_date = datetime.now(UTC) - timedelta(hours=1, minutes=30)
        to_date = datetime.now(UTC) - timedelta(minutes=30)
        result, total = await repo.get_all(from_date=from_date, to_date=to_date)

        assert len(result) == 1
        assert total == 1
        assert result[0] == sample_change_histories[1]
        assert result[0].old_name == "Old Title"
        assert result[0].new_name == "New Title"

    async def test_get_all_empty(self, mock_session):
        """Test getting all change history when no entries exist."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0
        mock_session.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        repo = DialogueScenarioChangeHistoryRepository(mock_session)
        result, total = await repo.get_all()

        assert len(result) == 0
        assert total == 0
