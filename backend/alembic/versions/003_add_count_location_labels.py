"""Add user-entered file and section labels to count records.

Revision ID: 003
Revises: 002
"""
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE first_counts ADD COLUMN IF NOT EXISTS file_number VARCHAR(100)")
    op.execute("ALTER TABLE first_counts ADD COLUMN IF NOT EXISTS section_number VARCHAR(100)")
    op.execute("ALTER TABLE second_counts ADD COLUMN IF NOT EXISTS file_number VARCHAR(100)")
    op.execute("ALTER TABLE second_counts ADD COLUMN IF NOT EXISTS section_number VARCHAR(100)")


def downgrade() -> None:
    op.execute("ALTER TABLE first_counts DROP COLUMN IF EXISTS file_number")
    op.execute("ALTER TABLE first_counts DROP COLUMN IF EXISTS section_number")
    op.execute("ALTER TABLE second_counts DROP COLUMN IF EXISTS file_number")
    op.execute("ALTER TABLE second_counts DROP COLUMN IF EXISTS section_number")
