-- ZivaStock Seed Data
-- Run after 01_create_schema.sql
-- Provides default roles, permissions, and a super-admin user.
-- Default admin password must be changed immediately after first login.

-- -----------------------------------------------------------------------------
-- 1. DEFAULT ROLES
-- -----------------------------------------------------------------------------

INSERT INTO roles (name, description) VALUES
('super_admin', 'Full system access - can manage everything'),
('stocktake_manager', 'Manage stocktake sessions, users, and locations'),
('supervisor', 'Monitor counters and review progress'),
('counter', 'Count stock only - cannot modify master data'),
('auditor', 'View reports and audit logs only')
ON CONFLICT (name) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2. DEFAULT PERMISSIONS
-- -----------------------------------------------------------------------------

INSERT INTO permissions (name, description) VALUES
('users.create', 'Create new users'),
('users.read', 'View user information'),
('users.update', 'Update user information'),
('users.delete', 'Delete users'),
('roles.read', 'View roles and permissions'),
('roles.update', 'Assign permissions to roles'),
('products.create', 'Create products'),
('products.read', 'View products'),
('products.update', 'Update products'),
('products.delete', 'Delete products'),
('products.import', 'Import products from files'),
('counts.create', 'Create stock counts'),
('counts.read', 'View stock counts'),
('counts.update', 'Update stock counts'),
('counts.delete', 'Delete stock counts'),
('sessions.create', 'Create stocktake sessions'),
('sessions.read', 'View stocktake sessions'),
('sessions.update', 'Update stocktake sessions'),
('sessions.delete', 'Delete stocktake sessions'),
('sessions.start', 'Start a stocktake session'),
('sessions.complete', 'Complete a stocktake session'),
('reports.read', 'View reports'),
('reports.export', 'Export reports'),
('imports.create', 'Import data'),
('exports.create', 'Export data'),
('audit.read', 'View audit logs'),
('sync.read', 'View sync status'),
('sync.manage', 'Manage sync queue')
ON CONFLICT (name) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. ROLE-PERMISSION MAPPINGS
-- -----------------------------------------------------------------------------

WITH role_map AS (
    SELECT id, name FROM roles
), perm_map AS (
    SELECT id, name FROM permissions
)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM role_map r, perm_map p
WHERE r.name = 'super_admin'
ON CONFLICT (role_id, permission_id) DO NOTHING;

WITH role_map AS (
    SELECT id, name FROM roles
), perm_map AS (
    SELECT id, name FROM permissions
)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM role_map r, perm_map p
WHERE r.name = 'stocktake_manager'
  AND p.name IN (
    'users.create','users.read','users.update','users.delete','roles.read',
    'products.create','products.read','products.update','products.delete','products.import',
    'counts.create','counts.read','counts.update','counts.delete',
    'sessions.create','sessions.read','sessions.update','sessions.delete','sessions.start','sessions.complete',
    'reports.read','reports.export','imports.create','exports.create','audit.read','sync.read','sync.manage'
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;

WITH role_map AS (
    SELECT id, name FROM roles
), perm_map AS (
    SELECT id, name FROM permissions
)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM role_map r, perm_map p
WHERE r.name = 'supervisor'
  AND p.name IN (
    'users.read','products.read','counts.read','sessions.read','sessions.update',
    'reports.read','reports.export','audit.read','sync.read'
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;

WITH role_map AS (
    SELECT id, name FROM roles
), perm_map AS (
    SELECT id, name FROM permissions
)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM role_map r, perm_map p
WHERE r.name = 'counter'
  AND p.name IN ('counts.create','counts.read','counts.update','sessions.read','products.read')
ON CONFLICT (role_id, permission_id) DO NOTHING;

WITH role_map AS (
    SELECT id, name FROM roles
), perm_map AS (
    SELECT id, name FROM permissions
)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM role_map r, perm_map p
WHERE r.name = 'auditor'
  AND p.name IN ('reports.read','reports.export','audit.read','sessions.read','products.read','counts.read')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 4. DEFAULT SUPER ADMIN USER
-- Password: ChangeMe@123 (bcrypt hash below)
-- IMPORTANT: Change this password after first login.
-- -----------------------------------------------------------------------------

INSERT INTO users (email, password_hash, first_name, last_name, role_id, is_active, last_login)
VALUES (
    'admin@zivastock.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G',  -- ChangeMe@123
    'System',
    'Administrator',
    (SELECT id FROM roles WHERE name = 'super_admin'),
    TRUE,
    CURRENT_TIMESTAMP
)
ON CONFLICT (email) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 5. SAMPLE LOCATIONS (Optional - remove for clean production install)
-- -----------------------------------------------------------------------------

INSERT INTO locations (name, type) VALUES
('Main Shop', 'store'),
('Warehouse A', 'warehouse')
ON CONFLICT DO NOTHING;
