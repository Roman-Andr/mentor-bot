"""initial schema

Revision ID: bff590ea6d70
Revises: 
Create Date: 2026-04-23 15:47:44.344712+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'bff590ea6d70'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
