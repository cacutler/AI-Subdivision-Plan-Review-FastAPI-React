"""initial schema

Revision ID: 6a5462b0
Revises:
Create Date: 2026-07-12

Creates:
  - users table with CHECK constraint on status
  - plans table with CHECK constraints on review_status, FK to users
  - index on plans.user_id
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic
revision: str = "6a5462b0"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Enable pgcrypto for gen_random_uuid() — safe to run if already enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="engineer"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint(
            "status IN ('engineer', 'admin')",
            name="ck_users_status",
        ),
    )

    # ------------------------------------------------------------------
    # plans
    # ------------------------------------------------------------------
    op.create_table(
        "plans",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_path", sa.Text, nullable=False),
        sa.Column("ai_review_notes", JSONB, nullable=True),
        sa.Column(
            "review_status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_plans_user_id",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "review_status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_plans_review_status",
        ),
    )

    op.create_index("ix_plans_user_id", "plans", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_plans_user_id", table_name="plans")
    op.drop_table("plans")
    op.drop_table("users")