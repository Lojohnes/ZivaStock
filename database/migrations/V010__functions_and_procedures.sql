-- =============================================================================
-- ZivaStock Production Schema — V010
-- Functions & Stored Procedures
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Generic updated_at maintenance
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 2. Generic audit logging (reads app.current_user_id session GUC)
-- Application must run: SET LOCAL app.current_user_id = '<user_id>';
-- at the start of each write transaction.
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION generic_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id BIGINT;
BEGIN
    BEGIN
        v_user_id := NULLIF(current_setting('app.current_user_id', true), '')::BIGINT;
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;

    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_trail (user_id, action, entity_type, entity_id, new_value)
        VALUES (v_user_id, 'INSERT', TG_TABLE_NAME, NEW.id, to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_trail (user_id, action, entity_type, entity_id, old_value, new_value)
        VALUES (v_user_id, 'UPDATE', TG_TABLE_NAME, NEW.id, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_trail (user_id, action, entity_type, entity_id, old_value)
        VALUES (v_user_id, 'DELETE', TG_TABLE_NAME, OLD.id, to_jsonb(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 3. Reusable monthly RANGE-partition creator (for audit_trail, extensible)
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_create_monthly_partition(p_table_name TEXT, p_month DATE)
RETURNS TEXT AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    start_date := DATE_TRUNC('month', p_month);
    end_date := start_date + INTERVAL '1 month';
    partition_name := p_table_name || '_' || TO_CHAR(start_date, 'YYYY_MM');

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
        partition_name, p_table_name, start_date, end_date
    );

    RETURN partition_name;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 4. Session variance/stats summary
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_calculate_session_variance(p_session_id BIGINT)
RETURNS TABLE (
    total_products          BIGINT,
    total_adjustments        BIGINT,
    total_variance_quantity  NUMERIC,
    total_variance_value     NUMERIC,
    overcount_products       BIGINT,
    undercount_products      BIGINT,
    accurate_products        BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT a.product_id),
        COUNT(a.id),
        COALESCE(SUM(a.variance_quantity), 0),
        COALESCE(SUM(a.variance_value), 0),
        COUNT(*) FILTER (WHERE a.variance_quantity > 0),
        COUNT(*) FILTER (WHERE a.variance_quantity < 0),
        COUNT(*) FILTER (WHERE a.variance_quantity = 0)
    FROM adjustments a
    WHERE a.session_id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 5. Discrepancy detection between first and second counts (pre-reconciliation)
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_detect_count_discrepancy(p_session_id BIGINT, p_tolerance_pct NUMERIC DEFAULT 0)
RETURNS TABLE (
    product_id          BIGINT,
    shelf_section_id     BIGINT,
    first_quantity        NUMERIC,
    second_quantity       NUMERIC,
    difference             NUMERIC,
    difference_pct         NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        fc.product_id,
        fc.shelf_section_id,
        fc.quantity,
        sc.quantity,
        (sc.quantity - fc.quantity),
        CASE WHEN fc.quantity = 0 THEN NULL
             ELSE ROUND(ABS(sc.quantity - fc.quantity) / fc.quantity * 100, 2)
        END
    FROM first_counts fc
    JOIN second_counts sc
        ON sc.session_id = fc.session_id
       AND sc.product_id = fc.product_id
       AND sc.shelf_section_id = fc.shelf_section_id
    WHERE fc.session_id = p_session_id
      AND ABS(sc.quantity - fc.quantity) > 0
      AND (
            fc.quantity = 0
            OR (ABS(sc.quantity - fc.quantity) / fc.quantity * 100) > p_tolerance_pct
          );
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 6. Generate/refresh adjustments for a session from first/second counts
-- Rule: final_quantity = second_count if present, else first_count, else system_quantity.
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_generate_adjustments(p_session_id BIGINT, p_actor_id BIGINT)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
BEGIN
    WITH scope AS (
        SELECT DISTINCT product_id, shelf_section_id FROM first_counts WHERE session_id = p_session_id
        UNION
        SELECT DISTINCT product_id, shelf_section_id FROM second_counts WHERE session_id = p_session_id
    ),
    resolved AS (
        SELECT
            sc0.product_id,
            sc0.shelf_section_id,
            fc.id AS first_count_id,
            sc.id AS second_count_id,
            p.system_quantity,
            p.unit_cost,
            COALESCE(sc.quantity, fc.quantity, p.system_quantity) AS final_quantity
        FROM scope sc0
        JOIN products p ON p.id = sc0.product_id
        LEFT JOIN first_counts fc
               ON fc.session_id = p_session_id
              AND fc.product_id = sc0.product_id
              AND fc.shelf_section_id = sc0.shelf_section_id
        LEFT JOIN second_counts sc
               ON sc.session_id = p_session_id
              AND sc.product_id = sc0.product_id
              AND sc.shelf_section_id = sc0.shelf_section_id
    )
    INSERT INTO adjustments (
        session_id, product_id, shelf_section_id, first_count_id, second_count_id,
        system_quantity, final_quantity, unit_cost_snapshot, adjustment_type,
        status, created_by
    )
    SELECT
        p_session_id,
        r.product_id,
        r.shelf_section_id,
        r.first_count_id,
        r.second_count_id,
        r.system_quantity,
        r.final_quantity,
        r.unit_cost,
        CASE
            WHEN r.final_quantity > r.system_quantity THEN 'increase'
            WHEN r.final_quantity < r.system_quantity THEN 'decrease'
            ELSE 'none'
        END,
        'pending',
        p_actor_id
    FROM resolved r
    ON CONFLICT (session_id, product_id, shelf_section_id) DO UPDATE
        SET first_count_id     = EXCLUDED.first_count_id,
            second_count_id    = EXCLUDED.second_count_id,
            system_quantity    = EXCLUDED.system_quantity,
            final_quantity     = EXCLUDED.final_quantity,
            unit_cost_snapshot = EXCLUDED.unit_cost_snapshot,
            adjustment_type    = EXCLUDED.adjustment_type,
            updated_at         = CURRENT_TIMESTAMP;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 7. Close a stocktake session (generates adjustments, transitions status)
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_close_stocktake_session(p_session_id BIGINT, p_actor_id BIGINT)
RETURNS BOOLEAN AS $$
DECLARE
    v_status VARCHAR(20);
BEGIN
    SELECT status INTO v_status FROM stocktake_sessions WHERE id = p_session_id;

    IF v_status IS NULL THEN
        RAISE EXCEPTION 'Session % not found', p_session_id;
    END IF;

    IF v_status NOT IN ('in_progress', 'paused', 'counting_complete', 'reconciling') THEN
        RAISE EXCEPTION 'Session % cannot be closed from status %', p_session_id, v_status;
    END IF;

    PERFORM fn_generate_adjustments(p_session_id, p_actor_id);

    UPDATE stocktake_sessions
    SET status = 'completed', end_time = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
    WHERE id = p_session_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 8. Housekeeping: purge expired exports / old notifications
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION sp_purge_expired_exports()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    DELETE FROM exports WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_purge_old_notifications(p_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    DELETE FROM notifications
    WHERE is_read = TRUE
      AND created_at < CURRENT_TIMESTAMP - (p_days || ' days')::INTERVAL;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;
