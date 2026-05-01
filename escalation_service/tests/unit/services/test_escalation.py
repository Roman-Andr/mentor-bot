"""Unit tests for escalation_service/services/escalation.py."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from escalation_service.core.enums import EscalationSource, EscalationStatus, EscalationType
from escalation_service.core.exceptions import NotFoundException
from escalation_service.models import EscalationRequest
from escalation_service.schemas import EscalationRequestCreate, EscalationRequestUpdate
from escalation_service.services.escalation import EscalationService


@pytest.fixture(autouse=True)
def mock_notification_client():
    """Automatically mock NotificationClient for all service tests to prevent HTTP calls."""
    with patch("escalation_service.services.escalation.NotificationClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.notify_escalation_created = AsyncMock(return_value=True)
        mock_instance.notify_escalation_assigned = AsyncMock(return_value=True)
        mock_instance.notify_status_change = AsyncMock(return_value=True)
        mock_client.return_value = mock_instance
        yield mock_client


class TestEscalationServiceCreate:
    """Tests for creating escalation requests."""

    @pytest.mark.asyncio
    async def test_create_escalation_sets_pending_status(self, mock_uow: MagicMock) -> None:
        """Creating an escalation should set status to PENDING."""
        # Arrange
        service = EscalationService(mock_uow)
        create_data = EscalationRequestCreate(
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            reason="Test reason",
        )

        mock_created = MagicMock(spec=EscalationRequest)
        mock_uow.escalations.create.return_value = mock_created

        # Act
        result = await service.create_escalation(create_data)

        # Assert
        assert result == mock_created
        mock_uow.escalations.create.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

        # Verify the created request has PENDING status
        call_args = mock_uow.escalations.create.call_args[0][0]
        assert call_args.status == EscalationStatus.PENDING
        assert call_args.user_id == 100
        assert call_args.type == EscalationType.GENERAL


class TestEscalationServiceGet:
    """Tests for retrieving escalation requests."""

    @pytest.mark.asyncio
    async def test_get_escalation_by_id_found(self, mock_uow: MagicMock) -> None:
        """Getting an existing escalation should return it."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_request = MagicMock(spec=EscalationRequest)
        mock_uow.escalations.get_by_id.return_value = mock_request

        # Act
        result = await service.get_escalation_by_id(1)

        # Assert
        assert result == mock_request
        mock_uow.escalations.get_by_id.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_get_escalation_by_id_not_found(self, mock_uow: MagicMock) -> None:
        """Getting a non-existent escalation should raise NotFoundException."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_uow.escalations.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.get_escalation_by_id(999)

    @pytest.mark.asyncio
    async def test_get_escalations_with_filters(self, mock_uow: MagicMock) -> None:
        """Getting escalations with filters should pass them to repository."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_requests = [MagicMock(spec=EscalationRequest)]
        mock_uow.escalations.find_requests.return_value = (mock_requests, 1)

        # Act
        result, total = await service.get_escalations(
            skip=0,
            limit=10,
            user_id=100,
            assigned_to=200,
            escalation_type=EscalationType.HR,
            status=EscalationStatus.PENDING,
            search="test",
            sort_by="createdAt",
            sort_order="desc",
        )

        # Assert
        assert result == mock_requests
        assert total == 1
        mock_uow.escalations.find_requests.assert_awaited_once_with(
            skip=0,
            limit=10,
            user_id=100,
            assigned_to=200,
            escalation_type=EscalationType.HR,
            status=EscalationStatus.PENDING,
            search="test",
            sort_by="createdAt",
            sort_order="desc",
        )


class TestEscalationServiceStateMachine:
    """Tests for escalation state machine transitions."""

    @pytest.mark.asyncio
    async def test_pending_to_assigned_transition(self, mock_uow: MagicMock) -> None:
        """PENDING escalation can be assigned (PENDING→ASSIGNED)."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.PENDING,
            assigned_to=None,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        # Act
        result = await service.assign_escalation(1, assignee_id=200)

        # Assert
        assert result.status == EscalationStatus.ASSIGNED
        assert result.assigned_to == 200
        mock_uow.escalations.update.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_assigned_to_resolved_transition(self, mock_uow: MagicMock) -> None:
        """ASSIGNED escalation can be resolved (ASSIGNED→RESOLVED)."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.ASSIGNED,
            assigned_to=200,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        # Act
        result = await service.resolve_escalation(1)

        # Assert
        assert result.status == EscalationStatus.RESOLVED
        assert result.resolved_at is not None
        mock_uow.escalations.update.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_pending_to_resolved_via_update_blocked(self, mock_uow: MagicMock) -> None:
        """PENDING -> RESOLVED is blocked - must go through IN_PROGRESS first."""
        # Arrange
        from escalation_service.core.exceptions import ValidationException

        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.PENDING,
            assigned_to=None,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.RESOLVED)

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await service.update_escalation(1, update_data)

        assert "Invalid status transition" in str(exc_info.value.detail)
        mock_uow.escalations.update.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_resolve_sets_resolved_at_timestamp(self, mock_uow: MagicMock) -> None:
        """Resolving an escalation should set resolved_at timestamp."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.ASSIGNED,
            assigned_to=200,
            resolved_at=None,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        before = datetime.now(UTC)

        # Act
        result = await service.resolve_escalation(1)

        # Assert
        after = datetime.now(UTC)
        assert result.resolved_at is not None
        assert before <= result.resolved_at <= after

    @pytest.mark.asyncio
    async def test_update_escalation_with_resolution_note(self, mock_uow: MagicMock) -> None:
        """Updating with resolution_note should store it in context (IN_PROGRESS->RESOLVED)."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,  # Changed from ASSIGNED for valid transition
            assigned_to=200,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(
            status=EscalationStatus.RESOLVED,
            resolution_note="Issue resolved by HR team",
        )

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.context.get("resolution_note") == "Issue resolved by HR team"

    @pytest.mark.asyncio
    async def test_update_escalation_with_assignee(self, mock_uow: MagicMock) -> None:
        """Updating with assigned_to should update the assignee."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.PENDING,
            assigned_to=None,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(assigned_to=300)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.assigned_to == 300


class TestEscalationServiceStatusTransitions:
    """Tests for various status transition scenarios."""

    @pytest.mark.asyncio
    async def test_in_progress_to_resolved(self, mock_uow: MagicMock) -> None:
        """IN_PROGRESS escalation can be resolved."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.IT,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,
            assigned_to=200,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        # Act
        result = await service.resolve_escalation(1)

        # Assert
        assert result.status == EscalationStatus.RESOLVED

    @pytest.mark.asyncio
    async def test_in_progress_status_can_be_resolved(self, mock_uow: MagicMock) -> None:
        """IN_PROGRESS escalation can be resolved (valid transition)."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,
            assigned_to=200,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.RESOLVED)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.status == EscalationStatus.RESOLVED

    @pytest.mark.asyncio
    async def test_closed_status_via_update(self, mock_uow: MagicMock) -> None:
        """Escalation can be closed via update."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.RESOLVED,
            assigned_to=200,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.CLOSED)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.status == EscalationStatus.CLOSED
        assert result.resolved_at is not None


class TestEscalationServiceAllStatusValues:
    """Tests verifying all enum status values work correctly."""

    @pytest.mark.parametrize(
        ("start_status", "new_status"),
        [
            # Valid transitions from PENDING
            (EscalationStatus.PENDING, EscalationStatus.ASSIGNED),
            (EscalationStatus.PENDING, EscalationStatus.IN_PROGRESS),
            (EscalationStatus.PENDING, EscalationStatus.REJECTED),
            # Valid transitions from ASSIGNED
            (EscalationStatus.ASSIGNED, EscalationStatus.IN_PROGRESS),
            (EscalationStatus.ASSIGNED, EscalationStatus.REJECTED),
            (EscalationStatus.ASSIGNED, EscalationStatus.PENDING),
            # Valid transitions from IN_PROGRESS
            (EscalationStatus.IN_PROGRESS, EscalationStatus.RESOLVED),
            (EscalationStatus.IN_PROGRESS, EscalationStatus.REJECTED),
            (EscalationStatus.IN_PROGRESS, EscalationStatus.ASSIGNED),
            # Valid transitions from RESOLVED
            (EscalationStatus.RESOLVED, EscalationStatus.CLOSED),
            (EscalationStatus.RESOLVED, EscalationStatus.IN_PROGRESS),
            # Valid transitions from REJECTED
            (EscalationStatus.REJECTED, EscalationStatus.PENDING),
            # Same status (no-op)
            (EscalationStatus.PENDING, EscalationStatus.PENDING),
            (EscalationStatus.CLOSED, EscalationStatus.CLOSED),
        ],
    )
    @pytest.mark.asyncio
    async def test_valid_status_transitions_succeed(
        self,
        mock_uow: MagicMock,
        start_status: EscalationStatus,
        new_status: EscalationStatus,
    ) -> None:
        """Valid state transitions succeed via update_escalation."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            status=start_status,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=new_status)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.status == new_status

    @pytest.mark.asyncio
    @pytest.mark.parametrize("escalation_type", list(EscalationType))
    async def test_all_types_can_be_created(self, mock_uow: MagicMock, escalation_type: EscalationType) -> None:
        """Escalation can be created with any EscalationType."""
        # Arrange
        service = EscalationService(mock_uow)
        create_data = EscalationRequestCreate(
            user_id=100,
            type=escalation_type,
            source=EscalationSource.MANUAL,
        )
        mock_created = MagicMock(spec=EscalationRequest)
        mock_uow.escalations.create.return_value = mock_created

        # Act
        await service.create_escalation(create_data)

        # Assert
        call_args = mock_uow.escalations.create.call_args[0][0]
        assert call_args.type == escalation_type


class TestEscalationServiceEdgeCases:
    """Tests for edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_get_escalation_by_id_raises_not_found(self, mock_uow: MagicMock) -> None:
        """Getting non-existent escalation raises NotFoundException."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_uow.escalations.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            await service.get_escalation_by_id(999)

        assert "not found" in str(exc_info.value.detail).lower()
        mock_uow.escalations.get_by_id.assert_awaited_once_with(999)

    @pytest.mark.asyncio
    async def test_assign_escalation_not_found(self, mock_uow: MagicMock) -> None:
        """Assigning non-existent escalation raises NotFoundException."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_uow.escalations.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.assign_escalation(999, 200)

    @pytest.mark.asyncio
    async def test_resolve_escalation_not_found(self, mock_uow: MagicMock) -> None:
        """Resolving non-existent escalation raises NotFoundException."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_uow.escalations.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.resolve_escalation(999)

    @pytest.mark.asyncio
    async def test_update_escalation_not_found(self, mock_uow: MagicMock) -> None:
        """Updating non-existent escalation raises NotFoundException."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_uow.escalations.get_by_id.return_value = None

        update_data = EscalationRequestUpdate(status=EscalationStatus.RESOLVED)

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.update_escalation(999, update_data)


class TestEscalationServiceStateMachineTransitions:
    """Comprehensive tests for escalation state machine transitions."""

    @pytest.mark.asyncio
    async def test_pending_to_assigned_via_assign_method(self, mock_uow: MagicMock) -> None:
        """PENDING -> ASSIGNED via assign_escalation method."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.PENDING,
            assigned_to=None,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        # Act
        result = await service.assign_escalation(1, 200)

        # Assert
        assert result.status == EscalationStatus.ASSIGNED
        assert result.assigned_to == 200
        mock_uow.escalations.update.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_pending_to_in_progress_via_update(self, mock_uow: MagicMock) -> None:
        """PENDING -> IN_PROGRESS via update_escalation."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.IT,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.PENDING,
            assigned_to=200,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.IN_PROGRESS)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.status == EscalationStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_in_progress_to_assigned_via_update(self, mock_uow: MagicMock) -> None:
        """IN_PROGRESS -> ASSIGNED via update_escalation."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,
            assigned_to=200,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.ASSIGNED)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.status == EscalationStatus.ASSIGNED

    @pytest.mark.asyncio
    async def test_assigned_to_in_progress_via_update(self, mock_uow: MagicMock) -> None:
        """ASSIGNED -> IN_PROGRESS via update_escalation."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.MENTOR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.ASSIGNED,
            assigned_to=200,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.IN_PROGRESS)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.status == EscalationStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_pending_to_rejected_via_update(self, mock_uow: MagicMock) -> None:
        """PENDING -> REJECTED via update_escalation."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.PENDING,
            assigned_to=None,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.REJECTED)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.status == EscalationStatus.REJECTED

    @pytest.mark.asyncio
    async def test_rejected_to_pending_via_update(self, mock_uow: MagicMock) -> None:
        """REJECTED -> PENDING via update_escalation (reopen)."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.REJECTED,
            assigned_to=None,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.PENDING)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.status == EscalationStatus.PENDING

    @pytest.mark.asyncio
    async def test_any_status_to_closed_sets_resolved_at(self, mock_uow: MagicMock) -> None:
        """Transitioning to CLOSED status sets resolved_at timestamp."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.RESOLVED,
            assigned_to=200,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        before = datetime.now(UTC)

        update_data = EscalationRequestUpdate(status=EscalationStatus.CLOSED)

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        after = datetime.now(UTC)
        assert result.status == EscalationStatus.CLOSED
        assert result.resolved_at is not None
        assert before <= result.resolved_at <= after

    @pytest.mark.asyncio
    async def test_resolve_method_sets_status_and_timestamp(self, mock_uow: MagicMock) -> None:
        """resolve_escalation method correctly sets RESOLVED status and resolved_at."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,
            assigned_to=200,
            resolved_at=None,
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        before = datetime.now(UTC)

        # Act
        result = await service.resolve_escalation(1)

        # Assert
        after = datetime.now(UTC)
        assert result.status == EscalationStatus.RESOLVED
        assert result.resolved_at is not None
        assert before <= result.resolved_at <= after
        assert result.updated_at is not None


class TestEscalationServiceContextOperations:
    """Tests for escalation context operations."""

    @pytest.mark.asyncio
    async def test_update_escalation_merges_resolution_note_with_existing_context(self, mock_uow: MagicMock) -> None:
        """Resolution note should be merged with existing context (IN_PROGRESS->RESOLVED)."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,  # Changed from ASSIGNED for valid transition
            assigned_to=200,
            context={"previous": "data", "key": "value"},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(
            status=EscalationStatus.RESOLVED,
            resolution_note="Resolved by HR team",
        )

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.context["resolution_note"] == "Resolved by HR team"
        assert result.context["previous"] == "data"
        assert result.context["key"] == "value"

    @pytest.mark.asyncio
    async def test_update_escalation_resolution_note_with_none_context(self, mock_uow: MagicMock) -> None:
        """Resolution note should work even if context was None initially."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.ASSIGNED,
            assigned_to=200,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(
            resolution_note="Issue resolved",
        )

        # Act
        result = await service.update_escalation(1, update_data)

        # Assert
        assert result.context.get("resolution_note") == "Issue resolved"


class TestEscalationServiceGetEscalations:
    """Additional tests for get_escalations method."""

    @pytest.mark.asyncio
    async def test_get_escalations_empty_list(self, mock_uow: MagicMock) -> None:
        """Getting escalations with no results returns empty list."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_uow.escalations.find_requests.return_value = ([], 0)

        # Act
        requests, total = await service.get_escalations(skip=0, limit=10)

        # Assert
        assert requests == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_escalations_default_parameters(self, mock_uow: MagicMock) -> None:
        """Getting escalations uses default skip and limit."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_uow.escalations.find_requests.return_value = ([], 0)

        # Act
        _requests, _total = await service.get_escalations()

        # Assert
        call_kwargs = mock_uow.escalations.find_requests.call_args.kwargs
        assert call_kwargs["skip"] == 0
        assert call_kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_get_escalations_with_search(self, mock_uow: MagicMock) -> None:
        """Search parameter is passed to repository."""
        # Arrange
        service = EscalationService(mock_uow)
        mock_request = MagicMock(spec=EscalationRequest)
        mock_uow.escalations.find_requests.return_value = ([mock_request], 1)

        # Act
        _requests, _total = await service.get_escalations(search="urgent")

        # Assert
        call_kwargs = mock_uow.escalations.find_requests.call_args.kwargs
        assert call_kwargs["search"] == "urgent"
