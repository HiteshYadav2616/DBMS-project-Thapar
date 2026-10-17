"""Add the admin role required by protected catalog endpoints.

Revision ID: 0001_add_user_role
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_add_user_role"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "Users",
        sa.Column("role", sa.String(length=20), server_default="user", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("Users", "role")
