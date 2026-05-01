"""
add_certificates.

Revision ID: a1b2c3d4e5f6
Revises: b29bbdf86ff8
Create Date: 2026-04-29 20:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "b29bbdf86ff8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.create_table("certificates",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("cert_uid", sa.String(length=36), nullable=False),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("checklist_id", sa.Integer(), nullable=False),
    sa.Column("hr_id", sa.Integer(), nullable=True),
    sa.Column("mentor_id", sa.Integer(), nullable=True),
    sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.ForeignKeyConstraint(["checklist_id"], ["checklists.id"], ),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("cert_uid", name="uq_cert_uid"),
    )
    op.create_index(op.f("ix_certificates_cert_uid"), "certificates", ["cert_uid"], unique=False)
    op.create_index(op.f("ix_certificates_checklist_id"), "certificates", ["checklist_id"], unique=True)
    op.create_index(op.f("ix_certificates_id"), "certificates", ["id"], unique=False)
    op.create_index(op.f("ix_certificates_user_id"), "certificates", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_certificates_user_id"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_id"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_checklist_id"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_cert_uid"), table_name="certificates")
    op.drop_table("certificates")
