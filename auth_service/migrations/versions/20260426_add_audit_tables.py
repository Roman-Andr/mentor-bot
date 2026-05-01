"""
add_audit_tables.

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-26 10:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6g7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
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
    op.create_index(op.f("ix_password_change_history_user_id_changed_at"), "password_change_history", ["user_id", "changed_at"])

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
    op.create_index(op.f("ix_invitation_status_history_invitation_id_changed_at"), "invitation_status_history", ["invitation_id", "changed_at"])

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
    op.create_index(op.f("ix_mentor_assignment_history_user_id_changed_at"), "mentor_assignment_history", ["user_id", "changed_at"])
    op.create_index(op.f("ix_mentor_assignment_history_mentor_id_changed_at"), "mentor_assignment_history", ["mentor_id", "changed_at"])


def downgrade() -> None:
    """Downgrade database schema."""
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
