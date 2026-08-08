-- ZivaStock Views, Stored Procedures, Functions, and Triggers
-- Run after 01_create_schema.sql and 02_seed_data.sql

-- -----------------------------------------------------------------------------
-- 1. VIEWS
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_count_summary AS
SELECT
    s.id AS session_id,
    s.name AS session_name,
    l.id AS location_id,
    l.name AS location_name,
    sh.id AS shelf_id,
    sh.name AS shelf_name,
    sec.id AS section_id,
    sec.name AS section_name,
    p.id AS product_id,
    p.barcode,
    p.product_code,
    p.description,
    p.unit_of_measure,
    p.system_quantity,
    COALESCE(SUM(c.quantity), 0) AS counted_quantity,
    COUNT(DISTINCT c.user_id) AS user_count,
    COUNT(c.id) AS count_entries,
    MIN(c.counted_at) AS first_counted,
    MAX(c.counted_at) AS last_counted,
    COALESCE(SUM(c.quantity), 0) - p.system_quantity AS variance,
    CASE
        WHEN COALESCE(SUM(c.quantity), 0) - p.system_quantity > 0 THEN 'overcount'
        WHEN COALESCE(SUM(c.quantity), 0) - p.system_quantity < 0 THEN 'undercount'
        ELSE 'accurate'
    END AS variance_type,
    p.unit_cost,
    (COALESCE(SUM(c.quantity), 0) - p.system_quantity) * p.unit_cost AS cost_impact
FROM stocktake_sessions s
JOIN locations l ON s.location_id = l.id
JOIN shelves sh ON sh.location_id = l.id
JOIN sections sec ON sec.shelf_id = sh.id
LEFT JOIN counts c ON c.section_id = sec.id AND c.session_id = s.id
LEFT JOIN products p ON c.product_id = p.id
GROUP BY s.id, s.name, l.id, l.name, sh.id, sh.name, sec.id, sec.name,
         p.id, p.barcode, p.product_code, p.description,
         p.unit_of_measure, p.system_quantity, p.unit_cost;

CREATE OR REPLACE VIEW v_variance AS
SELECT
    p.id AS product_id,
    p.barcode,
    p.product_code,
    p.description,
    p.unit_of_measure,
    p.system_quantity,
    COALESCE(SUM(c.quantity), 0) AS counted_quantity,
    COALESCE(SUM(c.quantity), 0) - p.system_quantity AS variance,
    CASE
        WHEN COALESCE(SUM(c.quantity), 0) - p.system_quantity > 0 THEN 'overcount'
        WHEN COALESCE(SUM(c.quantity), 0) - p.system_quantity < 0 THEN 'undercount'
        ELSE 'accurate'
    END AS variance_type,
    p.unit_cost,
    (COALESCE(SUM(c.quantity), 0) - p.system_quantity) * p.unit_cost AS cost_impact
FROM products p
LEFT JOIN counts c ON c.product_id = p.id
GROUP BY p.id, p.barcode, p.product_code, p.description,
         p.unit_of_measure, p.system_quantity, p.unit_cost;

CREATE OR REPLACE VIEW v_user_productivity AS
SELECT
    u.id AS user_id,
    u.email,
    u.first_name,
    u.last_name,
    r.name AS role,
    COUNT(c.id) AS total_counts,
    MIN(c.counted_at) AS first_count,
    MAX(c.counted_at) AS last_count,
    COUNT(DISTINCT c.session_id) AS sessions_participated,
    COUNT(DISTINCT c.section_id) AS sections_covered,
    COALESCE(SUM(c.quantity), 0) AS total_quantity_counted
FROM users u
JOIN roles r ON u.role_id = r.id
LEFT JOIN counts c ON c.user_id = u.id
GROUP BY u.id, u.email, u.first_name, u.last_name, r.name;

CREATE OR REPLACE VIEW v_session_progress AS
SELECT
    s.id AS session_id,
    s.name AS session_name,
    s.status,
    s.start_time,
    s.end_time,
    l.id AS location_id,
    l.name AS location_name,
    COUNT(DISTINCT sec.id) AS total_sections,
    COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN sec.id END) AS sections_counted,
    COUNT(DISTINCT c.id) AS total_counts,
    COUNT(DISTINCT c.user_id) AS active_users,
    COUNT(DISTINCT c.product_id) AS unique_products_counted,
    ROUND(
        ((COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN sec.id END)::FLOAT /
         NULLIF(COUNT(DISTINCT sec.id), 0)) * 100)::numeric, 2
    ) AS section_completion_percentage
FROM stocktake_sessions s
JOIN locations l ON s.location_id = l.id
JOIN shelves sh ON sh.location_id = l.id
JOIN sections sec ON sec.shelf_id = sh.id
LEFT JOIN counts c ON c.section_id = sec.id AND c.session_id = s.id
GROUP BY s.id, s.name, s.status, s.start_time, s.end_time, l.id, l.name;

CREATE OR REPLACE VIEW v_missing_stock AS
SELECT
    s.id AS session_id,
    p.id AS product_id,
    p.barcode,
    p.product_code,
    p.description,
    p.unit_of_measure,
    p.system_quantity,
    l.name AS location_name
FROM stocktake_sessions s
JOIN locations l ON s.location_id = l.id
CROSS JOIN products p
LEFT JOIN counts c ON c.session_id = s.id AND c.product_id = p.id
WHERE c.id IS NULL
  AND p.is_active = TRUE
  AND s.status IN ('in_progress', 'paused', 'completed');

CREATE OR REPLACE VIEW v_duplicate_counts AS
SELECT
    d.id AS duplicate_id,
    d.status,
    d.notes,
    d.resolved_by,
    d.resolved_at,
    d.created_at,
    c1.id AS count_id_1,
    c1.quantity AS quantity_1,
    c1.counted_at AS counted_at_1,
    u1.id AS user_id_1,
    u1.email AS user_email_1,
    c2.id AS count_id_2,
    c2.quantity AS quantity_2,
    c2.counted_at AS counted_at_2,
    u2.id AS user_id_2,
    u2.email AS user_email_2,
    p.id AS product_id,
    p.barcode,
    p.description,
    sec.id AS section_id,
    sec.name AS section_name,
    sh.name AS shelf_name,
    l.name AS location_name,
    s.id AS session_id,
    s.name AS session_name
FROM duplicates d
JOIN counts c1 ON d.count_id_1 = c1.id
JOIN counts c2 ON d.count_id_2 = c2.id
JOIN users u1 ON c1.user_id = u1.id
JOIN users u2 ON c2.user_id = u2.id
JOIN products p ON c1.product_id = p.id
JOIN sections sec ON c1.section_id = sec.id
JOIN shelves sh ON sec.shelf_id = sh.id
JOIN locations l ON sh.location_id = l.id
JOIN stocktake_sessions s ON c1.session_id = s.id;

-- -----------------------------------------------------------------------------
-- 2. FUNCTIONS & STORED PROCEDURES
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION detect_duplicates(p_session_id BIGINT)
RETURNS TABLE(duplicate_id BIGINT, count_id_1 BIGINT, count_id_2 BIGINT, quantity_1 DECIMAL, quantity_2 DECIMAL)
AS $$
BEGIN
    RETURN QUERY
    INSERT INTO duplicates (count_id_1, count_id_2, status)
    SELECT
        c1.id AS count_id_1,
        c2.id AS count_id_2,
        'pending' AS status
    FROM counts c1
    JOIN counts c2 ON
        c1.product_id = c2.product_id AND
        c1.section_id = c2.section_id AND
        c1.session_id = c2.session_id AND
        c1.id < c2.id
    WHERE c1.session_id = p_session_id
    ON CONFLICT (count_id_1, count_id_2) DO NOTHING
    RETURNING duplicates.id, duplicates.count_id_1, duplicates.count_id_2,
              (SELECT quantity FROM counts WHERE id = duplicates.count_id_1),
              (SELECT quantity FROM counts WHERE id = duplicates.count_id_2);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_session_stats(p_session_id BIGINT)
RETURNS TABLE(
    total_products BIGINT,
    total_counts BIGINT,
    total_variance DECIMAL,
    completion_percentage DECIMAL,
    overcount_products BIGINT,
    undercount_products BIGINT,
    accurate_products BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT c.product_id) AS total_products,
        COUNT(c.id) AS total_counts,
        COALESCE(SUM(c.quantity - p.system_quantity), 0) AS total_variance,
        ROUND(
            ((COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN sec.id END)::FLOAT /
             NULLIF(COUNT(DISTINCT sec.id), 0)) * 100)::numeric, 2
        ) AS completion_percentage,
        COUNT(DISTINCT CASE WHEN c.quantity > p.system_quantity THEN c.product_id END) AS overcount_products,
        COUNT(DISTINCT CASE WHEN c.quantity < p.system_quantity THEN c.product_id END) AS undercount_products,
        COUNT(DISTINCT CASE WHEN c.quantity = p.system_quantity THEN c.product_id END) AS accurate_products
    FROM stocktake_sessions s
    JOIN locations l ON s.location_id = l.id
    JOIN shelves sh ON sh.location_id = l.id
    LEFT JOIN sections sec ON sec.shelf_id = sh.id
    LEFT JOIN counts c ON c.section_id = sec.id AND c.session_id = s.id
    LEFT JOIN products p ON c.product_id = p.id
    WHERE s.id = p_session_id
    GROUP BY s.id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION archive_session(p_session_id BIGINT)
RETURNS BOOLEAN AS $$
DECLARE
    v_status VARCHAR(20);
BEGIN
    SELECT status INTO v_status
    FROM stocktake_sessions
    WHERE id = p_session_id;

    IF v_status IS NULL THEN
        RAISE EXCEPTION 'Session not found';
    END IF;

    IF v_status != 'completed' THEN
        RAISE EXCEPTION 'Only completed sessions can be archived';
    END IF;

    UPDATE stocktake_sessions
    SET status = 'archived', updated_at = CURRENT_TIMESTAMP
    WHERE id = p_session_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_audit_partition(p_month DATE)
RETURNS TEXT AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    start_date := DATE_TRUNC('month', p_month);
    end_date := start_date + INTERVAL '1 month';
    partition_name := 'audit_logs_' || TO_CHAR(start_date, 'YYYY_MM');

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF audit_logs
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );

    RETURN partition_name;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 3. TRIGGERS
-- -----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_roles_updated_at ON roles;
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_permissions_updated_at ON permissions;
CREATE TRIGGER update_permissions_updated_at BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_locations_updated_at ON locations;
CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_shelves_updated_at ON shelves;
CREATE TRIGGER update_shelves_updated_at BEFORE UPDATE ON shelves
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sections_updated_at ON sections;
CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sessions_updated_at ON stocktake_sessions;
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON stocktake_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_import_batches_updated_at ON import_batches;
CREATE TRIGGER update_import_batches_updated_at BEFORE UPDATE ON import_batches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Audit log trigger for critical tables
CREATE OR REPLACE FUNCTION audit_log_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (user_id, entity_type, entity_id, action, new_value)
        VALUES (NULL, TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (user_id, entity_type, entity_id, action, old_value, new_value)
        VALUES (NULL, TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (user_id, entity_type, entity_id, action, old_value)
        VALUES (NULL, TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_users ON users;
CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

DROP TRIGGER IF EXISTS audit_products ON products;
CREATE TRIGGER audit_products AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

DROP TRIGGER IF EXISTS audit_counts ON counts;
CREATE TRIGGER audit_counts AFTER INSERT OR UPDATE OR DELETE ON counts
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

DROP TRIGGER IF EXISTS audit_sessions ON stocktake_sessions;
CREATE TRIGGER audit_sessions AFTER INSERT OR UPDATE OR DELETE ON stocktake_sessions
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

DROP TRIGGER IF EXISTS audit_locations ON locations;
CREATE TRIGGER audit_locations AFTER INSERT OR UPDATE OR DELETE ON locations
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

-- Duplicate detection trigger on counts
CREATE OR REPLACE FUNCTION check_duplicate_on_count()
RETURNS TRIGGER AS $$
DECLARE
    v_duplicate_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_duplicate_count
    FROM counts
    WHERE product_id = NEW.product_id
      AND section_id = NEW.section_id
      AND session_id = NEW.session_id
      AND user_id != NEW.user_id;

    IF v_duplicate_count > 0 THEN
        INSERT INTO duplicates (count_id_1, count_id_2, status)
        SELECT NEW.id, id, 'pending'
        FROM counts
        WHERE product_id = NEW.product_id
          AND section_id = NEW.section_id
          AND session_id = NEW.session_id
          AND user_id != NEW.user_id
          AND id != NEW.id
        ON CONFLICT (count_id_1, count_id_2) DO NOTHING;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_check_duplicate ON counts;
CREATE TRIGGER trigger_check_duplicate AFTER INSERT ON counts
    FOR EACH ROW EXECUTE FUNCTION check_duplicate_on_count();
