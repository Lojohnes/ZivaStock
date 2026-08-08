# ZivaStock PostgreSQL Database Setup Script (Windows PowerShell)
# Reads connection details from .env file in project root.

param(
    [string]$EnvFile = "..\.env",
    [switch]$SkipSeed
)

$ErrorActionPreference = "Stop"

function Get-EnvValue {
    param([string]$Key, [string]$FilePath)
    $line = Get-Content $FilePath | Where-Object { $_ -match "^\s*$Key\s*=" }
    if (-not $line) { throw "Missing $Key in $FilePath" }
    return ($line -split "=", 2)[1].Trim()
}

$root = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $root ".env"

Write-Host "Loading environment from $envPath" -ForegroundColor Cyan

$DB_HOST = Get-EnvValue -Key "DB_HOST" -FilePath $envPath
$DB_PORT = Get-EnvValue -Key "DB_PORT" -FilePath $envPath
$DB_NAME = Get-EnvValue -Key "DB_NAME" -FilePath $envPath
$DB_USER = Get-EnvValue -Key "DB_USER" -FilePath $envPath
$DB_PASSWORD = Get-EnvValue -Key "DB_PASSWORD" -FilePath $envPath

$env:PGPASSWORD = $DB_PASSWORD

Write-Host "Creating database $DB_NAME (if not exists)..." -ForegroundColor Cyan
$exists = psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>$null
if ($exists -ne "1") {
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME WITH OWNER = $DB_USER ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE = template0;"
    Write-Host "Database created." -ForegroundColor Green
} else {
    Write-Host "Database already exists." -ForegroundColor Yellow
}

Write-Host "Applying schema..." -ForegroundColor Cyan
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$root\database\01_create_schema.sql"

if (-not $SkipSeed) {
    Write-Host "Applying seed data..." -ForegroundColor Cyan
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$root\database\02_seed_data.sql"
}

Write-Host "Applying views, procedures, and triggers..." -ForegroundColor Cyan
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$root\database\03_views_procedures_triggers.sql"

Write-Host "Database setup complete." -ForegroundColor Green
