"""Tests for Category change history repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import CategoryChangeHistory
from knowledge_service.repositories.implementations.category_change_history import CategoryChangeHistoryRepository


class TestCategoryChangeHistoryRepository:
    """Test Category change history repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_history(self):
        """Create a sample category change history entry."""
        return CategoryChangeHistory(
            id=1,
            category_id=1,
            user_id=1,
            action="created",
            old_name=None,
            new_name="New Category",
            changed_at=datetime.now(UTC),
            changed_by=1,
        )

    async def test_create(self, mock_session, sample_history):
        """Test creating category change history entry."""
        repo = CategoryChangeHistoryRepository(mock_session)
        result = await repo.create(sample_history)

        assert result == sample_history
        mock_session.add.assert_called_once_with(sample_history)
        mock_session.flush.assert_called_once()

    async def test_get_by_category_id(self, mock_session, sample_history):
        """Test getting history by category ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result = await repo.get_by_category_id(1)

        assert len(result) == 1
        assert result[0] == sample_history

    async def test_get_by_category_id_with_from_date(self, mock_session, sample_history):
        """Test getting history by category ID with from_date filter."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result = await repo.get_by_category_id(1, from_date=from_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].category_id == 1
        assert result[0].action == "created"
        mock_session.execute.assert_called_once()

    async def test_get_by_category_id_with_to_date(self, mock_session, sample_history):
        """Test getting history by category ID with to_date filter."""
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result = await repo.get_by_category_id(1, to_date=to_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].new_name == "New Category"
        mock_session.execute.assert_called_once()

    async def test_get_by_category_id_with_both_dates(self, mock_session, sample_history):
        """Test getting history by category ID with both date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result = await repo.get_by_category_id(1, from_date=from_date, to_date=to_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].user_id == 1
        mock_session.execute.assert_called_once()

    async def test_get_all(self, mock_session, sample_history):
        """Test getting all history entries."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result, total = await repo.get_all()

        assert len(result) == 1
        assert total == 1

    async def test_get_all_with_from_date(self, mock_session, sample_history):
        """Test getting all history with from_date filter."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result, total = await repo.get_all(from_date=from_date)

        assert len(result) == 1
        assert total == 1
        assert result[0] == sample_history
        assert result[0].action == "created"

    async def test_get_all_with_to_date(self, mock_session, sample_history):
        """Test getting all history with to_date filter."""
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result, total = await repo.get_all(to_date=to_date)

        assert len(result) == 1
        assert total == 1
        assert result[0] == sample_history
        assert result[0].category_id == 1

    async def test_get_all_with_pagination(self, mock_session, sample_history):
        """Test getting all history with pagination."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result, total = await repo.get_all(limit=10, offset=5)

        assert len(result) == 1
        assert total == 1
        assert result[0] == sample_history
        assert result[0].new_name == "New Category"

    async def test_get_all_empty(self, mock_session):
        """Test getting all history when empty."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        repo = CategoryChangeHistoryRepository(mock_session)
        result, total = await repo.get_all()

        assert len(result) == 0
        assert total == 0
