-- =============================================================================
-- ZivaStock Production Schema — V012
-- Partition Bootstrap
-- Creates initial monthly partitions for audit_trail (current + next 3 months).
-- Schedule fn_create_monthly_partition('audit_trail', <future_month>) via
-- pg_cron / an external scheduler to keep this rolling forward in production.
-- =============================================================================

DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 0..3 LOOP
        PERFORM fn_create_monthly_partition('audit_trail', (CURRENT_DATE + (i || ' months')::INTERVAL)::DATE);
    END LOOP;
END $$;

-- Recommended production cron (via pg_cron extension, if installed):
--
-- SELECT cron.schedule(
--     'zivastock_audit_partition_rollover',
--     '0 0 25 * *',  -- 25th of each month
--     $$ SELECT fn_create_monthly_partition('audit_trail', CURRENT_DATE + INTERVAL '1 month'); $$
-- );
--
-- SELECT cron.schedule(
--     'zivastock_purge_expired_exports',
--     '0 2 * * *',   -- daily at 02:00
--     $$ SELECT sp_purge_expired_exports(); $$
-- );
--
-- SELECT cron.schedule(
--     'zivastock_purge_old_notifications',
--     '0 3 * * 0',   -- weekly, Sunday 03:00
--     $$ SELECT sp_purge_old_notifications(90); $$
-- );
