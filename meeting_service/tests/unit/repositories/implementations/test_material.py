"""Unit tests for Material repository implementation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models.material import MeetingMaterial
from meeting_service.repositories.implementations.material import MaterialRepository


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create a repository instance with mock session."""
    return MaterialRepository(mock_session)


class TestGetByMeeting:
    """Tests for get_by_meeting method (lines 22-24)."""

    async def test_get_by_meeting_returns_materials(self, mock_session, repository):
        """Test get_by_meeting returns materials for a specific meeting."""
        # Arrange
        materials = [
            MeetingMaterial(id=1, meeting_id=1, title="PDF Guide", type="PDF", order=1),
            MeetingMaterial(id=2, meeting_id=1, title="Video Tutorial", type="VIDEO", order=2),
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = materials
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_meeting(1)

        # Assert
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[0].order == 1
        assert result[1].order == 2
        mock_session.execute.assert_called_once()

        # Verify the query includes ordering
        call_args = mock_session.execute.call_args[0][0]
        query_str = str(call_args)
        assert "WHERE" in query_str
        assert "ORDER BY" in query_str

    async def test_get_by_meeting_returns_empty_list(self, mock_session, repository):
        """Test get_by_meeting returns empty list when no materials found."""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_meeting(999)

        # Assert
        assert len(result) == 0
        assert result == []


class TestMaterialRepositoryInheritance:
    """Tests for inherited methods from SqlAlchemyBaseRepository."""

    async def test_material_repository_uses_correct_model(self, mock_session):
        """Test that MaterialRepository is initialized with MeetingMaterial model."""
        # Arrange & Act
        repo = MaterialRepository(mock_session)

        # Assert
        assert repo._model_class == MeetingMaterial
