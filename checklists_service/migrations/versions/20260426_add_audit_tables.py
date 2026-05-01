"""
add_audit_tables.

Revision ID: b2c3d4e5f6g7
Revises: b29bbdf86ff8
Create Date: 2026-04-26 10:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6g7"
down_revision: str | None = "b29bbdf86ff8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Checklist status history table
    op.create_table(
        "checklist_status_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("meta_data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["checklist_id"], ["checklists.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_checklist_status_history_checklist_id_changed_at"), "checklist_status_history", ["checklist_id", "changed_at"])
    op.create_index(op.f("ix_checklist_status_history_user_id_changed_at"), "checklist_status_history", ["user_id", "changed_at"])

    # Task completion history table
    op.create_table(
        "task_completion_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("completion_notes", sa.Text(), nullable=True),
        sa.Column("attachments", sa.JSON(), nullable=True),
        sa.Column("completed_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["checklist_id"], ["checklists.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_completion_history_task_id"), "task_completion_history", ["task_id"])
    op.create_index(op.f("ix_task_completion_history_checklist_id"), "task_completion_history", ["checklist_id"])
    op.create_index(op.f("ix_task_completion_history_user_id"), "task_completion_history", ["user_id"])

    # Template change history table
    op.create_table(
        "template_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_name", sa.Text(), nullable=True),
        sa.Column("new_name", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_template_change_history_template_id_changed_at"), "template_change_history", ["template_id", "changed_at"])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_template_change_history_template_id_changed_at"), table_name="template_change_history")
    op.drop_table("template_change_history")

    op.drop_index(op.f("ix_task_completion_history_user_id"), table_name="task_completion_history")
    op.drop_index(op.f("ix_task_completion_history_checklist_id"), table_name="task_completion_history")
    op.drop_index(op.f("ix_task_completion_history_task_id"), table_name="task_completion_history")
    op.drop_table("task_completion_history")

    op.drop_index(op.f("ix_checklist_status_history_user_id_changed_at"), table_name="checklist_status_history")
    op.drop_index(op.f("ix_checklist_status_history_checklist_id_changed_at"), table_name="checklist_status_history")
    op.drop_table("checklist_status_history")
