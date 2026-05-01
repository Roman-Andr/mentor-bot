"""Unit tests for escalation_service/repositories/implementations."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from escalation_service.core.enums import EscalationStatus, EscalationType
from escalation_service.models import EscalationRequest, EscalationStatusHistory, MentorInterventionHistory
from escalation_service.repositories.implementations import EscalationRepository
from escalation_service.repositories.implementations.base import SqlAlchemyBaseRepository
from escalation_service.repositories.implementations.escalation_status_history import EscalationStatusHistoryRepository
from escalation_service.repositories.implementations.mentor_intervention_history import (
    MentorInterventionHistoryRepository,
)


class TestEscalationRepository:
    """Tests for EscalationRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        return AsyncMock()

    @pytest.fixture
    def escalation_repo(self, mock_session):
        """Create an EscalationRepository with mock session."""
        return EscalationRepository(mock_session)

    @pytest.mark.asyncio
    async def test_find_requests_with_no_filters(self, mock_session, escalation_repo):
        """Test find_requests with no filters."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        requests, total = await escalation_repo.find_requests()

        # Assert
        assert requests == []
        assert total == 10
        assert mock_session.execute.await_count == 2  # count + select

    @pytest.mark.asyncio
    async def test_find_requests_with_user_id_filter(self, mock_session, escalation_repo):
        """Test find_requests with user_id filter."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_escalation = MagicMock(spec=EscalationRequest)
        mock_result.scalars().all.return_value = [mock_escalation]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        requests, total = await escalation_repo.find_requests(user_id=100)

        # Assert
        assert len(requests) == 1
        assert total == 5

    @pytest.mark.asyncio
    async def test_find_requests_with_status_filter(self, mock_session, escalation_repo):
        """Test find_requests with status filter."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        _requests, total = await escalation_repo.find_requests(status=EscalationStatus.PENDING)

        # Assert
        assert total == 3

    @pytest.mark.asyncio
    async def test_find_requests_with_type_filter(self, mock_session, escalation_repo):
        """Test find_requests with escalation_type filter."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 2
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        _requests, total = await escalation_repo.find_requests(escalation_type=EscalationType.HR)

        # Assert
        assert total == 2

    @pytest.mark.asyncio
    async def test_find_requests_with_search(self, mock_session, escalation_repo):
        """Test find_requests with search filter."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        _requests, total = await escalation_repo.find_requests(search="urgent")

        # Assert
        assert total == 1

    @pytest.mark.asyncio
    async def test_find_requests_with_assigned_to_filter(self, mock_session, escalation_repo):
        """Test find_requests with assigned_to filter (lines 42-43)."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_escalation = MagicMock(spec=EscalationRequest)
        mock_result.scalars().all.return_value = [mock_escalation]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        requests, total = await escalation_repo.find_requests(assigned_to=200)

        # Assert
        assert len(requests) == 1
        assert total == 3
        # Verify execute was called for both count and select queries
        assert mock_session.execute.await_count == 2

    @pytest.mark.asyncio
    async def test_find_requests_pagination(self, mock_session, escalation_repo):
        """Test find_requests with pagination."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 100
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        _requests, total = await escalation_repo.find_requests(skip=20, limit=10)

        # Assert
        assert total == 100

    @pytest.mark.asyncio
    async def test_find_requests_with_asc_sort_order(self, mock_session, escalation_repo):
        """Test find_requests with ascending sort order (line 82)."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act - use asc sort order to cover line 82
        _requests, total = await escalation_repo.find_requests(sort_by="status", sort_order="asc")

        # Assert
        assert total == 5
        assert mock_session.execute.await_count == 2

    @pytest.mark.asyncio
    async def test_get_user_requests(self, mock_session, escalation_repo):
        """Test get_user_requests returns user requests."""
        # Arrange
        mock_result = MagicMock()
        mock_escalation = MagicMock(spec=EscalationRequest)
        mock_result.scalars().all.return_value = [mock_escalation]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        requests = await escalation_repo.get_user_requests(user_id=100)

        # Assert
        assert len(requests) == 1

    @pytest.mark.asyncio
    async def test_get_user_requests_pagination(self, mock_session, escalation_repo):
        """Test get_user_requests with pagination."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        requests = await escalation_repo.get_user_requests(user_id=100, skip=10, limit=5)

        # Assert
        assert requests == []

    @pytest.mark.asyncio
    async def test_get_assigned_requests(self, mock_session, escalation_repo):
        """Test get_assigned_requests returns assigned requests."""
        # Arrange
        mock_result = MagicMock()
        mock_escalation = MagicMock(spec=EscalationRequest)
        mock_result.scalars().all.return_value = [mock_escalation]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        requests = await escalation_repo.get_assigned_requests(assignee_id=200)

        # Assert
        assert len(requests) == 1


class TestSqlAlchemyBaseRepository:
    """Tests for SqlAlchemyBaseRepository base class."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def base_repo(self, mock_session):
        """Create a base repository with mock session."""

        # Create a concrete class for testing
        class TestRepo(SqlAlchemyBaseRepository[EscalationRequest, int]):
            pass

        return TestRepo(mock_session, EscalationRequest)

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, mock_session, base_repo):
        """Test get_by_id returns entity when found."""
        # Arrange
        mock_entity = MagicMock(spec=EscalationRequest)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await base_repo.get_by_id(1)

        # Assert
        assert result == mock_entity

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_session, base_repo):
        """Test get_by_id returns None when not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await base_repo.get_by_id(999)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, mock_session, base_repo):
        """Test get_all returns all entities."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await base_repo.get_all()

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, mock_session, base_repo):
        """Test get_all with pagination."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await base_repo.get_all(skip=10, limit=5)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_create(self, mock_session, base_repo):
        """Test create adds entity to session."""
        # Arrange
        mock_entity = MagicMock(spec=EscalationRequest)

        # Act
        result = await base_repo.create(mock_entity)

        # Assert
        mock_session.add.assert_called_once_with(mock_entity)
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_entity)
        assert result == mock_entity

    @pytest.mark.asyncio
    async def test_update(self, mock_session, base_repo):
        """Test update flushes and returns entity."""
        # Arrange
        mock_entity = MagicMock(spec=EscalationRequest)

        # Act
        result = await base_repo.update(mock_entity)

        # Assert
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_entity)
        assert result == mock_entity

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_session, base_repo):
        """Test delete returns True when entity is deleted."""
        # Arrange
        mock_entity = MagicMock(spec=EscalationRequest)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await base_repo.delete(1)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(mock_entity)
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_session, base_repo):
        """Test delete returns False when entity not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await base_repo.delete(999)

        # Assert
        assert result is False
        mock_session.delete.assert_not_awaited()


class TestEscalationStatusHistoryRepository:
    """Tests for EscalationStatusHistoryRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def status_history_repo(self, mock_session):
        """Create an EscalationStatusHistoryRepository with mock session."""
        return EscalationStatusHistoryRepository(mock_session)

    @pytest.mark.asyncio
    async def test_create(self, mock_session, status_history_repo):
        """Test create adds entity to session."""
        # Arrange
        mock_entity = MagicMock(spec=EscalationStatusHistory)

        # Act
        result = await status_history_repo.create(mock_entity)

        # Assert
        mock_session.add.assert_called_once_with(mock_entity)
        mock_session.flush.assert_awaited_once()
        assert result == mock_entity

    @pytest.mark.asyncio
    async def test_get_by_escalation_id(self, mock_session, status_history_repo):
        """Test get_by_escalation_id returns history entries."""
        # Arrange
        mock_result = MagicMock()
        mock_entity = MagicMock(spec=EscalationStatusHistory)
        mock_result.scalars().all.return_value = [mock_entity]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await status_history_repo.get_by_escalation_id(escalation_id=1)

        # Assert
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_by_escalation_id_with_date_filters(self, mock_session, status_history_repo):
        """Test get_by_escalation_id with date filters."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        from_date = datetime.now(tz=UTC)
        to_date = datetime.now(tz=UTC)
        result = await status_history_repo.get_by_escalation_id(escalation_id=1, from_date=from_date, to_date=to_date)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, mock_session, status_history_repo):
        """Test get_by_user_id returns history entries."""
        # Arrange
        mock_result = MagicMock()
        mock_entity = MagicMock(spec=EscalationStatusHistory)
        mock_result.scalars().all.return_value = [mock_entity]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await status_history_repo.get_by_user_id(user_id=100)

        # Assert
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_by_user_id_with_date_filters(self, mock_session, status_history_repo):
        """Test get_by_user_id with date filters."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        from_date = datetime.now(tz=UTC)
        to_date = datetime.now(tz=UTC)
        result = await status_history_repo.get_by_user_id(user_id=100, from_date=from_date, to_date=to_date)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all(self, mock_session, status_history_repo):
        """Test get_all returns history entries with total count."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result, total = await status_history_repo.get_all()

        # Assert
        assert result == []
        assert total == 10

    @pytest.mark.asyncio
    async def test_get_all_with_filters(self, mock_session, status_history_repo):
        """Test get_all with date filters and pagination."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        from_date = datetime.now(tz=UTC)
        to_date = datetime.now(tz=UTC)
        result, total = await status_history_repo.get_all(from_date=from_date, to_date=to_date, limit=10, offset=5)

        # Assert
        assert result == []
        assert total == 5


class TestMentorInterventionHistoryRepository:
    """Tests for MentorInterventionHistoryRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def intervention_repo(self, mock_session):
        """Create a MentorInterventionHistoryRepository with mock session."""
        return MentorInterventionHistoryRepository(mock_session)

    @pytest.mark.asyncio
    async def test_create(self, mock_session, intervention_repo):
        """Test create adds entity to session."""
        # Arrange
        mock_entity = MagicMock(spec=MentorInterventionHistory)

        # Act
        result = await intervention_repo.create(mock_entity)

        # Assert
        mock_session.add.assert_called_once_with(mock_entity)
        mock_session.flush.assert_awaited_once()
        assert result == mock_entity

    @pytest.mark.asyncio
    async def test_get_by_escalation_id(self, mock_session, intervention_repo):
        """Test get_by_escalation_id returns intervention entries."""
        # Arrange
        mock_result = MagicMock()
        mock_entity = MagicMock(spec=MentorInterventionHistory)
        mock_result.scalars().all.return_value = [mock_entity]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await intervention_repo.get_by_escalation_id(escalation_id=1)

        # Assert
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_by_escalation_id_with_date_filters(self, mock_session, intervention_repo):
        """Test get_by_escalation_id with date filters."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        from_date = datetime.now(tz=UTC)
        to_date = datetime.now(tz=UTC)
        result = await intervention_repo.get_by_escalation_id(escalation_id=1, from_date=from_date, to_date=to_date)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_mentor_id(self, mock_session, intervention_repo):
        """Test get_by_mentor_id returns intervention entries."""
        # Arrange
        mock_result = MagicMock()
        mock_entity = MagicMock(spec=MentorInterventionHistory)
        mock_result.scalars().all.return_value = [mock_entity]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await intervention_repo.get_by_mentor_id(mentor_id=200)

        # Assert
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_by_mentor_id_with_date_filters(self, mock_session, intervention_repo):
        """Test get_by_mentor_id with date filters."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        from_date = datetime.now(tz=UTC)
        to_date = datetime.now(tz=UTC)
        result = await intervention_repo.get_by_mentor_id(mentor_id=200, from_date=from_date, to_date=to_date)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all(self, mock_session, intervention_repo):
        """Test get_all returns intervention entries with total count."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result, total = await intervention_repo.get_all()

        # Assert
        assert result == []
        assert total == 10

    @pytest.mark.asyncio
    async def test_get_all_with_filters(self, mock_session, intervention_repo):
        """Test get_all with date filters and pagination."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_result.scalars().all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        from_date = datetime.now(tz=UTC)
        to_date = datetime.now(tz=UTC)
        result, total = await intervention_repo.get_all(from_date=from_date, to_date=to_date, limit=10, offset=5)

        # Assert
        assert result == []
        assert total == 5
