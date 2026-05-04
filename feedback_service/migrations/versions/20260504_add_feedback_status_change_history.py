"""
add_feedback_status_change_history.

Revision ID: a7f8c1d2e3b4
Revises: e5f6g7h8i9j0
Create Date: 2026-05-04 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a7f8c1d2e3b4"
down_revision: str | None = "e5f6g7h8i9j0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.create_table(
        "feedback_status_change_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feedback_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("meta_data", sa.JSON(), nullable=True),
    )
    op.create_index(
        "ix_feedback_status_change_history_feedback_id_changed_at",
        "feedback_status_change_history",
        ["feedback_id", "changed_at"],
    )
    op.create_index(
        "ix_feedback_status_change_history_changed_at",
        "feedback_status_change_history",
        ["changed_at"],
    )


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(
        "ix_feedback_status_change_history_changed_at",
        table_name="feedback_status_change_history",
    )
    op.drop_index(
        "ix_feedback_status_change_history_feedback_id_changed_at",
        table_name="feedback_status_change_history",
    )
    op.drop_table("feedback_status_change_history")
