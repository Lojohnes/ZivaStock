# ZivaStock - Database Design

## Database Overview

**Database Name**: zivastockdb  
**Database Engine**: PostgreSQL 14+  
**Character Set**: UTF-8  
**Collation**: en_US.UTF-8  

---

## 1. Entity Relationship Diagram (ERD)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │   roles         │       │  permissions    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ id (PK)         │◄──────│ id (PK)         │
│ email (UNIQUE)  │       │ name            │       │ name            │
│ password_hash   │       │ description     │       │ description     │
│ first_name      │       │ created_at      │       │ created_at      │
│ last_name       │       │ updated_at      │       │ updated_at      │
│ role_id (FK)    │       └─────────────────┘       └─────────────────┘
│ is_active       │                                     ▲
│ created_at      │                                     │
│ updated_at      │                                     │
│ last_login      │                            ┌────────┴────────┐
└─────────────────┘                            │ role_permissions│
                                              ├─────────────────┤
                                              │ role_id (FK)    │
                                              │ permission_id   │
                                              └─────────────────┘

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   locations     │       │   shelves       │       │    sections     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ id (PK)         │◄──────│ id (PK)         │
│ name            │       │ location_id (FK)│       │ shelf_id (FK)   │
│ type            │       │ name            │       │ name            │
│ parent_id (FK)  │       │ description     │       │ description     │
│ created_at      │       │ created_at      │       │ created_at      │
│ updated_at      │       │ updated_at      │       │ updated_at      │
└─────────────────┘       └─────────────────┘       └─────────────────┘
         ▲                                                   │
         │                                                   │
         │                                                   ▼
         │                                          ┌─────────────────┐
         │                                          │     counts       │
         │                                          ├─────────────────┤
         │                                          │ id (PK)         │
         │                                          │ product_id (FK) │
         │                                          │ section_id (FK) │
         │                                          │ quantity        │
         │                                          │ user_id (FK)    │
         │                                          │ session_id (FK) │
         │                                          │ counted_at      │
         │                                          │ synced_at       │
         │                                          │ is_synced       │
         │                                          └─────────────────┘
         │                                                   ▲
         │                                                   │
         │                                          ┌────────┴────────┐
         │                                          │  duplicates     │
         │                                          ├─────────────────┤
         │                                          │ id (PK)         │
         │                                          │ count_id_1 (FK) │
         │                                          │ count_id_2 (FK) │
         │                                          │ status          │
         │                                          │ resolved_by     │
         │                                          │ resolved_at     │
         │                                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   products      │       │ stocktake_sessions│      │   audit_logs    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ barcode (UNIQUE)│       │ name            │       │ user_id (FK)    │
│ product_code    │       │ description     │       │ action          │
│ description     │       │ location_id (FK)│       │ entity_type     │
│ unit_of_measure │       │ start_time      │       │ entity_id       │
│ system_quantity │       │ end_time        │       │ old_value       │
│ unit_cost       │       │ status          │       │ new_value       │
│ created_at      │       │ created_by (FK) │       │ ip_address      │
│ updated_at      │       │ created_at      │       │ user_agent      │
└─────────────────┘       │ updated_at      │       │ created_at      │
         ▲                └─────────────────┘       └─────────────────┘
         │                         ▲
         │                         │
         │                ┌────────┴────────┐
         │                │ session_users   │
         │                ├─────────────────┤
         │                │ session_id (FK) │
         │                │ user_id (FK)     │
         │                │ joined_at        │
         │                └─────────────────┘
         │
         │
┌────────┴────────┐
│  import_batches  │
├─────────────────┤
│ id (PK)         │
│ filename        │
│ source          │
│ status          │
│ total_records   │
│ success_count   │
│ error_count     │
│ uploaded_by (FK)│
│ uploaded_at     │
│ processed_at    │
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│  sync_queue     │       │ sync_records    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │       │ user_id (FK)    │
│ entity_type     │       │ sync_type       │
│ entity_id       │       │ records_count   │
│ action          │       │ status          │
│ payload         │       │ started_at      │
│ retry_count     │       │ completed_at    │
│ last_attempt    │       │ error_message   │
│ status          │       └─────────────────┘
│ created_at      │
└─────────────────┘
```

---

## 2. Detailed Table Definitions

### 2.1 Users Table

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role_id BIGINT NOT NULL REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_active ON users(is_active);
```

### 2.2 Roles Table

```sql
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO roles (name, description) VALUES
('super_admin', 'Full system access'),
('stocktake_manager', 'Manage stocktake sessions'),
('supervisor', 'Monitor counters'),
('counter', 'Count stock only'),
('auditor', 'View reports only');
```

### 2.3 Permissions Table

```sql
CREATE TABLE permissions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO permissions (name, description) VALUES
('users.create', 'Create new users'),
('users.read', 'View user information'),
('users.update', 'Update user information'),
('users.delete', 'Delete users'),
('products.create', 'Create products'),
('products.read', 'View products'),
('products.update', 'Update products'),
('products.delete', 'Delete products'),
('counts.create', 'Create stock counts'),
('counts.read', 'View stock counts'),
('counts.update', 'Update stock counts'),
('counts.delete', 'Delete stock counts'),
('sessions.create', 'Create stocktake sessions'),
('sessions.read', 'View stocktake sessions'),
('sessions.update', 'Update stocktake sessions'),
('sessions.delete', 'Delete stocktake sessions'),
('reports.read', 'View reports'),
('reports.export', 'Export reports'),
('imports.create', 'Import data'),
('exports.create', 'Export data'),
('audit.read', 'View audit logs');
```

### 2.4 Role Permissions Table

```sql
CREATE TABLE role_permissions (
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);
```

### 2.5 Locations Table

```sql
CREATE TABLE locations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('store', 'warehouse', 'zone', 'area')),
    parent_id BIGINT REFERENCES locations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locations_parent ON locations(parent_id);
CREATE INDEX idx_locations_type ON locations(type);
```

### 2.6 Shelves Table

```sql
CREATE TABLE shelves (
    id BIGSERIAL PRIMARY KEY,
    location_id BIGINT NOT NULL REFERENCES locations(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location_id, name)
);

CREATE INDEX idx_shelves_location ON shelves(location_id);
```

### 2.7 Sections Table

```sql
CREATE TABLE sections (
    id BIGSERIAL PRIMARY KEY,
    shelf_id BIGINT NOT NULL REFERENCES shelves(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(shelf_id, name)
);

CREATE INDEX idx_sections_shelf ON sections(shelf_id);
```

### 2.8 Products Table

```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    product_code VARCHAR(50),
    description TEXT NOT NULL,
    unit_of_measure VARCHAR(20) DEFAULT 'EA',
    system_quantity DECIMAL(15, 2) DEFAULT 0,
    unit_cost DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_code ON products(product_code);
CREATE INDEX idx_products_description ON products USING gin(to_tsvector('english', description));
```

### 2.9 Stocktake Sessions Table

```sql
CREATE TABLE stocktake_sessions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    location_id BIGINT NOT NULL REFERENCES locations(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'paused', 'completed', 'archived')),
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_location ON stocktake_sessions(location_id);
CREATE INDEX idx_sessions_status ON stocktake_sessions(status);
CREATE INDEX idx_sessions_dates ON stocktake_sessions(start_time, end_time);
```

### 2.10 Session Users Table

```sql
CREATE TABLE session_users (
    session_id BIGINT NOT NULL REFERENCES stocktake_sessions(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, user_id)
);

CREATE INDEX idx_session_users_user ON session_users(user_id);
```

### 2.11 Counts Table

```sql
CREATE TABLE counts (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(id),
    section_id BIGINT NOT NULL REFERENCES sections(id),
    quantity DECIMAL(15, 2) NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id),
    session_id BIGINT NOT NULL REFERENCES stocktake_sessions(id),
    counted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP,
    is_synced BOOLEAN DEFAULT FALSE,
    UNIQUE(product_id, section_id, user_id, session_id)
);

CREATE INDEX idx_counts_product ON counts(product_id);
CREATE INDEX idx_counts_section ON counts(section_id);
CREATE INDEX idx_counts_user ON counts(user_id);
CREATE INDEX idx_counts_session ON counts(session_id);
CREATE INDEX idx_counts_synced ON counts(is_synced);
CREATE INDEX idx_counts_timestamp ON counts(counted_at);
```

### 2.12 Duplicates Table

```sql
CREATE TABLE duplicates (
    id BIGSERIAL PRIMARY KEY,
    count_id_1 BIGINT NOT NULL REFERENCES counts(id),
    count_id_2 BIGINT NOT NULL REFERENCES counts(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'resolved', 'ignored')),
    resolved_by BIGINT REFERENCES users(id),
    resolved_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_duplicates_status ON duplicates(status);
CREATE INDEX idx_duplicates_counts ON duplicates(count_id_1, count_id_2);
```

### 2.13 Audit Logs Table

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_timestamp ON audit_logs(created_at);
CREATE INDEX idx_audit_timestamp_user ON audit_logs(created_at, user_id);

-- Partition audit logs by month for better performance
CREATE TABLE audit_logs_y2026m06 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
```

### 2.14 Import Batches Table

```sql
CREATE TABLE import_batches (
    id BIGSERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    total_records INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    uploaded_by BIGINT NOT NULL REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE INDEX idx_import_status ON import_batches(status);
CREATE INDEX idx_import_uploaded ON import_batches(uploaded_by);
```

### 2.15 Sync Queue Table (for mobile offline sync)

```sql
CREATE TABLE sync_queue (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT,
    action VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'delete')),
    payload JSONB NOT NULL,
    retry_count INTEGER DEFAULT 0,
    last_attempt TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sync_user ON sync_queue(user_id);
CREATE INDEX idx_sync_status ON sync_queue(status);
CREATE INDEX idx_sync_retry ON sync_queue(status, retry_count);
```

### 2.16 Sync Records Table

```sql
CREATE TABLE sync_records (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    sync_type VARCHAR(20) NOT NULL CHECK (sync_type IN ('push', 'pull', 'full')),
    records_count INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'failed')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE INDEX idx_sync_records_user ON sync_records(user_id);
CREATE INDEX idx_sync_records_status ON sync_records(status);
CREATE INDEX idx_sync_records_timestamp ON sync_records(started_at);
```

---

## 3. Views

### 3.1 Count Summary View

```sql
CREATE VIEW v_count_summary AS
SELECT 
    s.id as session_id,
    s.name as session_name,
    l.name as location_name,
    sh.name as shelf_name,
    sec.name as section_name,
    p.barcode,
    p.product_code,
    p.description,
    p.unit_of_measure,
    p.system_quantity,
    SUM(c.quantity) as counted_quantity,
    COUNT(DISTINCT c.user_id) as user_count,
    MIN(c.counted_at) as first_counted,
    MAX(c.counted_at) as last_counted
FROM stocktake_sessions s
JOIN locations l ON s.location_id = l.id
JOIN shelves sh ON sh.location_id = l.id
JOIN sections sec ON sec.shelf_id = sh.id
JOIN counts c ON c.section_id = sec.id AND c.session_id = s.id
JOIN products p ON c.product_id = p.id
GROUP BY s.id, s.name, l.name, sh.name, sec.name, 
         p.barcode, p.product_code, p.description, 
         p.unit_of_measure, p.system_quantity;
```

### 3.2 Variance View

```sql
CREATE VIEW v_variance AS
SELECT 
    p.id as product_id,
    p.barcode,
    p.product_code,
    p.description,
    p.system_quantity,
    COALESCE(SUM(c.quantity), 0) as counted_quantity,
    COALESCE(SUM(c.quantity), 0) - p.system_quantity as variance,
    CASE 
        WHEN COALESCE(SUM(c.quantity), 0) - p.system_quantity > 0 THEN 'overcount'
        WHEN COALESCE(SUM(c.quantity), 0) - p.system_quantity < 0 THEN 'undercount'
        ELSE 'accurate'
    END as variance_type,
    p.unit_cost,
    (COALESCE(SUM(c.quantity), 0) - p.system_quantity) * p.unit_cost as cost_impact
FROM products p
LEFT JOIN counts c ON c.product_id = p.id
GROUP BY p.id, p.barcode, p.product_code, p.description, 
         p.system_quantity, p.unit_cost;
```

### 3.3 User Productivity View

```sql
CREATE VIEW v_user_productivity AS
SELECT 
    u.id as user_id,
    u.email,
    u.first_name,
    u.last_name,
    r.name as role,
    COUNT(c.id) as total_counts,
    MIN(c.counted_at) as first_count,
    MAX(c.counted_at) as last_count,
    COUNT(DISTINCT c.session_id) as sessions_participated,
    COUNT(DISTINCT c.section_id) as sections_covered
FROM users u
JOIN roles r ON u.role_id = r.id
LEFT JOIN counts c ON c.user_id = u.id
GROUP BY u.id, u.email, u.first_name, u.last_name, r.name;
```

### 3.4 Session Progress View

```sql
CREATE VIEW v_session_progress AS
SELECT 
    s.id as session_id,
    s.name as session_name,
    s.status,
    s.start_time,
    s.end_time,
    l.name as location_name,
    COUNT(DISTINCT sec.id) as total_sections,
    COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN sec.id END) as sections_counted,
    COUNT(DISTINCT c.id) as total_counts,
    COUNT(DISTINCT c.user_id) as active_users,
    ROUND(
        (COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN sec.id END)::FLOAT / 
         NULLIF(COUNT(DISTINCT sec.id), 0)) * 100, 2
    ) as completion_percentage
FROM stocktake_sessions s
JOIN locations l ON s.location_id = l.id
JOIN shelves sh ON sh.location_id = l.id
JOIN sections sec ON sec.shelf_id = sh.id
LEFT JOIN counts c ON c.section_id = sec.id AND c.session_id = s.id
GROUP BY s.id, s.name, s.status, s.start_time, s.end_time, l.name;
```

---

## 4. Stored Procedures

### 4.1 Detect Duplicates Procedure

```sql
CREATE OR REPLACE FUNCTION detect_duplicates(p_session_id BIGINT)
RETURNS TABLE(duplicate_id BIGINT, count_id_1 BIGINT, count_id_2 BIGINT, quantity_1 DECIMAL, quantity_2 DECIMAL) 
AS $$
BEGIN
    RETURN QUERY
    INSERT INTO duplicates (count_id_1, count_id_2, status)
    SELECT 
        c1.id as count_id_1,
        c2.id as count_id_2,
        'pending' as status
    FROM counts c1
    JOIN counts c2 ON 
        c1.product_id = c2.product_id AND
        c1.section_id = c2.section_id AND
        c1.session_id = c2.session_id AND
        c1.id < c2.id
    WHERE c1.session_id = p_session_id
    ON CONFLICT DO NOTHING
    RETURNING 
        (SELECT id FROM duplicates WHERE count_id_1 = c1.id AND count_id_2 = c2.id),
        c1.id,
        c2.id,
        c1.quantity,
        c2.quantity;
END;
$$ LANGUAGE plpgsql;
```

### 4.2 Calculate Session Statistics Procedure

```sql
CREATE OR REPLACE FUNCTION calculate_session_stats(p_session_id BIGINT)
RETURNS TABLE(
    total_products BIGINT,
    total_counts BIGINT,
    total_variance DECIMAL,
    completion_percentage DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT c.product_id) as total_products,
        COUNT(c.id) as total_counts,
        SUM(c.quantity - p.system_quantity) as total_variance,
        ROUND(
            (COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN sec.id END)::FLOAT / 
             NULLIF(COUNT(DISTINCT sec.id), 0)) * 100, 2
        ) as completion_percentage
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
```

### 4.3 Archive Session Procedure

```sql
CREATE OR REPLACE FUNCTION archive_session(p_session_id BIGINT)
RETURNS BOOLEAN AS $$
DECLARE
    v_status VARCHAR(20);
BEGIN
    -- Check session status
    SELECT status INTO v_status 
    FROM stocktake_sessions 
    WHERE id = p_session_id;
    
    IF v_status != 'completed' THEN
        RAISE EXCEPTION 'Only completed sessions can be archived';
    END IF;
    
    -- Update session status
    UPDATE stocktake_sessions 
    SET status = 'archived', updated_at = CURRENT_TIMESTAMP
    WHERE id = p_session_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
```

---

## 5. Triggers

### 5.1 Update Timestamp Trigger

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_permissions_updated_at BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shelves_updated_at BEFORE UPDATE ON shelves
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON stocktake_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5.2 Audit Log Trigger

```sql
CREATE OR REPLACE FUNCTION audit_log_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (entity_type, entity_id, action, new_value)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (entity_type, entity_id, action, old_value, new_value)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (entity_type, entity_id, action, old_value)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', row_to_json(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply to critical tables
CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

CREATE TRIGGER audit_products AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

CREATE TRIGGER audit_counts AFTER INSERT OR UPDATE OR DELETE ON counts
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

CREATE TRIGGER audit_sessions AFTER INSERT OR UPDATE OR DELETE ON stocktake_sessions
    FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();
```

### 5.3 Duplicate Detection Trigger

```sql
CREATE OR REPLACE FUNCTION check_duplicate_on_count()
RETURNS TRIGGER AS $$
DECLARE
    v_duplicate_count INTEGER;
BEGIN
    -- Check for potential duplicates
    SELECT COUNT(*) INTO v_duplicate_count
    FROM counts
    WHERE product_id = NEW.product_id
      AND section_id = NEW.section_id
      AND session_id = NEW.session_id
      AND user_id != NEW.user_id;
    
    IF v_duplicate_count > 0 THEN
        -- Create duplicate record
        INSERT INTO duplicates (count_id_1, count_id_2, status)
        SELECT NEW.id, id, 'pending'
        FROM counts
        WHERE product_id = NEW.product_id
          AND section_id = NEW.section_id
          AND session_id = NEW.session_id
          AND user_id != NEW.user_id
          AND id != NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_duplicate AFTER INSERT ON counts
    FOR EACH ROW EXECUTE FUNCTION check_duplicate_on_count();
```

---

## 6. Indexes Summary

### Primary Indexes
- All tables have primary key indexes on `id` columns

### Foreign Key Indexes
- `idx_users_role` on users(role_id)
- `idx_locations_parent` on locations(parent_id)
- `idx_shelves_location` on shelves(location_id)
- `idx_sections_shelf` on sections(shelf_id)
- `idx_counts_product` on counts(product_id)
- `idx_counts_section` on counts(section_id)
- `idx_counts_user` on counts(user_id)
- `idx_counts_session` on counts(session_id)
- `idx_sessions_location` on stocktake_sessions(location_id)
- `idx_session_users_user` on session_users(user_id)

### Performance Indexes
- `idx_products_barcode` on products(barcode) - UNIQUE
- `idx_products_code` on products(product_code)
- `idx_products_description` on products (GIN full-text search)
- `idx_counts_synced` on counts(is_synced)
- `idx_counts_timestamp` on counts(counted_at)
- `idx_sessions_status` on stocktake_sessions(status)
- `idx_sessions_dates` on stocktake_sessions(start_time, end_time)
- `idx_audit_user` on audit_logs(user_id)
- `idx_audit_entity` on audit_logs(entity_type, entity_id)
- `idx_audit_action` on audit_logs(action)
- `idx_audit_timestamp` on audit_logs(created_at)
- `idx_sync_user` on sync_queue(user_id)
- `idx_sync_status` on sync_queue(status)

---

## 7. Constraints Summary

### Unique Constraints
- users.email
- roles.name
- permissions.name
- products.barcode
- shelves(location_id, name)
- sections(shelf_id, name)
- counts(product_id, section_id, user_id, session_id)

### Check Constraints
- locations.type IN ('store', 'warehouse', 'zone', 'area')
- stocktake_sessions.status IN ('not_started', 'in_progress', 'paused', 'completed', 'archived')
- sync_queue.action IN ('create', 'update', 'delete')
- sync_queue.status IN ('pending', 'processing', 'completed', 'failed')
- duplicates.status IN ('pending', 'resolved', 'ignored')
- import_batches.status IN ('pending', 'processing', 'completed', 'failed')

### Foreign Key Constraints
- All foreign keys with appropriate ON DELETE CASCADE/SET NULL

---

## 8. Database Migration Strategy

### Migration Tool: Alembic

### Migration Files Structure
```
database/migrations/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_indexes.py
│   ├── 003_create_views.py
│   ├── 004_create_procedures.py
│   └── 005_create_triggers.py
└── env.py
```

### Migration Commands
```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View current version
alembic current
```

---

## 9. Backup Strategy

### Daily Full Backup
```bash
pg_dump -h localhost -U postgres -d zivastockdb -F c -f /backups/zivastockdb_$(date +%Y%m%d).dump
```

### Hourly WAL Archiving
```bash
# In postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backups/wal/%f'
```

### Restore Command
```bash
pg_restore -h localhost -U postgres -d zivastockdb /backups/zivastockdb_20260609.dump
```

---

## 10. Performance Optimization

### Query Optimization
- Use EXPLAIN ANALYZE for slow queries
- Add appropriate indexes based on query patterns
- Use connection pooling (PgBouncer)
- Enable query caching in Redis

### Database Configuration
```postgresql
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_parallel_maintenance_workers = 2
```

---

## Document Version
- Version: 1.0
- Date: June 9, 2026
- Author: Database Architecture Team
- Status: Approved
