"""
initial_schema.

Revision ID: 20260510_checklists_initial
Revises:
Create Date: 2026-05-10 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260510_checklists_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # From checklists_service/migrations/versions/20260425_1440_initial_schema.py
    op.create_table(
        "templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("level", sa.Enum("JUNIOR", "MIDDLE", "SENIOR", "LEAD", name="employeelevel"), nullable=True),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("task_categories", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("default_assignee_role", sa.String(length=50), nullable=True),
        sa.Column(
            "status", sa.Enum("DRAFT", "ACTIVE", "ARCHIVED", "DEPRECATED", name="templatestatus"), nullable=False
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_templates_id"), "templates", ["id"], unique=False)
    op.create_index(op.f("ix_templates_department_id"), "templates", ["department_id"], unique=False)
    op.create_table(
        "checklists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", "BLOCKED", "CANCELLED", name="status"),
            nullable=False,
        ),
        sa.Column("progress_percentage", sa.Integer(), nullable=False),
        sa.Column("completed_tasks", sa.Integer(), nullable=False),
        sa.Column("total_tasks", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mentor_id", sa.Integer(), nullable=True),
        sa.Column("hr_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_checklists_employee_id"), "checklists", ["employee_id"], unique=False)
    op.create_index(op.f("ix_checklists_id"), "checklists", ["id"], unique=False)
    op.create_index(op.f("ix_checklists_user_id"), "checklists", ["user_id"], unique=False)
    op.create_table(
        "task_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False, index=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column(
            "category",
            sa.Enum(
                "DOCUMENTATION",
                "INTRODUCTION",
                "TECHNICAL",
                "TRAINING",
                "MEETING",
                "PAPERWORK",
                "SECURITY",
                "HR",
                "OTHER",
                name="taskcategory",
            ),
            nullable=False,
        ),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("due_days", sa.Integer(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("resources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("required_documents", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("assignee_role", sa.String(length=50), nullable=True),
        sa.Column("auto_assign", sa.Boolean(), nullable=False),
        sa.Column("depends_on", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_templates_id"), "task_templates", ["id"], unique=False)
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("template_task_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category",
            sa.Enum(
                "DOCUMENTATION",
                "INTRODUCTION",
                "TECHNICAL",
                "TRAINING",
                "MEETING",
                "PAPERWORK",
                "SECURITY",
                "HR",
                "OTHER",
                name="taskcategory",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", "BLOCKED", "CANCELLED", name="status"),
            nullable=False,
        ),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("assignee_id", sa.Integer(), nullable=True),
        sa.Column("assignee_role", sa.String(length=50), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_by", sa.Integer(), nullable=True),
        sa.Column("completion_notes", sa.Text(), nullable=True),
        sa.Column("attachments", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("depends_on", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("blocks", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["checklist_id"], ["checklists.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)

    # From checklists_service/migrations/versions/20260426_add_audit_tables.py
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
    op.create_index(
        op.f("ix_checklist_status_history_checklist_id_changed_at"),
        "checklist_status_history",
        ["checklist_id", "changed_at"],
    )
    op.create_index(
        op.f("ix_checklist_status_history_user_id_changed_at"), "checklist_status_history", ["user_id", "changed_at"]
    )

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
    op.create_index(
        op.f("ix_template_change_history_template_id_changed_at"),
        "template_change_history",
        ["template_id", "changed_at"],
    )

    # From checklists_service/migrations/versions/20260429_2000_add_certificates.py
    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cert_uid", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("hr_id", sa.Integer(), nullable=True),
        sa.Column("mentor_id", sa.Integer(), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["checklist_id"], ["checklists.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cert_uid", name="uq_cert_uid"),
    )
    op.create_index(op.f("ix_certificates_cert_uid"), "certificates", ["cert_uid"], unique=False)
    op.create_index(op.f("ix_certificates_checklist_id"), "certificates", ["checklist_id"], unique=True)
    op.create_index(op.f("ix_certificates_id"), "certificates", ["id"], unique=False)
    op.create_index(op.f("ix_certificates_user_id"), "certificates", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    # From checklists_service/migrations/versions/20260429_2000_add_certificates.py
    op.drop_index(op.f("ix_certificates_user_id"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_id"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_checklist_id"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_cert_uid"), table_name="certificates")
    op.drop_table("certificates")

    # From checklists_service/migrations/versions/20260426_add_audit_tables.py
    op.drop_index(op.f("ix_template_change_history_template_id_changed_at"), table_name="template_change_history")
    op.drop_table("template_change_history")

    op.drop_index(op.f("ix_task_completion_history_user_id"), table_name="task_completion_history")
    op.drop_index(op.f("ix_task_completion_history_checklist_id"), table_name="task_completion_history")
    op.drop_index(op.f("ix_task_completion_history_task_id"), table_name="task_completion_history")
    op.drop_table("task_completion_history")

    op.drop_index(op.f("ix_checklist_status_history_user_id_changed_at"), table_name="checklist_status_history")
    op.drop_index(op.f("ix_checklist_status_history_checklist_id_changed_at"), table_name="checklist_status_history")
    op.drop_table("checklist_status_history")

    # From checklists_service/migrations/versions/20260425_1440_initial_schema.py
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_task_templates_id"), table_name="task_templates")
    op.drop_table("task_templates")
    op.drop_index(op.f("ix_checklists_user_id"), table_name="checklists")
    op.drop_index(op.f("ix_checklists_id"), table_name="checklists")
    op.drop_index(op.f("ix_checklists_employee_id"), table_name="checklists")
    op.drop_table("checklists")
    op.drop_index(op.f("ix_templates_department_id"), table_name="templates")
    op.drop_index(op.f("ix_templates_id"), table_name="templates")
    op.drop_table("templates")
