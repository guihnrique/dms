# DMS Backend - Auth Security Foundation

Backend implementation following TDD (Test-Driven Development) methodology.

## Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Setup PostgreSQL Database

```bash
# Create development database
createdb dms

# Create test database
createdb test_dms

# Run migrations
psql -d dms -f migrations/001_create_auth_tables.sql
psql -d test_dms -f migrations/001_create_auth_tables.sql
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/integration/test_database_schema.py
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Run Single Test
```bash
pytest tests/integration/test_database_schema.py::test_users_table_exists -v
```

## TDD Workflow

**Task 1.1** - Database Schema (Current)

🔴 **RED**: Tests written in `tests/integration/test_database_schema.py` (currently failing)

🟢 **GREEN**: Run migration `001_create_auth_tables.sql` to make tests pass

🔵 **REFACTOR**: Improve schema if needed while keeping tests green

## Project Structure

```
backend/
├── app/
│   ├── models/         # SQLAlchemy models
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic
│   ├── routers/        # API endpoints
│   └── middleware/     # Auth, CORS, rate limiting
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── fixtures/      # Test data factories
├── migrations/        # SQL migrations
├── requirements.txt
└── pytest.ini
```

## Next Steps

- Task 1.2: Create SQLAlchemy User model
- Task 1.3: Create auth_audit_log model
- Task 2.1: Implement password hashing service
