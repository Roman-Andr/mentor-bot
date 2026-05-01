"""
add_audit_tables.

Revision ID: e5f6g7h8i9j0
Revises: 0444f265d1b2
Create Date: 2026-04-26 10:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6g7h8i9j0"
down_revision: str | None = "0444f265d1b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Feedback status change history table
    op.create_table(
        "feedback_status_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("feedback_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["feedback_id"], ["feedback.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_status_change_history_feedback_id_changed_at"), "feedback_status_change_history", ["feedback_id", "changed_at"])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_feedback_status_change_history_feedback_id_changed_at"), table_name="feedback_status_change_history")
    op.drop_table("feedback_status_change_history")
