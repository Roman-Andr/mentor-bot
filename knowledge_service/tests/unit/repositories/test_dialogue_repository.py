"""Tests for Dialogue repository implementation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.core import DialogueCategory
from knowledge_service.models import DialogueScenario, DialogueStep
from knowledge_service.repositories.implementations.dialogue import (
    DialogueScenarioRepository,
    DialogueStepRepository,
)


class TestDialogueScenarioRepository:
    """Test DialogueScenario repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_scenario(self):
        """Create a sample dialogue scenario."""
        return DialogueScenario(
            id=1,
            title="Welcome Flow",
            description="New employee welcome flow",
            category=DialogueCategory.CONTACTS,
            is_active=True,
            display_order=0,
            keywords=["welcome", "new employee"],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def test_create_with_steps(self, mock_session, sample_scenario):
        """Test creating scenario with eager-loaded steps."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_scenario
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result = await repo.create(sample_scenario)

        assert result == sample_scenario
        mock_session.add.assert_called_once_with(sample_scenario)
        mock_session.flush.assert_called_once()

    async def test_update_with_steps(self, mock_session, sample_scenario):
        """Test updating scenario with eager-loaded steps."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_scenario
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result = await repo.update(sample_scenario)

        assert result == sample_scenario
        mock_session.flush.assert_called_once()

    async def test_get_by_id_with_steps(self, mock_session, sample_scenario):
        """Test getting scenario by ID with steps."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_scenario
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result = await repo.get_by_id_with_steps(1)

        assert result == sample_scenario

    async def test_get_active_scenarios(self, mock_session, sample_scenario):
        """Test getting active scenarios."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_scenario]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result, total = await repo.get_active_scenarios()

        assert len(result) == 1
        assert total == 1
        assert result[0].is_active is True

    async def test_get_active_scenarios_pagination(self, mock_session, sample_scenario):
        """Test getting active scenarios with pagination."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result, total = await repo.get_active_scenarios(skip=10, limit=5)

        assert len(result) == 0
        assert total == 0

    async def test_get_by_category(self, mock_session, sample_scenario):
        """Test getting scenarios by category."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_scenario]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result, total = await repo.get_by_category(DialogueCategory.CONTACTS.value)

        assert len(result) == 1
        assert total == 1

    async def test_find_scenarios_all_filters(self, mock_session, sample_scenario):
        """Test finding scenarios with all filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_scenario]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result, total = await repo.find_scenarios(
            category=DialogueCategory.CONTACTS.value,
            is_active=True,
            search="welcome",
        )

        assert len(result) == 1
        assert total == 1

    async def test_find_scenarios_search_only(self, mock_session, sample_scenario):
        """Test finding scenarios with search only."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_scenario]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result, _total = await repo.find_scenarios(search="welcome")

        assert len(result) == 1

    async def test_find_scenarios_empty_search(self, mock_session, sample_scenario):
        """Test finding scenarios with empty search (should be ignored)."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_scenario]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result, _total = await repo.find_scenarios(search="   ")

        assert len(result) == 1


class TestDialogueStepRepository:
    """Test DialogueStep repository implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def sample_step(self):
        """Create a sample dialogue step."""
        return DialogueStep(
            id=1,
            scenario_id=1,
            step_number=1,
            question="Welcome message",
            answer_type="text",
            next_step_id=None,
            parent_step_id=None,
            options=None,
            answer_content=None,
            is_final=False,
        )

    @pytest.fixture
    def sample_steps(self):
        """Create sample dialogue steps."""
        return [
            DialogueStep(
                id=1,
                scenario_id=1,
                step_number=1,
                question="Step 1",
                answer_type="text",
            ),
            DialogueStep(
                id=2,
                scenario_id=1,
                step_number=2,
                question="Step 2",
                answer_type="choice",
            ),
        ]

    async def test_get_by_scenario_id(self, mock_session, sample_steps):
        """Test getting steps by scenario ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_steps
        mock_session.execute.return_value = mock_result

        repo = DialogueStepRepository(mock_session)
        result = await repo.get_by_scenario_id(1)

        assert len(result) == 2
        assert result[0].step_number == 1
        assert result[1].step_number == 2

    async def test_get_first_step(self, mock_session, sample_step):
        """Test getting first step for a scenario."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_step
        mock_session.execute.return_value = mock_result

        repo = DialogueStepRepository(mock_session)
        result = await repo.get_first_step(1)

        assert result == sample_step
        assert result.step_number == 1

    async def test_get_first_step_not_found(self, mock_session):
        """Test getting first step when none exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = DialogueStepRepository(mock_session)
        result = await repo.get_first_step(1)

        assert result is None

    async def test_reorder_steps(self, mock_session):
        """Test reordering steps."""
        step1 = DialogueStep(id=1, scenario_id=1, step_number=1, question="Step 1", answer_type="text")
        step2 = DialogueStep(id=2, scenario_id=1, step_number=2, question="Step 2", answer_type="text")
        step3 = DialogueStep(id=3, scenario_id=1, step_number=3, question="Step 3", answer_type="text")

        # The repository calls execute for each step_id in order
        # We need to return the steps in the order they're queried
        call_count = [0]

        async def mock_execute(stmt) -> MagicMock:
            call_count[0] += 1
            mock_result = MagicMock()
            # First call queries step_id=2, second step_id=3, third step_id=1
            if call_count[0] == 1:
                mock_result.scalar_one_or_none.return_value = step2
            elif call_count[0] == 2:
                mock_result.scalar_one_or_none.return_value = step3
            else:
                mock_result.scalar_one_or_none.return_value = step1
            return mock_result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        repo = DialogueStepRepository(mock_session)
        await repo.reorder_steps(1, [2, 3, 1])  # New order: step2=1, step3=2, step1=3

        assert step2.step_number == 1
        assert step3.step_number == 2
        assert step1.step_number == 3
        mock_session.flush.assert_called_once()

    async def test_reorder_steps_missing_step(self, mock_session):
        """Test reordering when a step is missing (should skip)."""
        step1 = DialogueStep(id=1, scenario_id=1, step_number=1, question="Step 1", answer_type="text")

        # First call returns None (step 2 not found), second returns step1
        call_count = [0]

        async def mock_execute(stmt) -> MagicMock:
            call_count[0] += 1
            mock_result = MagicMock()
            if call_count[0] == 1:
                mock_result.scalar_one_or_none.return_value = None  # Step 2 not found
            else:
                mock_result.scalar_one_or_none.return_value = step1  # Step 1 found
            return mock_result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        repo = DialogueStepRepository(mock_session)
        await repo.reorder_steps(1, [2, 1])  # Step 2 doesn't exist

        # Only step 1 should be renumbered (to position 2, since step 2 was skipped)
        assert step1.step_number == 2


class TestDialogueScenarioRepositorySortOrder:
    """Test DialogueScenario repository sort order."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def sample_scenario(self):
        """Create a sample dialogue scenario."""
        return DialogueScenario(
            id=1,
            title="Welcome Flow",
            description="New employee welcome flow",
            category=DialogueCategory.CONTACTS,
            is_active=True,
            display_order=0,
            keywords=["welcome", "new employee"],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def test_find_scenarios_desc_sort_order(self, mock_session, sample_scenario):
        """Test finding scenarios with descending sort order."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_scenario]
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        repo = DialogueScenarioRepository(mock_session)
        result, total = await repo.find_scenarios(sort_by="title", sort_order="desc")

        assert len(result) == 1
        assert total == 1
