-- =============================================================================
-- ZivaStock Production Schema — V011
-- Triggers
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. updated_at maintenance triggers
-- -----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_roles_updated_at ON roles;
CREATE TRIGGER trg_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_permissions_updated_at ON permissions;
CREATE TRIGGER trg_permissions_updated_at BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_categories_updated_at ON product_categories;
CREATE TRIGGER trg_categories_updated_at BEFORE UPDATE ON product_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_products_updated_at ON products;
CREATE TRIGGER trg_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_locations_updated_at ON locations;
CREATE TRIGGER trg_locations_updated_at BEFORE UPDATE ON locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_shelves_updated_at ON shelves;
CREATE TRIGGER trg_shelves_updated_at BEFORE UPDATE ON shelves
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_shelf_sections_updated_at ON shelf_sections;
CREATE TRIGGER trg_shelf_sections_updated_at BEFORE UPDATE ON shelf_sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_sessions_updated_at ON stocktake_sessions;
CREATE TRIGGER trg_sessions_updated_at BEFORE UPDATE ON stocktake_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_adjustments_updated_at ON adjustments;
CREATE TRIGGER trg_adjustments_updated_at BEFORE UPDATE ON adjustments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_imports_updated_at ON imports;
CREATE TRIGGER trg_imports_updated_at BEFORE UPDATE ON imports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_settings_updated_at ON settings;
CREATE TRIGGER trg_settings_updated_at BEFORE UPDATE ON settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------------------------------------------------------
-- 2. Audit triggers on critical/master-data tables
-- -----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS audit_users ON users;
CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION generic_audit_trigger();

DROP TRIGGER IF EXISTS audit_products ON products;
CREATE TRIGGER audit_products AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION generic_audit_trigger();

DROP TRIGGER IF EXISTS audit_locations ON locations;
CREATE TRIGGER audit_locations AFTER INSERT OR UPDATE OR DELETE ON locations
    FOR EACH ROW EXECUTE FUNCTION generic_audit_trigger();

DROP TRIGGER IF EXISTS audit_stocktake_sessions ON stocktake_sessions;
CREATE TRIGGER audit_stocktake_sessions AFTER INSERT OR UPDATE OR DELETE ON stocktake_sessions
    FOR EACH ROW EXECUTE FUNCTION generic_audit_trigger();

DROP TRIGGER IF EXISTS audit_adjustments ON adjustments;
CREATE TRIGGER audit_adjustments AFTER INSERT OR UPDATE OR DELETE ON adjustments
    FOR EACH ROW EXECUTE FUNCTION generic_audit_trigger();

DROP TRIGGER IF EXISTS audit_settings ON settings;
CREATE TRIGGER audit_settings AFTER INSERT OR UPDATE OR DELETE ON settings
    FOR EACH ROW EXECUTE FUNCTION generic_audit_trigger();

-- -----------------------------------------------------------------------------
-- 3. Segregation of duties: block second count by the same user as first count
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION trg_prevent_same_user_second_count()
RETURNS TRIGGER AS $$
DECLARE
    v_first_user_id BIGINT;
BEGIN
    IF NEW.first_count_id IS NOT NULL THEN
        SELECT user_id INTO v_first_user_id FROM first_counts WHERE id = NEW.first_count_id;

        IF v_first_user_id IS NOT NULL AND v_first_user_id = NEW.user_id THEN
            RAISE EXCEPTION 'Segregation of duties violation: user % cannot perform the second count for a product/section they already first-counted (first_count_id=%)',
                NEW.user_id, NEW.first_count_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_second_count_segregation ON second_counts;
CREATE TRIGGER trg_second_count_segregation BEFORE INSERT OR UPDATE ON second_counts
    FOR EACH ROW EXECUTE FUNCTION trg_prevent_same_user_second_count();

-- -----------------------------------------------------------------------------
-- 4. Notification triggers
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION trg_notify_session_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO notifications (user_id, notification_type, title, message, data)
        SELECT
            sa.user_id,
            'session_status_change',
            'Session status updated: ' || NEW.name,
            'Session "' || NEW.name || '" changed from ' || OLD.status || ' to ' || NEW.status,
            jsonb_build_object('session_id', NEW.id, 'old_status', OLD.status, 'new_status', NEW.status)
        FROM session_assignments sa
        WHERE sa.session_id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_session_status_notify ON stocktake_sessions;
CREATE TRIGGER trg_session_status_notify AFTER UPDATE ON stocktake_sessions
    FOR EACH ROW EXECUTE FUNCTION trg_notify_session_status_change();

CREATE OR REPLACE FUNCTION trg_notify_adjustment_pending()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'pending' THEN
        INSERT INTO notifications (user_id, notification_type, title, message, data)
        SELECT DISTINCT
            u.id,
            'adjustment_pending',
            'Adjustment awaiting approval',
            'A stock adjustment for product ID ' || NEW.product_id || ' requires approval.',
            jsonb_build_object('adjustment_id', NEW.id, 'session_id', NEW.session_id)
        FROM users u
        JOIN roles r ON u.role_id = r.id
        JOIN role_permissions rp ON rp.role_id = r.id
        JOIN permissions p ON p.id = rp.permission_id
        WHERE p.name = 'adjustments.approve'
          AND u.is_active = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_adjustment_pending_notify ON adjustments;
CREATE TRIGGER trg_adjustment_pending_notify AFTER INSERT ON adjustments
    FOR EACH ROW EXECUTE FUNCTION trg_notify_adjustment_pending();
