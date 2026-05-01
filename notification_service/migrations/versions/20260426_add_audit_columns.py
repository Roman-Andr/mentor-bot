"""
add_audit_columns.

Revision ID: g7h8i9j0k1l2
Revises: 0444f265d1b2
Create Date: 2026-04-26 10:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "g7h8i9j0k1l2"
down_revision: str | None = "0444f265d1b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Add audit columns to notifications table
    op.add_column("notifications", sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notifications", sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notifications", sa.Column("read_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notifications", sa.Column("failure_reason", sa.Text(), nullable=True))
    op.add_column("notifications", sa.Column("metadata", sa.JSON(), nullable=True))

    # Create indexes for audit columns
    op.create_index(op.f("ix_notifications_sent_at"), "notifications", ["sent_at"])
    op.create_index(op.f("ix_notifications_delivered_at"), "notifications", ["delivered_at"])
    op.create_index(op.f("ix_notifications_read_at"), "notifications", ["read_at"])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_notifications_read_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_delivered_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_sent_at"), table_name="notifications")

    op.drop_column("notifications", "metadata")
    op.drop_column("notifications", "failure_reason")
    op.drop_column("notifications", "read_at")
    op.drop_column("notifications", "delivered_at")
    op.drop_column("notifications", "sent_at")
