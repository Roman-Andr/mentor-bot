"""Unit tests for User model."""

from datetime import UTC, datetime

import pytest

from auth_service.core.enums import UserRole
from auth_service.models import User


class TestUserFullNameProperty:
    """Tests for User.full_name property (lines 85-87)."""

    def test_full_name_with_last_name(self):
        """Test full_name when both first_name and last_name are set."""
        user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )
        assert user.full_name == "John Doe"

    def test_full_name_without_last_name(self):
        """Test full_name when last_name is None (covers line 87)."""
        user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name=None,
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )
        assert user.full_name == "John"

    def test_full_name_with_empty_last_name(self):
        """Test full_name when last_name is empty string (covers line 85-87)."""
        user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )
        # Empty string is falsy, so should return just first_name
        assert user.full_name == "John"


class TestUserNormalizeEmail:
    """Tests for User email normalization event listeners (lines 98-99)."""

    def test_email_normalized_on_before_insert(self):
        """Test that email is normalized to lowercase before insert (line 98-99)."""
        user = User(
            id=1,
            email="UPPERCASE@EXAMPLE.COM",
            first_name="John",
            last_name="Doe",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )

        # Manually trigger the event listener (simulating what SQLAlchemy does)
        from auth_service.models.user import normalize_email_case
        normalize_email_case(None, None, user)

        assert user.email == "uppercase@example.com"

    def test_email_normalized_on_before_update(self):
        """Test that email is normalized to lowercase before update (line 98-99)."""
        user = User(
            id=1,
            email="lowercase@example.com",
            first_name="John",
            last_name="Doe",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )

        # Change email to uppercase
        user.email = "NEWEMAIL@EXAMPLE.COM"

        # Manually trigger the event listener
        from auth_service.models.user import normalize_email_case
        normalize_email_case(None, None, user)

        assert user.email == "newemail@example.com"

    def test_email_none_not_normalized(self):
        """Test that None email is handled properly (covers line 98)."""
        # This tests the edge case where email might be None
        user = User(
            id=1,
            email="test@example.com",  # Valid initially
            first_name="John",
            last_name="Doe",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )

        # Set email to None
        user.email = None

        # Manually trigger the event listener
        from auth_service.models.user import normalize_email_case
        # Should not raise any error
        normalize_email_case(None, None, user)

        # Email should remain None
        assert user.email is None


class TestUserRepr:
    """Tests for User.__repr__ method (line 91)."""

    def test_repr(self):
        """Test the string representation of User."""
        user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            employee_id="EMP001",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        repr_str = repr(user)
        assert "User(id=1" in repr_str
        assert "email=test@example.com" in repr_str
        assert "role=ADMIN" in repr_str


class TestUserMentorIdProperty:
    """Tests for User.mentor_id property (lines 75-80)."""

    def test_mentor_id_with_active_assignment(self):
        """Test mentor_id when there's an active assignment."""
        from auth_service.models import UserMentor

        user = User(
            id=1,
            email="newbie@example.com",
            first_name="Newbie",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )

        # Add an active mentor assignment
        mentor_relation = UserMentor(
            id=1,
            user_id=1,
            mentor_id=5,
            is_active=True,
            created_at=datetime.now(UTC),
        )
        user.mentor_assignments.append(mentor_relation)

        assert user.mentor_id == 5

    def test_mentor_id_with_inactive_assignment(self):
        """Test mentor_id when assignment is not active."""
        from auth_service.models import UserMentor

        user = User(
            id=1,
            email="newbie@example.com",
            first_name="Newbie",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )

        # Add an inactive mentor assignment
        mentor_relation = UserMentor(
            id=1,
            user_id=1,
            mentor_id=5,
            is_active=False,  # Inactive
            created_at=datetime.now(UTC),
        )
        user.mentor_assignments.append(mentor_relation)

        assert user.mentor_id is None

    def test_mentor_id_no_assignments(self):
        """Test mentor_id when there are no assignments."""
        user = User(
            id=1,
            email="newbie@example.com",
            first_name="Newbie",
            employee_id="EMP001",
            role=UserRole.NEWBIE,
            is_active=True,
            is_verified=True,
        )

        assert user.mentor_id is None
