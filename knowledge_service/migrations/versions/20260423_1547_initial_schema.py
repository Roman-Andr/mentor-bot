"""initial schema

Revision ID: d4f9a73f3559
Revises: 
Create Date: 2026-04-23 15:47:45.377522+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'd4f9a73f3559'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
