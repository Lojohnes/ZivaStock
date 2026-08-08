-- =============================================================================
-- ZivaStock Production Schema — V002
-- Product Categories, Products, Locations, Shelves, Shelf Sections
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. PRODUCT_CATEGORIES (self-referential hierarchy)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS product_categories (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    parent_id       BIGINT REFERENCES product_categories(id) ON DELETE SET NULL,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_category_not_self_parent CHECK (parent_id IS DISTINCT FROM id),
    CONSTRAINT uq_category_name_parent UNIQUE (parent_id, name)
);

CREATE INDEX IF NOT EXISTS idx_categories_parent ON product_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_active ON product_categories(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE product_categories IS 'Hierarchical product categorisation (e.g. Beverages > Soft Drinks).';

-- -----------------------------------------------------------------------------
-- 2. PRODUCTS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS products (
    id                  BIGSERIAL PRIMARY KEY,
    sku                 VARCHAR(50) UNIQUE,
    barcode             VARCHAR(50) UNIQUE NOT NULL,
    product_code        VARCHAR(50),
    category_id         BIGINT REFERENCES product_categories(id) ON DELETE SET NULL,
    description         TEXT NOT NULL,
    unit_of_measure     VARCHAR(20) NOT NULL DEFAULT 'EA',
    system_quantity     NUMERIC(18,4) NOT NULL DEFAULT 0,
    unit_cost           NUMERIC(18,4) NOT NULL DEFAULT 0,
    unit_price          NUMERIC(18,4) NOT NULL DEFAULT 0,
    reorder_level       NUMERIC(18,4) NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_products_system_quantity_nonneg CHECK (system_quantity >= 0),
    CONSTRAINT chk_products_unit_cost_nonneg       CHECK (unit_cost >= 0),
    CONSTRAINT chk_products_unit_price_nonneg      CHECK (unit_price >= 0),
    CONSTRAINT chk_products_reorder_nonneg         CHECK (reorder_level >= 0)
);

CREATE INDEX IF NOT EXISTS idx_products_barcode             ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_code                ON products(product_code);
CREATE INDEX IF NOT EXISTS idx_products_category             ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_active               ON products(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_products_description_trgm     ON products USING gin (description gin_trgm_ops);

COMMENT ON TABLE products IS 'Master product catalog with system-of-record quantities used for variance calculation.';

-- -----------------------------------------------------------------------------
-- 3. LOCATIONS (self-referential hierarchy: store/warehouse/zone/area)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS locations (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    type            VARCHAR(50)  NOT NULL CHECK (type IN ('store', 'warehouse', 'zone', 'area')),
    parent_id       BIGINT REFERENCES locations(id) ON DELETE SET NULL,
    address         TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_location_not_self_parent CHECK (parent_id IS DISTINCT FROM id)
);

CREATE INDEX IF NOT EXISTS idx_locations_parent ON locations(parent_id);
CREATE INDEX IF NOT EXISTS idx_locations_type   ON locations(type);
CREATE INDEX IF NOT EXISTS idx_locations_active ON locations(is_active) WHERE is_active = TRUE;

-- -----------------------------------------------------------------------------
-- 4. SHELVES
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS shelves (
    id              BIGSERIAL PRIMARY KEY,
    location_id     BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_shelf_location_name UNIQUE (location_id, name)
);

CREATE INDEX IF NOT EXISTS idx_shelves_location ON shelves(location_id);

-- -----------------------------------------------------------------------------
-- 5. SHELF_SECTIONS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS shelf_sections (
    id              BIGSERIAL PRIMARY KEY,
    shelf_id        BIGINT NOT NULL REFERENCES shelves(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_shelf_section_name UNIQUE (shelf_id, name)
);

CREATE INDEX IF NOT EXISTS idx_shelf_sections_shelf      ON shelf_sections(shelf_id);
CREATE INDEX IF NOT EXISTS idx_shelf_sections_shelf_name ON shelf_sections(shelf_id, name);
