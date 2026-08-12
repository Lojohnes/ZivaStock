"""Make count identity include File No and Section No.

Revision ID: 004
Revises: 003
"""
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE first_counts DROP CONSTRAINT IF EXISTS uq_first_count_scope")
    op.execute("ALTER TABLE second_counts DROP CONSTRAINT IF EXISTS uq_second_count_scope")
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_first_count_scope_v2
        ON first_counts (session_id, product_id, shelf_section_id, user_id,
                         COALESCE(file_number, ''), COALESCE(section_number, ''))
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_second_count_scope_v2
        ON second_counts (session_id, product_id, shelf_section_id, user_id,
                          COALESCE(file_number, ''), COALESCE(section_number, ''))
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_first_count_scope_v2")
    op.execute("DROP INDEX IF EXISTS uq_second_count_scope_v2")
    op.execute("""
        ALTER TABLE first_counts ADD CONSTRAINT uq_first_count_scope
        UNIQUE (session_id, product_id, shelf_section_id, user_id)
    """)
    op.execute("""
        ALTER TABLE second_counts ADD CONSTRAINT uq_second_count_scope
        UNIQUE (session_id, product_id, shelf_section_id, user_id)
    """)
