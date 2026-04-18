"""Unit tests for escalation_service/models/escalation.py."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from escalation_service.core.enums import EscalationSource, EscalationStatus, EscalationType
from escalation_service.models import EscalationRequest


class TestEscalationRequestModel:
    """Tests for EscalationRequest model."""

    def test_escalation_request_creation(self):
        """Test creating an EscalationRequest."""
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            reason="Test reason",
            context={"key": "value"},
            status=EscalationStatus.PENDING,
            assigned_to=200,
            related_entity_type="task",
            related_entity_id=42,
        )

        assert request.id == 1
        assert request.user_id == 100
        assert request.type == EscalationType.GENERAL
        assert request.source == EscalationSource.MANUAL
        assert request.reason == "Test reason"
        assert request.context == {"key": "value"}
        assert request.status == EscalationStatus.PENDING
        assert request.assigned_to == 200
        assert request.related_entity_type == "task"
        assert request.related_entity_id == 42

    def test_escalation_request_repr(self):
        """Test EscalationRequest __repr__ method (line 47)."""
        request = EscalationRequest(
            id=1,
            user_id=100,
            type=EscalationType.GENERAL,
            source=EscalationSource.MANUAL,
            reason="Test reason",
            context={},
            status=EscalationStatus.PENDING,
            assigned_to=None,
        )

        repr_str = repr(request)

        assert "EscalationRequest" in repr_str
        assert "id=1" in repr_str
        assert "user_id=100" in repr_str
        assert "type=<EscalationType.GENERAL" in repr_str or "type=EscalationType.GENERAL" in repr_str
        assert "status=<EscalationStatus.PENDING" in repr_str or "status=EscalationStatus.PENDING" in repr_str

    def test_escalation_request_repr_with_different_status(self):
        """Test EscalationRequest __repr__ with different statuses."""
        # Test with RESOLVED status
        resolved_request = EscalationRequest(
            id=2,
            user_id=200,
            type=EscalationType.IT,
            source=EscalationSource.AUTO_NO_ANSWER,
            status=EscalationStatus.RESOLVED,
        )

        repr_str = repr(resolved_request)

        assert "id=2" in repr_str
        assert "user_id=200" in repr_str
        assert "type=" in repr_str
        assert "status=" in repr_str

    def test_escalation_request_defaults(self):
        """Test EscalationRequest default values before database insertion."""
        request = EscalationRequest(
            user_id=100,
            type=EscalationType.HR,
            source=EscalationSource.MANUAL,
        )

        assert request.id is None
        assert request.reason is None
        # context is a Mapped[dict] with default=dict, will be {} when accessed but starts as None
        assert request.context is None or request.context == {}
        # status has a default in SQLAlchemy but is None until inserted into DB
        assert request.status is None or request.status == EscalationStatus.PENDING
        assert request.assigned_to is None
        assert request.related_entity_type is None
        assert request.related_entity_id is None
        assert request.created_at is None
        assert request.updated_at is None
        assert request.resolved_at is None
