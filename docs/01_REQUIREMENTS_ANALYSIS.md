# ZivaStock - Requirements Analysis

## Project Overview
ZivaStock is an enterprise-grade multiuser stocktake system designed for retail shops and warehouses. The system enables simultaneous stock counting by multiple users with real-time synchronization, offline-first mobile capabilities, and comprehensive reporting.

---

## 1. Functional Requirements

### 1.1 Multiuser Stock Counting
- **FR-001**: Multiple users must be able to count stock simultaneously from different locations
- **FR-002**: System must support concurrent counting on same shelf but different sections
- **FR-003**: System must intelligently merge counts from multiple users
- **FR-004**: No conflicts must occur when users count different sections
- **FR-005**: Real-time visibility of counts across all users

### 1.2 Stocktake Session Management
- **FR-006**: System must support multiple stocktake sessions (e.g., June 2026, July 2026)
- **FR-007**: Each session must track: Session ID, Session name, Date, Users involved, Start time, End time, Status
- **FR-008**: Sessions must maintain complete count history
- **FR-009**: Management must review historical stocktakes for minimum 6 months
- **FR-010**: Session status: Not Started, In Progress, Paused, Completed, Archived

### 1.3 Product Scanning
- **FR-011**: Android app must scan products using phone camera
- **FR-012**: Support barcode formats: EAN, UPC, QR, Custom product barcodes
- **FR-013**: Auto-detect: Barcode, Product description, Product code, Unit of measure, Existing stock quantity
- **FR-014**: User must input: Counted quantity, Shelf number, Section number, Location
- **FR-015**: Display all counted products in current section
- **FR-016**: Users can Add, Edit, Delete, Correct mistakes, Save section
- **FR-017**: Workflow: Section → Shelf → Next Section → Next Shelf

### 1.4 Shelf & Location Logic
- **FR-018**: Support hierarchy: Store → Location → Shelf → Section
- **FR-019**: Each section stores: Products, Quantities, Counter user, Timestamp
- **FR-020**: System must prevent confusion between sections
- **FR-021**: Location management with unlimited nesting levels

### 1.5 Duplicate Detection
- **FR-022**: Back office must intelligently detect duplicates
- **FR-023**: Duplicate criteria: Same Product + Same Shelf + Same Section + Same Location + Same Quantity
- **FR-024**: If quantities differ: System must compare, add/subtract intelligently, recommend reconciliation
- **FR-025**: Conflict-resolution rules must be configurable
- **FR-026**: Duplicate report generation

### 1.6 Data Import from ERP Systems
- **FR-027**: Import product master data from external ERP systems
- **FR-028**: Supported formats: Excel, CSV, Sage exports, Text files
- **FR-029**: ETL pipeline with Extract, Transform, Load phases
- **FR-030**: Column mapping capability (user-defined field mappings)
- **FR-031**: Data cleaning: Remove duplicates, Handle nulls, Validate data, Normalize formats
- **FR-032**: Preview before final import
- **FR-033**: Import logs with success/failure tracking

### 1.7 Sage Evolution Integration
- **FR-034**: Import valuation reports from Sage Evolution
- **FR-035**: Export final stocktake results in Sage-compatible format
- **FR-036**: Manual Excel valuation report import support
- **FR-037**: Fields: Product code, Barcode, Description, Quantity, Cost, Total valuation
- **FR-038**: ETL transformation before final loading

### 1.8 Reporting Module
- **FR-039**: Variation Report (System quantity vs Counted quantity, Variance calculation)
- **FR-040**: Duplicate Report
- **FR-041**: Missing Stock Report (Products in system not counted)
- **FR-042**: Overcount Report (Unexpected counted items)
- **FR-043**: User Productivity Report (User, Counts completed, Time taken, Accuracy)
- **FR-044**: Audit Trail Report (Who did what, When, Before, After)
- **FR-045**: Historical Stocktake Report (Filter by Month, User, Location, Session)
- **FR-046**: Export reports to Excel and PDF

### 1.9 Dashboard & Analytics
- **FR-047**: Real-time dashboard with KPIs
- **FR-048**: Metrics: Total products counted, Total outstanding, Variances, Not counted items, Duplicate counts
- **FR-049**: User performance metrics
- **FR-050**: Shelf completion percentage
- **FR-051**: Section completion percentage
- **FR-052**: Live counting progress
- **FR-053**: Charts and visualizations
- **FR-054**: Real-time refresh

### 1.10 User Management
- **FR-055**: Admin user registration capability
- **FR-056**: Role-based access control (RBAC)
- **FR-057**: Roles: Super Admin, Stocktake Manager, Supervisor, Counter, Auditor
- **FR-058**: Configurable permissions per role
- **FR-059**: User profile management

### 1.11 Audit Trail
- **FR-060**: Track every action in the system
- **FR-061**: Tracked actions: Login, Logout, Edit quantity, Delete count, Import file, Export report, User creation
- **FR-062**: Stored data: User, Date, Time, IP, Action, Old value, New value
- **FR-063**: Immutable audit logs

### 1.12 Offline-First Mobile App
- **FR-064**: Mobile app must work without internet
- **FR-065**: Continue scanning and counting offline
- **FR-066**: Save data locally using SQLite/Room
- **FR-067**: Auto-sync when network restored
- **FR-068**: No data loss allowed
- **FR-069**: Offline queue implementation
- **FR-070**: Sync retry mechanism
- **FR-071**: Duplicate prevention in offline mode
- **FR-072**: Conflict handling for sync

---

## 2. Non-Functional Requirements

### 2.1 Performance
- **NFR-001**: Support 100+ simultaneous users
- **NFR-002**: Handle large inventory (100,000+ products)
- **NFR-003**: Fast barcode scanning (< 1 second per scan)
- **NFR-004**: Fast sync operations (< 5 seconds for typical sync)
- **NFR-005**: Optimized database queries (< 500ms for standard queries)
- **NFR-006**: Dashboard refresh < 2 seconds

### 2.2 Scalability
- **NFR-007**: Horizontal scaling capability
- **NFR-008**: Database connection pooling
- **NFR-009**: Caching layer for frequently accessed data
- **NFR-010**: Load balancing support

### 2.3 Security
- **NFR-011**: JWT authentication
- **NFR-012**: Refresh token mechanism
- **NFR-013**: Password hashing (bcrypt/argon2)
- **NFR-014**: SQL injection prevention
- **NFR-015**: API rate limiting
- **NFR-016**: Secure API endpoints (HTTPS)
- **NFR-017**: Role-based authorization
- **NFR-018**: Audit logging for security events
- **NFR-019**: Secure password policies
- **NFR-020**: Session management

### 2.4 Reliability
- **NFR-021**: 99.9% uptime target
- **NFR-022**: Automatic failover
- **NFR-023**: Data backup strategies
- **NFR-024**: Disaster recovery plan
- **NFR-025**: Error handling and logging

### 2.5 Usability
- **NFR-026**: User-friendly interface
- **NFR-027**: Modern design
- **NFR-028**: Easy to learn (minimal training required)
- **NFR-029**: Fast response times
- **NFR-030**: Mobile responsive
- **NFR-031**: Professional enterprise design
- **NFR-032**: Android UI: Extremely simple for counters, minimize clicks, fast scanning workflow

### 2.6 Compatibility
- **NFR-033**: Cross-platform support (Web, Android)
- **NFR-034**: Browser compatibility (Chrome, Firefox, Safari, Edge)
- **NFR-035**: Android version support (Android 8.0+)
- **NFR-036**: Database: PostgreSQL 12+

### 2.7 Maintainability
- **NFR-037**: Modular architecture
- **NFR-038**: Clean code principles
- **NFR-039**: Comprehensive documentation
- **NFR-040**: Automated testing
- **NFR-041**: CI/CD pipeline
- **NFR-042**: Code review process

### 2.8 Data Integrity
- **NFR-043**: ACID compliance for transactions
- **NFR-044**: Data validation at all layers
- **NFR-045**: Foreign key constraints
- **NFR-046**: Unique constraints
- **NFR-047**: Check constraints
- **NFR-048**: Referential integrity

---

## 3. Business Rules

### 3.1 Stock Counting Rules
- **BR-001**: A product can be counted multiple times in different sections
- **BR-002**: Same product in same section by different users triggers duplicate detection
- **BR-003**: Variance = Counted Quantity - System Quantity
- **BR-004**: Positive variance = Overcount
- **BR-005**: Negative variance = Undercount
- **BR-006**: Zero variance = Accurate count

### 3.2 Session Rules
- **BR-007**: Only one active session per location at a time
- **BR-008**: Completed sessions cannot be modified
- **BR-009**: Archived sessions are read-only
- **BR-010**: Session can be paused and resumed

### 3.3 User Rules
- **BR-011**: Counter role can only count stock
- **BR-012**: Supervisor can monitor counters
- **BR-013**: Stocktake Manager can manage stocktakes
- **BR-014**: Super Admin has full access
- **BR-015**: Auditor can review reports only

### 3.4 Sync Rules
- **BR-016**: Last-write-wins for conflicting edits
- **BR-017**: Timestamp-based conflict resolution
- **BR-018**: Offline changes sync on network restore
- **BR-019**: Sync queue processes in FIFO order
- **BR-020**: Failed sync retries with exponential backoff

---

## 4. Data Requirements

### 4.1 Master Data
- Products (barcode, description, code, unit of measure, cost)
- Locations (store, warehouse, shelf, section)
- Users (name, email, role, permissions)
- Suppliers (optional)

### 4.2 Transaction Data
- Stock counts (product, quantity, location, user, timestamp)
- Stocktake sessions
- Audit logs
- Sync records

### 4.3 Historical Data
- Minimum 6 months retention
- Archived stocktakes
- Historical reports
- Audit trail (12 months minimum)

---

## 5. Integration Requirements

### 5.1 Sage Evolution
- Import: Valuation reports
- Export: Stocktake results
- Format: Excel/CSV
- Fields: Product code, Barcode, Description, Quantity, Cost, Total valuation

### 5.2 ERP Systems
- Generic import from Excel/CSV
- Field mapping capability
- Data transformation
- Validation rules

### 5.3 External Systems (Future)
- API endpoints for third-party integration
- Webhook support
- Batch import/export

---

## 6. Constraints

### 6.1 Technical Constraints
- Must use PostgreSQL
- Must support offline-first Android app
- Must use environment variables for credentials
- No hardcoded credentials in source code

### 6.2 Business Constraints
- Budget considerations
- Timeline constraints
- Resource availability
- Training requirements

### 6.3 Regulatory Constraints
- Data protection compliance
- Audit trail requirements
- Security standards

---

## 7. Assumptions

- Users have smartphones with cameras
- Internet connectivity available (but not guaranteed)
- PostgreSQL server available
- Android devices support required APIs
- Users have basic technical literacy

---

## 8. Dependencies

- PostgreSQL database server
- Android development environment
- Web browser for dashboard
- Network connectivity for sync
- Barcode scanning library

---

## 9. Success Criteria

- 100+ simultaneous users supported
- < 1 second barcode scan time
- < 5 second sync time
- 99.9% system uptime
- Zero data loss in offline mode
- User training time < 2 hours
- Stocktake accuracy > 95%

---

## 10. Risks (Initial Assessment)

- Network connectivity issues for mobile users
- Barcode scanning accuracy
- Data synchronization conflicts
- User adoption resistance
- Performance at scale
- Security vulnerabilities
- Integration complexity with Sage Evolution

---

## Document Version
- Version: 1.0
- Date: June 9, 2026
- Author: System Architecture Team
- Status: Approved
