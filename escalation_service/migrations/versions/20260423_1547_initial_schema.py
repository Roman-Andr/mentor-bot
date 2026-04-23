"""initial schema

Revision ID: 4cec4b279299
Revises: 
Create Date: 2026-04-23 15:47:47.271135+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '4cec4b279299'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
