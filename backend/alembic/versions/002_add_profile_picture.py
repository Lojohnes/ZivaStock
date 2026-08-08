"""Add profile picture storage to users.

Revision ID: 002
Revises: 001
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS profile_picture")
