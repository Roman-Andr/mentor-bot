"""
initial_schema.

Revision ID: 20260510_escalation_initial
Revises:
Create Date: 2026-05-10 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260510_escalation_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # From escalation_service/migrations/versions/20260425_1441_initial_schema.py
    op.create_table(
        "escalation_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.Enum("HR", "MENTOR", "IT", "GENERAL", name="escalationtype"), nullable=False),
        sa.Column(
            "source",
            sa.Enum("MANUAL", "AUTO_OVERDUE", "AUTO_SEARCH_FAILED", "AUTO_NO_ANSWER", name="escalationsource"),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "REJECTED", "CLOSED", name="escalationstatus"),
            nullable=False,
        ),
        sa.Column("assigned_to", sa.Integer(), nullable=True),
        sa.Column("related_entity_type", sa.String(length=50), nullable=True),
        sa.Column("related_entity_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_escalation_requests_assigned_to"), "escalation_requests", ["assigned_to"], unique=False)
    op.create_index(op.f("ix_escalation_requests_id"), "escalation_requests", ["id"], unique=False)
    op.create_index(op.f("ix_escalation_requests_source"), "escalation_requests", ["source"], unique=False)
    op.create_index(op.f("ix_escalation_requests_status"), "escalation_requests", ["status"], unique=False)
    op.create_index(op.f("ix_escalation_requests_type"), "escalation_requests", ["type"], unique=False)
    op.create_index(op.f("ix_escalation_requests_user_id"), "escalation_requests", ["user_id"], unique=False)

    # From escalation_service/migrations/versions/20260426_add_audit_tables.py
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
        sa.ForeignKeyConstraint(["escalation_id"], ["escalation_requests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_escalation_status_history_escalation_id_changed_at"),
        "escalation_status_history",
        ["escalation_id", "changed_at"],
    )
    op.create_index(
        op.f("ix_escalation_status_history_user_id_changed_at"), "escalation_status_history", ["user_id", "changed_at"]
    )

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
        sa.ForeignKeyConstraint(["escalation_id"], ["escalation_requests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mentor_intervention_history_escalation_id"), "mentor_intervention_history", ["escalation_id"]
    )
    op.create_index(op.f("ix_mentor_intervention_history_mentor_id"), "mentor_intervention_history", ["mentor_id"])
    op.create_index(
        op.f("ix_mentor_intervention_history_intervention_at"), "mentor_intervention_history", ["intervention_at"]
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # From escalation_service/migrations/versions/20260426_add_audit_tables.py
    op.drop_index(op.f("ix_mentor_intervention_history_intervention_at"), table_name="mentor_intervention_history")
    op.drop_index(op.f("ix_mentor_intervention_history_mentor_id"), table_name="mentor_intervention_history")
    op.drop_index(op.f("ix_mentor_intervention_history_escalation_id"), table_name="mentor_intervention_history")
    op.drop_table("mentor_intervention_history")

    op.drop_index(op.f("ix_escalation_status_history_user_id_changed_at"), table_name="escalation_status_history")
    op.drop_index(op.f("ix_escalation_status_history_escalation_id_changed_at"), table_name="escalation_status_history")
    op.drop_table("escalation_status_history")

    # From escalation_service/migrations/versions/20260425_1441_initial_schema.py
    op.drop_index(op.f("ix_escalation_requests_user_id"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_type"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_status"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_source"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_id"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_assigned_to"), table_name="escalation_requests")
    op.drop_table("escalation_requests")
