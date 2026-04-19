"""Unit tests for tasks API endpoints."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile

from checklists_service.api.deps import UserInfo
from checklists_service.api.endpoints import tasks
from checklists_service.core import NotFoundException, ValidationException
from checklists_service.core.enums import TaskStatus
from checklists_service.schemas import (
    TaskBulkUpdate,
    TaskProgress,
    TaskUpdate,
)


@pytest.fixture
def sample_user():
    """Create sample user."""
    return UserInfo({
        "id": 1, "email": "test@example.com", "role": "EMPLOYEE",
        "is_active": True, "employee_id": "EMP001"
    })


@pytest.fixture
def sample_hr_user():
    """Create sample HR user."""
    return UserInfo({
        "id": 10, "email": "hr@example.com", "role": "HR",
        "is_active": True, "employee_id": "HR001"
    })


@pytest.fixture
def sample_mentor_user():
    """Create sample mentor user."""
    return UserInfo({
        "id": 2, "email": "mentor@example.com", "role": "MENTOR",
        "is_active": True, "employee_id": "MEN001"
    })


@pytest.fixture
def sample_task():
    """Create sample task."""
    now = datetime.now(UTC)
    return MagicMock(
        id=1,
        checklist_id=1,
        template_task_id=1,
        title="Complete Documentation",
        description="Read and sign documentation",
        category="DOCUMENTATION",
        order=0,
        assignee_id=2,
        assignee_role="MENTOR",
        due_date=now + timedelta(days=3),
        depends_on=[],
        status=TaskStatus.PENDING,
        started_at=None,
        completed_at=None,
        completed_by=None,
        completion_notes=None,
        attachments=[],
        blocks=[],
        created_at=now,
        updated_at=None,
    )


class TestGetChecklistTasks:
    """Test GET /tasks/checklist/{checklist_id} endpoint."""

    async def test_get_checklist_tasks(self, sample_user, sample_task) -> None:
        """Test getting tasks for a checklist."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_checklist_tasks = AsyncMock(return_value=[sample_task])

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(
                id=1, user_id=1, status="IN_PROGRESS"
            ))

            result = await tasks.get_checklist_tasks(
                checklist_id=1,
                uow=uow,
                current_user=sample_user,
            )

            assert len(result) == 1
            assert result[0].checklist_id == 1

    async def test_get_checklist_tasks_not_found(self, sample_user) -> None:
        """Test 404 raised when checklist not found (line 112)."""
        uow = MagicMock()

        from fastapi import HTTPException

        from checklists_service.core import NotFoundException

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_checklist_tasks = AsyncMock(return_value=[])

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(side_effect=NotFoundException("Checklist"))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.get_checklist_tasks(
                    checklist_id=999,
                    uow=uow,
                    current_user=sample_user,
                )

            # Should raise HTTPException with 404 status
            assert exc_info.value.status_code == 404


class TestGetMyAssignedTasks:
    """Test GET /tasks/assigned-to-me endpoint."""

    async def test_get_my_assigned_tasks(self, sample_mentor_user, sample_task) -> None:
        """Test getting tasks assigned to current user."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_assigned_tasks = AsyncMock(return_value=([sample_task], 1))

            result = await tasks.get_my_assigned_tasks(
                uow=uow,
                current_user=sample_mentor_user,
            )

            assert len(result) == 1


class TestUpdateTask:
    """Test PUT /tasks/{task_id} endpoint."""

    async def test_update_task_success(self, sample_user, sample_task) -> None:
        """Test successful task update."""
        uow = MagicMock()

        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS, assignee_id=3)

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=sample_task)

            updated_task = MagicMock(
                id=1, checklist_id=1, template_task_id=1,
                title="Complete Documentation", description="Read and sign documentation",
                category="DOCUMENTATION", order=0, assignee_id=3, assignee_role="MENTOR",
                due_date=datetime.now(UTC) + timedelta(days=3),
                depends_on=[], status=TaskStatus.IN_PROGRESS,
                started_at=datetime.now(UTC), completed_at=None, completed_by=None,
                completion_notes=None, attachments=[], blocks=[],
                created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
            )
            task_instance.update_task = AsyncMock(return_value=updated_task)

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(
                id=1, user_id=1, assignee_id=2
            ))

            result = await tasks.update_task(
                task_id=1,
                task_data=update_data,
                uow=uow,
                current_user=sample_user,
            )

            assert result.id == 1


class TestUpdateTaskProgress:
    """Test POST /tasks/{task_id}/progress endpoint."""

    async def test_update_task_progress(self, sample_user, sample_task) -> None:
        """Test updating task progress."""
        uow = MagicMock()

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.COMPLETED,
            progress_percentage=100,
            notes="Task completed successfully",
            attachments=[],
        )

        sample_task.assignee_id = 1

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_task = AsyncMock(return_value=sample_task)

            updated_task = MagicMock(
                id=1, checklist_id=1, template_task_id=1,
                title="Complete Documentation", description="Read and sign documentation",
                category="DOCUMENTATION", order=0, assignee_id=1, assignee_role="MENTOR",
                due_date=datetime.now(UTC) + timedelta(days=3),
                depends_on=[], status=TaskStatus.COMPLETED,
                started_at=datetime.now(UTC), completed_at=datetime.now(UTC), completed_by=1,
                completion_notes="Task completed successfully", attachments=[],
                blocks=[], created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
            )
            instance.update_task_progress = AsyncMock(return_value=updated_task)

            result = await tasks.update_task_progress(
                task_id=1,
                progress_data=progress_data,
                uow=uow,
                current_user=sample_user,
            )

            assert result.status == TaskStatus.COMPLETED


class TestCompleteTask:
    """Test POST /tasks/{task_id}/complete endpoint."""

    async def test_complete_task(self, sample_user) -> None:
        """Test completing a task."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance

            completed_task = MagicMock(
                id=1, checklist_id=1, template_task_id=1,
                title="Complete Documentation", description="Read and sign documentation",
                category="DOCUMENTATION", order=0, assignee_id=1, assignee_role="MENTOR",
                due_date=datetime.now(UTC) + timedelta(days=3),
                depends_on=[], status=TaskStatus.COMPLETED,
                started_at=datetime.now(UTC), completed_at=datetime.now(UTC), completed_by=1,
                completion_notes="Done!", attachments=[], blocks=[],
                created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
            )
            instance.complete_task = AsyncMock(return_value=completed_task)

            result = await tasks.complete_task(
                task_id=1,
                uow=uow,
                current_user=sample_user,
                completion_notes="Done!",
            )

            assert result.status == TaskStatus.COMPLETED
            assert result.completed_by == 1


class TestBulkUpdateTasks:
    """Test POST /tasks/bulk-update endpoint."""

    async def test_bulk_update_tasks(self, sample_hr_user) -> None:
        """Test bulk updating tasks."""
        uow = MagicMock()

        bulk_data = TaskBulkUpdate(
            task_ids=[1, 2, 3],
            status=TaskStatus.IN_PROGRESS,
            assignee_id=5,
        )

        # Return proper MessageResponse - construct the expected message
        expected_message = f"Updated {len(bulk_data.task_ids)} tasks"

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.bulk_update_tasks = AsyncMock(return_value=None)

            result = await tasks.bulk_update_tasks(
                bulk_data=bulk_data,
                uow=uow,
                _current_user=sample_hr_user,
            )

            # Should return MessageResponse with expected message
            assert result.message == expected_message


class TestGetTaskDependencies:
    """Test GET /tasks/{task_id}/dependencies endpoint."""

    async def test_get_task_dependencies(self, sample_user) -> None:
        """Test getting task dependencies."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))
            task_instance.get_task_dependencies = AsyncMock(return_value={
                "task_id": 1,
                "dependencies": [{"id": 1, "title": "Dep Task", "status": "COMPLETED"}],
                "blocked_tasks": [{"id": 3, "title": "Blocked Task", "status": "BLOCKED"}],
                "can_complete": True,
            })

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            result = await tasks.get_task_dependencies(
                task_id=1,
                uow=uow,
                current_user=sample_user,
            )

            assert result["task_id"] == 1
            assert result["can_complete"] is True


class TestListTaskAttachments:
    """Test GET /tasks/{task_id}/attachments endpoint."""

    async def test_list_task_attachments(self, sample_user) -> None:
        """Test listing task attachments."""
        uow = MagicMock()

        now = datetime.now(UTC)

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))
            # Return dicts that will be validated into TaskAttachmentResponse
            task_instance.get_attachments = AsyncMock(return_value=[
                {
                    "id": 1, "filename": "doc1.pdf", "file_size": 1024,
                    "mime_type": "application/pdf", "description": None,
                    "uploaded_at": now.isoformat(), "uploaded_by": 1,
                },
                {
                    "id": 2, "filename": "doc2.pdf", "file_size": 2048,
                    "mime_type": "application/pdf", "description": None,
                    "uploaded_at": now.isoformat(), "uploaded_by": 2,
                },
            ])

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            result = await tasks.list_task_attachments(
                task_id=1,
                uow=uow,
                current_user=sample_user,
            )

            assert len(result) == 2
            assert result[0].filename == "doc1.pdf"

    async def test_list_task_attachments_not_found(self, sample_user) -> None:
        """Test listing attachments for non-existent task raises 404."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls:
            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(side_effect=NotFoundException("Task"))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.list_task_attachments(
                    task_id=999,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404

    async def test_list_task_attachments_permission_denied(self, sample_user) -> None:
        """Test listing attachments without permission raises 403."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))

            # Checklist belongs to different user
            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=999))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.list_task_attachments(
                    task_id=1,
                    uow=uow,
                    current_user=sample_user,  # User ID is 1, but checklist owner is 999
                )

            assert exc_info.value.status_code == 403


class TestUploadTaskAttachment:
    """Test POST /tasks/{task_id}/attachments endpoint."""

    async def test_upload_task_attachment_success(self, sample_user) -> None:
        """Test successful file upload."""
        uow = MagicMock()
        uow.commit = AsyncMock()

        # Create a mock UploadFile
        file_content = b"test file content"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "document.pdf"
        mock_file.size = len(file_content)
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=file_content)

        # Mock storage service
        mock_storage = MagicMock()
        mock_storage.upload_file = AsyncMock(return_value="tasks/1/document.pdf")
        mock_storage.get_presigned_url = MagicMock(return_value="http://minio:9000/checklists/tasks/1/document.pdf")

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls, \
             patch("checklists_service.api.endpoints.tasks.validate_file_size", return_value=True), \
             patch("checklists_service.api.endpoints.tasks.validate_file_type", return_value=True), \
             patch("checklists_service.api.endpoints.tasks.validate_filename", return_value="document.pdf"), \
             patch("checklists_service.api.endpoints.tasks.get_storage_service", return_value=mock_storage):

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1, assignee_id=1))

            task_instance.add_attachment = AsyncMock(return_value={
                "id": 1,
                "filename": "document.pdf",
                "file_size": len(file_content),
                "mime_type": "application/pdf",
                "description": "Test description",
                "uploaded_at": datetime.now(UTC).isoformat(),
                "uploaded_by": 1,
            })

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            result = await tasks.upload_task_attachment(
                task_id=1,
                uow=uow,
                current_user=sample_user,
                file=mock_file,
                description="Test description",
            )

            assert result.filename == "document.pdf"
            assert result.file_size == len(file_content)
            uow.commit.assert_awaited_once()
            mock_storage.upload_file.assert_awaited_once()

    async def test_upload_task_attachment_file_too_large(self, sample_user) -> None:
        """Test upload with file exceeding size limit raises 400."""
        uow = MagicMock()

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "large.pdf"
        mock_file.size = 20 * 1024 * 1024  # 20 MB

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls, \
             patch("checklists_service.api.endpoints.tasks.validate_file_size", return_value=False):

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1, assignee_id=1))

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.upload_task_attachment(
                    task_id=1,
                    uow=uow,
                    current_user=sample_user,
                    file=mock_file,
                )

            assert exc_info.value.status_code == 400

    async def test_upload_task_attachment_invalid_type(self, sample_user) -> None:
        """Test upload with disallowed file type raises 400."""
        uow = MagicMock()

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "script.exe"
        mock_file.size = 1024

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls, \
             patch("checklists_service.api.endpoints.tasks.validate_file_size", return_value=True), \
             patch("checklists_service.api.endpoints.tasks.validate_file_type", return_value=False):

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1, assignee_id=1))

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.upload_task_attachment(
                    task_id=1,
                    uow=uow,
                    current_user=sample_user,
                    file=mock_file,
                )

            assert exc_info.value.status_code == 400

    async def test_upload_task_attachment_not_found(self, sample_user) -> None:
        """Test upload to non-existent task raises 404."""
        uow = MagicMock()

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "document.pdf"
        mock_file.size = 1024

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls:
            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(side_effect=NotFoundException("Task"))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.upload_task_attachment(
                    task_id=999,
                    uow=uow,
                    current_user=sample_user,
                    file=mock_file,
                )

            assert exc_info.value.status_code == 404

    async def test_upload_task_attachment_permission_denied(self, sample_user) -> None:
        """Test upload without permission raises 403."""
        uow = MagicMock()

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "document.pdf"
        mock_file.size = 1024

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1, assignee_id=999))

            # Checklist belongs to different user and task is assigned to different user
            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=999))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.upload_task_attachment(
                    task_id=1,
                    uow=uow,
                    current_user=sample_user,  # User ID 1, but neither owner nor assignee
                    file=mock_file,
                )

            assert exc_info.value.status_code == 403


class TestDownloadTaskAttachment:
    """Test GET /tasks/{task_id}/attachments/file/{filename} endpoint."""

    async def test_download_task_attachment_success(self, sample_user, tmp_path) -> None:
        """Test successful file download via S3 presigned URL."""
        uow = MagicMock()

        # Mock storage service
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = MagicMock(return_value="http://minio:9000/checklists/tasks/1/document.pdf")

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls, \
             patch("checklists_service.api.endpoints.tasks.get_storage_service", return_value=mock_storage):

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            result = await tasks.download_task_attachment(
                task_id=1,
                filename="document.pdf",
                uow=uow,
                current_user=sample_user,
            )

            # Should return a RedirectResponse to the presigned URL
            assert result.status_code == 307
            assert result.headers["location"] == "http://minio:9000/checklists/tasks/1/document.pdf"
            mock_storage.get_presigned_url.assert_called_once_with("tasks/1/document.pdf", expires=3600)

    async def test_download_task_attachment_not_found(self, sample_user) -> None:
        """Test download when S3 file not found raises 404."""
        uow = MagicMock()

        # Mock storage service to raise FileNotFoundError (wrapped as StorageError -> NotFoundException)
        from checklists_service.utils import StorageError

        mock_storage = MagicMock()
        mock_storage.get_presigned_url = MagicMock(side_effect=StorageError("File not found"))

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls, \
             patch("checklists_service.api.endpoints.tasks.get_storage_service", return_value=mock_storage), \
             patch("checklists_service.api.endpoints.tasks.StorageError", StorageError):

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.download_task_attachment(
                    task_id=1,
                    filename="nonexistent.pdf",
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404

    async def test_download_task_attachment_success_with_mimetype(self, sample_user) -> None:
        """Test successful file download via S3 presigned URL."""
        uow = MagicMock()

        # Mock storage service
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = MagicMock(return_value="http://minio:9000/checklists/tasks/1/document.pdf")

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls, \
             patch("checklists_service.api.endpoints.tasks.get_storage_service", return_value=mock_storage):

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            result = await tasks.download_task_attachment(
                task_id=1,
                filename="document.pdf",
                uow=uow,
                current_user=sample_user,
            )

            # Should return a RedirectResponse to the presigned URL
            assert result.status_code == 307
            assert result.headers["location"] == "http://minio:9000/checklists/tasks/1/document.pdf"

    async def test_download_task_attachment_permission_denied(self, sample_user) -> None:
        """Test download without permission raises 403."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))

            # Checklist belongs to different user
            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=999))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.download_task_attachment(
                    task_id=1,
                    filename="document.pdf",
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 403


class TestTaskEndpointsErrorHandling:
    """Test error handling across task endpoints."""

    async def test_get_checklist_tasks_permission_denied(self, sample_user) -> None:
        """Test get_checklist_tasks with permission denied raises 403."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_checklist_tasks = AsyncMock(return_value=[])

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            # Checklist belongs to different user
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=999))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.get_checklist_tasks(
                    checklist_id=1,
                    uow=uow,
                    current_user=sample_user,  # User ID 1
                )

            assert exc_info.value.status_code == 403

    async def test_update_task_permission_denied(self, sample_user, sample_task) -> None:
        """Test update_task with permission denied raises 403."""
        uow = MagicMock()

        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            sample_task.checklist_id = 1
            sample_task.assignee_id = 999  # Different from current user
            task_instance.get_task = AsyncMock(return_value=sample_task)

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(
                id=1, user_id=999  # Different from current user
            ))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.update_task(
                    task_id=1,
                    task_data=update_data,
                    uow=uow,
                    current_user=sample_user,  # User ID 1, not owner or assignee
                )

            assert exc_info.value.status_code == 403

    async def test_update_task_not_found(self, sample_user) -> None:
        """Test update_task for non-existent task raises 404."""
        uow = MagicMock()

        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls:
            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(side_effect=NotFoundException("Task"))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.update_task(
                    task_id=999,
                    task_data=update_data,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404

    async def test_update_task_progress_permission_denied(self, sample_user) -> None:
        """Test update_task_progress with permission denied raises 403."""
        uow = MagicMock()

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.IN_PROGRESS,
            progress_percentage=50,
        )

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            # Task assigned to different user
            instance.get_task = AsyncMock(return_value=MagicMock(
                id=1, checklist_id=1, assignee_id=999
            ))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.update_task_progress(
                    task_id=1,
                    progress_data=progress_data,
                    uow=uow,
                    current_user=sample_user,  # User ID 1, not the assignee
                )

            assert exc_info.value.status_code == 403

    async def test_complete_task_not_found(self, sample_user) -> None:
        """Test complete_task for non-existent task raises 404."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.complete_task = AsyncMock(side_effect=NotFoundException("Task"))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.complete_task(
                    task_id=999,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404

    async def test_update_task_progress_not_found(self, sample_user) -> None:
        """Test update_task_progress for non-existent task raises 404 (line 226)."""
        uow = MagicMock()

        progress_data = TaskProgress(
            task_id=1,
            status=TaskStatus.IN_PROGRESS,
            progress_percentage=50,
        )

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.get_task = AsyncMock(side_effect=NotFoundException("Task"))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.update_task_progress(
                    task_id=999,
                    progress_data=progress_data,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404

    async def test_upload_task_attachment_file_save_error(self, sample_user) -> None:
        """Test S3 upload error during file upload raises 500."""
        uow = MagicMock()
        uow.commit = AsyncMock()

        # Create a mock UploadFile
        file_content = b"test file content"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "document.pdf"
        mock_file.size = len(file_content)
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=file_content)

        # Mock storage service to raise StorageError
        from checklists_service.utils import StorageError

        mock_storage = MagicMock()
        mock_storage.upload_file = AsyncMock(side_effect=StorageError("S3 upload failed"))

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls, \
             patch("checklists_service.api.endpoints.tasks.validate_file_size", return_value=True), \
             patch("checklists_service.api.endpoints.tasks.validate_file_type", return_value=True), \
             patch("checklists_service.api.endpoints.tasks.validate_filename", return_value="document.pdf"), \
             patch("checklists_service.api.endpoints.tasks.get_storage_service", return_value=mock_storage):

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1, assignee_id=1))

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.upload_task_attachment(
                    task_id=1,
                    uow=uow,
                    current_user=sample_user,
                    file=mock_file,
                    description="Test description",
                )

            assert exc_info.value.status_code == 500
            assert "File upload failed" in str(exc_info.value.detail)

    async def test_download_task_attachment_storage_error(self, sample_user) -> None:
        """Test download when S3 raises StorageError raises 404."""
        uow = MagicMock()

        from checklists_service.utils import StorageError

        mock_storage = MagicMock()
        mock_storage.get_presigned_url = MagicMock(side_effect=StorageError("File not found in S3"))

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls, \
             patch("checklists_service.api.endpoints.tasks.get_storage_service", return_value=mock_storage):

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=1))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.download_task_attachment(
                    task_id=1,
                    filename="nonexistent.pdf",
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404

    async def test_bulk_update_tasks_validation_error(self, sample_hr_user) -> None:
        """Test bulk_update_tasks with validation error raises 400."""
        uow = MagicMock()

        bulk_data = TaskBulkUpdate(
            task_ids=[1, 2],
            status=TaskStatus.IN_PROGRESS,
        )

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value = instance
            instance.bulk_update_tasks = AsyncMock(side_effect=ValidationException("Invalid status"))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.bulk_update_tasks(
                    bulk_data=bulk_data,
                    uow=uow,
                    _current_user=sample_hr_user,
                )

            assert exc_info.value.status_code == 400

    async def test_get_task_dependencies_not_found(self, sample_user) -> None:
        """Test get_task_dependencies for non-existent task raises 404."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls:
            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(side_effect=NotFoundException("Task"))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.get_task_dependencies(
                    task_id=999,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 404

    async def test_get_task_dependencies_permission_denied(self, sample_user) -> None:
        """Test get_task_dependencies with permission denied raises 403."""
        uow = MagicMock()

        with patch("checklists_service.api.endpoints.tasks.TaskService") as mock_task_cls, \
             patch("checklists_service.api.endpoints.tasks.ChecklistService") as mock_checklist_cls:

            task_instance = MagicMock()
            mock_task_cls.return_value = task_instance
            task_instance.get_task = AsyncMock(return_value=MagicMock(id=1, checklist_id=1))

            checklist_instance = MagicMock()
            mock_checklist_cls.return_value = checklist_instance
            checklist_instance.get_checklist = AsyncMock(return_value=MagicMock(id=1, user_id=999))

            with pytest.raises(HTTPException) as exc_info:
                await tasks.get_task_dependencies(
                    task_id=1,
                    uow=uow,
                    current_user=sample_user,
                )

            assert exc_info.value.status_code == 403


class TestBuildTaskResponse:
    """Test _build_task_response helper function."""

    async def test_build_task_response_with_dependencies(self, sample_task) -> None:
        """Test building response with dependencies."""
        uow = MagicMock()

        # Set up task with dependencies
        sample_task.depends_on = [2, 3]
        sample_task.status = TaskStatus.PENDING

        # Mock dependency tasks
        dep_task_2 = MagicMock(id=2, status=TaskStatus.COMPLETED)
        dep_task_3 = MagicMock(id=3, status=TaskStatus.COMPLETED)
        uow.tasks.find_by_ids = AsyncMock(return_value=[dep_task_2, dep_task_3])

        result = await tasks._build_task_response(sample_task, uow)

        assert result.can_start is True
        assert result.can_complete is True
        assert result.is_overdue is False

    async def test_build_task_response_with_incomplete_deps(self, sample_task) -> None:
        """Test building response with incomplete dependencies."""
        uow = MagicMock()

        sample_task.depends_on = [2]
        sample_task.status = TaskStatus.PENDING

        # One dependency not completed
        dep_task = MagicMock(id=2, status=TaskStatus.IN_PROGRESS)
        uow.tasks.find_by_ids = AsyncMock(return_value=[dep_task])

        result = await tasks._build_task_response(sample_task, uow)

        assert result.can_start is False
        assert result.can_complete is False

    async def test_build_task_response_overdue(self, sample_task) -> None:
        """Test building response for overdue task."""
        uow = MagicMock()

        # Set due date in the past
        sample_task.due_date = datetime.now(UTC) - timedelta(days=5)
        sample_task.status = TaskStatus.PENDING
        sample_task.depends_on = []

        uow.tasks.find_by_ids = AsyncMock(return_value=[])

        result = await tasks._build_task_response(sample_task, uow)

        assert result.is_overdue is True

    async def test_build_task_response_completed_not_overdue(self, sample_task) -> None:
        """Test completed task is not marked overdue even if past due date."""
        uow = MagicMock()

        # Set due date in the past but task is completed
        sample_task.due_date = datetime.now(UTC) - timedelta(days=5)
        sample_task.status = TaskStatus.COMPLETED
        sample_task.depends_on = []

        uow.tasks.find_by_ids = AsyncMock(return_value=[])

        result = await tasks._build_task_response(sample_task, uow)

        assert result.is_overdue is False  # Completed tasks aren't overdue
        assert result.can_complete is False  # Already completed

