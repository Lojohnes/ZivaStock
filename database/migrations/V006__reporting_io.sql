-- =============================================================================
-- ZivaStock Production Schema — V006
-- Reports, Imports, Exports
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. REPORTS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS reports (
    id              BIGSERIAL PRIMARY KEY,
    uuid            UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    report_type     VARCHAR(50) NOT NULL
        CHECK (report_type IN ('variance', 'productivity', 'duplicates', 'missing_stock',
                                'audit', 'historical', 'adjustment_summary', 'custom')),
    session_id      BIGINT REFERENCES stocktake_sessions(id) ON DELETE SET NULL,
    generated_by    BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    parameters      JSONB NOT NULL DEFAULT '{}'::jsonb,
    file_path       VARCHAR(512),
    file_format     VARCHAR(10) NOT NULL DEFAULT 'pdf' CHECK (file_format IN ('pdf', 'xlsx', 'csv', 'json')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'generating', 'completed', 'failed')),
    error_message   TEXT,
    generated_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reports_session      ON reports(session_id);
CREATE INDEX IF NOT EXISTS idx_reports_generated_by  ON reports(generated_by);
CREATE INDEX IF NOT EXISTS idx_reports_type           ON reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_status          ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_parameters_gin   ON reports USING gin (parameters);

COMMENT ON TABLE reports IS 'Generated report artifacts (PDF/XLSX/CSV) with async generation status tracking.';

-- -----------------------------------------------------------------------------
-- 2. IMPORTS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS imports (
    id                  BIGSERIAL PRIMARY KEY,
    uuid                UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    entity_type         VARCHAR(50) NOT NULL
        CHECK (entity_type IN ('products', 'locations', 'users', 'counts', 'categories')),
    filename            VARCHAR(255) NOT NULL,
    original_filename   VARCHAR(255) NOT NULL,
    file_path           VARCHAR(512),
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'completed_with_errors', 'failed')),
    total_records       INTEGER NOT NULL DEFAULT 0,
    success_count       INTEGER NOT NULL DEFAULT 0,
    error_count         INTEGER NOT NULL DEFAULT 0,
    mapping_config      JSONB,
    error_log           JSONB,
    uploaded_by         BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    uploaded_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at        TIMESTAMPTZ,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_imports_counts_nonneg CHECK (total_records >= 0 AND success_count >= 0 AND error_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_imports_status        ON imports(status);
CREATE INDEX IF NOT EXISTS idx_imports_entity_type     ON imports(entity_type);
CREATE INDEX IF NOT EXISTS idx_imports_uploaded_by      ON imports(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_imports_uploaded_at       ON imports(uploaded_at);

COMMENT ON TABLE imports IS 'Bulk data import batches (products, locations, users, etc.) via CSV/XLSX.';

-- -----------------------------------------------------------------------------
-- 3. EXPORTS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS exports (
    id              BIGSERIAL PRIMARY KEY,
    uuid            UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    export_type     VARCHAR(50) NOT NULL,
    entity_type     VARCHAR(50) NOT NULL,
    filters         JSONB NOT NULL DEFAULT '{}'::jsonb,
    file_path       VARCHAR(512),
    file_format     VARCHAR(10) NOT NULL DEFAULT 'xlsx' CHECK (file_format IN ('xlsx', 'csv', 'pdf', 'json')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message   TEXT,
    requested_by    BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    download_count  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_exports_requested_by  ON exports(requested_by);
CREATE INDEX IF NOT EXISTS idx_exports_status         ON exports(status);
CREATE INDEX IF NOT EXISTS idx_exports_entity_type      ON exports(entity_type);
CREATE INDEX IF NOT EXISTS idx_exports_expires           ON exports(expires_at) WHERE expires_at IS NOT NULL;

COMMENT ON TABLE exports IS 'On-demand data export jobs; expires_at drives cleanup via sp_purge_expired_exports().';
