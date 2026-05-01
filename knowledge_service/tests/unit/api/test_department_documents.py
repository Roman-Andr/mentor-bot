"""Tests for department documents API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from knowledge_service.core import NotFoundException, PermissionDenied, ValidationException
from knowledge_service.models import DepartmentDocument
from knowledge_service.schemas import DepartmentDocumentUpdate


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.department_documents = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def mock_current_user_hr():
    """Create a mock HR user."""
    user = MagicMock()
    user.id = 1
    user.role = "HR"
    user.department_id = 1
    return user


@pytest.fixture
def mock_current_user_regular():
    """Create a mock regular user."""
    user = MagicMock()
    user.id = 2
    user.role = "USER"
    user.department_id = 2
    return user


@pytest.fixture
def sample_document():
    """Create a sample department document."""
    from datetime import UTC, datetime

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


class TestListDepartmentDocuments:
    """Tests for listing department documents."""

    async def test_list_documents_as_hr(self, mock_uow, mock_current_user_hr, sample_document):
        """Test listing documents as HR user."""
        mock_uow.department_documents.get_all.return_value = [sample_document]

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=None,
            category=None,
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.total == 1
        assert len(result.documents) == 1
        mock_uow.department_documents.get_all.assert_called_once()

    async def test_list_documents_as_regular_user_own_department(
        self, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test listing documents as regular user for own department."""
        sample_document.department_id = 2
        mock_uow.department_documents.get_by_department.return_value = [sample_document]
        mock_uow.department_documents.get_all.return_value = []

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=2,
            category=None,
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.total == 1
        mock_uow.department_documents.get_by_department.assert_called_once()

    async def test_list_documents_as_regular_user_with_public_docs(
        self, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test listing documents includes public docs for regular users."""
        sample_document.department_id = 2
        public_doc = DepartmentDocument(
            id=2,
            department_id=3,
            title="Public Doc",
            description="Public",
            category="policy",
            file_name="public.pdf",
            file_path="dept/3/public.pdf",
            file_size=1024,
            mime_type="application/pdf",
            is_public=True,
            uploaded_by=1,
            created_at=datetime.now(UTC),
            updated_at=None,
        )
        mock_uow.department_documents.get_by_department.return_value = [sample_document]
        mock_uow.department_documents.get_all.return_value = [public_doc]

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=2,
            category=None,
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.total == 2
        mock_uow.department_documents.get_by_department.assert_called_once()
        mock_uow.department_documents.get_all.assert_called_once()

    async def test_list_documents_as_regular_user_with_category_filter(
        self, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test listing documents with category filter for regular users."""
        sample_document.department_id = 2
        sample_document.category = "policy"
        mock_uow.department_documents.get_by_department.return_value = [sample_document]
        mock_uow.department_documents.get_all.return_value = []

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=2,
            category="policy",
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.total == 1
        mock_uow.department_documents.get_by_department.assert_called_once_with(2, category="policy")

    async def test_list_documents_regular_user_with_category_and_public_docs(
        self, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test regular user with category filter includes matching public docs."""
        sample_document.department_id = 2
        sample_document.category = "policy"
        public_doc = DepartmentDocument(
            id=2,
            department_id=3,
            title="Public Policy",
            description="Public",
            category="policy",
            file_name="public.pdf",
            file_path="dept/3/public.pdf",
            file_size=1024,
            mime_type="application/pdf",
            is_public=True,
            uploaded_by=1,
            created_at=datetime.now(UTC),
            updated_at=None,
        )
        other_public_doc = DepartmentDocument(
            id=3,
            department_id=3,
            title="Other Public",
            description="Other",
            category="other",
            file_name="other.pdf",
            file_path="dept/3/other.pdf",
            file_size=1024,
            mime_type="application/pdf",
            is_public=True,
            uploaded_by=1,
            created_at=datetime.now(UTC),
            updated_at=None,
        )
        mock_uow.department_documents.get_by_department.return_value = [sample_document]
        mock_uow.department_documents.get_all.return_value = [public_doc, other_public_doc]

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=2,
            category="policy",
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.total == 2  # department doc + matching public doc

    async def test_list_documents_as_regular_user_other_department_denied(self, mock_uow, mock_current_user_regular):
        """Test listing documents from other department is denied for regular users."""
        from knowledge_service.api.endpoints.department_documents import list_department_documents

        with pytest.raises(PermissionDenied):
            await list_department_documents(
                department_id=1,  # Different from user's department_id (2)
                category=None,
                is_public=None,
                uow=mock_uow,
                current_user=mock_current_user_regular,
            )

    async def test_list_documents_as_regular_user_no_department_shows_public(
        self, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test listing public documents when user has no department."""
        mock_current_user_regular.department_id = None
        sample_document.is_public = True
        mock_uow.department_documents.get_all.return_value = [sample_document]

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=None,
            category=None,
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.total == 1

    async def test_list_documents_as_regular_user_no_department_with_category(
        self, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test listing public documents with category filter when user has no department."""
        mock_current_user_regular.department_id = None
        sample_document.is_public = True
        sample_document.category = "policy"
        other_doc = DepartmentDocument(
            id=2,
            department_id=3,
            title="Other Doc",
            description="Other",
            category="other",
            file_name="other.pdf",
            file_path="dept/3/other.pdf",
            file_size=1024,
            mime_type="application/pdf",
            is_public=True,
            uploaded_by=1,
            created_at=datetime.now(UTC),
            updated_at=None,
        )
        mock_uow.department_documents.get_all.return_value = [sample_document, other_doc]

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=None,
            category="policy",
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.total == 1
        assert result.documents[0].category == "policy"

    async def test_list_documents_as_regular_user_auto_department_id(
        self, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test listing documents as regular user auto-sets department_id."""
        sample_document.department_id = 2
        mock_uow.department_documents.get_by_department.return_value = [sample_document]
        mock_uow.department_documents.get_all.return_value = []

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=None,  # Should auto-set to user's department_id (2)
            category=None,
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.total == 1
        mock_uow.department_documents.get_by_department.assert_called_once_with(2, category=None)

    async def test_list_documents_with_filters(self, mock_uow, mock_current_user_hr, sample_document):
        """Test listing documents with category filter."""
        mock_uow.department_documents.get_by_category.return_value = [sample_document]

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=None,
            category="policy",
            is_public=None,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.total == 1
        mock_uow.department_documents.get_by_category.assert_called_once_with("policy")

    async def test_list_documents_hr_with_department_and_filters(self, mock_uow, mock_current_user_hr, sample_document):
        """Test HR listing documents with department_id, category and is_public filters."""
        mock_uow.department_documents.get_by_department.return_value = [sample_document]

        from knowledge_service.api.endpoints.department_documents import list_department_documents

        result = await list_department_documents(
            department_id=1,
            category="policy",
            is_public=True,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.total == 1
        mock_uow.department_documents.get_by_department.assert_called_once_with(1, category="policy", is_public=True)


class TestGetDepartmentDocument:
    """Tests for getting a department document."""

    async def test_get_document_as_owner(self, mock_uow, mock_current_user_hr, sample_document):
        """Test getting document as HR user."""
        sample_document.department_id = 1
        mock_uow.department_documents.get_by_id.return_value = sample_document

        from knowledge_service.api.endpoints.department_documents import get_department_document

        result = await get_department_document(
            document_id=1,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.title == "Test Document"

    async def test_get_document_not_found(self, mock_uow, mock_current_user_hr):
        """Test getting non-existent document."""
        mock_uow.department_documents.get_by_id.return_value = None

        from knowledge_service.api.endpoints.department_documents import get_department_document

        with pytest.raises(NotFoundException):
            await get_department_document(
                document_id=999,
                uow=mock_uow,
                current_user=mock_current_user_hr,
            )

    async def test_get_document_access_denied(self, mock_uow, mock_current_user_regular, sample_document):
        """Test accessing private document from other department is denied."""
        sample_document.department_id = 1  # Different from user's department
        sample_document.is_public = False
        mock_uow.department_documents.get_by_id.return_value = sample_document

        from knowledge_service.api.endpoints.department_documents import get_department_document

        with pytest.raises(PermissionDenied):
            await get_department_document(
                document_id=1,
                uow=mock_uow,
                current_user=mock_current_user_regular,
            )

    async def test_get_public_document_allowed(self, mock_uow, mock_current_user_regular, sample_document):
        """Test accessing public document is allowed."""
        sample_document.department_id = 1
        sample_document.is_public = True
        mock_uow.department_documents.get_by_id.return_value = sample_document

        from knowledge_service.api.endpoints.department_documents import get_department_document

        result = await get_department_document(
            document_id=1,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.title == "Test Document"


class TestCreateDepartmentDocument:
    """Tests for creating department documents."""

    @patch("knowledge_service.api.endpoints.department_documents.validate_file_size")
    @patch("knowledge_service.api.endpoints.department_documents.validate_file_type")
    @patch("knowledge_service.api.endpoints.department_documents.validate_filename")
    @patch("knowledge_service.api.endpoints.department_documents.get_storage_service")
    async def test_create_document_success(
        self,
        mock_get_storage,
        mock_validate_filename,
        mock_validate_file_type,
        mock_validate_file_size,
        mock_uow,
        mock_current_user_hr,
        sample_document,
    ):
        """Test successful document creation."""
        mock_validate_file_size.return_value = True
        mock_validate_file_type.return_value = True
        mock_validate_filename.return_value = "safe.pdf"
        mock_storage = AsyncMock()
        mock_storage.upload_file = AsyncMock()
        mock_get_storage.return_value = mock_storage
        mock_uow.department_documents.create.return_value = sample_document

        from knowledge_service.api.endpoints.department_documents import create_department_document

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.size = 1024
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"file content")

        result = await create_department_document(
            uow=mock_uow,
            current_user=mock_current_user_hr,
            department_id=1,
            title="Test Document",
            description="Test description",
            category="policy",
            is_public=True,
            file=mock_file,
        )

        assert result.title == "Test Document"
        mock_uow.commit.assert_called_once()

    async def test_create_document_no_file(self, mock_uow, mock_current_user_hr):
        """Test document creation without file raises error."""
        from knowledge_service.api.endpoints.department_documents import create_department_document

        with pytest.raises(ValidationException):
            await create_department_document(
                uow=mock_uow,
                current_user=mock_current_user_hr,
                department_id=1,
                title="Test Document",
                description=None,
                category="policy",
                is_public=True,
                file=None,
            )

    @patch("knowledge_service.api.endpoints.department_documents.validate_file_size")
    async def test_create_document_file_too_large(self, mock_validate_file_size, mock_uow, mock_current_user_hr):
        """Test document creation with oversized file raises error."""
        mock_validate_file_size.return_value = False

        from knowledge_service.api.endpoints.department_documents import create_department_document

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.size = 100 * 1024 * 1024  # Large file

        with pytest.raises(ValidationException):
            await create_department_document(
                uow=mock_uow,
                current_user=mock_current_user_hr,
                department_id=1,
                title="Test Document",
                description=None,
                category="policy",
                is_public=True,
                file=mock_file,
            )

    @patch("knowledge_service.api.endpoints.department_documents.validate_file_size")
    @patch("knowledge_service.api.endpoints.department_documents.validate_file_type")
    async def test_create_document_invalid_type(
        self, mock_validate_file_type, mock_validate_file_size, mock_uow, mock_current_user_hr
    ):
        """Test document creation with invalid file type raises error."""
        mock_validate_file_size.return_value = True
        mock_validate_file_type.return_value = False

        from knowledge_service.api.endpoints.department_documents import create_department_document

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.exe"
        mock_file.size = 1024

        with pytest.raises(ValidationException):
            await create_department_document(
                uow=mock_uow,
                current_user=mock_current_user_hr,
                department_id=1,
                title="Test Document",
                description=None,
                category="policy",
                is_public=True,
                file=mock_file,
            )

    @patch("knowledge_service.api.endpoints.department_documents.validate_file_size")
    @patch("knowledge_service.api.endpoints.department_documents.validate_file_type")
    @patch("knowledge_service.api.endpoints.department_documents.validate_filename")
    @patch("knowledge_service.api.endpoints.department_documents.get_storage_service")
    async def test_create_document_storage_error(
        self,
        mock_get_storage_service,
        mock_validate_filename,
        mock_validate_file_type,
        mock_validate_file_size,
        mock_uow,
        mock_current_user_hr,
    ):
        """Test document creation with S3 storage error raises HTTPException."""
        from knowledge_service.api.endpoints.department_documents import create_department_document
        from knowledge_service.utils.storage import StorageError

        mock_validate_file_size.return_value = True
        mock_validate_file_type.return_value = True
        mock_validate_filename.return_value = "test.pdf"

        mock_storage = AsyncMock()
        mock_storage.upload_file = AsyncMock(side_effect=StorageError("S3 upload failed"))
        mock_get_storage_service.return_value = mock_storage

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.size = 1024
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"file content")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await create_department_document(
                uow=mock_uow,
                current_user=mock_current_user_hr,
                department_id=1,
                title="Test Document",
                description=None,
                category="policy",
                is_public=True,
                file=mock_file,
            )

        assert exc_info.value.status_code == 500
        assert "File upload failed" in exc_info.value.detail


class TestUpdateDepartmentDocument:
    """Tests for updating department documents."""

    async def test_update_document_success(self, mock_uow, mock_current_user_hr, sample_document):
        """Test successful document update."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_uow.department_documents.update.return_value = sample_document

        from knowledge_service.api.endpoints.department_documents import update_department_document

        update_data = DepartmentDocumentUpdate(title="Updated Title")
        result = await update_department_document(
            document_id=1,
            update_data=update_data,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.title == "Updated Title"
        mock_uow.commit.assert_called_once()

    async def test_update_document_not_found(self, mock_uow, mock_current_user_hr):
        """Test updating non-existent document."""
        mock_uow.department_documents.get_by_id.return_value = None

        from knowledge_service.api.endpoints.department_documents import update_department_document

        update_data = DepartmentDocumentUpdate(title="Updated")
        with pytest.raises(NotFoundException):
            await update_department_document(
                document_id=999,
                update_data=update_data,
                uow=mock_uow,
                current_user=mock_current_user_hr,
            )

    async def test_update_document_all_fields(self, mock_uow, mock_current_user_hr, sample_document):
        """Test updating all document fields."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_uow.department_documents.update.return_value = sample_document

        from knowledge_service.api.endpoints.department_documents import update_department_document

        update_data = DepartmentDocumentUpdate(
            title="Updated Title",
            description="Updated description",
            category="updated",
            is_public=False,
        )
        result = await update_department_document(
            document_id=1,
            update_data=update_data,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.title == "Updated Title"
        assert result.description == "Updated description"


class TestDeleteDepartmentDocument:
    """Tests for deleting department documents."""

    @patch("knowledge_service.api.endpoints.department_documents.get_storage_service")
    async def test_delete_document_success(self, mock_get_storage, mock_uow, mock_current_user_hr, sample_document):
        """Test successful document deletion."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_uow.department_documents.delete.return_value = True
        mock_storage = AsyncMock()
        mock_storage.delete_file = AsyncMock()
        mock_get_storage.return_value = mock_storage

        from knowledge_service.api.endpoints.department_documents import delete_department_document

        result = await delete_department_document(
            document_id=1,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.message == "Document deleted successfully"
        mock_storage.delete_file.assert_called_once()
        mock_uow.commit.assert_called_once()

    @patch("knowledge_service.api.endpoints.department_documents.get_storage_service")
    async def test_delete_document_s3_error_continues(
        self, mock_get_storage, mock_uow, mock_current_user_hr, sample_document
    ):
        """Test document deletion continues even if S3 deletion fails."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_uow.department_documents.delete.return_value = True
        mock_storage = AsyncMock()
        from knowledge_service.utils.storage import StorageError

        mock_storage.delete_file = AsyncMock(side_effect=StorageError("S3 error"))
        mock_get_storage.return_value = mock_storage

        from knowledge_service.api.endpoints.department_documents import delete_department_document

        result = await delete_department_document(
            document_id=1,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.message == "Document deleted successfully"
        mock_uow.commit.assert_called_once()

    async def test_delete_document_not_found(self, mock_uow, mock_current_user_hr):
        """Test deleting non-existent document."""
        mock_uow.department_documents.get_by_id.return_value = None

        from knowledge_service.api.endpoints.department_documents import delete_department_document

        with pytest.raises(NotFoundException):
            await delete_department_document(
                document_id=999,
                uow=mock_uow,
                current_user=mock_current_user_hr,
            )


class TestDownloadDepartmentDocument:
    """Tests for downloading department documents."""

    @patch("knowledge_service.api.endpoints.department_documents.get_storage_service")
    async def test_download_document_success(self, mock_get_storage, mock_uow, mock_current_user_hr, sample_document):
        """Test successful document download."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_storage = MagicMock()
        mock_storage.get_presigned_url.return_value = "https://example.com/presigned-url"
        mock_get_storage.return_value = mock_storage

        from knowledge_service.api.endpoints.department_documents import download_department_document

        result = await download_department_document(
            document_id=1,
            uow=mock_uow,
            current_user=mock_current_user_hr,
        )

        assert result.status_code == 307  # Redirect

    async def test_download_document_not_found(self, mock_uow, mock_current_user_hr):
        """Test downloading non-existent document."""
        mock_uow.department_documents.get_by_id.return_value = None

        from knowledge_service.api.endpoints.department_documents import download_department_document

        with pytest.raises(NotFoundException):
            await download_department_document(
                document_id=999,
                uow=mock_uow,
                current_user=mock_current_user_hr,
            )

    @patch("knowledge_service.api.endpoints.department_documents.get_storage_service")
    async def test_download_document_access_denied(
        self, mock_get_storage, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test downloading private document from other department is denied."""
        sample_document.department_id = 1
        sample_document.is_public = False
        mock_uow.department_documents.get_by_id.return_value = sample_document

        from knowledge_service.api.endpoints.department_documents import download_department_document

        with pytest.raises(PermissionDenied):
            await download_department_document(
                document_id=1,
                uow=mock_uow,
                current_user=mock_current_user_regular,
            )

    @patch("knowledge_service.api.endpoints.department_documents.get_storage_service")
    async def test_download_public_document_allowed(
        self, mock_get_storage, mock_uow, mock_current_user_regular, sample_document
    ):
        """Test downloading public document is allowed."""
        sample_document.department_id = 1
        sample_document.is_public = True
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_storage = MagicMock()
        mock_storage.get_presigned_url.return_value = "https://example.com/presigned-url"
        mock_get_storage.return_value = mock_storage

        from knowledge_service.api.endpoints.department_documents import download_department_document

        result = await download_department_document(
            document_id=1,
            uow=mock_uow,
            current_user=mock_current_user_regular,
        )

        assert result.status_code == 307

    @patch("knowledge_service.api.endpoints.department_documents.get_storage_service")
    async def test_download_document_s3_error(self, mock_get_storage, mock_uow, mock_current_user_hr, sample_document):
        """Test download when S3 returns error."""
        mock_uow.department_documents.get_by_id.return_value = sample_document
        mock_storage = MagicMock()
        from knowledge_service.utils.storage import StorageError

        mock_storage.get_presigned_url.side_effect = StorageError("S3 error")
        mock_get_storage.return_value = mock_storage

        from knowledge_service.api.endpoints.department_documents import download_department_document

        with pytest.raises(NotFoundException):
            await download_department_document(
                document_id=1,
                uow=mock_uow,
                current_user=mock_current_user_hr,
            )


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_object_name(self):
        """Test object name generation."""
        from knowledge_service.api.endpoints.department_documents import _get_object_name

        result = _get_object_name(1, "test.pdf")
        assert result == "department-documents/1/test.pdf"

    def test_get_object_name_with_spaces(self):
        """Test object name generation with spaces in filename."""
        from knowledge_service.api.endpoints.department_documents import _get_object_name

        result = _get_object_name(2, "my document.pdf")
        assert result == "department-documents/2/my document.pdf"
