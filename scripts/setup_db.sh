#!/bin/bash
# ZivaStock PostgreSQL Database Setup Script (Linux/macOS)
# Reads connection details from .env file in project root.

set -e

ENV_FILE="${1:-../.env}"
SKIP_SEED=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --skip-seed) SKIP_SEED=true ;;
        *) ENV_FILE="$1" ;;
    esac
    shift
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_PATH="$ROOT_DIR/.env"

if [ ! -f "$ENV_PATH" ]; then
    echo "ERROR: .env file not found at $ENV_PATH"
    exit 1
fi

get_env() {
    local key="$1"
    local value=$(grep -E "^\s*${key}\s*=" "$ENV_PATH" | head -n1 | cut -d'=' -f2-)
    echo "$value"
}

DB_HOST=$(get_env DB_HOST)
DB_PORT=$(get_env DB_PORT)
DB_NAME=$(get_env DB_NAME)
DB_USER=$(get_env DB_USER)
DB_PASSWORD=$(get_env DB_PASSWORD)

export PGPASSWORD="$DB_PASSWORD"

echo "Creating database $DB_NAME (if not exists)..."
DB_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" || true)

if [ "$DB_EXISTS" != "1" ]; then
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME WITH OWNER = $DB_USER ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE = template0;"
    echo "Database created."
else
    echo "Database already exists."
fi

echo "Applying schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$ROOT_DIR/database/01_create_schema.sql"

if [ "$SKIP_SEED" = false ]; then
    echo "Applying seed data..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$ROOT_DIR/database/02_seed_data.sql"
fi

echo "Applying views, procedures, and triggers..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$ROOT_DIR/database/03_views_procedures_triggers.sql"

echo "Database setup complete."
