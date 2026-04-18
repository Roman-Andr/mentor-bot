"""Unit tests for escalation_service/core/enums.py."""

from escalation_service.core.enums import EscalationSource, EscalationStatus, EscalationType


class TestEscalationType:
    """Tests for EscalationType enum."""

    def test_enum_values_match_contract(self) -> None:
        """Enum values should match the contract for persistence."""
        assert EscalationType.HR == "HR"
        assert EscalationType.MENTOR == "MENTOR"
        assert EscalationType.IT == "IT"
        assert EscalationType.GENERAL == "GENERAL"

    def test_enum_values_are_strings(self) -> None:
        """Enum values should be strings (for str, Enum)."""
        for member in EscalationType:
            assert isinstance(member.value, str)
            assert len(member.value) > 0

    def test_no_duplicate_values(self) -> None:
        """No two enum members should have the same value."""
        values = [member.value for member in EscalationType]
        assert len(values) == len(set(values))

    def test_enum_members_are_distinct(self) -> None:
        """Each enum member is a distinct object."""
        assert EscalationType.HR is not EscalationType.MENTOR
        assert EscalationType.HR is not EscalationType.IT
        assert EscalationType.HR is not EscalationType.GENERAL

    def test_string_coercion(self) -> None:
        """Enum with str mixin should allow string comparison via value."""
        # str(Enum) produces "EnumType.MEMBER" in Python
        # But value property gives the actual string value
        assert EscalationType.HR.value == "HR"
        assert EscalationType.GENERAL.value == "GENERAL"
        # Direct comparison with string works via str mixin
        assert EscalationType.HR == "HR"
        assert EscalationType.GENERAL == "GENERAL"


class TestEscalationStatus:
    """Tests for EscalationStatus enum."""

    def test_enum_values_match_contract(self) -> None:
        """Enum values should match the contract for persistence."""
        assert EscalationStatus.PENDING == "PENDING"
        assert EscalationStatus.ASSIGNED == "ASSIGNED"
        assert EscalationStatus.IN_PROGRESS == "IN_PROGRESS"
        assert EscalationStatus.RESOLVED == "RESOLVED"
        assert EscalationStatus.REJECTED == "REJECTED"
        assert EscalationStatus.CLOSED == "CLOSED"

    def test_enum_values_are_strings(self) -> None:
        """Enum values should be strings (for str, Enum)."""
        for member in EscalationStatus:
            assert isinstance(member.value, str)
            assert len(member.value) > 0

    def test_no_duplicate_values(self) -> None:
        """No two enum members should have the same value."""
        values = [member.value for member in EscalationStatus]
        assert len(values) == len(set(values))

    def test_enum_members_are_distinct(self) -> None:
        """Each enum member is a distinct object."""
        statuses = list(EscalationStatus)
        for i, status_a in enumerate(statuses):
            for status_b in statuses[i + 1 :]:
                assert status_a is not status_b

    def test_string_coercion(self) -> None:
        """Enum with str mixin should allow string comparison via value."""
        assert EscalationStatus.PENDING.value == "PENDING"
        assert EscalationStatus.RESOLVED.value == "RESOLVED"
        # Direct comparison with string works via str mixin
        assert EscalationStatus.PENDING == "PENDING"
        assert EscalationStatus.RESOLVED == "RESOLVED"


class TestEscalationSource:
    """Tests for EscalationSource enum."""

    def test_enum_values_match_contract(self) -> None:
        """Enum values should match the contract for persistence."""
        assert EscalationSource.MANUAL == "MANUAL"
        assert EscalationSource.AUTO_OVERDUE == "AUTO_OVERDUE"
        assert EscalationSource.AUTO_SEARCH_FAILED == "AUTO_SEARCH_FAILED"
        assert EscalationSource.AUTO_NO_ANSWER == "AUTO_NO_ANSWER"

    def test_enum_values_are_strings(self) -> None:
        """Enum values should be strings (for str, Enum)."""
        for member in EscalationSource:
            assert isinstance(member.value, str)
            assert len(member.value) > 0

    def test_no_duplicate_values(self) -> None:
        """No two enum members should have the same value."""
        values = [member.value for member in EscalationSource]
        assert len(values) == len(set(values))

    def test_enum_members_are_distinct(self) -> None:
        """Each enum member is a distinct object."""
        sources = list(EscalationSource)
        for i, source_a in enumerate(sources):
            for source_b in sources[i + 1 :]:
                assert source_a is not source_b

    def test_string_coercion(self) -> None:
        """Enum with str mixin should allow string comparison via value."""
        assert EscalationSource.MANUAL.value == "MANUAL"
        assert EscalationSource.AUTO_OVERDUE.value == "AUTO_OVERDUE"
        # Direct comparison with string works via str mixin
        assert EscalationSource.MANUAL == "MANUAL"
        assert EscalationSource.AUTO_OVERDUE == "AUTO_OVERDUE"


class TestEnumComparison:
    """Tests for cross-enum behavior and comparisons."""

    def test_enums_are_independent(self) -> None:
        """Different enum types should not compare equal."""
        # Even if values somehow overlapped, they are different types
        assert EscalationType.HR != EscalationStatus.ASSIGNED
        assert EscalationStatus.PENDING != EscalationSource.MANUAL

    def test_enum_membership(self) -> None:
        """Test that we can check enum membership."""
        assert EscalationType.HR in EscalationType
        assert EscalationStatus.RESOLVED in EscalationStatus
        assert EscalationSource.AUTO_NO_ANSWER in EscalationSource

    def test_enum_iteration(self) -> None:
        """Test that enums are iterable."""
        type_names = [e.name for e in EscalationType]
        assert "HR" in type_names
        assert "MENTOR" in type_names
        assert "IT" in type_names
        assert "GENERAL" in type_names

        status_names = [e.name for e in EscalationStatus]
        assert "PENDING" in status_names
        assert "ASSIGNED" in status_names
        assert "RESOLVED" in status_names
