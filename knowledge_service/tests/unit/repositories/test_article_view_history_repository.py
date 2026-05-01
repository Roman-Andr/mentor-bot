"""Tests for Article view history repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.models import ArticleViewHistory
from knowledge_service.repositories.implementations.article_view_history import ArticleViewHistoryRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestArticleViewHistoryRepository:
    """Test Article view history repository implementation."""

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
        """Create a sample article view history entry."""
        return ArticleViewHistory(
            id=1,
            article_id=1,
            user_id=1,
            viewed_at=datetime.now(UTC),
        )

    async def test_create(self, mock_session, sample_history):
        """Test creating article view history entry."""
        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.create(sample_history)

        assert result == sample_history
        mock_session.add.assert_called_once_with(sample_history)
        mock_session.flush.assert_called_once()

    async def test_get_by_article_id(self, mock_session, sample_history):
        """Test getting history by article ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.get_by_article_id(1)

        assert len(result) == 1
        assert result[0] == sample_history

    async def test_get_by_article_id_with_from_date(self, mock_session, sample_history):
        """Test getting history by article ID with from_date filter."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.get_by_article_id(1, from_date=from_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].article_id == 1
        assert result[0].user_id == 1
        mock_session.execute.assert_called_once()

    async def test_get_by_article_id_with_to_date(self, mock_session, sample_history):
        """Test getting history by article ID with to_date filter."""
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.get_by_article_id(1, to_date=to_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].article_id == 1
        mock_session.execute.assert_called_once()

    async def test_get_by_article_id_with_both_dates(self, mock_session, sample_history):
        """Test getting history by article ID with both date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.get_by_article_id(1, from_date=from_date, to_date=to_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].user_id == 1
        mock_session.execute.assert_called_once()

    async def test_get_by_user_id(self, mock_session, sample_history):
        """Test getting history by user ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1)

        assert len(result) == 1
        assert result[0] == sample_history

    async def test_get_by_user_id_with_from_date(self, mock_session, sample_history):
        """Test getting history by user ID with from_date filter."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1, from_date=from_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].user_id == 1
        assert result[0].article_id == 1
        mock_session.execute.assert_called_once()

    async def test_get_by_user_id_with_to_date(self, mock_session, sample_history):
        """Test getting history by user ID with to_date filter."""
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1, to_date=to_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].user_id == 1
        mock_session.execute.assert_called_once()

    async def test_get_by_user_id_with_both_dates(self, mock_session, sample_history):
        """Test getting history by user ID with both date filters."""
        from_date = datetime(2024, 1, 1, tzinfo=UTC)
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result = await repo.get_by_user_id(1, from_date=from_date, to_date=to_date)

        assert len(result) == 1
        assert result[0] == sample_history
        assert result[0].article_id == 1
        mock_session.execute.assert_called_once()

    async def test_get_all(self, mock_session, sample_history):
        """Test getting all history entries."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
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

        repo = ArticleViewHistoryRepository(mock_session)
        result, total = await repo.get_all(from_date=from_date)

        assert len(result) == 1
        assert total == 1
        assert result[0] == sample_history
        assert result[0].article_id == 1

    async def test_get_all_with_to_date(self, mock_session, sample_history):
        """Test getting all history with to_date filter."""
        to_date = datetime(2024, 12, 31, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result, total = await repo.get_all(to_date=to_date)

        assert len(result) == 1
        assert total == 1
        assert result[0] == sample_history
        assert result[0].user_id == 1

    async def test_get_all_with_pagination(self, mock_session, sample_history):
        """Test getting all history with pagination."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result, total = await repo.get_all(limit=10, offset=5)

        assert len(result) == 1
        assert total == 1
        assert result[0] == sample_history
        assert result[0].article_id == 1
        assert result[0].user_id == 1

    async def test_get_all_empty(self, mock_session):
        """Test getting all history when empty."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        repo = ArticleViewHistoryRepository(mock_session)
        result, total = await repo.get_all()

        assert len(result) == 0
        assert total == 0
