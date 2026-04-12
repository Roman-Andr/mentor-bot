"""Escalation management service with repository pattern."""

from datetime import UTC, datetime

from escalation_service.core.enums import EscalationStatus, EscalationType
from escalation_service.core.exceptions import NotFoundException
from escalation_service.models import EscalationRequest
from escalation_service.repositories.unit_of_work import IUnitOfWork
from escalation_service.schemas import EscalationRequestCreate, EscalationRequestUpdate


class EscalationService:
    """Service for escalation request management."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize EscalationService with Unit of Work."""
        self._uow = uow

    async def create_escalation(self, data: EscalationRequestCreate) -> EscalationRequest:
        """Create a new escalation request."""
        request = EscalationRequest(
            user_id=data.user_id,
            type=data.type,
            source=data.source,
            reason=data.reason,
            context=data.context,
            assigned_to=data.assigned_to,
            related_entity_type=data.related_entity_type,
            related_entity_id=data.related_entity_id,
            status=EscalationStatus.PENDING,
        )
        created = await self._uow.escalations.create(request)
        await self._uow.commit()
        return created

    async def get_escalation_by_id(self, escalation_id: int) -> EscalationRequest:
        """Get escalation request by ID."""
        request = await self._uow.escalations.get_by_id(escalation_id)
        if not request:
            msg = "Escalation request"
            raise NotFoundException(msg)
        return request

    async def get_escalations(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
        assigned_to: int | None = None,
        escalation_type: EscalationType | None = None,
        status: EscalationStatus | None = None,
        search: str | None = None,
    ) -> tuple[list[EscalationRequest], int]:
        """Get paginated list of escalation requests with filters."""
        requests, total = await self._uow.escalations.find_requests(
            skip=skip,
            limit=limit,
            user_id=user_id,
            assigned_to=assigned_to,
            escalation_type=escalation_type,
            status=status,
            search=search,
        )
        return list(requests), total

    async def update_escalation(self, escalation_id: int, update_data: EscalationRequestUpdate) -> EscalationRequest:
        """Update escalation request (status, assignee)."""
        request = await self.get_escalation_by_id(escalation_id)

        if update_data.status is not None:
            request.status = update_data.status
            if update_data.status in (EscalationStatus.RESOLVED, EscalationStatus.CLOSED):
                request.resolved_at = datetime.now(UTC)

        if update_data.assigned_to is not None:
            request.assigned_to = update_data.assigned_to

        # You could store resolution note in contexxt if needed
        if update_data.resolution_note:
            request.context = request.context or {}
            request.context["resolution_note"] = update_data.resolution_note

        request.updated_at = datetime.now(UTC)
        updated = await self._uow.escalations.update(request)
        await self._uow.commit()
        return updated

    async def assign_escalation(self, escalation_id: int, assignee_id: int) -> EscalationRequest:
        """Assign escalation to a user."""
        request = await self.get_escalation_by_id(escalation_id)
        request.assigned_to = assignee_id
        request.status = EscalationStatus.ASSIGNED
        request.updated_at = datetime.now(UTC)
        updated = await self._uow.escalations.update(request)
        await self._uow.commit()
        return updated

    async def resolve_escalation(self, escalation_id: int) -> EscalationRequest:
        """Mark escalation as resolved."""
        request = await self.get_escalation_by_id(escalation_id)
        request.status = EscalationStatus.RESOLVED
        request.resolved_at = datetime.now(UTC)
        request.updated_at = datetime.now(UTC)
        updated = await self._uow.escalations.update(request)
        await self._uow.commit()
        return updated
