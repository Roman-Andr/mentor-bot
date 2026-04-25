"""
initial_schema.

Revision ID: 9724532a34a7
Revises:
Create Date: 2026-04-25 14:40:55.343025+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "9724532a34a7"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.create_table("notification_templates",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("name", sa.String(length=100), nullable=False),
    sa.Column("channel", sa.String(length=20), nullable=False),
    sa.Column("language", sa.String(length=10), nullable=False),
    sa.Column("subject", sa.String(length=500), nullable=True),
    sa.Column("body_html", sa.Text(), nullable=True),
    sa.Column("body_text", sa.Text(), nullable=True),
    sa.Column("version", sa.Integer(), nullable=False),
    sa.Column("is_active", sa.Boolean(), nullable=False),
    sa.Column("is_default", sa.Boolean(), nullable=False),
    sa.Column("variables", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("created_by", sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("name", "channel", "language", "is_active", name="uix_template_name_channel_lang_active"),
    )
    op.create_index(op.f("ix_notification_templates_id"), "notification_templates", ["id"], unique=False)
    op.create_index(op.f("ix_notification_templates_name"), "notification_templates", ["name"], unique=False)
    op.create_table("notifications",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("recipient_telegram_id", sa.Integer(), nullable=True),
    sa.Column("recipient_email", sa.String(length=255), nullable=True),
    sa.Column("type", sa.Enum("TASK_REMINDER", "MEETING_REMINDER", "ONBOARDING_EVENT", "GENERAL", "ESCALATION", name="notificationtype"), nullable=False),
    sa.Column("channel", sa.Enum("TELEGRAM", "EMAIL", "BOTH", name="notificationchannel"), nullable=False),
    sa.Column("subject", sa.String(length=500), nullable=True),
    sa.Column("body", sa.Text(), nullable=False),
    sa.Column("data", sa.JSON(), nullable=False),
    sa.Column("status", sa.Enum("PENDING", "SENT", "FAILED", name="notificationstatus"), nullable=False),
    sa.Column("error_message", sa.String(length=1000), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
    sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_type"), "notifications", ["type"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)
    op.create_table("scheduled_notifications",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("recipient_telegram_id", sa.Integer(), nullable=True),
    sa.Column("recipient_email", sa.String(length=255), nullable=True),
    sa.Column("type", sa.Enum("TASK_REMINDER", "MEETING_REMINDER", "ONBOARDING_EVENT", "GENERAL", "ESCALATION", name="notificationtype"), nullable=False),
    sa.Column("channel", sa.Enum("TELEGRAM", "EMAIL", "BOTH", name="notificationchannel"), nullable=False),
    sa.Column("subject", sa.String(length=500), nullable=True),
    sa.Column("body", sa.Text(), nullable=False),
    sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column("scheduled_time", sa.DateTime(timezone=True), nullable=False),
    sa.Column("processed", sa.Boolean(), nullable=False),
    sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("retry_count", sa.Integer(), nullable=False),
    sa.Column("max_retries", sa.Integer(), nullable=False),
    sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scheduled_notifications_id"), "scheduled_notifications", ["id"], unique=False)
    op.create_index(op.f("ix_scheduled_notifications_processed"), "scheduled_notifications", ["processed"], unique=False)
    op.create_index(op.f("ix_scheduled_notifications_scheduled_time"), "scheduled_notifications", ["scheduled_time"], unique=False)
    op.create_index(op.f("ix_scheduled_notifications_type"), "scheduled_notifications", ["type"], unique=False)
    op.create_index(op.f("ix_scheduled_notifications_user_id"), "scheduled_notifications", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_scheduled_notifications_user_id"), table_name="scheduled_notifications")
    op.drop_index(op.f("ix_scheduled_notifications_type"), table_name="scheduled_notifications")
    op.drop_index(op.f("ix_scheduled_notifications_scheduled_time"), table_name="scheduled_notifications")
    op.drop_index(op.f("ix_scheduled_notifications_processed"), table_name="scheduled_notifications")
    op.drop_index(op.f("ix_scheduled_notifications_id"), table_name="scheduled_notifications")
    op.drop_table("scheduled_notifications")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_notification_templates_name"), table_name="notification_templates")
    op.drop_index(op.f("ix_notification_templates_id"), table_name="notification_templates")
    op.drop_table("notification_templates")
