-- =============================================================================
-- ZivaStock Production Schema — V007
-- Settings, Notifications
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. SETTINGS (system-wide key/value configuration)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS settings (
    id              BIGSERIAL PRIMARY KEY,
    setting_key     VARCHAR(150) UNIQUE NOT NULL,
    setting_value   JSONB NOT NULL,
    category        VARCHAR(50) NOT NULL DEFAULT 'general'
        CHECK (category IN ('general', 'system', 'security', 'notification', 'stocktake', 'sync')),
    description     TEXT,
    data_type       VARCHAR(20) NOT NULL DEFAULT 'string'
        CHECK (data_type IN ('string', 'number', 'boolean', 'json', 'array')),
    is_public       BOOLEAN NOT NULL DEFAULT FALSE,   -- readable by non-admin clients
    is_editable     BOOLEAN NOT NULL DEFAULT TRUE,
    updated_by      BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);
CREATE INDEX IF NOT EXISTS idx_settings_public   ON settings(is_public) WHERE is_public = TRUE;

COMMENT ON TABLE settings IS 'System-wide configuration key/value store (feature flags, thresholds, defaults).';

-- -----------------------------------------------------------------------------
-- 2. NOTIFICATIONS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS notifications (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL
        CHECK (notification_type IN ('session_assigned', 'session_status_change', 'adjustment_pending',
                                      'adjustment_approved', 'sync_failed', 'import_completed',
                                      'export_ready', 'report_ready', 'system')),
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    data            JSONB NOT NULL DEFAULT '{}'::jsonb,
    priority        VARCHAR(10) NOT NULL DEFAULT 'normal'
        CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    read_at         TIMESTAMPTZ,
    action_url      VARCHAR(512),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_notifications_user            ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread            ON notifications(user_id, created_at DESC) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_type               ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_created_brin         ON notifications USING brin (created_at);

COMMENT ON TABLE notifications IS 'Per-user in-app notifications; idx_notifications_unread supports fast unread-count queries.';
