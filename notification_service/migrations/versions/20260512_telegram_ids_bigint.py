"""Store Telegram recipient IDs as bigint.

Revision ID: 20260512_telegram_ids_bigint
Revises: 20260510_notification_initial
Create Date: 2026-05-12 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260512_telegram_ids_bigint"
down_revision: str | None = "20260510_notification_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.alter_column(
        "notifications",
        "recipient_telegram_id",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=True,
    )
    op.alter_column(
        "scheduled_notifications",
        "recipient_telegram_id",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade database schema."""
    op.alter_column(
        "scheduled_notifications",
        "recipient_telegram_id",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
    op.alter_column(
        "notifications",
        "recipient_telegram_id",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
