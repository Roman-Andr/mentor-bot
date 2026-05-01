"""
add_user_preferences.

Revision ID: a1b2c3d4e5f6
Revises: 0444f265d1b2
Create Date: 2026-04-26 12:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "0444f265d1b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.add_column("users", sa.Column("language", sa.String(length=10), nullable=False, server_default="ru"))
    op.add_column("users", sa.Column("notification_telegram_enabled", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("users", sa.Column("notification_email_enabled", sa.Boolean(), nullable=False, server_default="true"))


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column("users", "notification_email_enabled")
    op.drop_column("users", "notification_telegram_enabled")
    op.drop_column("users", "language")
