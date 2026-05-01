"""Tests for dialogue service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from knowledge_service.core import DialogueAnswerType, DialogueCategory, NotFoundException
from knowledge_service.models import DialogueScenario, DialogueStep
from knowledge_service.schemas import (
    DialogueScenarioCreate,
    DialogueScenarioUpdate,
    DialogueStepCreate,
    DialogueStepUpdate,
)
from knowledge_service.services.dialogue import DialogueService


@pytest.fixture
def mock_uow():
    """Create a mock Unit of Work."""
    uow = MagicMock()
    uow.dialogue_scenarios = AsyncMock()
    uow.dialogue_steps = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def sample_scenario():
    """Create a sample dialogue scenario for testing."""
    scenario = DialogueScenario(
        id=1,
        title="Welcome Flow",
        description="New employee welcome flow",
        keywords=["welcome", "new employee"],
        category=DialogueCategory.CONTACTS,
        is_active=True,
        display_order=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    scenario.steps = []
    return scenario


@pytest.fixture
def sample_scenario_with_steps():
    """Create a sample scenario with steps."""
    scenario = DialogueScenario(
        id=1,
        title="Welcome Flow",
        description="New employee welcome flow",
        keywords=["welcome", "new employee"],
        category=DialogueCategory.CONTACTS,
        is_active=True,
        display_order=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    step1 = DialogueStep(
        id=1,
        scenario_id=1,
        step_number=1,
        question="What is your name?",
        answer_type=DialogueAnswerType.TEXT,
        options=None,
        answer_content=None,
        next_step_id=None,
        parent_step_id=None,
        is_final=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    step2 = DialogueStep(
        id=2,
        scenario_id=1,
        step_number=2,
        question="Select your department",
        answer_type=DialogueAnswerType.CHOICE,
        options=[{"value": "eng", "label": "Engineering"}, {"value": "hr", "label": "HR"}],
        answer_content=None,
        next_step_id=None,
        parent_step_id=None,
        is_final=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    scenario.steps = [step1, step2]
    return scenario


@pytest.fixture
def sample_step():
    """Create a sample dialogue step for testing."""
    return DialogueStep(
        id=1,
        scenario_id=1,
        step_number=1,
        question="What is your name?",
        answer_type=DialogueAnswerType.TEXT,
        options=None,
        answer_content=None,
        next_step_id=None,
        parent_step_id=None,
        is_final=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


class TestCreateScenario:
    """Tests for creating scenarios."""

    async def test_create_scenario_basic(self, mock_uow, sample_scenario):
        """Test basic scenario creation."""
        mock_uow.dialogue_scenarios.create.return_value = sample_scenario
        mock_uow.dialogue_scenarios.get_by_id_with_steps.return_value = sample_scenario

        service = DialogueService(mock_uow)
        scenario_data = DialogueScenarioCreate(
            title="Welcome Flow",
            description="New employee welcome flow",
            keywords=["welcome", "new employee"],
            category=DialogueCategory.CONTACTS,
            is_active=True,
            display_order=0,
        )

        result = await service.create_scenario(scenario_data)

        assert result == sample_scenario
        mock_uow.dialogue_scenarios.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_create_scenario_with_steps(self, mock_uow, sample_scenario_with_steps):
        """Test scenario creation with steps."""
        mock_uow.dialogue_scenarios.create.return_value = sample_scenario_with_steps
        mock_uow.dialogue_steps.create.return_value = None
        mock_uow.dialogue_scenarios.get_by_id_with_steps.return_value = sample_scenario_with_steps

        service = DialogueService(mock_uow)
        scenario_data = DialogueScenarioCreate(
            title="Welcome Flow",
            description="New employee welcome flow",
            keywords=["welcome", "new employee"],
            category=DialogueCategory.CONTACTS,
            is_active=True,
            display_order=0,
            steps=[
                DialogueStepCreate(
                    step_number=1,
                    question="What is your name?",
                    answer_type=DialogueAnswerType.TEXT,
                ),
                DialogueStepCreate(
                    step_number=2,
                    question="Select your department",
                    answer_type=DialogueAnswerType.CHOICE,
                    options=[{"value": "eng", "label": "Engineering"}],
                    is_final=True,
                ),
            ],
        )

        result = await service.create_scenario(scenario_data)

        assert result == sample_scenario_with_steps
        assert mock_uow.dialogue_steps.create.call_count == 2


class TestGetScenario:
    """Tests for getting scenarios."""

    async def test_get_scenario_by_id_success(self, mock_uow, sample_scenario_with_steps):
        """Test getting scenario by ID successfully."""
        mock_uow.dialogue_scenarios.get_by_id_with_steps.return_value = sample_scenario_with_steps

        service = DialogueService(mock_uow)
        result = await service.get_scenario_by_id(1)

        assert result == sample_scenario_with_steps
        assert len(result.steps) == 2
        mock_uow.dialogue_scenarios.get_by_id_with_steps.assert_called_once_with(1)

    async def test_get_scenario_by_id_not_found(self, mock_uow):
        """Test getting non-existent scenario."""
        mock_uow.dialogue_scenarios.get_by_id_with_steps.return_value = None

        service = DialogueService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.get_scenario_by_id(999)

    async def test_get_active_scenarios(self, mock_uow, sample_scenario):
        """Test getting active scenarios."""
        mock_uow.dialogue_scenarios.get_active_scenarios.return_value = ([sample_scenario], 1)

        service = DialogueService(mock_uow)
        result, total = await service.get_active_scenarios(skip=0, limit=100)

        assert len(result) == 1
        assert total == 1
        mock_uow.dialogue_scenarios.get_active_scenarios.assert_called_once_with(skip=0, limit=100)

    async def test_get_scenarios_by_category(self, mock_uow, sample_scenario):
        """Test getting scenarios by category."""
        mock_uow.dialogue_scenarios.get_by_category.return_value = ([sample_scenario], 1)

        service = DialogueService(mock_uow)
        result, total = await service.get_scenarios_by_category(
            category=DialogueCategory.CONTACTS,
            skip=0,
            limit=100,
        )

        assert len(result) == 1
        assert total == 1
        mock_uow.dialogue_scenarios.get_by_category.assert_called_once_with(
            DialogueCategory.CONTACTS,
            skip=0,
            limit=100,
        )

    async def test_find_scenarios_with_filters(self, mock_uow, sample_scenario):
        """Test finding scenarios with filters."""
        mock_uow.dialogue_scenarios.find_scenarios.return_value = ([sample_scenario], 1)

        service = DialogueService(mock_uow)
        result, total = await service.find_scenarios(
            skip=0,
            limit=100,
            category=DialogueCategory.CONTACTS,
            is_active=True,
            search="welcome",
        )

        assert len(result) == 1
        assert total == 1
        mock_uow.dialogue_scenarios.find_scenarios.assert_called_once_with(
            skip=0,
            limit=100,
            category=DialogueCategory.CONTACTS,
            is_active=True,
            search="welcome",
            sort_by=None,
            sort_order="asc",
        )


class TestUpdateScenario:
    """Tests for updating scenarios."""

    async def test_update_scenario_basic(self, mock_uow, sample_scenario):
        """Test basic scenario update."""
        mock_uow.dialogue_scenarios.get_by_id.return_value = sample_scenario
        mock_uow.dialogue_scenarios.update.return_value = sample_scenario
        mock_uow.dialogue_scenarios.get_by_id_with_steps.return_value = sample_scenario

        service = DialogueService(mock_uow)
        update_data = DialogueScenarioUpdate(title="Updated Title")

        result = await service.update_scenario(1, update_data)

        assert result.title == "Updated Title"
        mock_uow.commit.assert_called_once()

    async def test_update_scenario_all_fields(self, mock_uow, sample_scenario):
        """Test updating all scenario fields."""
        mock_uow.dialogue_scenarios.get_by_id.return_value = sample_scenario
        mock_uow.dialogue_scenarios.update.return_value = sample_scenario
        mock_uow.dialogue_scenarios.get_by_id_with_steps.return_value = sample_scenario

        service = DialogueService(mock_uow)
        update_data = DialogueScenarioUpdate(
            title="Updated Title",
            description="Updated description",
            keywords=["updated", "keywords"],
            category=DialogueCategory.BENEFITS,
            is_active=False,
            display_order=5,
        )

        result = await service.update_scenario(1, update_data)

        assert result.title == "Updated Title"
        assert result.description == "Updated description"
        assert result.keywords == ["updated", "keywords"]
        assert result.category == DialogueCategory.BENEFITS
        assert result.is_active is False
        assert result.display_order == 5

    async def test_update_scenario_not_found(self, mock_uow):
        """Test updating non-existent scenario."""
        mock_uow.dialogue_scenarios.get_by_id.return_value = None

        service = DialogueService(mock_uow)
        update_data = DialogueScenarioUpdate(title="Updated")

        with pytest.raises(NotFoundException):
            await service.update_scenario(999, update_data)


class TestDeleteScenario:
    """Tests for deleting scenarios."""

    async def test_delete_scenario(self, mock_uow, sample_scenario):
        """Test scenario deletion."""
        mock_uow.dialogue_scenarios.get_by_id.return_value = sample_scenario
        mock_uow.dialogue_scenarios.delete.return_value = True

        service = DialogueService(mock_uow)
        result = await service.delete_scenario(1)

        assert result is True
        mock_uow.dialogue_scenarios.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    async def test_delete_scenario_not_found(self, mock_uow):
        """Test deleting non-existent scenario."""
        mock_uow.dialogue_scenarios.get_by_id.return_value = None

        service = DialogueService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.delete_scenario(999)


class TestManageSteps:
    """Tests for step management."""

    async def test_add_step(self, mock_uow, sample_scenario, sample_step):
        """Test adding a step to scenario."""
        mock_uow.dialogue_scenarios.get_by_id.return_value = sample_scenario
        mock_uow.dialogue_steps.create.return_value = sample_step

        service = DialogueService(mock_uow)
        step_data = DialogueStepCreate(
            step_number=1,
            question="What is your name?",
            answer_type=DialogueAnswerType.TEXT,
        )

        result = await service.add_step(1, step_data)

        assert result == sample_step
        mock_uow.dialogue_steps.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_add_step_scenario_not_found(self, mock_uow):
        """Test adding step to non-existent scenario."""
        mock_uow.dialogue_scenarios.get_by_id.return_value = None

        service = DialogueService(mock_uow)
        step_data = DialogueStepCreate(
            step_number=1,
            question="What is your name?",
            answer_type=DialogueAnswerType.TEXT,
        )

        with pytest.raises(NotFoundException):
            await service.add_step(999, step_data)

    async def test_add_step_with_all_fields(self, mock_uow, sample_scenario):
        """Test adding step with all fields set."""
        mock_uow.dialogue_scenarios.get_by_id.return_value = sample_scenario

        step = DialogueStep(
            id=2,
            scenario_id=1,
            step_number=2,
            question="Select option",
            answer_type=DialogueAnswerType.CHOICE,
            options=[{"value": "a", "label": "Option A"}],
            answer_content="Answer content",
            next_step_id=None,
            parent_step_id=1,
            is_final=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_uow.dialogue_steps.create.return_value = step

        service = DialogueService(mock_uow)
        step_data = DialogueStepCreate(
            step_number=2,
            question="Select option",
            answer_type=DialogueAnswerType.CHOICE,
            options=[{"value": "a", "label": "Option A"}],
            answer_content="Answer content",
            next_step_id=None,
            parent_step_id=1,
            is_final=True,
        )

        result = await service.add_step(1, step_data)

        assert result.question == "Select option"
        assert result.answer_type == DialogueAnswerType.CHOICE
        assert result.is_final is True

    async def test_update_step(self, mock_uow, sample_step):
        """Test updating a step."""
        mock_uow.dialogue_steps.get_by_id.return_value = sample_step
        mock_uow.dialogue_steps.update.return_value = sample_step

        service = DialogueService(mock_uow)
        update_data = DialogueStepUpdate(question="Updated question")

        result = await service.update_step(1, update_data)

        assert result.question == "Updated question"
        mock_uow.commit.assert_called_once()

    async def test_update_step_all_fields(self, mock_uow, sample_step):
        """Test updating all step fields."""
        mock_uow.dialogue_steps.get_by_id.return_value = sample_step
        mock_uow.dialogue_steps.update.return_value = sample_step

        service = DialogueService(mock_uow)
        update_data = DialogueStepUpdate(
            step_number=2,
            question="Updated question",
            answer_type=DialogueAnswerType.CHOICE,
            options=[{"value": "a", "label": "A"}],
            answer_content="New content",
            next_step_id=3,
            parent_step_id=1,
            is_final=True,
        )

        result = await service.update_step(1, update_data)

        assert result.step_number == 2
        assert result.question == "Updated question"
        assert result.answer_type == DialogueAnswerType.CHOICE
        assert result.is_final is True

    async def test_update_step_not_found(self, mock_uow):
        """Test updating non-existent step."""
        mock_uow.dialogue_steps.get_by_id.return_value = None

        service = DialogueService(mock_uow)
        update_data = DialogueStepUpdate(question="Updated")

        with pytest.raises(NotFoundException):
            await service.update_step(999, update_data)

    async def test_delete_step(self, mock_uow, sample_step):
        """Test deleting a step."""
        mock_uow.dialogue_steps.get_by_id.return_value = sample_step
        mock_uow.dialogue_steps.delete.return_value = True

        service = DialogueService(mock_uow)
        result = await service.delete_step(1)

        assert result is True
        mock_uow.dialogue_steps.delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()

    async def test_delete_step_not_found(self, mock_uow):
        """Test deleting non-existent step."""
        mock_uow.dialogue_steps.get_by_id.return_value = None

        service = DialogueService(mock_uow)

        with pytest.raises(NotFoundException):
            await service.delete_step(999)


class TestReorderSteps:
    """Tests for reordering steps."""

    async def test_reorder_steps(self, mock_uow):
        """Test reordering steps in a scenario."""
        mock_uow.dialogue_steps.reorder_steps.return_value = None

        service = DialogueService(mock_uow)
        await service.reorder_steps(1, [2, 1, 3])

        mock_uow.dialogue_steps.reorder_steps.assert_called_once_with(1, [2, 1, 3])
        mock_uow.commit.assert_called_once()


class TestGetFirstStep:
    """Tests for getting first step."""

    async def test_get_first_step_success(self, mock_uow, sample_step):
        """Test getting first step successfully."""
        mock_uow.dialogue_steps.get_first_step.return_value = sample_step

        service = DialogueService(mock_uow)
        result = await service.get_first_step(1)

        assert result == sample_step
        mock_uow.dialogue_steps.get_first_step.assert_called_once_with(1)

    async def test_get_first_step_none(self, mock_uow):
        """Test getting first step when none exists."""
        mock_uow.dialogue_steps.get_first_step.return_value = None

        service = DialogueService(mock_uow)
        result = await service.get_first_step(1)

        assert result is None
