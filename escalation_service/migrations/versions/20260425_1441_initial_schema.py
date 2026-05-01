"""
initial_schema.

Revision ID: 62158e46a6f2
Revises:
Create Date: 2026-04-25 14:41:00.044239+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "62158e46a6f2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
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


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_escalation_requests_user_id"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_type"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_status"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_source"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_id"), table_name="escalation_requests")
    op.drop_index(op.f("ix_escalation_requests_assigned_to"), table_name="escalation_requests")
    op.drop_table("escalation_requests")
