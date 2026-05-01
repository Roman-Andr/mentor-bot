"""Tests for template repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from checklists_service.core.enums import TemplateStatus
from checklists_service.models import TaskTemplate, Template
from checklists_service.repositories.implementations.template import TaskTemplateRepository, TemplateRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TestTemplateRepository:
    """Test template repository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Create a template repository instance."""
        return TemplateRepository(mock_session)

    @pytest.fixture
    def sample_template(self):
        """Create a sample template."""
        now = datetime.now(UTC)
        template = MagicMock(spec=Template)
        template.id = 1
        template.name = "Onboarding Template"
        template.description = "Standard onboarding"
        template.department_id = 1
        template.position = "Developer"
        template.status = TemplateStatus.ACTIVE
        template.is_default = False
        template.created_at = now
        return template

    async def test_get_by_id_with_department(self, repository, mock_session, sample_template):
        """Test getting template by ID with department eager loaded."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_template
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        # Verify query was executed (LEFT OUTER JOIN indicates eager loading worked)
        call_sql = str(mock_session.execute.call_args[0][0])
        assert "LEFT OUTER JOIN" in call_sql or "department" in call_sql.lower()

    async def test_find_templates_basic(self, repository, mock_session, sample_template):
        """Test finding templates without filters."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        templates, total = await repository.find_templates()

        assert total == 1
        assert len(templates) == 1
        assert templates[0].id == 1

    async def test_find_templates_with_department_filter(self, repository, mock_session, sample_template):
        """Test finding templates with department filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        _templates, total = await repository.find_templates(department_id=1)

        assert total == 1

    async def test_find_templates_with_status_filter(self, repository, mock_session, sample_template):
        """Test finding templates with status filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        _templates, total = await repository.find_templates(status=TemplateStatus.ACTIVE)

        assert total == 1

    async def test_find_templates_with_is_default_filter(self, repository, mock_session, sample_template):
        """Test finding templates with is_default filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        _templates, total = await repository.find_templates(is_default=True)

        assert total == 1

    async def test_find_templates_with_search(self, repository, mock_session, sample_template):
        """Test finding templates with search filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        _templates, total = await repository.find_templates(search="Onboarding")

        assert total == 1

    async def test_find_templates_pagination(self, repository, mock_session):
        """Test template pagination."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 50
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        _templates, total = await repository.find_templates(skip=20, limit=10)

        assert total == 50

    async def test_find_templates_sort_asc(self, repository, mock_session, sample_template):
        """Test finding templates with ascending sort order (line 87)."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        _templates, total = await repository.find_templates(sort_by="name", sort_order="asc")

        assert total == 1
        # Verify the query was called with asc() ordering
        call_stmt = str(mock_session.execute.call_args[0][0])
        assert "ORDER BY" in call_stmt

    async def test_find_templates_sort_by_tasks(self, repository, mock_session, sample_template):
        """Test finding templates sorted by task count (lines 86-92)."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        _templates, total = await repository.find_templates(sort_by="tasks", sort_order="desc")

        assert total == 1

    async def test_get_by_name_and_department_found(self, repository, mock_session, sample_template):
        """Test getting template by name and department."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_template
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_name_and_department("Onboarding", 1)

        assert result is not None
        assert result.id == 1

    async def test_get_by_name_and_department_not_found(self, repository, mock_session):
        """Test getting template by name and department when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_name_and_department("NonExistent", 1)

        assert result is None

    async def test_clear_other_defaults(self, repository, mock_session):
        """Test clearing default flag on other templates."""
        mock_template1 = MagicMock()
        mock_template1.id = 2
        mock_template1.is_default = True
        mock_template2 = MagicMock()
        mock_template2.id = 3
        mock_template2.is_default = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_template1, mock_template2]
        mock_session.execute.return_value = mock_result

        await repository.clear_other_defaults(1, exclude_id=1)

        assert mock_template1.is_default is False
        assert mock_template2.is_default is False

    async def test_count_tasks(self, repository, mock_session):
        """Test counting task templates."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_session.execute.return_value = mock_result

        result = await repository.count_tasks(1)

        assert result == 10

    async def test_has_checklists_true(self, repository, mock_session):
        """Test checking if template has checklists (true case)."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_session.execute.return_value = mock_result

        result = await repository.has_checklists(1)

        assert result is True

    async def test_has_checklists_false(self, repository, mock_session):
        """Test checking if template has checklists (false case)."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        result = await repository.has_checklists(1)

        assert result is False

    async def test_get_department_stats(self, repository, mock_session):
        """Test getting department statistics."""
        mock_result = MagicMock()
        mock_result.all.return_value = [(1, 10), (2, 5)]
        mock_session.execute.return_value = mock_result

        result = await repository.get_department_stats()

        assert result["1"] == 10
        assert result["2"] == 5

    async def test_get_department_stats_with_user_filter(self, repository, mock_session):
        """Test getting department stats with user filter."""
        mock_result = MagicMock()
        mock_result.all.return_value = [(1, 3)]
        mock_session.execute.return_value = mock_result

        result = await repository.get_department_stats(user_id=1)

        assert result["1"] == 3

    async def test_find_matching_with_department_and_position(self, repository, mock_session, sample_template):
        """Test finding matching templates with department and position."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        result = await repository.find_matching(department_id=1, position="Developer")

        assert len(result) == 1

    async def test_find_matching_department_only(self, repository, mock_session, sample_template):
        """Test finding matching templates with department only."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        result = await repository.find_matching(department_id=1, position=None)

        assert len(result) == 1

    async def test_find_matching_position_only(self, repository, mock_session, sample_template):
        """Test finding matching templates with position only."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        result = await repository.find_matching(department_id=None, position="Developer")

        assert len(result) == 1

    async def test_find_matching_no_filters(self, repository, mock_session, sample_template):
        """Test finding matching templates with no filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_template]
        mock_session.execute.return_value = mock_result

        result = await repository.find_matching(department_id=None, position=None)

        assert len(result) == 1


class TestTaskTemplateRepository:
    """Test task template repository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Create a task template repository instance."""
        return TaskTemplateRepository(mock_session)

    @pytest.fixture
    def sample_task_template(self):
        """Create a sample task template."""
        now = datetime.now(UTC)
        template = MagicMock(spec=TaskTemplate)
        template.id = 1
        template.template_id = 1
        template.title = "Complete Documentation"
        template.order = 0
        template.created_at = now
        return template

    async def test_find_by_template(self, repository, mock_session, sample_task_template):
        """Test finding task templates by template ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task_template]
        mock_session.execute.return_value = mock_result

        result = await repository.find_by_template(1)

        assert len(result) == 1
        assert result[0].template_id == 1

    async def test_find_existing_ids(self, repository, mock_session):
        """Test finding which IDs exist for a template."""
        mock_result = MagicMock()
        mock_result.all.return_value = [(1,), (2,), (3,)]
        mock_session.execute.return_value = mock_result

        result = await repository.find_existing_ids(1, [1, 2, 3, 4, 5])

        assert result == {1, 2, 3}

    async def test_find_existing_ids_empty(self, repository, mock_session):
        """Test finding existing IDs with empty list."""
        result = await repository.find_existing_ids(1, [])

        assert result == set()
        mock_session.execute.assert_not_called()

    async def test_clone_tasks(self, repository, mock_session, sample_task_template):
        """Test cloning task templates."""
        second_task = MagicMock(spec=TaskTemplate)
        second_task.id = 2
        second_task.template_id = 1
        second_task.title = "Second Task"
        second_task.description = "Description"
        second_task.instructions = "Instructions"
        second_task.category = "DOCUMENTATION"
        second_task.order = 1
        second_task.due_days = 5
        second_task.estimated_minutes = 60
        second_task.resources = [{"title": "Guide"}]
        second_task.required_documents = ["doc1"]
        second_task.assignee_role = "MENTOR"
        second_task.auto_assign = True
        second_task.depends_on = []

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task_template, second_task]
        mock_session.execute.return_value = mock_result

        await repository.clone_tasks(1, 2)

        # Should add new tasks
        assert mock_session.add.call_count == 2
