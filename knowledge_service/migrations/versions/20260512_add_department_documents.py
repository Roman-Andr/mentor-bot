"""
add_department_documents.

Revision ID: 20260512_add_dept_docs
Revises: 20260510_knowledge_initial
Create Date: 2026-05-12 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260512_add_dept_docs"
down_revision: str | None = "20260510_knowledge_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "department_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_department_documents_id"), "department_documents", ["id"], unique=False)
    op.create_index(
        op.f("ix_department_documents_department_id"), "department_documents", ["department_id"], unique=False
    )
    op.create_index(
        op.f("ix_department_documents_category"), "department_documents", ["category"], unique=False
    )
    op.create_index(
        op.f("ix_department_documents_is_public"), "department_documents", ["is_public"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_department_documents_is_public"), table_name="department_documents")
    op.drop_index(op.f("ix_department_documents_category"), table_name="department_documents")
    op.drop_index(op.f("ix_department_documents_department_id"), table_name="department_documents")
    op.drop_index(op.f("ix_department_documents_id"), table_name="department_documents")
    op.drop_table("department_documents")
