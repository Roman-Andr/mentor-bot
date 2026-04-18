"""Unit tests for escalation notification client and service integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from escalation_service.clients.notification_client import NotificationClient
from escalation_service.core.enums import EscalationSource, EscalationStatus, EscalationType
from escalation_service.models import EscalationRequest
from escalation_service.schemas import EscalationRequestCreate, EscalationRequestUpdate
from escalation_service.services.escalation import EscalationService


class TestNotificationClient:
    """Tests for NotificationClient class."""

    @pytest.fixture
    def notification_client(self) -> NotificationClient:
        """Create a NotificationClient instance."""
        return NotificationClient()

    async def test_notify_escalation_created_with_assignee(self, notification_client: NotificationClient) -> None:
        """Creating escalation should notify both requester and assignee."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_escalation_created(
                escalation_id=1,
                user_id=100,
                assignee_id=200,
                reason="Test escalation reason",
                priority="HIGH",
            )

            # Assert
            assert result is True
            assert mock_send.call_count == 2

            # Check assignee notification
            assignee_call = mock_send.call_args_list[0]
            assert assignee_call.kwargs["user_id"] == 200
            assert assignee_call.kwargs["template_name"] == "escalation_assigned"
            assert assignee_call.kwargs["variables"]["escalation_id"] == 1
            assert assignee_call.kwargs["variables"]["priority"] == "HIGH"
            assert "reason_preview" in assignee_call.kwargs["variables"]

            # Check requester notification
            requester_call = mock_send.call_args_list[1]
            assert requester_call.kwargs["user_id"] == 100
            assert requester_call.kwargs["template_name"] == "escalation_created_confirmation"
            assert requester_call.kwargs["variables"]["escalation_id"] == 1

    async def test_notify_escalation_created_without_assignee(self, notification_client: NotificationClient) -> None:
        """Creating escalation without assignee should only notify requester."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_escalation_created(
                escalation_id=1,
                user_id=100,
                assignee_id=None,
                reason="Test escalation reason",
                priority="MEDIUM",
            )

            # Assert
            assert result is True
            assert mock_send.call_count == 1

            # Only requester should be notified
            call = mock_send.call_args
            assert call.kwargs["user_id"] == 100
            assert call.kwargs["template_name"] == "escalation_created_confirmation"

    async def test_notify_escalation_created_reason_truncation(self, notification_client: NotificationClient) -> None:
        """Long reason should be truncated in notification."""
        # Arrange
        long_reason = "A" * 150

        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            await notification_client.notify_escalation_created(
                escalation_id=1,
                user_id=100,
                assignee_id=200,
                reason=long_reason,
                priority="LOW",
            )

            # Assert
            assignee_call = mock_send.call_args_list[0]
            reason_preview = assignee_call.kwargs["variables"]["reason_preview"]
            assert len(reason_preview) <= 103  # 100 + "..."
            assert reason_preview.endswith("...")

    async def test_notify_escalation_assigned(self, notification_client: NotificationClient) -> None:
        """Assigning escalation should notify new assignee."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_escalation_assigned(
                escalation_id=1,
                new_assignee_id=300,
                previous_assignee_id=None,
                assigned_by_id=200,
                reason="Test reason",
            )

            # Assert
            assert result is True
            mock_send.assert_awaited_once()
            call = mock_send.call_args
            assert call.kwargs["user_id"] == 300
            assert call.kwargs["template_name"] == "escalation_assigned_to_you"
            assert call.kwargs["variables"]["escalation_id"] == 1

    async def test_notify_escalation_reassigned(self, notification_client: NotificationClient) -> None:
        """Reassigning escalation should notify both old and new assignees."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_escalation_assigned(
                escalation_id=1,
                new_assignee_id=300,
                previous_assignee_id=200,
                assigned_by_id=100,
                reason="Test reason",
            )

            # Assert
            assert result is True
            assert mock_send.call_count == 2

            # New assignee
            new_call = mock_send.call_args_list[0]
            assert new_call.kwargs["user_id"] == 300
            assert new_call.kwargs["template_name"] == "escalation_assigned_to_you"

            # Old assignee
            old_call = mock_send.call_args_list[1]
            assert old_call.kwargs["user_id"] == 200
            assert old_call.kwargs["template_name"] == "escalation_reassigned"

    async def test_notify_escalation_reassigned_same_assignee(self, notification_client: NotificationClient) -> None:
        """Reassigning to same assignee should not notify twice."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act - same user is both old and new assignee
            result = await notification_client.notify_escalation_assigned(
                escalation_id=1,
                new_assignee_id=200,
                previous_assignee_id=200,
                assigned_by_id=100,
                reason="Test reason",
            )

            # Assert
            assert result is True
            mock_send.assert_awaited_once()  # Only once for new assignee

    async def test_notify_status_change_resolved(self, notification_client: NotificationClient) -> None:
        """Status change to RESOLVED should use correct template."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_status_change(
                escalation_id=1,
                user_id=100,
                old_status="IN_PROGRESS",
                new_status="RESOLVED",
                changed_by_id=200,
                comment="Fixed the issue",
            )

            # Assert
            assert result is True
            mock_send.assert_awaited_once()
            call = mock_send.call_args
            assert call.kwargs["user_id"] == 100
            assert call.kwargs["template_name"] == "escalation_resolved"
            assert call.kwargs["variables"]["comment"] == "Fixed the issue"

    async def test_notify_status_change_in_progress(self, notification_client: NotificationClient) -> None:
        """Status change to IN_PROGRESS should use correct template."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_status_change(
                escalation_id=1,
                user_id=100,
                old_status="ASSIGNED",
                new_status="IN_PROGRESS",
                changed_by_id=200,
            )

            # Assert
            assert result is True
            call = mock_send.call_args
            assert call.kwargs["template_name"] == "escalation_in_progress"

    async def test_notify_status_change_rejected(self, notification_client: NotificationClient) -> None:
        """Status change to REJECTED should use correct template."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_status_change(
                escalation_id=1,
                user_id=100,
                old_status="PENDING",
                new_status="REJECTED",
                changed_by_id=200,
                comment="Not a valid request",
            )

            # Assert
            assert result is True
            call = mock_send.call_args
            assert call.kwargs["template_name"] == "escalation_rejected"

    async def test_notify_status_change_closed(self, notification_client: NotificationClient) -> None:
        """Status change to CLOSED should use correct template."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_status_change(
                escalation_id=1,
                user_id=100,
                old_status="RESOLVED",
                new_status="CLOSED",
                changed_by_id=200,
            )

            # Assert
            assert result is True
            call = mock_send.call_args
            assert call.kwargs["template_name"] == "escalation_closed"

    async def test_notify_status_change_default_template(self, notification_client: NotificationClient) -> None:
        """Unknown status change should use default template."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            result = await notification_client.notify_status_change(
                escalation_id=1,
                user_id=100,
                old_status="UNKNOWN",
                new_status="SOME_STATUS",
                changed_by_id=200,
            )

            # Assert
            assert result is True
            call = mock_send.call_args
            assert call.kwargs["template_name"] == "escalation_updated"

    async def test_notify_status_change_default_comment(self, notification_client: NotificationClient) -> None:
        """Status change without comment should use default message."""
        # Arrange
        with patch.object(notification_client, '_send_notification', new=AsyncMock()) as mock_send:
            # Act
            await notification_client.notify_status_change(
                escalation_id=1,
                user_id=100,
                old_status="PENDING",
                new_status="RESOLVED",
                changed_by_id=200,
                comment=None,
            )

            # Assert
            call = mock_send.call_args
            assert call.kwargs["variables"]["comment"] == "No comment provided"


class TestEscalationServiceNotifications:
    """Tests for EscalationService notification integration."""

    async def test_create_escalation_sends_notification(self, mock_uow: MagicMock) -> None:
        """Creating escalation should trigger notification."""
        # Arrange
        service = EscalationService(mock_uow)
        create_data = EscalationRequestCreate(
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            reason="Test reason",
            context={"priority": "high"},
        )

        mock_created = MagicMock(spec=EscalationRequest)
        mock_created.id = 1
        mock_uow.escalations.create.return_value = mock_created

        with patch.object(service._notification, 'notify_escalation_created', new=AsyncMock()) as mock_notify:
            # Act
            await service.create_escalation(create_data)

            # Assert
            mock_notify.assert_awaited_once_with(
                escalation_id=1,
                user_id=100,
                assignee_id=None,
                reason="Test reason",
                priority="high",
            )

    async def test_create_escalation_notification_failure_not_fatal(self, mock_uow: MagicMock) -> None:
        """Notification failure should not fail escalation creation."""
        # Arrange
        service = EscalationService(mock_uow)
        create_data = EscalationRequestCreate(
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            reason="Test reason",
        )

        mock_created = MagicMock(spec=EscalationRequest)
        mock_created.id = 1
        mock_uow.escalations.create.return_value = mock_created

        with patch.object(service._notification, 'notify_escalation_created', new=AsyncMock()) as mock_notify:
            mock_notify.side_effect = Exception("Notification service down")

            # Act - should not raise
            result = await service.create_escalation(create_data)

            # Assert
            assert result == mock_created
            mock_notify.assert_awaited_once()
            mock_uow.commit.assert_awaited_once()  # Commit still happened

    async def test_assign_escalation_sends_notification(self, mock_uow: MagicMock) -> None:
        """Assigning escalation should trigger notification."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.PENDING,
            assigned_to=None,
            reason="HR issue",
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        with patch.object(service._notification, 'notify_escalation_assigned', new=AsyncMock()) as mock_notify:
            # Act
            await service.assign_escalation(1, assignee_id=200, assigned_by_id=100)

            # Assert
            mock_notify.assert_awaited_once_with(
                escalation_id=1,
                new_assignee_id=200,
                previous_assignee_id=None,
                assigned_by_id=100,
                reason="HR issue",
            )

    async def test_assign_escalation_notification_failure_not_fatal(self, mock_uow: MagicMock) -> None:
        """Notification failure should not fail escalation assignment."""
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

        with patch.object(service._notification, 'notify_escalation_assigned', new=AsyncMock()) as mock_notify:
            mock_notify.side_effect = Exception("Notification service down")

            # Act - should not raise
            result = await service.assign_escalation(1, assignee_id=200)

            # Assert
            assert result.status == EscalationStatus.ASSIGNED
            assert result.assigned_to == 200
            mock_uow.commit.assert_awaited_once()

    async def test_update_escalation_status_change_sends_notification(self, mock_uow: MagicMock) -> None:
        """Status change via update should trigger notification (IN_PROGRESS->RESOLVED)."""
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
            resolution_note="All done",
        )

        with patch.object(service._notification, 'notify_status_change', new=AsyncMock()) as mock_notify:
            # Act
            await service.update_escalation(1, update_data, changed_by_id=200)

            # Assert
            mock_notify.assert_awaited_once_with(
                escalation_id=1,
                user_id=100,
                old_status="IN_PROGRESS",
                new_status="RESOLVED",
                changed_by_id=200,
                comment="All done",
            )

    async def test_update_escalation_no_status_change_no_notification(self, mock_uow: MagicMock) -> None:
        """Update without status change should not trigger notification."""
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

        # Only updating assignee, not status
        update_data = EscalationRequestUpdate(assigned_to=300)

        with patch.object(service._notification, 'notify_status_change', new=AsyncMock()) as mock_notify:
            # Act
            await service.update_escalation(1, update_data)

            # Assert - no notification for status change
            mock_notify.assert_not_awaited()

    async def test_update_escalation_notification_failure_not_fatal(self, mock_uow: MagicMock) -> None:
        """Notification failure should not fail escalation update."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,
            assigned_to=200,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        update_data = EscalationRequestUpdate(status=EscalationStatus.RESOLVED)

        with patch.object(service._notification, 'notify_status_change', new=AsyncMock()) as mock_notify:
            mock_notify.side_effect = Exception("Notification service down")

            # Act - should not raise
            result = await service.update_escalation(1, update_data)

            # Assert
            assert result.status == EscalationStatus.RESOLVED
            mock_uow.commit.assert_awaited_once()

    async def test_resolve_escalation_sends_notification(self, mock_uow: MagicMock) -> None:
        """Resolving escalation should trigger notification."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,
            assigned_to=200,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        with patch.object(service._notification, 'notify_status_change', new=AsyncMock()) as mock_notify:
            # Act
            await service.resolve_escalation(1, resolved_by_id=200, comment="Resolved!")

            # Assert
            mock_notify.assert_awaited_once_with(
                escalation_id=1,
                user_id=100,
                old_status="IN_PROGRESS",
                new_status="RESOLVED",
                changed_by_id=200,
                comment="Resolved!",
            )

    async def test_resolve_escalation_stores_comment_in_context(self, mock_uow: MagicMock) -> None:
        """Resolving escalation should store comment in context."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,
            assigned_to=200,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        with patch.object(service._notification, 'notify_status_change', new=AsyncMock()):
            # Act
            result = await service.resolve_escalation(1, resolved_by_id=200, comment="Fixed it!")

            # Assert
            assert result.context.get("resolution_comment") == "Fixed it!"

    async def test_resolve_escalation_notification_failure_not_fatal(self, mock_uow: MagicMock) -> None:
        """Notification failure should not fail escalation resolution."""
        # Arrange
        service = EscalationService(mock_uow)
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
            status=EscalationStatus.IN_PROGRESS,
            assigned_to=200,
            context={},
        )
        mock_uow.escalations.get_by_id.return_value = request
        mock_uow.escalations.update.return_value = request

        with patch.object(service._notification, 'notify_status_change', new=AsyncMock()) as mock_notify:
            mock_notify.side_effect = Exception("Notification service down")

            # Act - should not raise
            result = await service.resolve_escalation(1, resolved_by_id=200)

            # Assert
            assert result.status == EscalationStatus.RESOLVED
            mock_uow.commit.assert_awaited_once()


class TestNotificationClientSendNotification:
    """Tests for _send_notification method."""

    async def test_send_notification_success(self) -> None:
        """Successful notification send should return True."""
        # Arrange
        client = NotificationClient()

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch('escalation_service.clients.notification_client.httpx.AsyncClient') as mock_http:
            mock_http.return_value.__aenter__ = AsyncMock(return_value=MagicMock(
                post=AsyncMock(return_value=mock_response)
            ))
            mock_http.return_value.__aexit__ = AsyncMock(return_value=None)

            # Act
            result = await client._send_notification(
                user_id=100,
                template_name="test_template",
                variables={"key": "value"},
                channel="telegram",
            )

            # Assert
            assert result is True

    async def test_send_notification_failure_returns_false(self) -> None:
        """Failed notification send should return False."""
        # Arrange
        client = NotificationClient()

        with patch('escalation_service.clients.notification_client.httpx.AsyncClient') as mock_http:
            mock_http.return_value.__aenter__ = AsyncMock(return_value=MagicMock(
                post=AsyncMock(side_effect=Exception("Connection error"))
            ))
            mock_http.return_value.__aexit__ = AsyncMock(return_value=None)

            # Act
            result = await client._send_notification(
                user_id=100,
                template_name="test_template",
                variables={"key": "value"},
                channel="telegram",
            )

            # Assert
            assert result is False

    async def test_send_notification_uses_correct_endpoint(self) -> None:
        """Notification should use correct notification service endpoint."""
        # Arrange
        client = NotificationClient()
        client.base_url = "http://notification_service:8000"
        client.api_key = "test_api_key"

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch('escalation_service.clients.notification_client.httpx.AsyncClient') as mock_http:
            mock_post = AsyncMock(return_value=mock_response)
            mock_http.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=mock_post))
            mock_http.return_value.__aexit__ = AsyncMock(return_value=None)

            # Act
            await client._send_notification(
                user_id=100,
                template_name="test_template",
                variables={"key": "value"},
                channel="telegram",
            )

            # Assert
            mock_post.assert_awaited_once()
            call_args = mock_post.call_args
            assert call_args.args[0] == "http://notification_service:8000/api/v1/notifications/send-template"
            assert call_args.kwargs["headers"]["X-Service-Key"] == "test_api_key"
            assert call_args.kwargs["json"]["user_id"] == 100
            assert call_args.kwargs["json"]["template_name"] == "test_template"
            assert call_args.kwargs["json"]["channel"] == "telegram"
