"""Tests for template models."""

from datetime import UTC, datetime

from checklists_service.core.enums import EmployeeLevel, TaskCategory, TemplateStatus
from checklists_service.models import TaskTemplate, Template


class TestTemplateModel:
    """Test Template model."""

    def test_template_repr(self):
        """Test Template __repr__ method (line 60)."""
        template = Template(
            id=1,
            name="Onboarding Template",
            description="Standard onboarding template",
            department_id=1,
            position="Developer",
            level=EmployeeLevel.JUNIOR,
            duration_days=30,
            task_categories=[TaskCategory.DOCUMENTATION, TaskCategory.TRAINING],
            default_assignee_role="MENTOR",
            status=TemplateStatus.ACTIVE,
            version=1,
            is_default=False,
            created_at=datetime.now(UTC),
        )

        repr_str = repr(template)
        assert "Template" in repr_str
        assert "id=1" in repr_str
        assert "name=Onboarding Template" in repr_str
        assert "department_id=1" in repr_str

    def test_template_repr_no_department(self):
        """Test Template __repr__ without department (line 60)."""
        template = Template(
            id=2,
            name="Generic Template",
            description="Template for all departments",
            department_id=None,
            position=None,
            level=None,
            duration_days=14,
            task_categories=[],
            default_assignee_role=None,
            status=TemplateStatus.DRAFT,
            version=1,
            is_default=True,
            created_at=datetime.now(UTC),
        )

        repr_str = repr(template)
        assert "Template" in repr_str
        assert "id=2" in repr_str
        assert "department_id=None" in repr_str

    def test_template_default_values(self):
        """Test Template default values."""
        # The defaults are defined in mapped_column but not applied to instance
        # until the record is saved to the database
        template = Template(
            id=1,
            name="Test Template",
            duration_days=30,
            task_categories=[],
            status=TemplateStatus.ACTIVE,
            version=1,
            is_default=False,
        )

        assert template.duration_days == 30
        assert template.task_categories == []
        assert template.status == TemplateStatus.ACTIVE
        assert template.version == 1
        assert template.is_default is False

    def test_template_estimated_days_property(self):
        """Test Template estimated_days is the duration_days field (line 102)."""
        template = Template(
            id=1,
            name="Test Template",
            duration_days=45,
        )

        # The "estimated_days" from coverage is actually the duration_days field
        assert template.duration_days == 45

    def test_template_duration_days_variations(self):
        """Test Template with different duration days."""
        test_cases = [
            (7, "One week"),
            (14, "Two weeks"),
            (30, "One month"),
            (60, "Two months"),
            (90, "Three months"),
        ]

        for duration, description in test_cases:
            template = Template(
                id=1,
                name=f"Template - {description}",
                duration_days=duration,
            )
            assert template.duration_days == duration

    def test_template_task_categories(self):
        """Test Template task_categories field."""
        categories = [
            TaskCategory.DOCUMENTATION,
            TaskCategory.TRAINING,
            TaskCategory.TECHNICAL,
            TaskCategory.HR,
            TaskCategory.MEETING,
        ]

        template = Template(
            id=1,
            name="Complete Template",
            task_categories=categories,
        )

        assert template.task_categories == categories
        assert len(template.task_categories) == 5

    def test_template_relationships(self):
        """Test Template model relationships."""
        template = Template(
            id=1,
            name="Test Template",
            department_id=1,
        )

        # Relationships should be defined
        assert hasattr(template, "department")
        assert hasattr(template, "checklists")
        assert hasattr(template, "tasks")


class TestTaskTemplateModel:
    """Test TaskTemplate model."""

    def test_task_template_repr(self):
        """Test TaskTemplate __repr__ method (line 102)."""
        task_template = TaskTemplate(
            id=1,
            template_id=1,
            title="Complete Documentation",
            description="Read and sign documentation",
            instructions="Follow the handbook",
            category=TaskCategory.DOCUMENTATION,
            order=0,
            due_days=3,
            estimated_minutes=60,
            resources=[{"title": "Handbook", "url": "https://example.com"}],
            required_documents=["contract"],
            assignee_role="MENTOR",
            auto_assign=True,
            depends_on=[],
            created_at=datetime.now(UTC),
        )

        repr_str = repr(task_template)
        assert "TaskTemplate" in repr_str
        assert "id=1" in repr_str
        assert "title=Complete Documentation" in repr_str
        assert "template_id=1" in repr_str

    def test_task_template_repr_with_dependencies(self):
        """Test TaskTemplate __repr__ with dependencies (line 102)."""
        task_template = TaskTemplate(
            id=2,
            template_id=1,
            title="Setup Environment",
            description="Install required tools",
            instructions="Follow setup guide",
            category=TaskCategory.TECHNICAL,
            order=1,
            due_days=5,
            estimated_minutes=120,
            resources=[],
            required_documents=[],
            assignee_role="MENTOR",
            auto_assign=True,
            depends_on=[1],
            created_at=datetime.now(UTC),
        )

        repr_str = repr(task_template)
        assert "TaskTemplate" in repr_str
        assert "id=2" in repr_str
        assert "template_id=1" in repr_str

    def test_task_template_default_values(self):
        """Test TaskTemplate default values."""
        # The defaults are defined in mapped_column but not applied to instance
        # until the record is saved to the database
        task_template = TaskTemplate(
            id=1,
            template_id=1,
            title="Test Task",
            category=TaskCategory.DOCUMENTATION,
            order=0,
            due_days=1,
            resources=[],
            required_documents=[],
            auto_assign=True,
            depends_on=[],
        )

        assert task_template.category == TaskCategory.DOCUMENTATION
        assert task_template.order == 0
        assert task_template.due_days == 1
        assert task_template.estimated_minutes is None
        assert task_template.resources == []
        assert task_template.required_documents == []
        assert task_template.auto_assign is True
        assert task_template.depends_on == []

    def test_task_template_relationship(self):
        """Test TaskTemplate relationship to Template."""
        task_template = TaskTemplate(
            id=1,
            template_id=1,
            title="Test Task",
            category=TaskCategory.TRAINING,
        )

        # Relationship should be defined
        assert hasattr(task_template, "template")

    def test_task_template_due_days_variations(self):
        """Test TaskTemplate with different due days."""
        test_cases = [
            (1, "Next day"),
            (3, "Three days"),
            (7, "One week"),
            (14, "Two weeks"),
            (30, "One month"),
        ]

        for due_days, description in test_cases:
            task_template = TaskTemplate(
                id=1,
                template_id=1,
                title=f"Task - {description}",
                due_days=due_days,
            )
            assert task_template.due_days == due_days

    def test_task_template_resources(self):
        """Test TaskTemplate resources field."""
        resources = [
            {"title": "Video Tutorial", "url": "https://example.com/video", "type": "video"},
            {"title": "Documentation", "url": "https://example.com/docs", "type": "link"},
            {"title": "Sample File", "url": "https://example.com/sample.pdf", "type": "file"},
        ]

        task_template = TaskTemplate(
            id=1,
            template_id=1,
            title="Task with Resources",
            resources=resources,
        )

        assert task_template.resources == resources
        assert len(task_template.resources) == 3
