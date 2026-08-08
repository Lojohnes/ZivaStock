-- =============================================================================
-- ZivaStock Production Schema — V004
-- First Counts, Second Counts, Adjustments
-- High-volume tables — optimised for millions of rows (see README for
-- the partitioning-vs-indexing trade-off rationale).
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. FIRST_COUNTS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS first_counts (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES stocktake_sessions(id) ON DELETE CASCADE,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    shelf_section_id    BIGINT NOT NULL REFERENCES shelf_sections(id) ON DELETE RESTRICT,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    quantity            NUMERIC(18,4) NOT NULL,
    client_id           VARCHAR(100),                 -- mobile-generated idempotency key
    device_id           VARCHAR(100),
    source              VARCHAR(20) NOT NULL DEFAULT 'mobile'
        CHECK (source IN ('mobile', 'web', 'api', 'import')),
    counted_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_synced           BOOLEAN NOT NULL DEFAULT FALSE,
    synced_at           TIMESTAMPTZ,

    CONSTRAINT chk_first_counts_qty_nonneg CHECK (quantity >= 0),
    CONSTRAINT uq_first_count_scope UNIQUE (session_id, product_id, shelf_section_id, user_id),
    CONSTRAINT uq_first_count_client UNIQUE (user_id, client_id)
);

CREATE INDEX IF NOT EXISTS idx_first_counts_session          ON first_counts(session_id);
CREATE INDEX IF NOT EXISTS idx_first_counts_product           ON first_counts(product_id);
CREATE INDEX IF NOT EXISTS idx_first_counts_shelf_section      ON first_counts(shelf_section_id);
CREATE INDEX IF NOT EXISTS idx_first_counts_user               ON first_counts(user_id);
CREATE INDEX IF NOT EXISTS idx_first_counts_synced              ON first_counts(is_synced) WHERE is_synced = FALSE;
CREATE INDEX IF NOT EXISTS idx_first_counts_session_section     ON first_counts(session_id, shelf_section_id);
CREATE INDEX IF NOT EXISTS idx_first_counts_session_product     ON first_counts(session_id, product_id);
-- BRIN: cheap, high-value index for large append-mostly time-ordered data
CREATE INDEX IF NOT EXISTS idx_first_counts_counted_at_brin ON first_counts USING brin (counted_at);

COMMENT ON TABLE first_counts IS 'Independent first-pass count entries submitted by counters.';

-- -----------------------------------------------------------------------------
-- 2. SECOND_COUNTS
-- Independent verification count, optionally linked to the first_counts row
-- it is reconciling against. Segregation of duties enforced via trigger
-- (see V011__triggers.sql: trg_prevent_same_user_second_count).
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS second_counts (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES stocktake_sessions(id) ON DELETE CASCADE,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    shelf_section_id    BIGINT NOT NULL REFERENCES shelf_sections(id) ON DELETE RESTRICT,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    first_count_id      BIGINT REFERENCES first_counts(id) ON DELETE SET NULL,
    quantity            NUMERIC(18,4) NOT NULL,
    client_id           VARCHAR(100),
    device_id           VARCHAR(100),
    source              VARCHAR(20) NOT NULL DEFAULT 'mobile'
        CHECK (source IN ('mobile', 'web', 'api', 'import')),
    counted_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_synced           BOOLEAN NOT NULL DEFAULT FALSE,
    synced_at           TIMESTAMPTZ,

    CONSTRAINT chk_second_counts_qty_nonneg CHECK (quantity >= 0),
    CONSTRAINT uq_second_count_scope UNIQUE (session_id, product_id, shelf_section_id, user_id),
    CONSTRAINT uq_second_count_client UNIQUE (user_id, client_id)
);

CREATE INDEX IF NOT EXISTS idx_second_counts_session         ON second_counts(session_id);
CREATE INDEX IF NOT EXISTS idx_second_counts_product          ON second_counts(product_id);
CREATE INDEX IF NOT EXISTS idx_second_counts_shelf_section     ON second_counts(shelf_section_id);
CREATE INDEX IF NOT EXISTS idx_second_counts_user              ON second_counts(user_id);
CREATE INDEX IF NOT EXISTS idx_second_counts_first_count        ON second_counts(first_count_id);
CREATE INDEX IF NOT EXISTS idx_second_counts_synced             ON second_counts(is_synced) WHERE is_synced = FALSE;
CREATE INDEX IF NOT EXISTS idx_second_counts_session_section    ON second_counts(session_id, shelf_section_id);
CREATE INDEX IF NOT EXISTS idx_second_counts_session_product    ON second_counts(session_id, product_id);
CREATE INDEX IF NOT EXISTS idx_second_counts_counted_at_brin ON second_counts USING brin (counted_at);

COMMENT ON TABLE second_counts IS 'Independent verification count entries; segregation of duties enforced by trigger.';

-- -----------------------------------------------------------------------------
-- 3. ADJUSTMENTS
-- One row per product per session — final reconciliation record.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS adjustments (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES stocktake_sessions(id) ON DELETE CASCADE,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    shelf_section_id    BIGINT REFERENCES shelf_sections(id) ON DELETE SET NULL,
    first_count_id      BIGINT REFERENCES first_counts(id) ON DELETE SET NULL,
    second_count_id     BIGINT REFERENCES second_counts(id) ON DELETE SET NULL,
    system_quantity     NUMERIC(18,4) NOT NULL,        -- snapshot at reconciliation time
    final_quantity      NUMERIC(18,4) NOT NULL,        -- agreed/resolved physical quantity
    variance_quantity   NUMERIC(18,4) GENERATED ALWAYS AS (final_quantity - system_quantity) STORED,
    unit_cost_snapshot  NUMERIC(18,4) NOT NULL DEFAULT 0,
    variance_value      NUMERIC(18,4) GENERATED ALWAYS AS ((final_quantity - system_quantity) * unit_cost_snapshot) STORED,
    adjustment_type     VARCHAR(20) NOT NULL DEFAULT 'none'
        CHECK (adjustment_type IN ('increase', 'decrease', 'none')),
    reason              TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected', 'posted')),
    created_by          BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    approved_by         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    approved_at         TIMESTAMPTZ,
    posted_at           TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_adjustment_scope UNIQUE (session_id, product_id, shelf_section_id)
);

CREATE INDEX IF NOT EXISTS idx_adjustments_session   ON adjustments(session_id);
CREATE INDEX IF NOT EXISTS idx_adjustments_product    ON adjustments(product_id);
CREATE INDEX IF NOT EXISTS idx_adjustments_status     ON adjustments(status);
CREATE INDEX IF NOT EXISTS idx_adjustments_type       ON adjustments(adjustment_type);
CREATE INDEX IF NOT EXISTS idx_adjustments_pending    ON adjustments(session_id) WHERE status = 'pending';

COMMENT ON TABLE adjustments IS 'Final per-product reconciliation between first/second counts and system quantity; drives inventory correction.';
