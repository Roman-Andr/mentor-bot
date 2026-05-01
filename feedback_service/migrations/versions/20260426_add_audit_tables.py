"""
add_audit_tables.

Revision ID: e5f6g7h8i9j0
Revises: 31eef9785faa
Create Date: 2026-04-26 10:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6g7h8i9j0"
down_revision: str | None = "31eef9785faa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # No audit tables needed for feedback service


def downgrade() -> None:
    """Downgrade database schema."""
    pass
