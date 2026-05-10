"""
initial_schema.

Revision ID: 20260510_auth_initial
Revises:
Create Date: 2026-05-10 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260510_auth_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # From auth_service/migrations/versions/20260425_1440_initial_schema.py
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_departments_id"), "departments", ["id"], unique=False)
    op.create_index(op.f("ix_departments_name"), "departments", ["name"], unique=True)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("level", sa.Enum("JUNIOR", "MIDDLE", "SENIOR", "LEAD", name="employeelevel"), nullable=True),
        sa.Column("hire_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("role", sa.Enum("NEWBIE", "MENTOR", "HR", "ADMIN", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_employee_id"), "users", ["employee_id"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)
    op.create_table(
        "invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("level", sa.Enum("JUNIOR", "MIDDLE", "SENIOR", "LEAD", name="employeelevel"), nullable=True),
        sa.Column("role", sa.Enum("NEWBIE", "MENTOR", "HR", "ADMIN", name="userrole"), nullable=False),
        sa.Column("mentor_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "USED", "REVOKED", name="invitationstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invitations_id"), "invitations", ["id"], unique=False)
    op.create_index(op.f("ix_invitations_token"), "invitations", ["token"], unique=True)
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_password_reset_tokens_id"), "password_reset_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_password_reset_tokens_token_hash"), "password_reset_tokens", ["token_hash"], unique=True)
    op.create_index(op.f("ix_password_reset_tokens_user_id"), "password_reset_tokens", ["user_id"], unique=False)
    op.create_table(
        "user_mentors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("mentor_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("user_id != mentor_id", name="ck_user_mentor_no_self"),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_mentors_id"), "user_mentors", ["id"], unique=False)
    op.create_index(op.f("ix_user_mentors_mentor_id"), "user_mentors", ["mentor_id"], unique=False)
    op.create_index(op.f("ix_user_mentors_user_id"), "user_mentors", ["user_id"], unique=False)

    # From auth_service/migrations/versions/20260426_1200_add_user_preferences.py
    op.add_column("users", sa.Column("language", sa.String(length=10), nullable=False, server_default="ru"))
    op.add_column(
        "users", sa.Column("notification_telegram_enabled", sa.Boolean(), nullable=False, server_default="true")
    )
    op.add_column("users", sa.Column("notification_email_enabled", sa.Boolean(), nullable=False, server_default="true"))

    # From auth_service/migrations/versions/20260426_add_audit_tables.py
    # Login history table
    op.create_table(
        "login_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("login_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("method", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_login_history_user_id_login_at"), "login_history", ["user_id", "login_at"])
    op.create_index(op.f("ix_login_history_login_at"), "login_history", ["login_at"])

    # Password change history table
    op.create_table(
        "password_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("method", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_password_change_history_user_id_changed_at"), "password_change_history", ["user_id", "changed_at"]
    )

    # Role change history table
    op.create_table(
        "role_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("old_role", sa.String(length=20), nullable=True),
        sa.Column("new_role", sa.String(length=20), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_role_change_history_user_id_changed_at"), "role_change_history", ["user_id", "changed_at"])

    # Invitation status history table
    op.create_table(
        "invitation_status_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invitation_id", sa.Integer(), nullable=False),
        sa.Column("old_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("meta_data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["invitation_id"], ["invitations.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_invitation_status_history_invitation_id_changed_at"),
        "invitation_status_history",
        ["invitation_id", "changed_at"],
    )

    # Mentor assignment history table
    op.create_table(
        "mentor_assignment_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("mentor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mentor_assignment_history_user_id_changed_at"), "mentor_assignment_history", ["user_id", "changed_at"]
    )
    op.create_index(
        op.f("ix_mentor_assignment_history_mentor_id_changed_at"),
        "mentor_assignment_history",
        ["mentor_id", "changed_at"],
    )

    # From auth_service/migrations/versions/20260504_add_logout_history.py
    # Logout history table
    op.create_table(
        "logout_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("logout_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("method", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_logout_history_user_id"), "logout_history", ["user_id"])
    op.create_index(op.f("ix_logout_history_logout_at"), "logout_history", ["logout_at"])


def downgrade() -> None:
    """Downgrade database schema."""
    # From auth_service/migrations/versions/20260504_add_logout_history.py
    op.drop_index(op.f("ix_logout_history_logout_at"), table_name="logout_history")
    op.drop_index(op.f("ix_logout_history_user_id"), table_name="logout_history")
    op.drop_table("logout_history")

    # From auth_service/migrations/versions/20260426_add_audit_tables.py
    op.drop_index(op.f("ix_mentor_assignment_history_mentor_id_changed_at"), table_name="mentor_assignment_history")
    op.drop_index(op.f("ix_mentor_assignment_history_user_id_changed_at"), table_name="mentor_assignment_history")
    op.drop_table("mentor_assignment_history")

    op.drop_index(op.f("ix_invitation_status_history_invitation_id_changed_at"), table_name="invitation_status_history")
    op.drop_table("invitation_status_history")

    op.drop_index(op.f("ix_role_change_history_user_id_changed_at"), table_name="role_change_history")
    op.drop_table("role_change_history")

    op.drop_index(op.f("ix_password_change_history_user_id_changed_at"), table_name="password_change_history")
    op.drop_table("password_change_history")

    op.drop_index(op.f("ix_login_history_login_at"), table_name="login_history")
    op.drop_index(op.f("ix_login_history_user_id_login_at"), table_name="login_history")
    op.drop_table("login_history")

    # From auth_service/migrations/versions/20260426_1200_add_user_preferences.py
    op.drop_column("users", "notification_email_enabled")
    op.drop_column("users", "notification_telegram_enabled")
    op.drop_column("users", "language")

    # From auth_service/migrations/versions/20260425_1440_initial_schema.py
    op.drop_index(op.f("ix_user_mentors_user_id"), table_name="user_mentors")
    op.drop_index(op.f("ix_user_mentors_mentor_id"), table_name="user_mentors")
    op.drop_index(op.f("ix_user_mentors_id"), table_name="user_mentors")
    op.drop_table("user_mentors")
    op.drop_index(op.f("ix_password_reset_tokens_user_id"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_token_hash"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_id"), table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_index(op.f("ix_invitations_token"), table_name="invitations")
    op.drop_index(op.f("ix_invitations_id"), table_name="invitations")
    op.drop_table("invitations")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_employee_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_departments_name"), table_name="departments")
    op.drop_index(op.f("ix_departments_id"), table_name="departments")
    op.drop_table("departments")
