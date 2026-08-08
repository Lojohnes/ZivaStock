-- =============================================================================
-- ZivaStock Production Schema — V001
-- Extensions, Roles, Permissions, Role-Permissions, Users
-- Database: zivastockdb | PostgreSQL 15+
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gin;    -- composite GIN indexes
CREATE EXTENSION IF NOT EXISTS pgcrypto;     -- gen_random_uuid(), digest()
CREATE EXTENSION IF NOT EXISTS citext;       -- case-insensitive email/text comparisons

-- -----------------------------------------------------------------------------
-- 1. ROLES
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS roles (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(50)  UNIQUE NOT NULL,
    description     TEXT,
    is_system       BOOLEAN NOT NULL DEFAULT FALSE,   -- system roles cannot be deleted
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_roles_name_not_blank CHECK (btrim(name) <> '')
);

COMMENT ON TABLE roles IS 'RBAC roles assignable to users.';

-- -----------------------------------------------------------------------------
-- 2. PERMISSIONS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS permissions (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) UNIQUE NOT NULL,      -- e.g. 'products.create'
    module          VARCHAR(50)  NOT NULL,             -- e.g. 'products'
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_permissions_module ON permissions(module);

COMMENT ON TABLE permissions IS 'Fine-grained permission catalog, grouped by module.';

-- -----------------------------------------------------------------------------
-- 3. ROLE_PERMISSIONS (many-to-many)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id         BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id   BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX IF NOT EXISTS idx_role_permissions_permission ON role_permissions(permission_id);

-- -----------------------------------------------------------------------------
-- 4. USERS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id                      BIGSERIAL PRIMARY KEY,
    uuid                    UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    email                   CITEXT UNIQUE NOT NULL,
    password_hash           VARCHAR(255) NOT NULL,
    first_name              VARCHAR(100) NOT NULL,
    last_name               VARCHAR(100) NOT NULL,
    phone_number            VARCHAR(30),
    role_id                 BIGINT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    is_locked               BOOLEAN NOT NULL DEFAULT FALSE,
    failed_login_attempts   SMALLINT NOT NULL DEFAULT 0,
    last_login_at           TIMESTAMPTZ,
    last_login_ip           INET,
    password_changed_at     TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_users_failed_attempts CHECK (failed_login_attempts >= 0)
);

CREATE INDEX IF NOT EXISTS idx_users_role            ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_active          ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_users_name            ON users(last_name, first_name);

COMMENT ON TABLE users IS 'Application users. email uses CITEXT for case-insensitive uniqueness/login lookups.';
COMMENT ON COLUMN users.uuid IS 'Public-facing identifier — never expose BIGSERIAL id externally.';
