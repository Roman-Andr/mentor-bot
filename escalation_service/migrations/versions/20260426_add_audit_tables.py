"""
add_audit_tables.

Revision ID: d4e5f6g7h8i9
Revises: 62158e46a6f2
Create Date: 2026-04-26 10:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6g7h8i9"
down_revision: str | None = "62158e46a6f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Escalation status history table
    op.create_table(
        "escalation_status_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("escalation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["escalation_id"], ["escalations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_escalation_status_history_escalation_id_changed_at"), "escalation_status_history", ["escalation_id", "changed_at"])
    op.create_index(op.f("ix_escalation_status_history_user_id_changed_at"), "escalation_status_history", ["user_id", "changed_at"])

    # Mentor intervention history table
    op.create_table(
        "mentor_intervention_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("escalation_id", sa.Integer(), nullable=False),
        sa.Column("mentor_id", sa.Integer(), nullable=False),
        sa.Column("intervention_type", sa.String(length=50), nullable=False),
        sa.Column("intervention_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("outcome", sa.String(length=50), nullable=True),
        sa.Column("escalation_resolved", sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(["escalation_id"], ["escalations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mentor_intervention_history_escalation_id"), "mentor_intervention_history", ["escalation_id"])
    op.create_index(op.f("ix_mentor_intervention_history_mentor_id"), "mentor_intervention_history", ["mentor_id"])
    op.create_index(op.f("ix_mentor_intervention_history_intervention_at"), "mentor_intervention_history", ["intervention_at"])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_mentor_intervention_history_intervention_at"), table_name="mentor_intervention_history")
    op.drop_index(op.f("ix_mentor_intervention_history_mentor_id"), table_name="mentor_intervention_history")
    op.drop_index(op.f("ix_mentor_intervention_history_escalation_id"), table_name="mentor_intervention_history")
    op.drop_table("mentor_intervention_history")

    op.drop_index(op.f("ix_escalation_status_history_user_id_changed_at"), table_name="escalation_status_history")
    op.drop_index(op.f("ix_escalation_status_history_escalation_id_changed_at"), table_name="escalation_status_history")
    op.drop_table("escalation_status_history")
