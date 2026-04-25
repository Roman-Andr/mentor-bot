"""
initial_schema.

Revision ID: 31eef9785faa
Revises:
Create Date: 2026-04-25 14:41:04.268796+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "31eef9785faa"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.create_table("comments",
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
    op.create_table("experience_ratings",
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
    op.create_table("pulse_surveys",
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


def downgrade() -> None:
    """Downgrade database schema."""
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
