# ZivaStock — Production Database Migrations (v2)

Database: **zivastockdb**  |  Engine: **PostgreSQL 15+**

This folder contains the **next-generation production schema** for ZivaStock,
designed to support millions of rows per high-volume table (counts, audit
trail, sync queue) for an enterprise multiuser stocktake system.

## Relationship to the existing `database/` scripts

The original `01_create_schema.sql` / `02_seed_data.sql` /
`03_views_procedures_triggers.sql` files remain untouched and describe the
schema currently consumed by the FastAPI backend (single `counts` table,
`sections` table, `import_batches` table, etc.).

This migration set is a **schema redesign** requested for the enterprise
roadmap and introduces breaking changes versus the current backend models:

| Current (`01_create_schema.sql`) | New (this migration set)              | Reason |
|---|---|---|
| `sections`                        | `shelf_sections`                      | Clearer naming, avoids collision with generic "section" terminology |
| `counts` (single table, `count_type` column) | `first_counts` + `second_counts` | Enforces segregation-of-duties (independent double-count) at the schema level |
| `duplicates`                      | *(superseded by `adjustments` + trigger)* | Reconciliation now happens via `adjustments`, comparing first/second/system quantity |
| `import_batches`                  | `imports`                             | Naming alignment with `exports` |
| *(none)*                          | `product_categories`, `session_assignments`, `reports`, `exports`, `settings`, `notifications` | New enterprise capabilities |

**Do not apply this migration set to a live database already running the
v1 schema without a data-migration plan.** For a brand-new environment,
apply only the files in this folder (skip `01`–`03` at the parent level).

## Apply order

Run sequentially, in ascending order, as a superuser or the `zivastockdb`
owner role:

```bash
psql -U postgres -d zivastockdb -f V001__extensions_and_identity.sql
psql -U postgres -d zivastockdb -f V002__catalog_and_locations.sql
psql -U postgres -d zivastockdb -f V003__stocktake_sessions.sql
psql -U postgres -d zivastockdb -f V004__counts_and_adjustments.sql
psql -U postgres -d zivastockdb -f V005__audit_and_sync.sql
psql -U postgres -d zivastockdb -f V006__reporting_io.sql
psql -U postgres -d zivastockdb -f V007__system_tables.sql
psql -U postgres -d zivastockdb -f V008__performance_indexes.sql
psql -U postgres -d zivastockdb -f V009__views.sql
psql -U postgres -d zivastockdb -f V010__functions_and_procedures.sql
psql -U postgres -d zivastockdb -f V011__triggers.sql
psql -U postgres -d zivastockdb -f V012__partition_bootstrap.sql
```

Or concatenate all files (in order) into one script for CI/CD pipelines and
Docker `docker-entrypoint-initdb.d` mounting.

## Design principles applied

- **Partitioning**: `audit_trail` is RANGE-partitioned by month
  (`created_at`) using a reusable partition-creation function
  (`fn_create_monthly_partition`). `first_counts` / `second_counts` are
  **not** physically partitioned (PostgreSQL requires unique constraints on
  partitioned tables to include the partition key, which would weaken
  duplicate-prevention); instead they rely on targeted B-Tree indexes plus a
  BRIN index on `counted_at` for cheap range scans at large scale.
- **Session-scoped app context for audit**: the generic audit trigger reads
  `current_setting('app.current_user_id', true)`, so the application must
  execute `SET LOCAL app.current_user_id = '<id>'` at the start of each
  transaction to get accurate `user_id` attribution in `audit_trail`.
- **Segregation of duties**: a trigger blocks a `second_counts` row from
  being inserted by the same user who recorded the linked `first_counts`
  row for the same product/section/session.
- **Soft-delete via `is_active`** on master-data tables; append-only
  tables (`audit_trail`, `sync_queue`, counts) are never updated in place.
- **UUID surrogate keys** on API-facing entities (`users`,
  `stocktake_sessions`, `reports`, `imports`, `exports`) so internal
  `BIGSERIAL` ids are never required to be exposed externally.
- **JSONB** used for flexible/variable-shape data (`old_value`/`new_value`,
  `parameters`, `filters`, `data`, `setting_value`) with GIN indexes where
  queried.
- **Numeric precision**: quantities and costs use `NUMERIC(18,4)` to avoid
  floating-point drift in financial variance calculations.

## Follow-ups (not included in this migration set)

- **Seed data**: roles/permissions/admin-user seed script was intentionally
  left out of scope for this schema-only task. When seeding, ensure the
  `permissions` table includes an `adjustments.approve` entry — the
  `trg_notify_adjustment_pending` trigger (V011) targets users whose role
  grants that permission.
- **`pg_cron`**: partition rollover and housekeeping jobs are documented as
  commented-out `cron.schedule(...)` calls in `V012__partition_bootstrap.sql`;
  enable the extension and uncomment for production.
- **Backend model migration**: SQLAlchemy models/services will need to be
  updated to target `shelf_sections`, `first_counts`, `second_counts`,
  `adjustments`, `imports` instead of the current v1 equivalents before the
  application can run against this schema.
