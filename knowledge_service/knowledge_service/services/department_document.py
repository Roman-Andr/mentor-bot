"""Department document management service with repository pattern."""

from knowledge_service.core import NotFoundException
from knowledge_service.models import DepartmentDocument
from knowledge_service.repositories import IUnitOfWork


class DepartmentDocumentService:
    """Service for department document management operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize department document service with Unit of Work."""
        self._uow = uow

    async def create_document(
        self,
        department_id: int,
        title: str,
        description: str | None,
        category: str,
        file_name: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        is_public: bool,
        uploaded_by: int,
    ) -> DepartmentDocument:
        """Create new department document."""
        document = DepartmentDocument(
            department_id=department_id,
            title=title,
            description=description,
            category=category,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            is_public=is_public,
            uploaded_by=uploaded_by,
        )
        created = await self._uow.department_documents.create(document)
        await self._uow.commit()
        return created

    async def get_document(self, document_id: int) -> DepartmentDocument:
        """Get document by ID."""
        document = await self._uow.department_documents.get_by_id(document_id)
        if not document:
            msg = "Department document"
            raise NotFoundException(msg)
        return document

    async def list_documents(
        self,
        department_id: int | None = None,
        category: str | None = None,
        is_public: bool | None = None,
    ) -> list[DepartmentDocument]:
        """List documents with optional filters."""
        if department_id:
            documents = await self._uow.department_documents.get_by_department(
                department_id, category=category, is_public=is_public
            )
        elif category:
            documents = await self._uow.department_documents.get_by_category(category)
        else:
            documents = await self._uow.department_documents.get_all()
        return list(documents)

    async def update_document(
        self,
        document_id: int,
        title: str | None = None,
        description: str | None = None,
        category: str | None = None,
        is_public: bool | None = None,
    ) -> DepartmentDocument:
        """Update document metadata."""
        document = await self.get_document(document_id)
        if title is not None:
            document.title = title
        if description is not None:
            document.description = description
        if category is not None:
            document.category = category
        if is_public is not None:
            document.is_public = is_public
        updated = await self._uow.department_documents.update(document)
        await self._uow.commit()
        return updated

    async def delete_document(self, document_id: int) -> None:
        """Delete document."""
        await self.get_document(document_id)
        await self._uow.department_documents.delete(document_id)
        await self._uow.commit()
