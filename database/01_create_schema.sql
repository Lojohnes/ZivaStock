-- ZivaStock Production Database Schema
-- Database: zivastockdb
-- Engine: PostgreSQL 14+
-- Created: 2026-07-02
-- Description: Complete schema for enterprise multiuser stocktake system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gin;    -- For GIN composite indexes

-- -----------------------------------------------------------------------------
-- 1. CORE IDENTITY & RBAC TABLES
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS permissions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role_id BIGINT NOT NULL REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- -----------------------------------------------------------------------------
-- 2. LOCATION HIERARCHY
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS locations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('store', 'warehouse', 'zone', 'area')),
    parent_id BIGINT REFERENCES locations(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS shelves (
    id BIGSERIAL PRIMARY KEY,
    location_id BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(location_id, name)
);

CREATE TABLE IF NOT EXISTS sections (
    id BIGSERIAL PRIMARY KEY,
    shelf_id BIGINT NOT NULL REFERENCES shelves(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(shelf_id, name)
);

-- -----------------------------------------------------------------------------
-- 3. PRODUCT MASTER DATA
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    product_code VARCHAR(50),
    description TEXT NOT NULL,
    unit_of_measure VARCHAR(20) DEFAULT 'EA' NOT NULL,
    system_quantity DECIMAL(15, 2) DEFAULT 0 NOT NULL,
    unit_cost DECIMAL(15, 2) DEFAULT 0 NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- -----------------------------------------------------------------------------
-- 4. STOCKTAKE SESSIONS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS stocktake_sessions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    location_id BIGINT NOT NULL REFERENCES locations(id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'not_started'
        CHECK (status IN ('not_started', 'in_progress', 'paused', 'completed', 'archived')),
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS session_users (
    session_id BIGINT NOT NULL REFERENCES stocktake_sessions(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (session_id, user_id)
);

-- -----------------------------------------------------------------------------
-- 5. STOCK COUNTS & DUPLICATES
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS counts (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(id),
    section_id BIGINT NOT NULL REFERENCES sections(id),
    quantity DECIMAL(15, 2) NOT NULL CHECK (quantity >= 0),
    user_id BIGINT NOT NULL REFERENCES users(id),
    session_id BIGINT NOT NULL REFERENCES stocktake_sessions(id),
    counted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    synced_at TIMESTAMP WITH TIME ZONE,
    is_synced BOOLEAN DEFAULT FALSE NOT NULL,
    source VARCHAR(20) DEFAULT 'mobile' CHECK (source IN ('mobile', 'web', 'api', 'import')),
    UNIQUE(product_id, section_id, user_id, session_id)
);

CREATE TABLE IF NOT EXISTS duplicates (
    id BIGSERIAL PRIMARY KEY,
    count_id_1 BIGINT NOT NULL REFERENCES counts(id) ON DELETE CASCADE,
    count_id_2 BIGINT NOT NULL REFERENCES counts(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'resolved', 'ignored')),
    resolved_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_different_counts CHECK (count_id_1 < count_id_2),
    UNIQUE(count_id_1, count_id_2)
);

-- -----------------------------------------------------------------------------
-- 6. AUDIT & IMPORT
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS import_batches (
    id BIGSERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    total_records INTEGER DEFAULT 0 NOT NULL,
    success_count INTEGER DEFAULT 0 NOT NULL,
    error_count INTEGER DEFAULT 0 NOT NULL,
    file_path VARCHAR(512),
    mapping_config JSONB,
    error_log JSONB,
    uploaded_by BIGINT NOT NULL REFERENCES users(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- -----------------------------------------------------------------------------
-- 7. MOBILE SYNC
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sync_queue (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT,
    client_id VARCHAR(100) NOT NULL,          -- Mobile-side generated ID for idempotency
    action VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'delete')),
    payload JSONB NOT NULL,
    retry_count INTEGER DEFAULT 0 NOT NULL,
    last_attempt TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, client_id)
);

CREATE TABLE IF NOT EXISTS sync_records (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(100),
    sync_type VARCHAR(20) NOT NULL CHECK (sync_type IN ('push', 'pull', 'full')),
    records_count INTEGER DEFAULT 0 NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('in_progress', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- -----------------------------------------------------------------------------
-- 8. INDEXES FOR PERFORMANCE
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_name ON users(last_name, first_name);

CREATE INDEX IF NOT EXISTS idx_locations_parent ON locations(parent_id);
CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type);
CREATE INDEX IF NOT EXISTS idx_locations_active ON locations(is_active);

CREATE INDEX IF NOT EXISTS idx_shelves_location ON shelves(location_id);
CREATE INDEX IF NOT EXISTS idx_shelves_location_name ON shelves(location_id, name);

CREATE INDEX IF NOT EXISTS idx_sections_shelf ON sections(shelf_id);
CREATE INDEX IF NOT EXISTS idx_sections_shelf_name ON sections(shelf_id, name);

CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_code ON products(product_code);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_description_trgm ON products USING gin (description gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_sessions_location ON stocktake_sessions(location_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON stocktake_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_dates ON stocktake_sessions(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_sessions_created_by ON stocktake_sessions(created_by);

CREATE INDEX IF NOT EXISTS idx_session_users_user ON session_users(user_id);

CREATE INDEX IF NOT EXISTS idx_counts_product ON counts(product_id);
CREATE INDEX IF NOT EXISTS idx_counts_section ON counts(section_id);
CREATE INDEX IF NOT EXISTS idx_counts_user ON counts(user_id);
CREATE INDEX IF NOT EXISTS idx_counts_session ON counts(session_id);
CREATE INDEX IF NOT EXISTS idx_counts_synced ON counts(is_synced);
CREATE INDEX IF NOT EXISTS idx_counts_timestamp ON counts(counted_at);
CREATE INDEX IF NOT EXISTS idx_counts_session_section ON counts(session_id, section_id);
CREATE INDEX IF NOT EXISTS idx_counts_session_product ON counts(session_id, product_id);

CREATE INDEX IF NOT EXISTS idx_duplicates_status ON duplicates(status);
CREATE INDEX IF NOT EXISTS idx_duplicates_counts ON duplicates(count_id_1, count_id_2);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp_user ON audit_logs(created_at, user_id);

CREATE INDEX IF NOT EXISTS idx_import_status ON import_batches(status);
CREATE INDEX IF NOT EXISTS idx_import_uploaded ON import_batches(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_import_uploaded_at ON import_batches(uploaded_at);

CREATE INDEX IF NOT EXISTS idx_sync_user ON sync_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_queue(status);
CREATE INDEX IF NOT EXISTS idx_sync_retry ON sync_queue(status, retry_count);
CREATE INDEX IF NOT EXISTS idx_sync_client ON sync_queue(client_id);
CREATE INDEX IF NOT EXISTS idx_sync_created ON sync_queue(created_at);

CREATE INDEX IF NOT EXISTS idx_sync_records_user ON sync_records(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_records_status ON sync_records(status);
CREATE INDEX IF NOT EXISTS idx_sync_records_timestamp ON sync_records(started_at);

-- -----------------------------------------------------------------------------
-- 9. PARTITIONING SETUP FOR AUDIT LOGS (12-month retention)
-- -----------------------------------------------------------------------------

-- Note: Range partitioning on audit_logs requires initial partition setup.
-- The application or DBA should create new monthly partitions ahead of time.
-- Example below creates partitions for current and next month.

DO $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    -- Convert audit_logs to partitioned table if not already (requires manual migration for existing data)
    -- For fresh installs, uncomment below if you want native partitioning.
    -- ALTER TABLE audit_logs SET PARTITION BY RANGE (created_at);

    -- Create dynamic partitions for current and next 3 months
    FOR i IN 0..3 LOOP
        partition_date := DATE_TRUNC('month', CURRENT_DATE + (i || ' months')::INTERVAL);
        start_date := partition_date;
        end_date := partition_date + INTERVAL '1 month';
        partition_name := 'audit_logs_' || TO_CHAR(partition_date, 'YYYY_MM');

        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF audit_logs
             FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
    END LOOP;
END $$;
