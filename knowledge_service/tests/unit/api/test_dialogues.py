"""Tests for dialogue API endpoints."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
from fastapi import HTTPException, status

from knowledge_service.api.endpoints.dialogues import (
    add_step,
    create_scenario,
    delete_scenario,
    delete_step,
    get_active_scenarios,
    get_first_step,
    get_scenario,
    get_scenarios,
    get_scenarios_by_category,
    reorder_steps,
    update_scenario,
    update_step,
)
from knowledge_service.core import DialogueCategory, NotFoundException
from knowledge_service.schemas import (
    DialogueScenarioCreate,
    DialogueScenarioListResponse,
    DialogueScenarioResponse,
    DialogueScenarioUpdate,
    DialogueStepCreate,
    DialogueStepReorderRequest,
    DialogueStepResponse,
    DialogueStepUpdate,
)

if TYPE_CHECKING:
    from knowledge_service.api.deps import UserInfo

from unittest.mock import AsyncMock


class TestGetScenarios:
    """Test GET /dialogue-scenarios endpoint."""

    async def test_get_scenarios_success(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test successful retrieval of scenarios."""
        result = await get_scenarios(
            dialogue_service=mock_dialogue_service,
        )

        assert isinstance(result, DialogueScenarioListResponse)
        mock_dialogue_service.find_scenarios.assert_called_once()

    async def test_get_scenarios_with_filters(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test getting scenarios with filters."""
        await get_scenarios(
            dialogue_service=mock_dialogue_service,
            skip=10,
            limit=20,
            category="onboarding",
            is_active=True,
            search="welcome",
        )

        call_kwargs = mock_dialogue_service.find_scenarios.call_args[1]
        assert call_kwargs["skip"] == 10
        assert call_kwargs["limit"] == 20
        assert call_kwargs["category"] == "onboarding"
        assert call_kwargs["is_active"] is True
        assert call_kwargs["search"] == "welcome"


class TestCreateScenario:
    """Test POST /dialogue-scenarios endpoint."""

    async def test_create_scenario_success(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful scenario creation by HR."""
        scenario_data = DialogueScenarioCreate(
            title="Welcome Flow",
            description="New employee welcome flow",
            category=DialogueCategory.VACATION,
        )

        result = await create_scenario(
            scenario_data=scenario_data,
            dialogue_service=mock_dialogue_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, DialogueScenarioResponse)
        mock_dialogue_service.create_scenario.assert_called_once_with(scenario_data)


class TestGetActiveScenarios:
    """Test GET /dialogue-scenarios/active endpoint."""

    async def test_get_active_scenarios_success(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test successful retrieval of active scenarios."""
        result = await get_active_scenarios(
            dialogue_service=mock_dialogue_service,
        )

        assert isinstance(result, DialogueScenarioListResponse)
        mock_dialogue_service.get_active_scenarios.assert_called_once()

    async def test_get_active_scenarios_with_pagination(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test active scenarios with pagination."""
        await get_active_scenarios(
            dialogue_service=mock_dialogue_service,
            skip=5,
            limit=15,
        )

        call_kwargs = mock_dialogue_service.get_active_scenarios.call_args[1]
        assert call_kwargs["skip"] == 5
        assert call_kwargs["limit"] == 15


class TestGetScenariosByCategory:
    """Test GET /dialogue-scenarios/category/{category} endpoint."""

    async def test_get_scenarios_by_category_success(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test successful retrieval of scenarios by category."""
        result = await get_scenarios_by_category(
            category="onboarding",
            dialogue_service=mock_dialogue_service,
        )

        assert isinstance(result, DialogueScenarioListResponse)
        mock_dialogue_service.get_scenarios_by_category.assert_called_once_with("onboarding", skip=0, limit=50)


class TestGetScenario:
    """Test GET /dialogue-scenarios/{scenario_id} endpoint."""

    async def test_get_scenario_success(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test successful retrieval of scenario by ID."""
        result = await get_scenario(
            scenario_id=1,
            dialogue_service=mock_dialogue_service,
        )

        assert isinstance(result, DialogueScenarioResponse)
        mock_dialogue_service.get_scenario_by_id.assert_called_once_with(1)

    async def test_get_scenario_not_found(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test getting non-existent scenario."""
        mock_dialogue_service.get_scenario_by_id.side_effect = NotFoundException("Scenario")

        with pytest.raises(HTTPException) as exc_info:
            await get_scenario(
                scenario_id=999,
                dialogue_service=mock_dialogue_service,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateScenario:
    """Test PUT /dialogue-scenarios/{scenario_id} endpoint."""

    async def test_update_scenario_success(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful scenario update by HR."""
        update_data = DialogueScenarioUpdate(
            title="Updated Welcome Flow",
            is_active=False,
        )

        result = await update_scenario(
            scenario_id=1,
            scenario_data=update_data,
            dialogue_service=mock_dialogue_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, DialogueScenarioResponse)
        mock_dialogue_service.update_scenario.assert_called_once_with(1, update_data)

    async def test_update_scenario_not_found(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test updating non-existent scenario."""
        mock_dialogue_service.update_scenario.side_effect = NotFoundException("Scenario")

        with pytest.raises(HTTPException) as exc_info:
            await update_scenario(
                scenario_id=999,
                scenario_data=DialogueScenarioUpdate(title="Test"),
                dialogue_service=mock_dialogue_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteScenario:
    """Test DELETE /dialogue-scenarios/{scenario_id} endpoint."""

    async def test_delete_scenario_success(
        self,
        mock_dialogue_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test successful scenario deletion by admin."""
        result = await delete_scenario(
            scenario_id=1,
            dialogue_service=mock_dialogue_service,
            _current_user=mock_admin_user,
        )

        assert result.message == "Dialogue scenario deleted successfully"
        mock_dialogue_service.delete_scenario.assert_called_once_with(1)

    async def test_delete_scenario_not_found(
        self,
        mock_dialogue_service: AsyncMock,
        mock_admin_user: UserInfo,
    ) -> None:
        """Test deleting non-existent scenario."""
        mock_dialogue_service.delete_scenario.side_effect = NotFoundException("Scenario")

        with pytest.raises(HTTPException) as exc_info:
            await delete_scenario(
                scenario_id=999,
                dialogue_service=mock_dialogue_service,
                _current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestGetFirstStep:
    """Test GET /dialogue-scenarios/{scenario_id}/steps/first endpoint."""

    async def test_get_first_step_success(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test successful retrieval of first step."""
        mock_step = AsyncMock()
        mock_step.id = 1
        mock_step.scenario_id = 1
        mock_step.step_number = 1
        mock_step.question = "Welcome! How can I help?"
        mock_step.answer_type = "TEXT"
        mock_step.options = None
        mock_step.answer_content = ""
        mock_step.next_step_id = None
        mock_step.parent_step_id = None
        mock_step.is_final = False
        mock_step.created_at = datetime.now(UTC)
        mock_step.updated_at = None
        mock_dialogue_service.get_first_step.return_value = mock_step

        result = await get_first_step(
            scenario_id=1,
            dialogue_service=mock_dialogue_service,
        )

        assert isinstance(result, DialogueStepResponse)
        mock_dialogue_service.get_first_step.assert_called_once_with(1)

    async def test_get_first_step_not_found(
        self,
        mock_dialogue_service: AsyncMock,
    ) -> None:
        """Test when scenario has no steps."""
        mock_dialogue_service.get_first_step.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_first_step(
                scenario_id=1,
                dialogue_service=mock_dialogue_service,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "No steps found" in exc_info.value.detail


class TestAddStep:
    """Test POST /dialogue-scenarios/{scenario_id}/steps endpoint."""

    async def test_add_step_success(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful step addition by HR."""
        step_data = DialogueStepCreate(
            question="Welcome! How can I help?",
            step_number=1,
        )

        mock_step = AsyncMock()
        mock_step.id = 1
        mock_step.scenario_id = 1
        mock_step.step_number = 1
        mock_step.question = "Welcome! How can I help?"
        mock_step.answer_type = "TEXT"
        mock_step.options = None
        mock_step.answer_content = ""
        mock_step.next_step_id = None
        mock_step.parent_step_id = None
        mock_step.is_final = False
        mock_step.created_at = datetime.now(UTC)
        mock_step.updated_at = None
        mock_dialogue_service.add_step.return_value = mock_step

        result = await add_step(
            scenario_id=1,
            step_data=step_data,
            dialogue_service=mock_dialogue_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, DialogueStepResponse)
        mock_dialogue_service.add_step.assert_called_once_with(1, step_data)

    async def test_add_step_not_found(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test adding step to non-existent scenario."""
        mock_dialogue_service.add_step.side_effect = NotFoundException("Scenario")

        with pytest.raises(HTTPException) as exc_info:
            await add_step(
                scenario_id=999,
                step_data=DialogueStepCreate(question="Test", step_number=1),
                dialogue_service=mock_dialogue_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateStep:
    """Test PUT /dialogue-scenarios/steps/{step_id} endpoint."""

    async def test_update_step_success(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful step update by HR."""
        step_data = DialogueStepUpdate(
            question="Updated question",
        )

        mock_step = AsyncMock()
        mock_step.id = 1
        mock_step.scenario_id = 1
        mock_step.step_number = 1
        mock_step.question = "Updated question"
        mock_step.answer_type = "TEXT"
        mock_step.options = None
        mock_step.answer_content = ""
        mock_step.next_step_id = None
        mock_step.parent_step_id = None
        mock_step.is_final = False
        mock_step.created_at = datetime.now(UTC)
        mock_step.updated_at = datetime.now(UTC)
        mock_dialogue_service.update_step.return_value = mock_step

        result = await update_step(
            step_id=1,
            step_data=step_data,
            dialogue_service=mock_dialogue_service,
            _current_user=mock_hr_user,
        )

        assert isinstance(result, DialogueStepResponse)
        mock_dialogue_service.update_step.assert_called_once_with(1, step_data)

    async def test_update_step_not_found(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test updating non-existent step."""
        mock_dialogue_service.update_step.side_effect = NotFoundException("Step")

        with pytest.raises(HTTPException) as exc_info:
            await update_step(
                step_id=999,
                step_data=DialogueStepUpdate(message="Test"),
                dialogue_service=mock_dialogue_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteStep:
    """Test DELETE /dialogue-scenarios/steps/{step_id} endpoint."""

    async def test_delete_step_success(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful step deletion by HR."""
        result = await delete_step(
            step_id=1,
            dialogue_service=mock_dialogue_service,
            _current_user=mock_hr_user,
        )

        assert result.message == "Dialogue step deleted successfully"
        mock_dialogue_service.delete_step.assert_called_once_with(1)

    async def test_delete_step_not_found(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test deleting non-existent step."""
        mock_dialogue_service.delete_step.side_effect = NotFoundException("Step")

        with pytest.raises(HTTPException) as exc_info:
            await delete_step(
                step_id=999,
                dialogue_service=mock_dialogue_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestReorderSteps:
    """Test POST /dialogue-scenarios/{scenario_id}/reorder endpoint."""

    async def test_reorder_steps_success(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test successful step reordering by HR."""
        reorder_data = DialogueStepReorderRequest(step_ids=[3, 1, 2])

        result = await reorder_steps(
            scenario_id=1,
            reorder_data=reorder_data,
            dialogue_service=mock_dialogue_service,
            _current_user=mock_hr_user,
        )

        assert result.message == "Steps reordered successfully"
        mock_dialogue_service.reorder_steps.assert_called_once_with(1, [3, 1, 2])

    async def test_reorder_steps_not_found(
        self,
        mock_dialogue_service: AsyncMock,
        mock_hr_user: UserInfo,
    ) -> None:
        """Test reordering steps in non-existent scenario."""
        mock_dialogue_service.reorder_steps.side_effect = NotFoundException("Scenario")

        with pytest.raises(HTTPException) as exc_info:
            await reorder_steps(
                scenario_id=999,
                reorder_data=DialogueStepReorderRequest(step_ids=[1, 2]),
                dialogue_service=mock_dialogue_service,
                _current_user=mock_hr_user,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
