"""Unit tests for meeting_service core enums."""

from meeting_service.core.enums import EmployeeLevel, MaterialType, MeetingStatus, MeetingType


class TestMeetingType:
    """Tests for MeetingType enum."""

    def test_enum_values_match_contract(self):
        """Enum values must match the persisted contract."""
        assert MeetingType.HR == "HR"
        assert MeetingType.SECURITY == "SECURITY"
        assert MeetingType.TEAM == "TEAM"
        assert MeetingType.MANAGER == "MANAGER"
        assert MeetingType.OTHER == "OTHER"

    def test_no_duplicate_values(self):
        """No duplicate values allowed - would break persistence."""
        values = [e.value for e in MeetingType]
        assert len(values) == len(set(values)), "Duplicate values detected in MeetingType"

    def test_all_members_present(self):
        """All expected members are present."""
        members = set(MeetingType.__members__.keys())
        expected = {"HR", "SECURITY", "TEAM", "MANAGER", "OTHER"}
        assert members == expected

    def test_is_strenum(self):
        """MeetingType is a string enum."""
        assert isinstance(MeetingType.HR, str)
        assert MeetingType.HR.value == "HR"


class TestMeetingStatus:
    """Tests for MeetingStatus enum."""

    def test_enum_values_match_contract(self):
        """Enum values must match the persisted contract."""
        assert MeetingStatus.SCHEDULED == "SCHEDULED"
        assert MeetingStatus.COMPLETED == "COMPLETED"
        assert MeetingStatus.MISSED == "MISSED"
        assert MeetingStatus.CANCELLED == "CANCELLED"

    def test_no_duplicate_values(self):
        """No duplicate values allowed - would break persistence."""
        values = [e.value for e in MeetingStatus]
        assert len(values) == len(set(values)), "Duplicate values detected in MeetingStatus"

    def test_all_members_present(self):
        """All expected members are present."""
        members = set(MeetingStatus.__members__.keys())
        expected = {"SCHEDULED", "COMPLETED", "MISSED", "CANCELLED"}
        assert members == expected

    def test_is_strenum(self):
        """MeetingStatus is a string enum."""
        assert isinstance(MeetingStatus.SCHEDULED, str)
        assert MeetingStatus.SCHEDULED.value == "SCHEDULED"


class TestMaterialType:
    """Tests for MaterialType enum."""

    def test_enum_values_match_contract(self):
        """Enum values must match the persisted contract."""
        assert MaterialType.PDF == "PDF"
        assert MaterialType.LINK == "LINK"
        assert MaterialType.DOC == "DOC"
        assert MaterialType.IMAGE == "IMAGE"
        assert MaterialType.VIDEO == "VIDEO"

    def test_no_duplicate_values(self):
        """No duplicate values allowed - would break persistence."""
        values = [e.value for e in MaterialType]
        assert len(values) == len(set(values)), "Duplicate values detected in MaterialType"

    def test_all_members_present(self):
        """All expected members are present."""
        members = set(MaterialType.__members__.keys())
        expected = {"PDF", "LINK", "DOC", "IMAGE", "VIDEO"}
        assert members == expected

    def test_is_strenum(self):
        """MaterialType is a string enum."""
        assert isinstance(MaterialType.PDF, str)
        assert MaterialType.PDF.value == "PDF"


class TestEmployeeLevel:
    """Tests for EmployeeLevel enum."""

    def test_enum_values_match_contract(self):
        """Enum values must match the persisted contract."""
        assert EmployeeLevel.JUNIOR == "JUNIOR"
        assert EmployeeLevel.MIDDLE == "MIDDLE"
        assert EmployeeLevel.SENIOR == "SENIOR"
        assert EmployeeLevel.LEAD == "LEAD"

    def test_no_duplicate_values(self):
        """No duplicate values allowed - would break persistence."""
        values = [e.value for e in EmployeeLevel]
        assert len(values) == len(set(values)), "Duplicate values detected in EmployeeLevel"

    def test_all_members_present(self):
        """All expected members are present."""
        members = set(EmployeeLevel.__members__.keys())
        expected = {"JUNIOR", "MIDDLE", "SENIOR", "LEAD"}
        assert members == expected

    def test_is_strenum(self):
        """EmployeeLevel is a string enum."""
        assert isinstance(EmployeeLevel.JUNIOR, str)
        assert EmployeeLevel.JUNIOR.value == "JUNIOR"


class TestEnumUniquenessAcrossTypes:
    """Tests to ensure enum types don't have overlapping value issues."""

    def test_meeting_type_values_unique(self):
        """MeetingType values are unique within the enum."""
        values = [e.value for e in MeetingType]
        assert len(values) == len(set(values))

    def test_meeting_status_values_unique(self):
        """MeetingStatus values are unique within the enum."""
        values = [e.value for e in MeetingStatus]
        assert len(values) == len(set(values))

    def test_material_type_values_unique(self):
        """MaterialType values are unique within the enum."""
        values = [e.value for e in MaterialType]
        assert len(values) == len(set(values))

    def test_employee_level_values_unique(self):
        """EmployeeLevel values are unique within the enum."""
        values = [e.value for e in EmployeeLevel]
        assert len(values) == len(set(values))
