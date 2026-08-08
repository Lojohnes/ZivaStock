# ZivaStock System Inspection Report

**Date:** 2026-08-07  
**Inspectors:** Devin CLI  
**Scope:** Full-stack inspection of the ZivaStock project (backend, frontend, Android app) and verification that each component can be built/run locally.

---

## 1. Executive Summary

ZivaStock is an offline-first, multi-user enterprise stocktake and reconciliation system. It consists of:

- a **FastAPI/Python** backend with PostgreSQL persistence,
- a **React/TypeScript/Vite** web dashboard,
- an **Android/Kotlin** mobile app with Room, WorkManager, and ML Kit barcode scanning.

At the end of this inspection:

| Component | Status |
| --- | --- |
| PostgreSQL `zivastockdb` | **Running and populated** |
| FastAPI backend | **Running** on `http://127.0.0.1:8000` |
| React frontend | **Running** on `http://localhost:3000`; production build passes |
| Android app | **Builds successfully** (`app:assembleDebug`) |
| Backend ↔ Android sync API | **Verified** via `/api/v1/sync/push` and `/api/v1/sync/pull` |

Two small source-code fixes were required to reach this state (see Section 6). Redis is not running in this environment and is reported as `unavailable` by the backend health check, although the API remains operational.

---

## 2. Environment

| Tool | Version / State |
| --- | --- |
| OS | Windows |
| Python | 3.11.4 |
| Node.js | v26.4.0 |
| Java / JDK | Microsoft OpenJDK 17.0.19 |
| PostgreSQL | 18.4 (service running, `zivastockdb` reachable) |
| Redis | Not running / not reachable on `localhost:6379` |
| Docker | 29.6.2 |

A `.env` file exists at the project root and contains development credentials for PostgreSQL and JWT settings. The `.env.example` file documents all variables.

---

## 3. Architecture & Technology Stack

### 3.1 Backend (`backend/`)

- **Framework:** FastAPI (Python 3.11)
- **ORM / Migrations:** SQLAlchemy 2.x + Alembic
- **Database driver:** psycopg2-binary + asyncpg
- **Auth:** JWT access/refresh tokens (`python-jose`, `passlib[bcrypt]`)
- **Cache / sessions:** Redis client configured, but no local Redis server running
- **Data processing:** pandas, openpyxl, xlsxwriter
- **Reporting / exports:** reportlab
- **Rate limiting:** slowapi
- **Testing:** pytest, httpx, faker

The backend exposes `/api/v1` routes grouped under `auth`, `users`, `roles`, `products`, `counts`, `adjustments`, `sessions`, `sync`, `reports`, `locations`, `imports`, and `exports`. OpenAPI/Swagger docs are available at `http://127.0.0.1:8000/docs`.

### 3.2 Frontend (`frontend/`)

- **Framework:** React 18 with TypeScript 5
- **Build tool:** Vite 5
- **UI library:** Material UI 5 (`@mui/material`, `@mui/x-data-grid`, `@mui/x-charts`)
- **State management:** Redux Toolkit + React Redux
- **HTTP client:** Axios
- **Charts:** recharts
- **Excel/CSV:** xlsx

The dev server proxies `/api` requests to `http://127.0.0.1:8000` (configured in `vite.config.ts`).

### 3.3 Android App (`android-app/`)

- **Language:** Kotlin
- **Compile SDK:** 34, minSdk 26, targetSdk 34
- **Build system:** Gradle 8.13 + Android Gradle Plugin
- **Dependency injection:** Hilt 2.48
- **Local database:** Room 2.6.1
- **Networking:** Retrofit 2.9 + OkHttp 4.12
- **Background sync:** WorkManager 2.9.0
- **Barcode scanning:** ML Kit Barcode Scanning 17.2.0 + CameraX 1.3.1
- **Logging:** Timber

The app keeps offline-first data in Room and syncs with the backend through `SyncWorker` → `SyncEngine` (see Section 5).

---

## 4. Database

- **Name:** `zivastockdb`
- **Engine:** PostgreSQL 18.4
- **Host:** `localhost:5432`
- **Alembic migrations:** Applied; migration scripts live in `backend/alembic/versions/`
- **Main entities observed:** `users`, `roles`, `permissions`, `role_permissions`, `products`, `product_categories`, `locations`, `shelves`, `shelf_sections`, `stocktake_sessions`, `session_users`, `counts` (first & second), `duplicates`, `adjustments`, `import_batches`, `sync_queue`, `sync_records`, `audit_logs`.

The database contains seed/sample data (products, users, roles, locations, sessions) and accepted new records during the API sync tests.

---

## 5. Offline-First Sync & Barcode Scanning (Android)

### 5.1 Offline storage

The Android app uses Room with both a legacy (`v1`) and a current (`v2`) entity set:

- `v2_first_counts` / `FirstCountEntity`
- `v2_second_counts` / `SecondCountEntity`
- `v2_products` / `ProductEntity`
- `v2_sync_queue` / `SyncQueueItemEntity`

Local DAOs support unsynced-record queries, marking records as synced, and session-based retrieval.

### 5.2 Sync engine

- `SyncWorker` (`sync/SyncWorker.kt`) is a `CoroutineWorker` that delegates to `SyncEngine.performSync()`.
- `SyncEngine` (`sync/SyncEngine.kt`) runs a 5-step process:
  1. Push legacy v1 counts via `POST /api/v1/sync/push`.
  2. Push v2 first counts via `POST /counts/first/bulk`.
  3. Push v2 second counts via `POST /counts/second/bulk`.
  4. Process generic v2 sync-queue items.
  5. Pull server changes via `GET /api/v1/sync/pull` (v1) or `POST /sync/pull` (v2) and update local data.
- `SyncScheduler` schedules periodic sync every 15 minutes and supports immediate one-off sync.
- `SyncQueueManager` enqueues changes with deduplication and retry logic (max 3 retries).

### 5.3 Barcode scanning

- `ScannerActivity` uses CameraX `ImageAnalysis` and ML Kit `BarcodeScanning`.
- Supported formats include EAN-13, EAN-8, UPC-A, UPC-E, CODE-128, CODE-39, and QR codes.
- After a scan, the barcode is returned to `FirstCountViewModel`/`SecondCountViewModel`, which currently looks it up only in the local Room product cache (`ProductRepository.getByBarcode`). There is **no remote fallback** in the current implementation, although the backend exposes `GET /api/v1/products/barcode/{barcode}` and the v2 API has a similar route.

---

## 6. Issues Found & Fixes Applied

| # | Issue | Component | Fix |
| --- | --- | --- | --- |
| 1 | Android build failed with `Platform declaration clash` / duplicate JVM signatures for `filterBySession` extension functions on collection subtypes. | `android-app/app/src/main/java/com/zivastock/data/repository/v2/ReportsRepository.kt` | Replaced the clashing extension functions with regular methods on `ReportsRepository` and explicitly cast `BaseData` components where needed. |
| 2 | Frontend production build failed TypeScript checks: unused `React` import in `App.tsx`, unused `Avatar` import in `Header.tsx`, incorrect `SelectChangeEvent` handler type in `Reports.tsx`, JSX children type errors around `unknown` data, and `import.meta.env` not recognized in `api.ts`. | `frontend/src/App.tsx`, `frontend/src/components/layout/Header.tsx`, `frontend/src/pages/Reports.tsx`, `frontend/src/services/api.ts` | Removed unused imports, imported `SelectChangeEvent`, restructured the report table renderer so JSX returns a concrete `ReactNode`, added `frontend/src/vite-env.d.ts` for Vite client types. Build now passes. |
| 3 | Redis server not available on `localhost:6379`. | Infrastructure | Documented; backend health check reports `redis: unavailable` but remains healthy. |
| 4 | Backend pytest collection fails because test files import `app.models.base`, which does not exist (`Base` lives in `app.core.database`). | `backend/tests/test_count_service.py`, `backend/tests/test_report_service.py` | Documented as an open issue; not required for runtime operation. |

No backend source-code changes were required to make the API run; earlier edits to `counts.py`, `locations.py`, and `location_service.py` appear to have been exploratory or minor.

---

## 7. Functional Verification

### 7.1 Backend health & auth

- `GET /health` returns `{"status": "healthy", ...}`.
- `POST /api/v1/auth/login` succeeds for the seeded admin account and returns an access token.

### 7.2 Core API endpoints (sample checks)

All of the following returned HTTP 200/201 when called with a valid bearer token:

- `GET /api/v1/products` — paginated product list
- `GET /api/v1/sessions` — stocktake sessions
- `GET /api/v1/locations` — locations
- `GET /api/v1/sync/status` — sync status
- `POST /api/v1/counts/first` — create a first count
- `POST /api/v1/sync/push` — push an offline change set (success_count: 1, failed_count: 0)
- `GET /api/v1/sync/pull` — pull products and other server changes

### 7.3 Frontend

- `npm run dev` starts successfully on `http://localhost:3000`.
- `npm run build` completes successfully (TypeScript compilation + Vite production build) after the fixes in Section 6.

### 7.4 Android

- `./gradlew :app:assembleDebug` completes with `BUILD SUCCESSFUL`.
- A debug APK is produced in `android-app/app/build/outputs/apk/debug/`.

---

## 8. Remaining Limitations / TODOs

- **Redis dependency:** If rate limiting, session caching, or pub/sub features are intended to use Redis, a Redis instance must be started and `REDIS_*` variables in `.env` must point to it.
- **Backend tests:** The pytest suite is not passing because of import-path drift (`app.models.base`). This should be corrected or a `conftest.py` should add the backend directory to `sys.path` and point tests to `app.core.database.Base`.
- **Android stubs:** Several v2 repositories and ViewModels contain `TODO` placeholders (e.g., `SyncRepository.pushPending/pullLatest`, `ConsolidationViewModel`, `ButcheryFnVViewModel`). These are not blocking a debug build but will need implementation for full feature parity.
- **No remote barcode fallback:** When a scanned barcode is absent from the local Room cache, the app marks it as wrong-product. Consider adding a network lookup to `GET /api/v1/products/barcode/{barcode}` before giving up.
- **V1/V2 duality:** The Android codebase maintains both legacy (`v1`) and current (`v2`) data layers. Long-term, the legacy layer should be removed once migration is confirmed safe.
- **Frontend runtime validation:** UI login flows and stocktake screens were not manually exercised in a browser; only dev-server startup and production build were verified.

---

## 9. Recommendations

1. **Start Redis** for local development if caching/rate-limiting features are required, or disable Redis-dependent middleware until a cache is available.
2. **Fix backend pytest imports** so the automated test suite can run in CI.
3. **Add instrumentation tests** for the Android sync engine and barcode lookup paths; at minimum add a unit test for `SyncEngine.performSync()` against a mocked API.
4. **Implement remote barcode fallback** in `ProductRepository` to handle products that are not yet cached locally.
5. **Run the frontend end-to-end** against the local backend to verify login, stocktake creation, and report export flows.
6. **Document a single command** (e.g., `start_system.ps1`) for launching the backend + frontend; ensure `.env` values are safe for non-production use.

---

*End of report.*
