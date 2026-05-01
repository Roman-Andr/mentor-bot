"""Tests for department document service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import NotFoundException
from knowledge_service.models import DepartmentDocument
from knowledge_service.services.department_document import DepartmentDocumentService


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.department_documents = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def sample_document():
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
        updated_at=None,
    )


class TestCreateDocument:
    """Tests for creating documents."""

    async def test_create_document_success(self, mock_uow, sample_document):
        """Test successful document creation."""
        mock_uow.department_documents.create.return_value = sample_document

        service = DepartmentDocumentService(mock_uow)
        result = await service.create_document(
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
        )

        assert result.title == "Test Document"
        mock_uow.department_documents.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_create_document_minimal_fields(self, mock_uow):
        """Test document creation with minimal required fields."""
        sample_document = DepartmentDocument(
            id=1,
            department_id=1,
            title="Test",
            description=None,
            category="policy",
            file_name="test.pdf",
            file_path="path/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            is_public=False,
            uploaded_by=1,
        )
        mock_uow.department_documents.create.return_value = sample_document

        service = DepartmentDocumentService(mock_uow)
        result = await service.create_document(
            department_id=1,
            title="Test",
            description=None,
            category="policy",
            file_name="test.pdf",
            file_path="path/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            is_public=False,
            uploaded_by=1,
        )

        assert result.title == "Test"
        assert result.description is None


class TestGetDocument:
    """Tests for getting documents."""

    async def test_get_document_success(self, mock_uow, sample_document):
        """Test getting document by ID successfully."""
        mock_uow.department_documents.get_by_id.return_value = sample_document

        service = DepartmentDocumentService(mock_uow)
        result = await service.get_document(1)

        assert result.title == "Test Document"
        mock_uow.department_documents.get_by_id.assert_called_once_with(1)

    async def test_get_document_not_found(self, mock_uow):
        """Test getting non-existent document."""
        mock_uow.department_documents.get_by_id.return_value = None

        service = DepartmentDocumentService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_document(999)


class TestListDocuments:
    """Tests for listing documents."""

    async def test_list_documents_all(self, mock_uow, sample_document):
        """Test listing all documents."""
        mock_uow.department_documents.get_all.return_value = [sample_document]

        service = DepartmentDocumentService(mock_uow)
        result = await service.list_documents()

        assert len(result) == 1
        mock_uow.department_documents.get_all.assert_called_once()

    async def test_list_documents_by_department(self, mock_uow, sample_document):
        """Test listing documents by department."""
        mock_uow.department_documents.get_by_department.return_value = [sample_document]

        service = DepartmentDocumentService(mock_uow)
        result = await service.list_documents(department_id=1)

        assert len(result) == 1
        mock_uow.department_documents.get_by_department.assert_called_once_with(1, category=None, is_public=None)

    async def test_list_documents_by_category(self, mock_uow, sample_document):
        """Test listing documents by category."""
        mock_uow.department_documents.get_by_category.return_value = [sample_document]

        service = DepartmentDocumentService(mock_uow)
        result = await service.list_documents(category="policy")

        assert len(result) == 1
        mock_uow.department_documents.get_by_category.assert_called_once_with("policy")

    async def test_list_documents_with_filters(self, mock_uow, sample_document):
        """Test listing documents with multiple filters."""
        mock_uow.department_documents.get_by_department.return_value = [sample_document]

        service = DepartmentDocumentService(mock_uow)
        result = await service.list_documents(department_id=1, category="policy", is_public=True)

        assert len(result) == 1
        mock_uow.department_documents.get_by_department.assert_called_once_with(1, category="policy", is_public=True)


class TestUpdateDocument:
    """Tests for updating documents."""

    async def test_update_document_title(self, mock_uow, sample_document):
        """Test updating document title."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_uow.department_documents.update.return_value = sample_document

        service = DepartmentDocumentService(mock_uow)
        result = await service.update_document(1, title="Updated Title")

        assert result.title == "Updated Title"
        mock_uow.commit.assert_called_once()

    async def test_update_document_all_fields(self, mock_uow, sample_document):
        """Test updating all document fields."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_uow.department_documents.update.return_value = sample_document

        service = DepartmentDocumentService(mock_uow)
        result = await service.update_document(
            1,
            title="Updated Title",
            description="Updated description",
            category="updated",
            is_public=False,
        )

        assert result.title == "Updated Title"
        assert result.description == "Updated description"
        assert result.category == "updated"
        assert result.is_public is False

    async def test_update_document_not_found(self, mock_uow):
        """Test updating non-existent document."""
        mock_uow.department_documents.get_by_id.return_value = None

        service = DepartmentDocumentService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.update_document(999, title="Updated")

    async def test_update_document_partial_fields(self, mock_uow, sample_document):
        """Test updating document with partial fields."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_uow.department_documents.update.return_value = sample_document

        service = DepartmentDocumentService(mock_uow)
        result = await service.update_document(1, description="New description")

        assert result.description == "New description"
        assert result.title == "Test Document"  # Unchanged


class TestDeleteDocument:
    """Tests for deleting documents."""

    async def test_delete_document_success(self, mock_uow, sample_document):
        """Test successful document deletion."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_uow.department_documents.delete.return_value = True

        service = DepartmentDocumentService(mock_uow)
        await service.delete_document(1)

        mock_uow.department_documents.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    async def test_delete_document_not_found(self, mock_uow):
        """Test deleting non-existent document."""
        mock_uow.department_documents.get_by_id.return_value = None

        service = DepartmentDocumentService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.delete_document(999)
