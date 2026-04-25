"""
initial_schema.

Revision ID: 0444f265d1b2
Revises:
Create Date: 2026-04-25 14:40:41.900588+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0444f265d1b2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.create_table("departments",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("name", sa.String(length=100), nullable=False),
    sa.Column("description", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_departments_id"), "departments", ["id"], unique=False)
    op.create_index(op.f("ix_departments_name"), "departments", ["name"], unique=True)
    op.create_table("users",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("telegram_id", sa.BigInteger(), nullable=True),
    sa.Column("username", sa.String(length=100), nullable=True),
    sa.Column("first_name", sa.String(length=100), nullable=False),
    sa.Column("last_name", sa.String(length=100), nullable=True),
    sa.Column("email", sa.String(length=255), nullable=False),
    sa.Column("phone", sa.String(length=20), nullable=True),
    sa.Column("employee_id", sa.String(length=50), nullable=False),
    sa.Column("department_id", sa.Integer(), nullable=True),
    sa.Column("position", sa.String(length=100), nullable=True),
    sa.Column("level", sa.Enum("JUNIOR", "MIDDLE", "SENIOR", "LEAD", name="employeelevel"), nullable=True),
    sa.Column("hire_date", sa.DateTime(timezone=True), nullable=True),
    sa.Column("password_hash", sa.String(length=255), nullable=True),
    sa.Column("role", sa.Enum("NEWBIE", "MENTOR", "HR", "ADMIN", name="userrole"), nullable=False),
    sa.Column("is_active", sa.Boolean(), nullable=False),
    sa.Column("is_verified", sa.Boolean(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(["department_id"], ["departments.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_employee_id"), "users", ["employee_id"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)
    op.create_table("invitations",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("token", sa.String(length=64), nullable=False),
    sa.Column("email", sa.String(length=255), nullable=False),
    sa.Column("employee_id", sa.String(length=50), nullable=False),
    sa.Column("first_name", sa.String(length=100), nullable=True),
    sa.Column("last_name", sa.String(length=100), nullable=True),
    sa.Column("department_id", sa.Integer(), nullable=True),
    sa.Column("position", sa.String(length=100), nullable=True),
    sa.Column("level", sa.Enum("JUNIOR", "MIDDLE", "SENIOR", "LEAD", name="employeelevel"), nullable=True),
    sa.Column("role", sa.Enum("NEWBIE", "MENTOR", "HR", "ADMIN", name="userrole"), nullable=False),
    sa.Column("mentor_id", sa.Integer(), nullable=True),
    sa.Column("status", sa.Enum("PENDING", "USED", "REVOKED", name="invitationstatus"), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("user_id", sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(["department_id"], ["departments.id"] ),
    sa.ForeignKeyConstraint(["mentor_id"], ["users.id"] ),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invitations_id"), "invitations", ["id"], unique=False)
    op.create_index(op.f("ix_invitations_token"), "invitations", ["token"], unique=True)
    op.create_table("password_reset_tokens",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("token_hash", sa.String(length=255), nullable=False),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("ip_address", sa.String(length=45), nullable=True),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_password_reset_tokens_id"), "password_reset_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_password_reset_tokens_token_hash"), "password_reset_tokens", ["token_hash"], unique=True)
    op.create_index(op.f("ix_password_reset_tokens_user_id"), "password_reset_tokens", ["user_id"], unique=False)
    op.create_table("user_mentors",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("mentor_id", sa.Integer(), nullable=False),
    sa.Column("is_active", sa.Boolean(), nullable=False),
    sa.Column("notes", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("user_id != mentor_id", name="ck_user_mentor_no_self"),
    sa.ForeignKeyConstraint(["mentor_id"], ["users.id"] ),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_mentors_id"), "user_mentors", ["id"], unique=False)
    op.create_index(op.f("ix_user_mentors_mentor_id"), "user_mentors", ["mentor_id"], unique=False)
    op.create_index(op.f("ix_user_mentors_user_id"), "user_mentors", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f("ix_user_mentors_user_id"), table_name="user_mentors")
    op.drop_index(op.f("ix_user_mentors_mentor_id"), table_name="user_mentors")
    op.drop_index(op.f("ix_user_mentors_id"), table_name="user_mentors")
    op.drop_table("user_mentors")
    op.drop_index(op.f("ix_password_reset_tokens_user_id"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_token_hash"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_id"), table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_index(op.f("ix_invitations_token"), table_name="invitations")
    op.drop_index(op.f("ix_invitations_id"), table_name="invitations")
    op.drop_table("invitations")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_employee_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_departments_name"), table_name="departments")
    op.drop_index(op.f("ix_departments_id"), table_name="departments")
    op.drop_table("departments")
