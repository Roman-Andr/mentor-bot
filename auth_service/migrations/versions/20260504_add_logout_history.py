"""
add_logout_history.

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-05-04 16:00:00.000000+00:00
"""

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6g7h8"
down_revision: str | None = "b2c3d4e5f6g7"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Upgrade database schema."""
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
    op.drop_index(op.f("ix_logout_history_logout_at"), table_name="logout_history")
    op.drop_index(op.f("ix_logout_history_user_id"), table_name="logout_history")
    op.drop_table("logout_history")
