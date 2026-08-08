# ZivaStock PostgreSQL Backup Script (Windows PowerShell)
# Creates timestamped backups in ../backups/

param(
    [string]$EnvFile = "..\.env",
    [string]$BackupDir = "..\backups"
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
$BackupDir = Join-Path $root (Resolve-Path -Relative -Path $BackupDir).Path.TrimStart('.\')

$DB_HOST = Get-EnvValue -Key "DB_HOST" -FilePath $envPath
$DB_PORT = Get-EnvValue -Key "DB_PORT" -FilePath $envPath
$DB_NAME = Get-EnvValue -Key "DB_NAME" -FilePath $envPath
$DB_USER = Get-EnvValue -Key "DB_USER" -FilePath $envPath
$DB_PASSWORD = Get-EnvValue -Key "DB_PASSWORD" -FilePath $envPath

$env:PGPASSWORD = $DB_PASSWORD

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupDir "zivastock_${DB_NAME}_${timestamp}.sql"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

Write-Host "Backing up database $DB_NAME to $backupFile" -ForegroundColor Cyan
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -F p -f $backupFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup completed successfully: $backupFile" -ForegroundColor Green
} else {
    Write-Error "Backup failed."
}
