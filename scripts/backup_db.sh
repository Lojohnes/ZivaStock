#!/bin/bash
# ZivaStock PostgreSQL Backup Script (Linux/macOS)
# Creates timestamped backups in ../backups/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${1:-$ROOT_DIR/.env}"
BACKUP_DIR="${2:-$ROOT_DIR/backups}"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env file not found at $ENV_FILE"
    exit 1
fi

get_env() {
    local key="$1"
    grep -E "^\s*${key}\s*=" "$ENV_FILE" | head -n1 | cut -d'=' -f2-
}

DB_HOST=$(get_env DB_HOST)
DB_PORT=$(get_env DB_PORT)
DB_NAME=$(get_env DB_NAME)
DB_USER=$(get_env DB_USER)
DB_PASSWORD=$(get_env DB_PASSWORD)

export PGPASSWORD="$DB_PASSWORD"

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/zivastock_${DB_NAME}_${TIMESTAMP}.sql"

echo "Backing up database $DB_NAME to $BACKUP_FILE"
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F p -f "$BACKUP_FILE"

echo "Backup completed successfully: $BACKUP_FILE"
