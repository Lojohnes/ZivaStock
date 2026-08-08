# ZivaStock - System Architecture

## Architecture Overview

ZivaStock is designed as a distributed enterprise system with a centralized server architecture and offline-first mobile clients. The system follows a microservices-inspired monolithic architecture for simplicity while maintaining scalability.

---

## 1. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ZivaStock System                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐  │
│  │   Web Dashboard  │      │  Admin Console   │      │  Reporting UI    │  │
│  │   (React + TS)   │      │   (React + TS)   │      │   (React + TS)   │  │
│  └────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘  │
│           │                          │                          │           │
│           └──────────────────────────┼──────────────────────────┘           │
│                                      │                                      │
│                           ┌──────────▼──────────┐                           │
│                           │   API Gateway /     │                           │
│                           │   Load Balancer     │                           │
│                           └──────────┬──────────┘                           │
│                                      │                                      │
│                           ┌──────────▼──────────┐                           │
│                           │   FastAPI Backend   │                           │
│                           │   (Python 3.11+)    │                           │
│                           │  ┌────────────────┐ │                           │
│                           │  │  Auth Service  │ │                           │
│                           │  │  User Service  │ │                           │
│                           │  │ Product Service│ │                           │
│                           │  │  Count Service │ │                           │
│                           │  │ Session Service│ │                           │
│                           │  │  Sync Service  │ │                           │
│                           │  │ Report Service │ │                           │
│                           │  │  Audit Service │ │                           │
│                           │  │  ETL Service   │ │                           │
│                           │  └────────────────┘ │                           │
│                           └──────────┬──────────┘                           │
│                                      │                                      │
│           ┌──────────────────────────┼──────────────────────────┐           │
│           │                          │                          │           │
│  ┌────────▼────────┐      ┌─────────▼─────────┐      ┌────────▼────────┐    │
│  │   PostgreSQL    │      │   Redis Cache     │      │  File Storage   │    │
│  │   (Primary DB)  │      │   (Session/Cache) │      │  (Uploads/Exports)│   │
│  └─────────────────┘      └───────────────────┘      └─────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              Mobile Layer                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐  │
│  │  Android App #1  │      │  Android App #2  │      │  Android App #N  │  │
│  │  (Kotlin)        │      │  (Kotlin)        │      │  (Kotlin)        │  │
│  │  ┌────────────┐  │      │  ┌────────────┐  │      │  ┌────────────┐  │  │
│  │  │ Room DB    │  │      │  │ Room DB    │  │      │  │ Room DB    │  │  │
│  │  │ (Offline)  │  │      │  │ (Offline)  │  │      │  │ (Offline)  │  │  │
│  │  └────────────┘  │      │  └────────────┘  │      │  └────────────┘  │  │
│  │  ┌────────────┐  │      │  ┌────────────┐  │      │  ┌────────────┐  │  │
│  │  │ Sync Engine│  │      │  │ Sync Engine│  │      │  │ Sync Engine│  │  │
│  │  └────────────┘  │      │  └────────────┘  │      │  └────────────┘  │  │
│  │  ┌────────────┐  │      │  ┌────────────┐  │      │  ┌────────────┐  │  │
│  │  │ Barcode    │  │      │  │ Barcode    │  │      │  │ Barcode    │  │  │
│  │  │ Scanner    │  │      │  │ Scanner    │  │      │  │ Scanner    │  │  │
│  │  └────────────┘  │      │  └────────────┘  │      │  └────────────┘  │  │
│  └────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘  │
│           │                          │                          │           │
│           └──────────────────────────┼──────────────────────────┘           │
│                                      │                                      │
│                           ┌──────────▼──────────┐                           │
│                           │   REST API /        │                           │
│                           │   WebSocket         │                           │
│                           │   (HTTPS)           │                           │
│                           └─────────────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Backend Services (FastAPI)

```
backend/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── v1/
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── users.py       # User management
│   │   │   ├── products.py    # Product CRUD
│   │   │   ├── counts.py      # Stock count operations
│   │   │   ├── sessions.py    # Stocktake session management
│   │   │   ├── locations.py   # Location hierarchy
│   │   │   ├── sync.py        # Sync endpoints for mobile
│   │   │   ├── reports.py     # Report generation
│   │   │   ├── imports.py     # Data import ETL
│   │   │   └── exports.py     # Data export
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── security.py        # JWT, password hashing
│   │   ├── database.py        # Database connection
│   │   └── cache.py           # Redis caching
│   ├── models/                 # Database models (SQLAlchemy)
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── count.py
│   │   ├── session.py
│   │   ├── location.py
│   │   ├── audit.py
│   │   └── sync.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── count.py
│   │   ├── session.py
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── count_service.py
│   │   ├── sync_service.py
│   │   ├── duplicate_service.py
│   │   ├── report_service.py
│   │   └── etl_service.py
│   ├── utils/                  # Utilities
│   │   ├── barcode.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── middleware/             # Custom middleware
│       ├── auth.py
│       ├── rate_limit.py
│       └── audit.py
├── tests/                      # Test suite
├── alembic/                    # Database migrations
├── scripts/                    # Utility scripts
├── requirements.txt            # Python dependencies
└── main.py                     # Application entry point
```

### 2.2 Frontend Architecture (React + TypeScript)

```
frontend/
├── src/
│   ├── components/             # Reusable components
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Table.tsx
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Layout.tsx
│   │   ├── dashboard/
│   │   │   ├── KPICard.tsx
│   │   │   ├── Chart.tsx
│   │   │   └── Progress.tsx
│   │   └── stocktake/
│   │       ├── ProductList.tsx
│   │       ├── CountForm.tsx
│   │       └── SessionManager.tsx
│   ├── pages/                  # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Stocktake.tsx
│   │   ├── Products.tsx
│   │   ├── Reports.tsx
│   │   ├── Users.tsx
│   │   ├── Settings.tsx
│   │   └── Imports.tsx
│   ├── services/               # API services
│   │   ├── api.ts              # Axios configuration
│   │   ├── auth.service.ts
│   │   ├── product.service.ts
│   │   ├── count.service.ts
│   │   └── report.service.ts
│   ├── store/                  # State management (Redux Toolkit)
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── productSlice.ts
│   │   │   ├── countSlice.ts
│   │   │   └── sessionSlice.ts
│   │   └── index.ts
│   ├── hooks/                  # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useProducts.ts
│   │   └── useSync.ts
│   ├── types/                  # TypeScript types
│   │   ├── user.ts
│   │   ├── product.ts
│   │   └── count.ts
│   ├── utils/                  # Utilities
│   │   ├── formatters.ts
│   │   └── validators.ts
│   └── App.tsx                 # Root component
├── public/                     # Static assets
├── package.json
└── tsconfig.json
```

### 2.3 Android App Architecture (Kotlin)

```
android-app/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/zivastock/
│   │   │   │   ├── data/
│   │   │   │   │   ├── local/
│   │   │   │   │   │   ├── database/
│   │   │   │   │   │   │   ├── AppDatabase.kt
│   │   │   │   │   │   │   ├── entities/
│   │   │   │   │   │   │   │   ├── ProductEntity.kt
│   │   │   │   │   │   │   │   ├── CountEntity.kt
│   │   │   │   │   │   │   │   └── SyncQueueEntity.kt
│   │   │   │   │   │   │   └── dao/
│   │   │   │   │   │   │       ├── ProductDao.kt
│   │   │   │   │   │   │       ├── CountDao.kt
│   │   │   │   │   │   │       └── SyncQueueDao.kt
│   │   │   │   │   │   └── preferences/
│   │   │   │   │   │       └── SharedPreferencesManager.kt
│   │   │   │   │   ├── remote/
│   │   │   │   │   │   ├── api/
│   │   │   │   │   │   │   ├── ApiService.kt
│   │   │   │   │   │   │   ├── AuthApi.kt
│   │   │   │   │   │   │   ├── ProductApi.kt
│   │   │   │   │   │   │   └── SyncApi.kt
│   │   │   │   │   │   └── dto/
│   │   │   │   │   │       ├── ProductDto.kt
│   │   │   │   │   │       └── CountDto.kt
│   │   │   │   │   └── repository/
│   │   │   │   │       ├── ProductRepository.kt
│   │   │   │   │       ├── CountRepository.kt
│   │   │   │   │       └── SyncRepository.kt
│   │   │   │   ├── domain/
│   │   │   │   │   ├── model/
│   │   │   │   │   │   ├── Product.kt
│   │   │   │   │   │   ├── Count.kt
│   │   │   │   │   │   └── SyncStatus.kt
│   │   │   │   │   ├── usecase/
│   │   │   │   │   │   ├── ScanBarcodeUseCase.kt
│   │   │   │   │   │   ├── SaveCountUseCase.kt
│   │   │   │   │   │   └── SyncDataUseCase.kt
│   │   │   │   │   └── repository/
│   │   │   │   │       └── IProductRepository.kt
│   │   │   │   ├── presentation/
│   │   │   │   │   ├── scanner/
│   │   │   │   │   │   ├── ScannerActivity.kt
│   │   │   │   │   │   ├── ScannerViewModel.kt
│   │   │   │   │   │   └── ScannerFragment.kt
│   │   │   │   │   ├── counting/
│   │   │   │   │   │   ├── CountingActivity.kt
│   │   │   │   │   │   ├── CountingViewModel.kt
│   │   │   │   │   │   └── CountingFragment.kt
│   │   │   │   │   ├── sync/
│   │   │   │   │   │   ├── SyncStatusActivity.kt
│   │   │   │   │   │   └── SyncViewModel.kt
│   │   │   │   │   └── login/
│   │   │   │   │       ├── LoginActivity.kt
│   │   │   │   │       └── LoginViewModel.kt
│   │   │   │   ├── sync/
│   │   │   │   │   ├── SyncEngine.kt
│   │   │   │   │   ├── SyncWorker.kt
│   │   │   │   │   ├── ConflictResolver.kt
│   │   │   │   │   └── OfflineQueue.kt
│   │   │   │   ├── barcode/
│   │   │   │   │   ├── BarcodeScanner.kt
│   │   │   │   │   └── BarcodeParser.kt
│   │   │   │   ├── di/
│   │   │   │   │   ├── DatabaseModule.kt
│   │   │   │   │   ├── NetworkModule.kt
│   │   │   │   │   └── RepositoryModule.kt
│   │   │   │   └── utils/
│   │   │   │       ├── NetworkUtils.kt
│   │   │   │       └── DateUtils.kt
│   │   │   ├── res/
│   │   │   │   ├── layout/
│   │   │   │   ├── values/
│   │   │   │   └── drawable/
│   │   │   └── AndroidManifest.xml
│   │   └── test/
│   └── build.gradle.kts
├── gradle/
├── gradle.properties
└── settings.gradle.kts
```

---

## 3. Data Flow Architecture

### 3.1 Stock Count Flow

```
User scans barcode (Android)
    ↓
Barcode parser validates format
    ↓
Product lookup in local Room DB
    ↓
If found: Display product info
If not found: Create new product locally
    ↓
User enters quantity, shelf, section
    ↓
Save to Room DB (offline)
    ↓
Add to sync queue
    ↓
Background sync worker checks network
    ↓
If online: POST to API
    ↓
API validates and saves to PostgreSQL
    ↓
WebSocket notifies other clients
    ↓
Dashboard updates in real-time
```

### 3.2 Sync Flow

```
Mobile App (Offline)
    ↓
User performs actions
    ↓
Actions saved to Room DB
    ↓
Actions queued in SyncQueue table
    ↓
WorkManager triggers SyncWorker
    ↓
Check network connectivity
    ↓
If offline: Retry with exponential backoff
    ↓
If online: Process queue in FIFO order
    ↓
For each queued action:
    - Serialize to JSON
    - Send to API endpoint
    - Handle success/failure
    - Update sync status
    - Remove from queue on success
    - Retry on failure
    ↓
Conflict resolution if needed
    ↓
Pull latest data from server
    ↓
Update local Room DB
    ↓
Notify user of sync completion
```

### 3.3 Duplicate Detection Flow

```
New count received
    ↓
Query existing counts for same:
    - Product ID
    - Shelf
    - Section
    - Location
    ↓
If match found:
    - Compare quantities
    - If same: Flag as duplicate
    - If different: Flag as conflict
    ↓
Apply conflict resolution rules:
    - Last-write-wins (default)
    - Or custom rules
    ↓
Create duplicate/conflict record
    ↓
Notify supervisor
    ↓
Add to duplicate report
```

---

## 4. Technology Stack Selection

### 4.1 Backend: FastAPI (Python)

**Rationale:**
- **Performance**: Async/await support for high concurrency
- **Type Safety**: Native Python type hints with Pydantic
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Validation**: Built-in request/response validation
- **Ecosystem**: Rich library ecosystem (SQLAlchemy, Alembic, etc.)
- **Ease of Development**: Rapid development with clean syntax
- **Testing**: Excellent testing support with pytest
- **WebSocket Support**: Native WebSocket for real-time features

**Alternatives Considered:**
- Node.js NestJS: Good but Python's data science ecosystem better for analytics
- Java Spring: Too verbose for rapid development
- Go: Great performance but smaller ecosystem

### 4.2 Frontend: React + TypeScript + Material UI

**Rationale:**
- **React**: Industry standard, large ecosystem, component reusability
- **TypeScript**: Type safety, better IDE support, fewer runtime errors
- **Material UI**: Professional enterprise components, consistent design
- **Redux Toolkit**: State management with excellent dev tools
- **React Query**: Server state management, caching, sync

**Alternatives Considered:**
- Vue.js: Good but smaller enterprise adoption
- Angular: Too complex for this use case
- Svelte: Too new for enterprise

### 4.3 Android: Kotlin + Room + WorkManager

**Rationale:**
- **Kotlin**: Modern, null-safe, concise, Google-recommended
- **Room Database**: Type-safe SQLite abstraction, compile-time verification
- **WorkManager**: Background task execution with constraints
- **Jetpack Compose**: Modern UI toolkit (optional)
- **ML Kit Barcode Scanning**: Google's ML-powered barcode detection
- **Coroutines & Flow**: Async programming, reactive streams

**Alternatives Considered:**
- Java: Verbose, null-unsafe
- Flutter: Good but native Kotlin better for performance
- React Native: Good but native camera access better in Kotlin

### 4.4 Database: PostgreSQL

**Rationale:**
- **ACID Compliance**: Strong data integrity
- **Complex Queries**: Advanced SQL features
- **JSON Support**: Flexible data storage
- **Performance**: Excellent for read-heavy workloads
- **Scalability**: Partitioning, replication support
- **Full-Text Search**: Built-in search capabilities
- **Extensions**: PostGIS, pg_stat_statements, etc.

**Alternatives Considered:**
- MySQL: Good but PostgreSQL has better features
- MongoDB: NoSQL not suitable for structured stock data
- SQL Server: Expensive licensing

### 4.5 Cache: Redis

**Rationale:**
- **Performance**: In-memory caching
- **Session Storage**: Fast session management
- **Pub/Sub**: Real-time notifications
- **Data Structures**: Rich data types
- **Persistence**: Optional disk persistence

### 4.6 Additional Technologies

- **Alembic**: Database migrations
- **SQLAlchemy**: Python ORM
- **Pydantic**: Data validation
- **PyJWT**: JWT token handling
- **Passlib**: Password hashing
- **Celery**: Background task processing (optional)
- **Pandas**: Data processing for reports
- **OpenPyXL**: Excel import/export
- **ReportLab**: PDF generation
- **Docker**: Containerization
- **Nginx**: Reverse proxy and load balancing

---

## 5. Security Architecture

### 5.1 Authentication Flow

```
User enters credentials
    ↓
POST /api/v1/auth/login
    ↓
Backend validates credentials
    ↓
If valid:
    - Generate JWT access token (15 min expiry)
    - Generate refresh token (7 days expiry)
    - Hash refresh token and store in DB
    - Return tokens to client
    ↓
Client stores tokens securely
    ↓
Subsequent requests include access token in header
    ↓
Backend validates JWT signature and expiry
    ↓
If expired:
    - Use refresh token to get new access token
    - If refresh token expired: Re-login required
```

### 5.2 Authorization Model

- **Role-Based Access Control (RBAC)**
- **Permissions**: Granular permissions per role
- **Middleware**: Authorization checks on protected routes
- **Resource Ownership**: Users can only access their own data (where applicable)

### 5.3 Security Measures

- **Password Hashing**: bcrypt with salt
- **JWT Signing**: RS256 asymmetric keys
- **HTTPS**: TLS 1.3 encryption
- **Rate Limiting**: Per-IP and per-user limits
- **SQL Injection Prevention**: Parameterized queries via ORM
- **XSS Prevention**: Input sanitization, CSP headers
- **CSRF Protection**: Token-based CSRF protection
- **Audit Logging**: All security events logged
- **API Key Management**: For external integrations

---

## 6. Scalability Architecture

### 6.1 Horizontal Scaling

- **Stateless API**: Multiple FastAPI instances
- **Load Balancer**: Nginx round-robin distribution
- **Database Pooling**: Connection pooling (PgBouncer)
- **Cache Layer**: Redis cluster for distributed caching
- **Session Storage**: Redis instead of in-memory

### 6.2 Database Scaling

- **Read Replicas**: Multiple read replicas for reporting
- **Connection Pooling**: PgBouncer for connection management
- **Indexing**: Optimized indexes for common queries
- **Partitioning**: Time-based partitioning for audit logs
- **Query Optimization**: EXPLAIN ANALYZE for slow queries

### 6.3 Mobile Scaling

- **Sync Batching**: Batch sync operations
- **Delta Sync**: Only sync changed data
- **Compression**: Gzip compression for API responses
- **Pagination**: Large datasets paginated
- **Lazy Loading**: Load data on demand

---

## 7. Disaster Recovery & Backup Strategy

### 7.1 Database Backups

- **Daily Full Backups**: pg_dump at 2 AM
- **Hourly Incremental**: WAL archiving
- **Retention**: 30 days onsite, 90 days offsite
- **Offsite Storage**: Cloud storage (AWS S3/Azure Blob)
- **Backup Verification**: Weekly restore tests

### 7.2 Application Backups

- **Code Repository**: Git with multiple remotes
- **Configuration**: Version-controlled config files
- **Media Files**: Regular sync to backup storage
- **Environment Variables**: Secure storage (Vault)

### 7.3 High Availability

- **Database Replication**: Streaming replication
- **Auto Failover**: Patroni for automatic failover
- **Load Balancer**: Active-passive configuration
- **Monitoring**: Prometheus + Grafana
- **Alerting**: PagerDuty/Slack integration

---

## 8. Monitoring & Observability

### 8.1 Application Monitoring

- **Metrics**: Prometheus metrics (request count, latency, errors)
- **Logging**: Structured JSON logs with ELK stack
- **Tracing**: Distributed tracing with Jaeger
- **Health Checks**: /health endpoint for uptime monitoring

### 8.2 Database Monitoring

- **Query Performance**: pg_stat_statements
- **Connection Pool**: PgBouncer stats
- **Replication Lag**: Monitoring replica lag
- **Disk Usage**: Storage capacity monitoring

### 8.3 Mobile Monitoring

- **Crash Reporting**: Firebase Crashlytics
- **Analytics**: Firebase Analytics
- **Performance**: Custom performance metrics
- **Sync Status**: Monitoring sync success rates

---

## 9. Deployment Architecture

### 9.1 Development Environment

- **Local Development**: Docker Compose
- **Database**: Local PostgreSQL container
- **Cache**: Local Redis container
- **Frontend**: Vite dev server
- **Android**: Android Studio emulator

### 9.2 Staging Environment

- **Cloud**: AWS/Azure/GCP
- **Containers**: Docker
- **Orchestration**: Docker Swarm or Kubernetes
- **CI/CD**: GitHub Actions or GitLab CI
- **Database**: Managed PostgreSQL (RDS/Azure Database)

### 9.3 Production Environment

- **High Availability**: Multi-AZ deployment
- **Load Balancing**: Application Load Balancer
- **Auto Scaling**: Horizontal pod autoscaling
- **CDN**: CloudFront for static assets
- **SSL/TLS**: Certificate managed by ACM
- **WAF**: Web Application Firewall

---

## 10. Integration Architecture

### 10.1 Sage Evolution Integration

```
Sage Evolution
    ↓
Export Valuation Report (Excel/CSV)
    ↓
Upload to ZivaStock
    ↓
ETL Process:
    - Extract file
    - Transform data (field mapping)
    - Validate data
    - Load to staging table
    - Preview to user
    - Final load to products table
    ↓
Stocktake Process
    ↓
Export Results (Sage-compatible format)
    ↓
Import to Sage Evolution
```

### 10.2 Generic ERP Integration

- **File-based**: Excel/CSV import/export
- **API-based**: REST API endpoints (future)
- **Webhook-based**: Event-driven integration (future)
- **Batch Processing**: Scheduled ETL jobs

---

## Document Version
- Version: 1.0
- Date: June 9, 2026
- Author: System Architecture Team
- Status: Approved
