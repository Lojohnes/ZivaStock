# ZivaStock Backend API

Enterprise-grade FastAPI backend for the ZivaStock multiuser stocktake system.

## Features

- RESTful API with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- Rate limiting
- Audit logging
- Offline-first sync support for mobile
- Comprehensive reporting
- Database migrations with Alembic

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0.23
- **Migrations**: Alembic 1.12.1
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Rate Limiting**: slowapi
- **Validation**: Pydantic 2.5.0

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Setup

1. **Clone the repository**
```bash
cd ZivaStock/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp ../.env.example .env
# Edit .env with your database credentials and settings
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Seed Data

Apply initial seed data (roles, admin user, locations, sections, products, sample session):

```bash
python seed_data.py
```

Default admin credentials: `admin@zivastock.com` / `admin123`

## Import / Syntax Check

Run a quick local import and syntax check without starting the server:

```bash
python check_imports.py
```

> Note: This requires the backend dependencies to be installed (`pip install -r requirements.txt`).

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

### View current version
```bash
alembic current
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── users.py         # User management endpoints
│   │       ├── products.py      # Product endpoints
│   │       ├── counts.py        # Stock count endpoints
│   │       ├── sessions.py      # Stocktake session endpoints
│   │       ├── sync.py          # Mobile sync endpoints
│   │       ├── reports.py       # Report generation endpoints
│   │       └── locations.py     # Location management endpoints
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database connection
│   │   └── security.py         # JWT and password hashing
│   ├── models/
│   │   ├── user.py             # User model
│   │   ├── role.py             # Role and permission models
│   │   ├── location.py         # Location, shelf, section models
│   │   ├── product.py          # Product model
│   │   ├── count.py            # Count and duplicate models
│   │   ├── session.py          # Stocktake session model
│   │   ├── audit.py            # Audit log model
│   │   ├── import_batch.py     # Import batch model
│   │   └── sync.py             # Sync queue and record models
│   ├── schemas/
│   │   ├── user.py             # User schemas
│   │   ├── role.py             # Role schemas
│   │   ├── product.py          # Product schemas
│   │   ├── location.py         # Location schemas
│   │   ├── count.py            # Count schemas
│   │   ├── session.py          # Session schemas
│   │   ├── audit.py            # Audit schemas
│   │   ├── sync.py             # Sync schemas
│   │   └── common.py           # Common schemas
│   ├── services/
│   │   ├── auth_service.py     # Authentication service
│   │   ├── user_service.py     # User service
│   │   ├── product_service.py  # Product service
│   │   ├── count_service.py    # Count service
│   │   ├── session_service.py  # Session service
│   │   ├── sync_service.py     # Sync service
│   │   ├── duplicate_service.py # Duplicate detection service
│   │   ├── report_service.py   # Report generation service
│   │   └── location_service.py # Location service
│   ├── middleware/
│   │   ├── auth.py             # Authentication middleware
│   │   ├── rate_limit.py       # Rate limiting middleware
│   │   └── audit.py            # Audit logging middleware
│   └── utils/                   # Utility functions
├── alembic/                     # Database migrations
│   ├── versions/
│   └── env.py
├── tests/                       # Test suite
├── scripts/                     # Utility scripts
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── alembic.ini                  # Alembic configuration
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

### Users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Products
- `POST /api/v1/products` - Create product
- `GET /api/v1/products` - List products
- `GET /api/v1/products/barcode/{barcode}` - Get product by barcode
- `GET /api/v1/products/{id}` - Get product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Counts
- `POST /api/v1/counts` - Create stock count
- `GET /api/v1/counts` - List counts
- `GET /api/v1/counts/{id}` - Get count
- `PUT /api/v1/counts/{id}` - Update count
- `DELETE /api/v1/counts/{id}` - Delete count

### Sessions
- `POST /api/v1/sessions` - Create stocktake session
- `GET /api/v1/sessions` - List sessions
- `GET /api/v1/sessions/{id}` - Get session
- `PUT /api/v1/sessions/{id}` - Update session
- `POST /api/v1/sessions/{id}/start` - Start session
- `POST /api/v1/sessions/{id}/pause` - Pause session
- `POST /api/v1/sessions/{id}/complete` - Complete session
- `POST /api/v1/sessions/{id}/archive` - Archive session

### Sync (Mobile)
- `POST /api/v1/sync/push` - Push counts from mobile
- `GET /api/v1/sync/pull` - Pull data to mobile
- `GET /api/v1/sync/status` - Get sync status

### Reports
- `GET /api/v1/reports/variance` - Variance report
- `GET /api/v1/reports/duplicates` - Duplicate report
- `GET /api/v1/reports/missing` - Missing stock report
- `GET /api/v1/reports/productivity` - User productivity report
- `GET /api/v1/reports/audit` - Audit trail report
- `GET /api/v1/reports/historical` - Historical stocktake report

### Locations
- `POST /api/v1/locations` - Create location
- `GET /api/v1/locations` - List locations
- `GET /api/v1/locations/tree` - Get location tree
- `POST /api/v1/shelves` - Create shelf
- `POST /api/v1/sections` - Create section

## Environment Variables

See `.env.example` for all available environment variables:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zivastockdb
DB_USER=postgres
DB_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=ZivaStock
DEBUG=True
ENVIRONMENT=development

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=100
```

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Role-based access control
- Rate limiting on all endpoints
- SQL injection prevention via ORM
- CORS configuration
- Audit logging for all actions

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Deployment

### Production Deployment

1. Set `DEBUG=False` and `ENVIRONMENT=production` in `.env`
2. Use a production WSGI server like Gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```
3. Configure nginx as reverse proxy
4. Enable HTTPS
5. Set up database backups
6. Configure monitoring and logging

### Docker Deployment

```bash
docker build -t zivastock-backend .
docker run -p 8000:8000 --env-file .env zivastock-backend
```

## Support

For issues and questions, please refer to the main project documentation.
