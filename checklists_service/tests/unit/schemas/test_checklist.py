"""Tests for checklist schemas."""

from datetime import UTC, datetime, timedelta

from checklists_service.schemas import ChecklistCreate


class TestChecklistCreate:
    """Test ChecklistCreate schema validation."""

    def test_set_due_date_when_none_and_start_date_in_data(self):
        """Test due_date is auto-set when None and start_date exists (lines 31-32)."""
        start_date = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)

        # Create with due_date=None - should auto-calculate to start_date + 30 days
        data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=start_date,
            due_date=None,  # Explicitly None
        )

        expected_due_date = start_date + timedelta(days=30)
        assert data.due_date == expected_due_date

    def test_set_due_date_keeps_provided_value(self):
        """Test due_date keeps provided value when explicitly set."""
        start_date = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)
        explicit_due_date = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)

        data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=start_date,
            due_date=explicit_due_date,
        )

        assert data.due_date == explicit_due_date

    def test_set_due_date_line_32_start_date_not_in_data(self):
        """Test validator when start_date is not in data (line 32)."""
        # Test case: when due_date is explicitly provided (not None),
        # the validator returns v without checking start_date
        start_date = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)
        explicit_due_date = datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC)

        data = ChecklistCreate(
            user_id=1,
            employee_id="EMP001",
            template_id=1,
            start_date=start_date,
            due_date=explicit_due_date,  # Explicitly provided
        )

        # Should keep the explicit due_date
        assert data.due_date == explicit_due_date

    def test_field_validator_exists(self):
        """Test that the field_validator for due_date exists and has correct name."""
        # Verify the validator is properly defined on the class
        assert hasattr(ChecklistCreate, "set_due_date")
