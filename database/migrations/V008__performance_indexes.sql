-- =============================================================================
-- ZivaStock Production Schema — V008
-- Additional composite / covering indexes for high-frequency reporting queries.
-- (Per-table single/dual-column indexes already declared in V001–V007.)
-- =============================================================================

-- Variance report: join first_counts + second_counts + products by session,
-- frequently filtered by session_id and grouped by product_id.
CREATE INDEX IF NOT EXISTS idx_first_counts_session_product_covering
    ON first_counts(session_id, product_id) INCLUDE (quantity, shelf_section_id, user_id);

CREATE INDEX IF NOT EXISTS idx_second_counts_session_product_covering
    ON second_counts(session_id, product_id) INCLUDE (quantity, shelf_section_id, user_id);

-- Session progress dashboard: count distinct sections/users per session quickly.
CREATE INDEX IF NOT EXISTS idx_assignments_session_covering
    ON session_assignments(session_id, status) INCLUDE (user_id, shelf_section_id, assignment_role);

-- Adjustment approval queue: pending adjustments ordered by creation time.
CREATE INDEX IF NOT EXISTS idx_adjustments_pending_queue
    ON adjustments(status, created_at) WHERE status = 'pending';

-- Product lookup by category for catalog browsing / import validation.
CREATE INDEX IF NOT EXISTS idx_products_category_active
    ON products(category_id, is_active) WHERE is_active = TRUE;

-- Sync queue worker pickup: oldest pending/failed items first, per user.
CREATE INDEX IF NOT EXISTS idx_sync_queue_worker_pickup
    ON sync_queue(status, created_at) WHERE status IN ('pending', 'failed');

-- Audit trail lookups by entity for "view history" screens (per-partition local index,
-- automatically applied to future partitions since declared on the parent).
CREATE INDEX IF NOT EXISTS idx_audit_trail_entity_created
    ON audit_trail(entity_type, entity_id, created_at DESC);

-- Notification badge counts per user (already partially covered by idx_notifications_unread;
-- this adds a pure count-optimised partial index without ordering overhead).
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread_count
    ON notifications(user_id) WHERE is_read = FALSE;
