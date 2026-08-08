"""Initial v2 production schema (zivastockdb)

Applies database/migrations/V001..V012 (schema, indexes, views, functions,
triggers, partition bootstrap) verbatim via exec_driver_sql so the SQL
design docs remain the single source of truth for DDL.

Revision ID: 001
Revises:
Create Date: 2026-08-01 00:00:00.000000

"""
from pathlib import Path
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

# backend/alembic/versions/001_initial_schema.py -> parents[3] == repo root
MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "database" / "migrations"

SQL_FILES = [
    "V001__extensions_and_identity.sql",
    "V002__catalog_and_locations.sql",
    "V003__stocktake_sessions.sql",
    "V004__counts_and_adjustments.sql",
    "V005__audit_and_sync.sql",
    "V006__reporting_io.sql",
    "V007__system_tables.sql",
    "V008__performance_indexes.sql",
    "V009__views.sql",
    "V010__functions_and_procedures.sql",
    "V011__triggers.sql",
    "V012__partition_bootstrap.sql",
]


def upgrade() -> None:
    bind = op.get_bind()
    raw_cursor = bind.connection.cursor()
    for filename in SQL_FILES:
        sql_path = MIGRATIONS_DIR / filename
        sql_text = sql_path.read_text(encoding="utf-8")
        raw_cursor.execute(sql_text)
    raw_cursor.close()


def downgrade() -> None:
    bind = op.get_bind()
    raw_cursor = bind.connection.cursor()
    raw_cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    raw_cursor.close()


_DELETE_MARKER_START = """
def _legacy_v1_upgrade_DO_NOT_CALL() -> None:
    op.create_table(
        'roles',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)
    
    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('permission_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    # Create locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['locations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_id'), 'locations', ['id'], unique=False)
    op.create_index(op.f('ix_locations_parent'), 'locations', ['parent_id'], unique=False)
    op.create_index(op.f('ix_locations_type'), 'locations', ['type'], unique=False)
    
    # Create shelves table
    op.create_table(
        'shelves',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('location_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('location_id', 'name')
    )
    op.create_index(op.f('ix_shelves_id'), 'shelves', ['id'], unique=False)
    op.create_index(op.f('ix_shelves_location'), 'shelves', ['location_id'], unique=False)
    
    # Create sections table
    op.create_table(
        'sections',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('shelf_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['shelf_id'], ['shelves.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('shelf_id', 'name')
    )
    op.create_index(op.f('ix_sections_id'), 'sections', ['id'], unique=False)
    op.create_index(op.f('ix_sections_shelf'), 'sections', ['shelf_id'], unique=False)
    
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('barcode', sa.String(length=50), nullable=False),
        sa.Column('product_code', sa.String(length=50), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('unit_of_measure', sa.String(length=20), nullable=True),
        sa.Column('system_quantity', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('unit_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('barcode')
    )
    op.create_index(op.f('ix_products_barcode'), 'products', ['barcode'], unique=True)
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_product_code'), 'products', ['product_code'], unique=False)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_active'), 'users', ['is_active'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role_id'], unique=False)
    
    # Create stocktake_sessions table
    op.create_table(
        'stocktake_sessions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location_id', sa.BigInteger(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stocktake_sessions_dates'), 'stocktake_sessions', ['start_time', 'end_time'], unique=False)
    op.create_index(op.f('ix_stocktake_sessions_id'), 'stocktake_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_stocktake_sessions_location'), 'stocktake_sessions', ['location_id'], unique=False)
    op.create_index(op.f('ix_stocktake_sessions_status'), 'stocktake_sessions', ['status'], unique=False)
    
    # Create session_users table
    op.create_table(
        'session_users',
        sa.Column('session_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['stocktake_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id', 'user_id')
    )
    op.create_index(op.f('ix_session_users_user'), 'session_users', ['user_id'], unique=False)
    
    # Create counts table
    op.create_table(
        'counts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('section_id', sa.BigInteger(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('session_id', sa.BigInteger(), nullable=False),
        sa.Column('counted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_synced', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id']),
        sa.ForeignKeyConstraint(['session_id'], ['stocktake_sessions.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'section_id', 'user_id', 'session_id', name='uq_count_section_user_session')
    )
    op.create_index(op.f('ix_counts_id'), 'counts', ['id'], unique=False)
    op.create_index(op.f('ix_counts_product'), 'counts', ['product_id'], unique=False)
    op.create_index(op.f('ix_counts_section'), 'counts', ['section_id'], unique=False)
    op.create_index(op.f('ix_counts_session'), 'counts', ['session_id'], unique=False)
    op.create_index(op.f('ix_counts_synced'), 'counts', ['is_synced'], unique=False)
    op.create_index(op.f('ix_counts_timestamp'), 'counts', ['counted_at'], unique=False)
    op.create_index(op.f('ix_counts_user'), 'counts', ['user_id'], unique=False)
    
    # Create duplicates table
    op.create_table(
        'duplicates',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('count_id_1', sa.BigInteger(), nullable=False),
        sa.Column('count_id_2', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('resolved_by', sa.BigInteger(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['count_id_1'], ['counts.id']),
        sa.ForeignKeyConstraint(['count_id_2'], ['counts.id']),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_duplicates_counts'), 'duplicates', ['count_id_1', 'count_id_2'], unique=False)
    op.create_index(op.f('ix_duplicates_id'), 'duplicates', ['id'], unique=False)
    op.create_index(op.f('ix_duplicates_status'), 'duplicates', ['status'], unique=False)
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.BigInteger(), nullable=True),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_entity'), 'audit_logs', ['entity_type', 'entity_id'], unique=False)
    op.create_index(op.f('ix_audit_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_timestamp'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_timestamp_user'), 'audit_logs', ['created_at', 'user_id'], unique=False)
    op.create_index(op.f('ix_audit_user'), 'audit_logs', ['user_id'], unique=False)
    
    # Create import_batches table
    op.create_table(
        'import_batches',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('total_records', sa.Integer(), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('uploaded_by', sa.BigInteger(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_import_status'), 'import_batches', ['status'], unique=False)
    op.create_index(op.f('ix_import_uploaded'), 'import_batches', ['uploaded_by'], unique=False)
    
    # Create sync_queue table
    op.create_table(
        'sync_queue',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('last_attempt', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sync_retry'), 'sync_queue', ['status', 'retry_count'], unique=False)
    op.create_index(op.f('ix_sync_status'), 'sync_queue', ['status'], unique=False)
    op.create_index(op.f('ix_sync_user'), 'sync_queue', ['user_id'], unique=False)
    
    # Create sync_records table
    op.create_table(
        'sync_records',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('sync_type', sa.String(length=20), nullable=False),
        sa.Column('records_count', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sync_records_status'), 'sync_records', ['status'], unique=False)
    op.create_index(op.f('ix_sync_records_timestamp'), 'sync_records', ['started_at'], unique=False)
    op.create_index(op.f('ix_sync_records_user'), 'sync_records', ['user_id'], unique=False)
    
    # Insert default roles
    op.execute("INSERT INTO roles (name, description) VALUES ('super_admin', 'Full system access')")
    op.execute("INSERT INTO roles (name, description) VALUES ('stocktake_manager', 'Manage stocktake sessions')")
    op.execute("INSERT INTO roles (name, description) VALUES ('supervisor', 'Monitor counters')")
    op.execute("INSERT INTO roles (name, description) VALUES ('counter', 'Count stock only')")
    op.execute("INSERT INTO roles (name, description) VALUES ('auditor', 'View reports only')")
    
    # Insert default permissions
    op.execute("INSERT INTO permissions (name, description) VALUES ('users.create', 'Create new users')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('users.read', 'View user information')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('users.update', 'Update user information')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('users.delete', 'Delete users')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('products.create', 'Create products')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('products.read', 'View products')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('products.update', 'Update products')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('products.delete', 'Delete products')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('counts.create', 'Create stock counts')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('counts.read', 'View stock counts')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('counts.update', 'Update stock counts')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('counts.delete', 'Delete stock counts')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('sessions.create', 'Create stocktake sessions')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('sessions.read', 'View stocktake sessions')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('sessions.update', 'Update stocktake sessions')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('sessions.delete', 'Delete stocktake sessions')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('reports.read', 'View reports')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('reports.export', 'Export reports')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('imports.create', 'Import data')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('exports.create', 'Export data')")
    op.execute("INSERT INTO permissions (name, description) VALUES ('audit.read', 'View audit logs')")


def _unused_reference_downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('sync_records')
    op.drop_table('sync_queue')
    op.drop_table('import_batches')
    op.drop_table('audit_logs')
    op.drop_table('duplicates')
    op.drop_table('counts')
    op.drop_table('session_users')
    op.drop_table('stocktake_sessions')
    op.drop_table('users')
    op.drop_table('products')
    op.drop_table('sections')
    op.drop_table('shelves')
    op.drop_table('locations')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
"""
