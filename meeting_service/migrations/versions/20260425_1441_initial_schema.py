"""
initial_schema.

Revision ID: 4a048ec3f254
Revises:
Create Date: 2026-04-25 14:41:08.739873+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4a048ec3f254"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.create_table(
        "google_calendar_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("calendar_id", sa.String(length=255), nullable=False),
        sa.Column("sync_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_google_calendar_accounts_id"), "google_calendar_accounts", ["id"], unique=False)
    op.create_index(op.f("ix_google_calendar_accounts_user_id"), "google_calendar_accounts", ["user_id"], unique=True)
    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.Enum("HR", "SECURITY", "TEAM", "MANAGER", "OTHER", name="meetingtype"), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("level", sa.Enum("JUNIOR", "MIDDLE", "SENIOR", "LEAD", name="employeelevel"), nullable=True),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("deadline_days", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meetings_department_id"), "meetings", ["department_id"], unique=False)
    op.create_index(op.f("ix_meetings_id"), "meetings", ["id"], unique=False)
    op.create_index(op.f("ix_meetings_level"), "meetings", ["level"], unique=False)
    op.create_index(op.f("ix_meetings_position"), "meetings", ["position"], unique=False)
    op.create_index(op.f("ix_meetings_type"), "meetings", ["type"], unique=False)
    op.create_table(
        "meeting_materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("type", sa.Enum("PDF", "LINK", "DOC", "IMAGE", "VIDEO", name="materialtype"), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meeting_materials_id"), "meeting_materials", ["id"], unique=False)
    op.create_table(
        "user_meetings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column(
            "status", sa.Enum("SCHEDULED", "COMPLETED", "MISSED", "CANCELLED", name="meetingstatus"), nullable=False
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("google_calendar_event_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "meeting_id", name="uq_user_meeting_assignment"),
    )
    op.create_index(
        op.f("ix_user_meetings_google_calendar_event_id"), "user_meetings", ["google_calendar_event_id"], unique=False
    )
    op.create_index(op.f("ix_user_meetings_id"), "user_meetings", ["id"], unique=False)
    op.create_index(op.f("ix_user_meetings_user_id"), "user_meetings", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_user_meetings_user_id"), table_name="user_meetings")
    op.drop_index(op.f("ix_user_meetings_id"), table_name="user_meetings")
    op.drop_index(op.f("ix_user_meetings_google_calendar_event_id"), table_name="user_meetings")
    op.drop_table("user_meetings")
    op.drop_index(op.f("ix_meeting_materials_id"), table_name="meeting_materials")
    op.drop_table("meeting_materials")
    op.drop_index(op.f("ix_meetings_type"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_position"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_level"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_id"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_department_id"), table_name="meetings")
    op.drop_table("meetings")
    op.drop_index(op.f("ix_google_calendar_accounts_user_id"), table_name="google_calendar_accounts")
    op.drop_index(op.f("ix_google_calendar_accounts_id"), table_name="google_calendar_accounts")
    op.drop_table("google_calendar_accounts")
