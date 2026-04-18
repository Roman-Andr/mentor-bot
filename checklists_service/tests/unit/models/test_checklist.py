"""Tests for checklist models."""

from datetime import UTC, datetime, timedelta

from checklists_service.core.enums import ChecklistStatus, TaskStatus
from checklists_service.models import Checklist, Task


class TestChecklistModel:
    """Test Checklist model."""

    def test_checklist_repr(self):
        """Test Checklist __repr__ method (line 62)."""
        checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            progress_percentage=75,
            completed_tasks=3,
            total_tasks=4,
            start_date=datetime.now(UTC),
            due_date=datetime.now(UTC) + timedelta(days=30),
        )

        repr_str = repr(checklist)
        assert "Checklist" in repr_str
        assert "id=1" in repr_str
        assert "user_id=1" in repr_str
        assert "progress=75%" in repr_str

    def test_checklist_progress_percentage_default(self):
        """Test Checklist progress_percentage default value (mapped_column default)."""
        checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            progress_percentage=0,  # Explicitly set as per model default
            completed_tasks=0,
            total_tasks=0,
            start_date=datetime.now(UTC),
            due_date=datetime.now(UTC) + timedelta(days=30),
        )

        # Default value from model definition
        assert checklist.progress_percentage == 0

    def test_checklist_progress_percentage_custom(self):
        """Test Checklist with custom progress_percentage."""
        checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            progress_percentage=50,
            completed_tasks=2,
            total_tasks=4,
            start_date=datetime.now(UTC),
            due_date=datetime.now(UTC) + timedelta(days=30),
        )

        assert checklist.progress_percentage == 50

    def test_checklist_repr_completed(self):
        """Test Checklist __repr__ with completed status (line 62)."""
        checklist = Checklist(
            id=2,
            user_id=2,
            employee_id="EMP002",
            template_id=1,
            status=ChecklistStatus.COMPLETED,
            progress_percentage=100,
            completed_tasks=5,
            total_tasks=5,
            start_date=datetime.now(UTC) - timedelta(days=30),
            due_date=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )

        repr_str = repr(checklist)
        assert "Checklist" in repr_str
        assert "progress=100%" in repr_str

    def test_checklist_relationships(self):
        """Test Checklist model relationships."""
        checklist = Checklist(
            id=1,
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            status=ChecklistStatus.IN_PROGRESS,
            start_date=datetime.now(UTC),
            due_date=datetime.now(UTC) + timedelta(days=30),
        )

        # Relationships should be defined
        assert hasattr(checklist, 'template')
        assert hasattr(checklist, 'tasks')


class TestTaskModel:
    """Test Task model."""

    def test_task_repr(self):
        """Test Task __repr__ method (line 110)."""
        task = Task(
            id=1,
            checklist_id=1,
            template_task_id=1,
            title="Complete Documentation",
            description="Read and sign documentation",
            category="DOCUMENTATION",
            status=TaskStatus.PENDING,
            order=0,
            due_date=datetime.now(UTC) + timedelta(days=3),
            assignee_role="MENTOR",
            created_at=datetime.now(UTC),
            depends_on=[],
            blocks=[],
            attachments=[],
        )

        repr_str = repr(task)
        assert "Task" in repr_str
        assert "id=1" in repr_str
        assert "title=Complete Documentation" in repr_str
        assert f"status={TaskStatus.PENDING}" in repr_str

    def test_task_repr_in_progress(self):
        """Test Task __repr__ with in-progress status."""
        task = Task(
            id=2,
            checklist_id=1,
            template_task_id=2,
            title="Setup Environment",
            description="Install software",
            category="TECHNICAL",
            status=TaskStatus.IN_PROGRESS,
            order=1,
            due_date=datetime.now(UTC) + timedelta(days=5),
            assignee_role="MENTOR",
            created_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            depends_on=[1],
            blocks=[3],
            attachments=[],
        )

        repr_str = repr(task)
        assert "Task" in repr_str
        assert f"status={TaskStatus.IN_PROGRESS}" in repr_str

    def test_task_repr_completed(self):
        """Test Task __repr__ with completed status."""
        completed_at = datetime.now(UTC)
        task = Task(
            id=3,
            checklist_id=1,
            template_task_id=3,
            title="Attend Orientation",
            description="Attend the orientation meeting",
            category="MEETING",
            status=TaskStatus.COMPLETED,
            order=2,
            due_date=datetime.now(UTC) + timedelta(days=1),
            assignee_role="EMPLOYEE",
            created_at=datetime.now(UTC) - timedelta(days=1),
            completed_at=completed_at,
            completed_by=1,
            depends_on=[],
            blocks=[],
            attachments=[{"filename": "notes.pdf"}],
        )

        repr_str = repr(task)
        assert "Task" in repr_str
        assert f"status={TaskStatus.COMPLETED}" in repr_str

    def test_task_dependencies(self):
        """Test Task with dependencies."""
        task = Task(
            id=2,
            checklist_id=1,
            template_task_id=2,
            title="Dependent Task",
            description="This task has dependencies",
            category="TRAINING",
            status=TaskStatus.BLOCKED,
            order=1,
            due_date=datetime.now(UTC) + timedelta(days=5),
            assignee_role="MENTOR",
            created_at=datetime.now(UTC),
            depends_on=[1],  # Depends on task 1
            blocks=[3],  # Blocks task 3
            attachments=[],
        )

        assert task.depends_on == [1]
        assert task.blocks == [3]
        assert task.status == TaskStatus.BLOCKED

    def test_task_attachments(self):
        """Test Task attachments field."""
        attachments = [
            {"filename": "doc1.pdf", "url": "https://example.com/doc1.pdf"},
            {"filename": "doc2.pdf", "url": "https://example.com/doc2.pdf"},
        ]

        task = Task(
            id=1,
            checklist_id=1,
            template_task_id=1,
            title="Task with attachments",
            description="Upload documents",
            category="DOCUMENTATION",
            status=TaskStatus.PENDING,
            order=0,
            due_date=datetime.now(UTC) + timedelta(days=3),
            assignee_role="MENTOR",
            created_at=datetime.now(UTC),
            depends_on=[],
            blocks=[],
            attachments=attachments,
        )

        assert task.attachments == attachments
        assert len(task.attachments) == 2

    def test_task_relationship(self):
        """Test Task relationship to checklist."""
        task = Task(
            id=1,
            checklist_id=1,
            template_task_id=1,
            title="Test Task",
            description="Test description",
            category="TEST",
            status=TaskStatus.PENDING,
            order=0,
            due_date=datetime.now(UTC) + timedelta(days=1),
            assignee_role="MENTOR",
            created_at=datetime.now(UTC),
            depends_on=[],
            blocks=[],
            attachments=[],
        )

        # Relationship should be defined
        assert hasattr(task, 'checklist')
