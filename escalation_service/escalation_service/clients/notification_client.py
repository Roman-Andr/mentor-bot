"""Client to send notifications via notification_service."""

import httpx
from loguru import logger

from escalation_service.config import settings


class NotificationClient:
    """Client to send notifications via notification_service."""

    def __init__(self) -> None:
        """Initialize notification client with service URL and API key."""
        self.base_url = settings.NOTIFICATION_SERVICE_URL
        self.api_key = settings.SERVICE_API_KEY

    async def notify_escalation_created(
        self,
        escalation_id: int,
        user_id: int,
        assignee_id: int | None,
        reason: str,
        priority: str,
    ) -> bool:
        """Notify relevant parties when escalation is created."""
        logger.debug(
            "Preparing escalation-created notifications (escalation_id={}, user_id={}, assignee_id={})",
            escalation_id,
            user_id,
            assignee_id,
        )
        reason_preview = reason[:100] + "..." if len(reason) > 100 else reason

        # Notify the assignee (if assigned)
        if assignee_id:
            await self._send_notification(
                user_id=assignee_id,
                template_name="escalation_assigned",
                variables={
                    "escalation_id": escalation_id,
                    "priority": priority,
                    "reason_preview": reason_preview,
                    "link": f"/escalations/{escalation_id}",
                },
                channel="telegram",
            )

        # Notify requester of successful creation
        await self._send_notification(
            user_id=user_id,
            template_name="escalation_created_confirmation",
            variables={
                "escalation_id": escalation_id,
                "link": f"/my-escalations/{escalation_id}",
            },
            channel="telegram",
        )

        return True

    async def notify_escalation_assigned(
        self,
        escalation_id: int,
        new_assignee_id: int,
        previous_assignee_id: int | None,
        assigned_by_id: int,
        reason: str,
    ) -> bool:
        """Notify when escalation is assigned/reassigned."""
        logger.debug(
            "Preparing escalation-assigned notifications (escalation_id={}, new_assignee_id={}, previous_assignee_id={})",
            escalation_id,
            new_assignee_id,
            previous_assignee_id,
        )
        reason_preview = reason[:100] + "..." if len(reason) > 100 else reason

        # Notify new assignee
        await self._send_notification(
            user_id=new_assignee_id,
            template_name="escalation_assigned_to_you",
            variables={
                "escalation_id": escalation_id,
                "reason_preview": reason_preview,
                "link": f"/escalations/{escalation_id}",
            },
            channel="telegram",
        )

        # Notify previous assignee (if reassigned)
        if previous_assignee_id and previous_assignee_id != new_assignee_id:
            await self._send_notification(
                user_id=previous_assignee_id,
                template_name="escalation_reassigned",
                variables={
                    "escalation_id": escalation_id,
                    "link": f"/escalations/{escalation_id}",
                },
                channel="telegram",
            )

        return True

    async def notify_status_change(
        self,
        escalation_id: int,
        user_id: int,  # Original requester
        old_status: str,
        new_status: str,
        changed_by_id: int,
        comment: str | None = None,
    ) -> bool:
        """Notify requester when escalation status changes."""
        logger.debug(
            "Preparing escalation status notification (escalation_id={}, user_id={}, from={}, to={})",
            escalation_id,
            user_id,
            old_status,
            new_status,
        )
        # Determine template based on new status
        template_map = {
            "IN_PROGRESS": "escalation_in_progress",
            "RESOLVED": "escalation_resolved",
            "REJECTED": "escalation_rejected",
            "CLOSED": "escalation_closed",
        }

        template = template_map.get(new_status, "escalation_updated")

        await self._send_notification(
            user_id=user_id,
            template_name=template,
            variables={
                "escalation_id": escalation_id,
                "old_status": old_status,
                "new_status": new_status,
                "comment": comment or "No comment provided",
                "link": f"/my-escalations/{escalation_id}",
            },
            channel="telegram",
        )

        return True

    async def _send_notification(
        self,
        user_id: int,
        template_name: str,
        variables: dict,
        channel: str = "telegram",
    ) -> bool:
        """Send notification via notification_service."""
        try:
            async with httpx.AsyncClient() as client:
                logger.debug(
                    "Sending notification template (user_id={}, template_name={}, channel={})",
                    user_id,
                    template_name,
                    channel,
                )
                response = await client.post(
                    f"{self.base_url}/api/v1/notifications/send-template",
                    json={
                        "user_id": user_id,
                        "template_name": template_name,
                        "variables": variables,
                        "channel": channel,
                    },
                    headers={"X-Service-Key": self.api_key},
                    timeout=10.0,
                )
                response.raise_for_status()
                logger.info(
                    "Notification template sent (user_id={}, template_name={}, channel={})",
                    user_id,
                    template_name,
                    channel,
                )
                return True
        except Exception:
            logger.warning(
                "Could not send notification (user_id={}, template_name={}, channel={})",
                user_id,
                template_name,
                channel,
            )
            return False
