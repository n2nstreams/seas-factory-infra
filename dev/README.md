# Local Development Environment

This directory contains Docker configuration for local development.

## Quick Start

```bash
# Start the development environment
make dev-up

# Stop the development environment
make dev-down
```

## Services

- **PostgreSQL 15** with pgvector extension
  - Host: localhost
  - Port: 5432
  - Database: factorydb
  - Username: factoryadmin
  - Password: localpass
  - Connection String: `postgresql://factoryadmin:localpass@localhost:5432/factorydb`

- **Adminer** (Database Admin UI)
  - URL: http://localhost:8080
  - Login with the PostgreSQL credentials above

## pgvector Extension

The pgvector extension is automatically installed and ready to use. You can verify it's working by connecting to the database and running:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## Development Workflow

1. Start the environment: `make dev-up`
2. Develop your application using the database connection string above
3. Use Adminer at http://localhost:8080 to inspect the database
4. Stop the environment when done: `make dev-down`

## Pre-commit Hooks (Optional)

Install pre-commit hooks to ensure code quality:

```bash
pip install pre-commit
pre-commit install
```

This will run code formatting and linting checks before each commit. 