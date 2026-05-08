"""
update_material_types.

Revision ID: 20260508_update_material_types
Revises: 4a048ec3f254
Create Date: 2026-05-08 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260508_update_material_types"
down_revision: str | None = "4a048ec3f254"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Make url nullable
    op.alter_column(
        "meeting_materials",
        "url",
        existing_type=sa.String(length=500),
        nullable=True,
    )
    
    # Add content column for NOTE type
    op.add_column(
        "meeting_materials",
        sa.Column("content", sa.String(length=5000), nullable=True),
    )
    
    # Update enum values from PDF, LINK, DOC, IMAGE, VIDEO to FILE, NOTE, URL
    # First, update existing data to map old types to new types
    op.execute(
        "UPDATE meeting_materials SET type = 'FILE' WHERE type IN ('PDF', 'DOC', 'IMAGE', 'VIDEO')"
    )
    op.execute(
        "UPDATE meeting_materials SET type = 'URL' WHERE type = 'LINK'"
    )
    
    # Then recreate the enum with new values
    op.execute("ALTER TYPE materialtype RENAME TO materialtype_old")
    sa.Enum("FILE", "NOTE", "URL", name="materialtype").create(op.get_bind())
    op.execute(
        "ALTER TABLE meeting_materials ALTER COLUMN type TYPE materialtype USING type::text::materialtype"
    )
    op.execute("DROP TYPE materialtype_old")


def downgrade() -> None:
    """Downgrade database schema."""
    # Revert enum values
    op.execute("ALTER TYPE materialtype RENAME TO materialtype_new")
    sa.Enum("PDF", "LINK", "DOC", "IMAGE", "VIDEO", name="materialtype").create(op.get_bind())
    op.execute(
        "ALTER TABLE meeting_materials ALTER COLUMN type TYPE materialtype USING type::text::materialtype"
    )
    op.execute("DROP TYPE materialtype_new")
    
    # Revert data mapping
    op.execute(
        "UPDATE meeting_materials SET type = 'LINK' WHERE type = 'URL'"
    )
    op.execute(
        "UPDATE meeting_materials SET type = 'PDF' WHERE type = 'FILE'"
    )
    
    # Remove content column
    op.drop_column("meeting_materials", "content")
    
    # Make url not nullable again
    op.alter_column(
        "meeting_materials",
        "url",
        existing_type=sa.String(length=500),
        nullable=False,
    )
