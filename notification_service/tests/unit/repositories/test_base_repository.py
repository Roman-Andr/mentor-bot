"""Unit tests for notification_service/repositories/implementations/base.py."""

from collections.abc import Sequence
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.core.enums import NotificationChannel, NotificationStatus, NotificationType
from notification_service.models import Notification
from notification_service.repositories.implementations.base import SqlAlchemyBaseRepository


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock AsyncSession."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session: MagicMock) -> SqlAlchemyBaseRepository:
    """Create a SqlAlchemyBaseRepository with mock session using Notification model."""
    return SqlAlchemyBaseRepository(mock_session, Notification)


@pytest.fixture
def sample_notification() -> Notification:
    """Create a sample Notification for testing."""
    return Notification(
        id=1,
        user_id=42,
        type=NotificationType.GENERAL,
        channel=NotificationChannel.EMAIL,
        body="Test body",
    )


class TestSqlAlchemyBaseRepositoryInit:
    """Tests for SqlAlchemyBaseRepository initialization."""

    def test_stores_session(self, mock_session: MagicMock) -> None:
        """Repository stores the session."""
        repo = SqlAlchemyBaseRepository(mock_session, Notification)
        assert repo._session is mock_session

    def test_stores_model_class(self, mock_session: MagicMock) -> None:
        """Repository stores the model class."""
        repo = SqlAlchemyBaseRepository(mock_session, Notification)
        assert repo._model_class is Notification


class TestGetById:
    """Tests for get_by_id method."""

    async def test_returns_entity_when_found(
        self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Returns entity when found by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_notification
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(1)

        assert result is sample_notification
        mock_session.execute.assert_awaited_once()

    async def test_returns_none_when_not_found(self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock) -> None:
        """Returns None when entity not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(999)

        assert result is None
        mock_session.execute.assert_awaited_once()


class TestGetAll:
    """Tests for get_all method."""

    async def test_returns_all_entities(
        self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Returns all entities with default pagination."""
        expected = [sample_notification, Notification(id=2, user_id=43, type=NotificationType.GENERAL, channel=NotificationChannel.TELEGRAM, body="Body 2")]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = expected
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert result == expected
        mock_session.execute.assert_awaited_once()

    async def test_respects_skip_parameter(self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock) -> None:
        """Respects skip parameter in query."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        with patch("notification_service.repositories.implementations.base.select") as mock_select:
            mock_stmt = MagicMock()
            mock_stmt.offset.return_value = mock_stmt
            mock_stmt.limit.return_value = mock_stmt
            mock_select.return_value = mock_stmt

            await repository.get_all(skip=10)

            mock_stmt.offset.assert_called_once_with(10)

    async def test_respects_limit_parameter(self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock) -> None:
        """Respects limit parameter in query."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        with patch("notification_service.repositories.implementations.base.select") as mock_select:
            mock_stmt = MagicMock()
            mock_stmt.offset.return_value = mock_stmt
            mock_stmt.limit.return_value = mock_stmt
            mock_select.return_value = mock_stmt

            await repository.get_all(limit=5)

            mock_stmt.limit.assert_called_once_with(5)

    async def test_returns_empty_sequence_when_no_entities(self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock) -> None:
        """Returns empty sequence when no entities exist."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert result == []
        assert isinstance(result, Sequence)


class TestCreate:
    """Tests for create method."""

    async def test_adds_entity_to_session(
        self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Adds entity to session."""
        await repository.create(sample_notification)

        mock_session.add.assert_called_once_with(sample_notification)

    async def test_flushes_and_refreshes_entity(
        self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Flushes and refreshes the entity."""
        await repository.create(sample_notification)

        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(sample_notification)

    async def test_returns_entity(
        self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Returns the created entity."""
        result = await repository.create(sample_notification)

        assert result is sample_notification
        assert result.id == 1


class TestUpdate:
    """Tests for update method."""

    async def test_flushes_and_refreshes_entity(
        self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Flushes and refreshes the entity."""
        await repository.update(sample_notification)

        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(sample_notification)

    async def test_returns_entity(
        self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Returns the updated entity."""
        sample_notification.body = "updated body"

        result = await repository.update(sample_notification)

        assert result is sample_notification
        assert result.body == "updated body"


class TestDelete:
    """Tests for delete method."""

    async def test_deletes_entity_when_found(
        self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock, sample_notification: Notification
    ) -> None:
        """Deletes entity when found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_notification
        mock_session.execute.return_value = mock_result

        result = await repository.delete(1)

        assert result is True
        mock_session.delete.assert_awaited_once_with(sample_notification)
        mock_session.flush.assert_awaited_once()

    async def test_returns_false_when_not_found(self, repository: SqlAlchemyBaseRepository, mock_session: MagicMock) -> None:
        """Returns False when entity not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.flush.assert_not_called()
