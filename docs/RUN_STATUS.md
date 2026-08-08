# ZivaStock Run Status

This document records how to start each ZivaStock component and the current state of the local development environment.

**Last updated:** 2026-08-07  
**Environment:** Windows local development machine

---

## 1. Required Services

### PostgreSQL

- **Database:** `zivastockdb`
- **Host:** `localhost:5432`
- **User:** `postgres`
- **Status:** Running and reachable
- **Verification:**
  ```powershell
  Invoke-RestMethod -Uri http://127.0.0.1:8000/health
  ```
  or connect directly with `psycopg2`/`psql`.

### Redis

- **Host:** `localhost:6379`
- **Status:** **Not running** in this environment
- **Impact:** Backend health check reports `redis: unavailable`, but core API endpoints work. Features that rely on Redis caching or distributed sessions may behave unexpectedly until Redis is started.

---

## 2. Backend

### How to start

From the project root:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info
```

### Current status

- **State:** Running
- **URL:** http://127.0.0.1:8000
- **Health:** `{"status":"healthy","app_name":"ZivaStock","version":"1.0.0","environment":"development"}`
- **API docs:** http://127.0.0.1:8000/docs
- **Migrations:** Already applied (`alembic upgrade head`) during setup

### Useful API checks

Login and list products:

```powershell
$login = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/auth/login `
  -Method POST -Body (@{email='admin@zivastock.com';password='Laugh@2012'} | ConvertTo-Json) `
  -ContentType 'application/json'

$headers = @{Authorization = "Bearer $($login.access_token)"}

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/products -Headers $headers
```

### Known issues

- Backend pytest suite currently fails during collection because some tests import the non-existent module `app.models.base`. Use `python -m pytest` from `backend/` and update `from app.models.base import Base` to `from app.core.database import Base` in affected tests.

---

## 3. Frontend

### How to start

From the project root:

```powershell
cd frontend
npm run dev
```

### Current status

- **State:** Running
- **URL:** http://localhost:3000
- **Proxy:** `/api` → `http://127.0.0.1:8000` (configured in `vite.config.ts`)

### Production build

```powershell
cd frontend
npm run build
```

**Status:** Passes after fixing TypeScript errors in `App.tsx`, `Header.tsx`, `Reports.tsx`, and adding `vite-env.d.ts`.

### Known issues

- Build emits a chunk-size warning (≈1.2 MB). Code-splitting with dynamic imports can reduce this.
- Manual browser testing of login/dashboard screens is still pending.

---

## 4. Android App

### How to build

From the project root:

```powershell
cd android-app
.\gradlew.bat :app:assembleDebug
```

### Current status

- **State:** Builds successfully
- **Output APK:** `android-app/app/build/outputs/apk/debug/app-debug.apk`
- **Target device:** Android Emulator or physical device with API 26+
- **Default API base URL:** `http://10.0.2.2:8000/api/v1/` (emulator loopback); can be overridden.

### How to install on an emulator

```powershell
cd android-app
.\gradlew.bat installDebug
```

or with `adb`:

```powershell
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Known issues

- A previous build failed due to clashing Kotlin extension-function JVM signatures in `ReportsRepository.kt`. This was fixed by converting the conflicting functions to regular methods and explicitly casting `BaseData` components.
- Several v2 repositories and ViewModels contain `TODO` stubs that need implementation for full feature parity.
- Barcode lookup currently only checks the local Room cache; if the product is not cached, it is reported as wrong. A remote fallback to `GET /api/v1/products/barcode/{barcode}` should be added.

---

## 5. Quick Smoke Test

Run these commands to confirm the system is operational end-to-end:

```powershell
# 1. Backend health
Invoke-RestMethod -Uri http://127.0.0.1:8000/health

# 2. Login
$login = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/auth/login `
  -Method POST `
  -Body (@{email='admin@zivastock.com';password='Laugh@2012'} | ConvertTo-Json) `
  -ContentType 'application/json'

$headers = @{Authorization = "Bearer $($login.access_token)"}

# 3. List products
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/products -Headers $headers

# 4. Sync a first count (mimics Android offline-sync push)
$syncBody = @{
  items = @(
    @{
      entity_type = 'first_count'
      action = 'create'
      client_id = 'smoke-test-001'
      payload = @{
        session_id = 1
        product_id = 2
        shelf_section_id = 1
        quantity = 3
      }
    }
  )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/sync/push `
  -Method POST -Body $syncBody -Headers $headers -ContentType 'application/json'

# 5. Pull server updates
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/sync/pull?last_sync=2026-01-01T00:00:00' -Headers $headers
```

All of the above returned HTTP 200/201 during the inspection.

---

## 6. One-Shot Launcher Script

The repository includes `start_system.ps1` at the project root. It kills any running Python/Node processes and opens the backend and frontend in separate console windows:

```powershell
.\start_system.ps1
```

After running the script:

- Backend: http://127.0.0.1:8000
- Frontend: http://localhost:3000

**Note:** The script starts processes in separate `cmd.exe` windows and may not be ideal for automated environments.

---

## 7. Summary Table

| Component | Command | URL / Artifact | Status |
| --- | --- | --- | --- |
| PostgreSQL | Service-dependent | `localhost:5432/zivastockdb` | Running |
| Backend | `python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload` | http://127.0.0.1:8000 | Running |
| Frontend | `npm run dev` | http://localhost:3000 | Running |
| Frontend build | `npm run build` | `frontend/dist/` | Passes |
| Android debug build | `gradlew :app:assembleDebug` | `android-app/app/build/outputs/apk/debug/app-debug.apk` | Passes |
| Backend tests | `python -m pytest tests` | — | Fails during collection |

---

*End of run-status document.*
