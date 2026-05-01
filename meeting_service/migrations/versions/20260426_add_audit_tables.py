"""
add_audit_tables.

Revision ID: f6g7h8i9j0k1
Revises: 4a048ec3f254
Create Date: 2026-04-26 10:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f6g7h8i9j0k1"
down_revision: str | None = "4a048ec3f254"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Meeting status change history table
    op.create_table(
        "meeting_status_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("meta_data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_meeting_status_change_history_meeting_id_changed_at"),
        "meeting_status_change_history",
        ["meeting_id", "changed_at"],
    )

    # Meeting participant history table
    op.create_table(
        "meeting_participant_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meeting_participant_history_meeting_id"), "meeting_participant_history", ["meeting_id"])
    op.create_index(op.f("ix_meeting_participant_history_user_id"), "meeting_participant_history", ["user_id"])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_meeting_participant_history_user_id"), table_name="meeting_participant_history")
    op.drop_index(op.f("ix_meeting_participant_history_meeting_id"), table_name="meeting_participant_history")
    op.drop_table("meeting_participant_history")

    op.drop_index(
        op.f("ix_meeting_status_change_history_meeting_id_changed_at"), table_name="meeting_status_change_history"
    )
    op.drop_table("meeting_status_change_history")
