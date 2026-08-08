-- =============================================================================
-- ZivaStock Production Schema — V009
-- Reporting Views
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. v_product_variance — per-session, per-product reconciliation view
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_product_variance AS
SELECT
    s.id AS session_id,
    s.name AS session_name,
    p.id AS product_id,
    p.barcode,
    p.description,
    p.unit_of_measure,
    p.system_quantity,
    fc.quantity AS first_count_quantity,
    sc.quantity AS second_count_quantity,
    a.final_quantity,
    a.variance_quantity,
    a.variance_value,
    a.adjustment_type,
    a.status AS adjustment_status
FROM stocktake_sessions s
JOIN adjustments a       ON a.session_id = s.id
JOIN products p          ON a.product_id = p.id
LEFT JOIN first_counts fc  ON a.first_count_id = fc.id
LEFT JOIN second_counts sc ON a.second_count_id = sc.id;

-- -----------------------------------------------------------------------------
-- 2. v_session_progress — completion tracking per session
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_session_progress AS
SELECT
    s.id AS session_id,
    s.name AS session_name,
    s.status,
    s.start_time,
    s.end_time,
    l.id AS location_id,
    l.name AS location_name,
    COUNT(DISTINCT sa.shelf_section_id) AS assigned_sections,
    COUNT(DISTINCT fc.shelf_section_id) AS sections_first_counted,
    COUNT(DISTINCT sc.shelf_section_id) AS sections_second_counted,
    COUNT(DISTINCT fc.id) AS total_first_counts,
    COUNT(DISTINCT sc.id) AS total_second_counts,
    COUNT(DISTINCT fc.user_id) AS active_counters,
    ROUND(
        (COUNT(DISTINCT fc.shelf_section_id)::NUMERIC /
         NULLIF(COUNT(DISTINCT sa.shelf_section_id), 0) * 100), 2
    ) AS first_count_completion_pct
FROM stocktake_sessions s
JOIN locations l ON s.location_id = l.id
LEFT JOIN session_assignments sa ON sa.session_id = s.id
LEFT JOIN first_counts fc        ON fc.session_id = s.id
LEFT JOIN second_counts sc       ON sc.session_id = s.id
GROUP BY s.id, s.name, s.status, s.start_time, s.end_time, l.id, l.name;

-- -----------------------------------------------------------------------------
-- 3. v_user_productivity — counting throughput per user
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_user_productivity AS
SELECT
    u.id AS user_id,
    u.email,
    u.first_name,
    u.last_name,
    r.name AS role,
    COUNT(DISTINCT fc.id) AS first_counts_submitted,
    COUNT(DISTINCT sc.id) AS second_counts_submitted,
    COUNT(DISTINCT fc.session_id) + COUNT(DISTINCT sc.session_id) AS sessions_participated,
    COALESCE(SUM(fc.quantity), 0) + COALESCE(SUM(sc.quantity), 0) AS total_quantity_counted,
    MIN(LEAST(fc.counted_at, sc.counted_at)) AS first_activity,
    MAX(GREATEST(fc.counted_at, sc.counted_at)) AS last_activity
FROM users u
JOIN roles r ON u.role_id = r.id
LEFT JOIN first_counts fc  ON fc.user_id = u.id
LEFT JOIN second_counts sc ON sc.user_id = u.id
GROUP BY u.id, u.email, u.first_name, u.last_name, r.name;

-- -----------------------------------------------------------------------------
-- 4. v_pending_adjustments — approval queue
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_pending_adjustments AS
SELECT
    a.id AS adjustment_id,
    a.session_id,
    s.name AS session_name,
    a.product_id,
    p.barcode,
    p.description,
    a.system_quantity,
    a.final_quantity,
    a.variance_quantity,
    a.variance_value,
    a.adjustment_type,
    a.reason,
    a.created_by,
    a.created_at
FROM adjustments a
JOIN stocktake_sessions s ON a.session_id = s.id
JOIN products p           ON a.product_id = p.id
WHERE a.status = 'pending'
ORDER BY a.created_at;

-- -----------------------------------------------------------------------------
-- 5. v_active_sync_queue — items needing operator attention
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_active_sync_queue AS
SELECT
    sq.id,
    sq.user_id,
    u.email AS user_email,
    sq.device_id,
    sq.entity_type,
    sq.action,
    sq.status,
    sq.retry_count,
    sq.error_message,
    sq.created_at,
    sq.last_attempt_at
FROM sync_queue sq
JOIN users u ON sq.user_id = u.id
WHERE sq.status IN ('pending', 'failed')
ORDER BY sq.created_at;

-- -----------------------------------------------------------------------------
-- 6. v_unread_notifications — per-user unread badge counts
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_unread_notifications AS
SELECT
    user_id,
    COUNT(*) AS unread_count,
    MAX(created_at) AS latest_notification_at
FROM notifications
WHERE is_read = FALSE
GROUP BY user_id;
