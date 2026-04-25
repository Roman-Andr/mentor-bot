"""Escalation management service with repository pattern."""

from datetime import UTC, datetime

from loguru import logger

from escalation_service.clients.notification_client import NotificationClient
from escalation_service.core.enums import EscalationStatus, EscalationType
from escalation_service.core.exceptions import NotFoundException, ValidationException
from escalation_service.models import EscalationRequest
from escalation_service.repositories.unit_of_work import IUnitOfWork
from escalation_service.schemas import EscalationRequestCreate, EscalationRequestUpdate

# Valid state transitions for the escalation workflow
# Key: current_status -> list of allowed next statuses
VALID_STATE_TRANSITIONS: dict[EscalationStatus, list[EscalationStatus]] = {
    EscalationStatus.PENDING: [
        EscalationStatus.ASSIGNED,
        EscalationStatus.IN_PROGRESS,
        EscalationStatus.REJECTED,
    ],
    EscalationStatus.ASSIGNED: [
        EscalationStatus.IN_PROGRESS,
        EscalationStatus.REJECTED,
        EscalationStatus.PENDING,  # Unassign
    ],
    EscalationStatus.IN_PROGRESS: [
        EscalationStatus.RESOLVED,
        EscalationStatus.REJECTED,
        EscalationStatus.ASSIGNED,  # Reassign
    ],
    EscalationStatus.RESOLVED: [
        EscalationStatus.CLOSED,
        EscalationStatus.IN_PROGRESS,  # Reopen
    ],
    EscalationStatus.REJECTED: [
        EscalationStatus.PENDING,  # Reopen/reconsider
    ],
    # CLOSED is terminal - no transitions out
    EscalationStatus.CLOSED: [],
}


def _validate_status_transition(
    current_status: EscalationStatus,
    new_status: EscalationStatus,
) -> None:
    """
    Validate that a status transition is allowed.

    Args:
        current_status: The current status of the escalation
        new_status: The requested new status

    Raises:
        ValidationException: If the transition is not valid

    """
    if current_status == new_status:
        return  # Same status is always valid (no-op)

    allowed_transitions = VALID_STATE_TRANSITIONS.get(current_status, [])
    if new_status not in allowed_transitions:
        msg = (
            f"Invalid status transition: {current_status.value} -> {new_status.value}. "
            f"Allowed transitions from {current_status.value}: "
            f"{[s.value for s in allowed_transitions] or ['none (terminal state)']}"
        )
        raise ValidationException(msg)


class EscalationService:
    """Service for escalation request management."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize EscalationService with Unit of Work."""
        self._uow = uow
        self._notification = NotificationClient()

    async def create_escalation(self, data: EscalationRequestCreate) -> EscalationRequest:
        """Create a new escalation request and notify relevant parties."""
        logger.debug(
            "Creating escalation (user_id={}, type={}, assigned_to={})",
            data.user_id,
            data.type,
            data.assigned_to,
        )
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
        logger.info(
            "Escalation created (escalation_id={}, user_id={}, type={}, assigned_to={})",
            created.id,
            created.user_id,
            created.type,
            created.assigned_to,
        )

        # Send notifications (non-blocking)
        try:
            await self._notification.notify_escalation_created(
                escalation_id=created.id,
                user_id=data.user_id,
                assignee_id=data.assigned_to,
                reason=data.reason or "",
                priority=data.context.get("priority", "normal") if data.context else "normal",
            )
        except Exception:
            logger.exception("Escalation creation notification failed (escalation_id={})", created.id)

        return created

    async def get_escalation_by_id(self, escalation_id: int) -> EscalationRequest:
        """Get escalation request by ID."""
        request = await self._uow.escalations.get_by_id(escalation_id)
        if not request:
            logger.warning("Escalation not found (escalation_id={})", escalation_id)
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
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[EscalationRequest], int]:
        """Get paginated list of escalation requests with filters."""
        logger.debug(
            "Listing escalations (skip={}, limit={}, user_id={}, assigned_to={}, type={}, status={})",
            skip,
            limit,
            user_id,
            assigned_to,
            escalation_type,
            status,
        )
        requests, total = await self._uow.escalations.find_requests(
            skip=skip,
            limit=limit,
            user_id=user_id,
            assigned_to=assigned_to,
            escalation_type=escalation_type,
            status=status,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        logger.debug("Escalations listed (count={}, total={})", len(requests), total)
        return list(requests), total

    async def update_escalation(
        self, escalation_id: int, update_data: EscalationRequestUpdate, changed_by_id: int = 1
    ) -> EscalationRequest:
        """Update escalation request (status, assignee) and notify on status change."""
        logger.debug("Updating escalation (escalation_id={}, changed_by_id={})", escalation_id, changed_by_id)
        request = await self.get_escalation_by_id(escalation_id)
        old_status = request.status

        if update_data.status is not None:
            # Validate state machine transition
            _validate_status_transition(old_status, update_data.status)
            logger.info(
                "Escalation status transition accepted (escalation_id={}, from={}, to={})",
                escalation_id,
                old_status,
                update_data.status,
            )

            request.status = update_data.status
            if update_data.status in (EscalationStatus.RESOLVED, EscalationStatus.CLOSED):
                request.resolved_at = datetime.now(UTC)

        if update_data.assigned_to is not None:
            request.assigned_to = update_data.assigned_to

        # Store resolution note in context if needed
        if update_data.resolution_note:
            request.context = request.context or {}
            request.context["resolution_note"] = update_data.resolution_note

        request.updated_at = datetime.now(UTC)
        updated = await self._uow.escalations.update(request)
        await self._uow.commit()

        # Notify requester of status change (non-blocking)
        if update_data.status is not None and old_status != update_data.status:
            try:
                resolution_note = None
                if update_data.resolution_note:
                    resolution_note = update_data.resolution_note

                await self._notification.notify_status_change(
                    escalation_id=escalation_id,
                    user_id=request.user_id,
                    old_status=old_status.value,
                    new_status=request.status.value,
                    changed_by_id=changed_by_id,
                    comment=resolution_note,
                )
            except Exception:
                logger.exception("Escalation status notification failed (escalation_id={})", escalation_id)

        return updated

    async def assign_escalation(
        self, escalation_id: int, assignee_id: int, assigned_by_id: int = 1
    ) -> EscalationRequest:
        """Assign escalation to a user and notify."""
        logger.debug(
            "Assigning escalation (escalation_id={}, assignee_id={}, assigned_by_id={})",
            escalation_id,
            assignee_id,
            assigned_by_id,
        )
        request = await self.get_escalation_by_id(escalation_id)
        previous_assignee = request.assigned_to

        request.assigned_to = assignee_id
        request.status = EscalationStatus.ASSIGNED
        request.updated_at = datetime.now(UTC)
        updated = await self._uow.escalations.update(request)
        await self._uow.commit()
        logger.info(
            "Escalation assigned (escalation_id={}, previous_assignee={}, new_assignee={})",
            escalation_id,
            previous_assignee,
            assignee_id,
        )

        # Notify (non-blocking)
        try:
            await self._notification.notify_escalation_assigned(
                escalation_id=escalation_id,
                new_assignee_id=assignee_id,
                previous_assignee_id=previous_assignee,
                assigned_by_id=assigned_by_id,
                reason=request.reason or "",
            )
        except Exception:
            logger.exception("Escalation assignment notification failed (escalation_id={})", escalation_id)

        return updated

    async def resolve_escalation(
        self, escalation_id: int, resolved_by_id: int = 1, comment: str | None = None
    ) -> EscalationRequest:
        """Mark escalation as resolved and notify requester."""
        logger.debug("Resolving escalation (escalation_id={}, resolved_by_id={})", escalation_id, resolved_by_id)
        request = await self.get_escalation_by_id(escalation_id)
        old_status = request.status

        request.status = EscalationStatus.RESOLVED
        request.resolved_at = datetime.now(UTC)
        request.updated_at = datetime.now(UTC)

        # Store resolution comment in context if provided
        if comment:
            request.context = request.context or {}
            request.context["resolution_comment"] = comment

        updated = await self._uow.escalations.update(request)
        await self._uow.commit()
        logger.info("Escalation resolved (escalation_id={}, previous_status={})", escalation_id, old_status)

        # Notify requester of resolution (non-blocking)
        try:
            await self._notification.notify_status_change(
                escalation_id=escalation_id,
                user_id=request.user_id,
                old_status=old_status.value,
                new_status="RESOLVED",
                changed_by_id=resolved_by_id,
                comment=comment,
            )
        except Exception:
            logger.exception("Escalation resolution notification failed (escalation_id={})", escalation_id)

        return updated
