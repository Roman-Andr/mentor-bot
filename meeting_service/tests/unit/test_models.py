"""Unit tests for model __repr__ methods."""


from meeting_service.core.enums import MeetingStatus, MeetingType
from meeting_service.models import Department, Meeting, MeetingMaterial, UserMeeting
from meeting_service.models.google_calendar_account import GoogleCalendarAccount


class TestDepartmentRepr:
    """Tests for Department model representation."""

    def test_department_repr(self):
        """Test Department __repr__ method."""
        dept = Department(id=1, name="Engineering")
        result = repr(dept)
        assert result == "<Department(id=1, name=Engineering)>"

    def test_department_repr_different_values(self):
        """Test Department __repr__ with different values."""
        dept = Department(id=42, name="Human Resources")
        result = repr(dept)
        assert "id=42" in result
        assert "name=Human Resources" in result


class TestGoogleCalendarAccountRepr:
    """Tests for GoogleCalendarAccount model representation."""

    def test_google_calendar_account_repr(self):
        """Test GoogleCalendarAccount __repr__ method."""
        account = GoogleCalendarAccount(user_id=100, calendar_id="primary")
        result = repr(account)
        assert result == "<GoogleCalendarAccount(user_id=100, calendar_id=primary)>"

    def test_google_calendar_account_repr_custom_calendar(self):
        """Test __repr__ with custom calendar ID."""
        account = GoogleCalendarAccount(user_id=5, calendar_id="work-calendar@example.com")
        result = repr(account)
        assert "user_id=5" in result
        assert "calendar_id=work-calendar@example.com" in result


class TestMeetingRepr:
    """Tests for Meeting model representation."""

    def test_meeting_repr(self):
        """Test Meeting __repr__ method."""
        meeting = Meeting(id=1, title="Quarterly Review", type=MeetingType.HR)
        result = repr(meeting)
        # Note: __repr__ shows type value directly (e.g., "HR") not "MeetingType.HR"
        assert result == "<Meeting(id=1, title=Quarterly Review, type=HR)>"

    def test_meeting_repr_different_type(self):
        """Test Meeting __repr__ with different meeting type."""
        meeting = Meeting(id=5, title="Team Sync", type=MeetingType.TEAM)
        result = repr(meeting)
        assert "id=5" in result
        assert "title=Team Sync" in result
        assert "type=TEAM" in result


class TestMeetingMaterialRepr:
    """Tests for MeetingMaterial model representation."""

    def test_meeting_material_repr(self):
        """Test MeetingMaterial __repr__ method."""
        material = MeetingMaterial(id=1, title="Employee Handbook")
        result = repr(material)
        assert result == "<MeetingMaterial(id=1, title=Employee Handbook)>"

    def test_meeting_material_repr_different_title(self):
        """Test __repr__ with different title."""
        material = MeetingMaterial(id=10, title="Safety Guidelines.pdf")
        result = repr(material)
        assert "id=10" in result
        assert "title=Safety Guidelines.pdf" in result


class TestUserMeetingRepr:
    """Tests for UserMeeting model representation."""

    def test_user_meeting_repr(self):
        """Test UserMeeting __repr__ method."""
        assignment = UserMeeting(id=1, user_id=100, meeting_id=5, status=MeetingStatus.SCHEDULED)
        result = repr(assignment)
        # Note: __repr__ only includes id, user_id, and status (not meeting_id)
        assert result == "<UserMeeting(id=1, user_id=100, status=SCHEDULED)>"

    def test_user_meeting_repr_different_status(self):
        """Test UserMeeting __repr__ with different status."""
        assignment = UserMeeting(id=5, user_id=50, meeting_id=10, status=MeetingStatus.COMPLETED)
        result = repr(assignment)
        assert "id=5" in result
        assert "user_id=50" in result
        assert "status=COMPLETED" in result
