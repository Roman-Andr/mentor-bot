"""
initial_schema.

Revision ID: 20260510_feedback_initial
Revises:
Create Date: 2026-05-10 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260510_feedback_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # From feedback_service/migrations/versions/20260425_1441_initial_schema.py
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("reply", sa.Text(), nullable=True),
        sa.Column("replied_at", sa.DateTime(), nullable=True),
        sa.Column("replied_by", sa.Integer(), nullable=True),
        sa.Column("allow_contact", sa.Boolean(), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_department_id"), "comments", ["department_id"], unique=False)
    op.create_index(op.f("ix_comments_replied_by"), "comments", ["replied_by"], unique=False)
    op.create_index(op.f("ix_comments_user_id"), "comments", ["user_id"], unique=False)
    op.create_table(
        "experience_ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_experience_ratings_department_id"), "experience_ratings", ["department_id"], unique=False)
    op.create_index(op.f("ix_experience_ratings_rating"), "experience_ratings", ["rating"], unique=False)
    op.create_index(op.f("ix_experience_ratings_user_id"), "experience_ratings", ["user_id"], unique=False)
    op.create_table(
        "pulse_surveys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position_level", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pulse_surveys_department_id"), "pulse_surveys", ["department_id"], unique=False)
    op.create_index(op.f("ix_pulse_surveys_rating"), "pulse_surveys", ["rating"], unique=False)
    op.create_index(op.f("ix_pulse_surveys_user_id"), "pulse_surveys", ["user_id"], unique=False)

    # From feedback_service/migrations/versions/20260426_add_audit_tables.py
    # No audit tables needed for feedback service

    # From feedback_service/migrations/versions/20260504_add_feedback_status_change_history.py
    op.create_table(
        "feedback_status_change_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feedback_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("meta_data", sa.JSON(), nullable=True),
    )
    op.create_index(
        "ix_feedback_status_change_history_feedback_id_changed_at",
        "feedback_status_change_history",
        ["feedback_id", "changed_at"],
    )
    op.create_index(
        "ix_feedback_status_change_history_changed_at",
        "feedback_status_change_history",
        ["changed_at"],
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # From feedback_service/migrations/versions/20260504_add_feedback_status_change_history.py
    op.drop_index(
        "ix_feedback_status_change_history_changed_at",
        table_name="feedback_status_change_history",
    )
    op.drop_index(
        "ix_feedback_status_change_history_feedback_id_changed_at",
        table_name="feedback_status_change_history",
    )
    op.drop_table("feedback_status_change_history")

    # From feedback_service/migrations/versions/20260425_1441_initial_schema.py
    op.drop_index(op.f("ix_pulse_surveys_user_id"), table_name="pulse_surveys")
    op.drop_index(op.f("ix_pulse_surveys_rating"), table_name="pulse_surveys")
    op.drop_index(op.f("ix_pulse_surveys_department_id"), table_name="pulse_surveys")
    op.drop_table("pulse_surveys")
    op.drop_index(op.f("ix_experience_ratings_user_id"), table_name="experience_ratings")
    op.drop_index(op.f("ix_experience_ratings_rating"), table_name="experience_ratings")
    op.drop_index(op.f("ix_experience_ratings_department_id"), table_name="experience_ratings")
    op.drop_table("experience_ratings")
    op.drop_index(op.f("ix_comments_user_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_replied_by"), table_name="comments")
    op.drop_index(op.f("ix_comments_department_id"), table_name="comments")
    op.drop_table("comments")
