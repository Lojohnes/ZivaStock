-- =============================================================================
-- ZivaStock Production Schema — V003
-- Stocktake Sessions, Session Assignments
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. STOCKTAKE_SESSIONS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS stocktake_sessions (
    id              BIGSERIAL PRIMARY KEY,
    uuid            UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    location_id     BIGINT NOT NULL REFERENCES locations(id) ON DELETE RESTRICT,
    session_type    VARCHAR(20) NOT NULL DEFAULT 'full'
        CHECK (session_type IN ('full', 'cycle', 'spot_check')),
    status          VARCHAR(20) NOT NULL DEFAULT 'not_started'
        CHECK (status IN ('not_started', 'in_progress', 'paused', 'counting_complete',
                           'reconciling', 'completed', 'archived', 'cancelled')),
    start_time      TIMESTAMPTZ,
    end_time        TIMESTAMPTZ,
    created_by      BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    approved_by     BIGINT REFERENCES users(id) ON DELETE SET NULL,
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_session_times CHECK (end_time IS NULL OR start_time IS NULL OR end_time >= start_time)
);

CREATE INDEX IF NOT EXISTS idx_sessions_location    ON stocktake_sessions(location_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status       ON stocktake_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_dates         ON stocktake_sessions(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_sessions_created_by    ON stocktake_sessions(created_by);

COMMENT ON TABLE stocktake_sessions IS 'A discrete stocktake event scoped to one location.';

-- -----------------------------------------------------------------------------
-- 2. SESSION_ASSIGNMENTS
-- Assigns users to a session (and optionally a specific shelf_section) with a role.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS session_assignments (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES stocktake_sessions(id) ON DELETE CASCADE,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shelf_section_id    BIGINT REFERENCES shelf_sections(id) ON DELETE CASCADE,
    assignment_role     VARCHAR(20) NOT NULL DEFAULT 'first_counter'
        CHECK (assignment_role IN ('first_counter', 'second_counter', 'supervisor', 'reconciler')),
    status              VARCHAR(20) NOT NULL DEFAULT 'assigned'
        CHECK (status IN ('assigned', 'in_progress', 'completed', 'reassigned')),
    assigned_by         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    assigned_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,

    CONSTRAINT uq_session_assignment UNIQUE (session_id, user_id, shelf_section_id, assignment_role)
);

CREATE INDEX IF NOT EXISTS idx_assignments_session       ON session_assignments(session_id);
CREATE INDEX IF NOT EXISTS idx_assignments_user           ON session_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_shelf_section  ON session_assignments(shelf_section_id);
CREATE INDEX IF NOT EXISTS idx_assignments_status         ON session_assignments(status);

COMMENT ON TABLE session_assignments IS 'Maps counters/supervisors to sessions and, optionally, specific shelf sections.';
