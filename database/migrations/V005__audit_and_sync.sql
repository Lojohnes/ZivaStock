-- =============================================================================
-- ZivaStock Production Schema — V005
-- Audit Trail (range-partitioned by month), Sync Queue
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. AUDIT_TRAIL (partitioned by created_at, monthly)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_trail (
    id              BIGSERIAL,
    user_id         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action          VARCHAR(20) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    entity_type     VARCHAR(100) NOT NULL,
    entity_id       BIGINT,
    old_value       JSONB,
    new_value       JSONB,
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE INDEX IF NOT EXISTS idx_audit_trail_user           ON audit_trail(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_entity          ON audit_trail(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_action           ON audit_trail(action);
CREATE INDEX IF NOT EXISTS idx_audit_trail_created           ON audit_trail(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_trail_old_value_gin      ON audit_trail USING gin (old_value);
CREATE INDEX IF NOT EXISTS idx_audit_trail_new_value_gin      ON audit_trail USING gin (new_value);

COMMENT ON TABLE audit_trail IS 'Append-only change history for critical tables. Partitioned monthly; see fn_create_monthly_partition().';

-- -----------------------------------------------------------------------------
-- 2. SYNC_QUEUE (mobile offline-sync ingestion queue)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sync_queue (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id       VARCHAR(100),
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       BIGINT,
    client_id       VARCHAR(100) NOT NULL,        -- mobile-generated idempotency key
    action          VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'delete')),
    payload         JSONB NOT NULL,
    retry_count     INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at    TIMESTAMPTZ,

    CONSTRAINT uq_sync_queue_user_client UNIQUE (user_id, client_id),
    CONSTRAINT chk_sync_retry_nonneg CHECK (retry_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_sync_queue_user     ON sync_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_queue_status    ON sync_queue(status);
CREATE INDEX IF NOT EXISTS idx_sync_queue_retry      ON sync_queue(status, retry_count);
CREATE INDEX IF NOT EXISTS idx_sync_queue_created     ON sync_queue(created_at);
CREATE INDEX IF NOT EXISTS idx_sync_queue_pending      ON sync_queue(created_at) WHERE status = 'pending';

COMMENT ON TABLE sync_queue IS 'Ingestion queue for offline mobile writes; processed asynchronously by the backend sync service.';
