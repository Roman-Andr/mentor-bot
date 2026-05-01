"""Tests for Department document repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import DepartmentDocument
from knowledge_service.repositories.implementations.department_document import DepartmentDocumentRepository


class TestDepartmentDocumentRepository:
    """Test Department document repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def sample_document(self):
        """Create a sample department document."""
        return DepartmentDocument(
            id=1,
            department_id=1,
            title="Test Document",
            description="Test description",
            category="policy",
            file_name="test.pdf",
            file_path="department-documents/1/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            is_public=True,
            uploaded_by=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def test_get_by_department(self, mock_session, sample_document):
        """Test getting documents by department."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_document]
        mock_session.execute.return_value = mock_result

        repo = DepartmentDocumentRepository(mock_session)
        result = await repo.get_by_department(1)

        assert len(result) == 1
        assert result[0] == sample_document

    async def test_get_by_department_with_category(self, mock_session, sample_document):
        """Test getting documents by department with category filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_document]
        mock_session.execute.return_value = mock_result

        repo = DepartmentDocumentRepository(mock_session)
        result = await repo.get_by_department(1, category="policy")

        assert len(result) == 1

    async def test_get_by_department_with_is_public(self, mock_session, sample_document):
        """Test getting documents by department with is_public filter."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_document]
        mock_session.execute.return_value = mock_result

        repo = DepartmentDocumentRepository(mock_session)
        result = await repo.get_by_department(1, is_public=True)

        assert len(result) == 1

    async def test_get_by_department_with_all_filters(self, mock_session, sample_document):
        """Test getting documents by department with all filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_document]
        mock_session.execute.return_value = mock_result

        repo = DepartmentDocumentRepository(mock_session)
        result = await repo.get_by_department(1, category="policy", is_public=True)

        assert len(result) == 1

    async def test_get_by_department_empty(self, mock_session):
        """Test getting documents by department - empty result."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        repo = DepartmentDocumentRepository(mock_session)
        result = await repo.get_by_department(999)

        assert result == []

    async def test_get_by_category(self, mock_session, sample_document):
        """Test getting documents by category."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_document]
        mock_session.execute.return_value = mock_result

        repo = DepartmentDocumentRepository(mock_session)
        result = await repo.get_by_category("policy")

        assert len(result) == 1
        assert result[0] == sample_document

    async def test_get_by_category_empty(self, mock_session):
        """Test getting documents by category - empty result."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        repo = DepartmentDocumentRepository(mock_session)
        result = await repo.get_by_category("nonexistent")

        assert result == []
