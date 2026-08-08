# Start ZivaStock backend and frontend in separate CMD windows
$root = $PSScriptRoot
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"

# Stop any existing processes
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Start backend
Start-Process -FilePath "cmd.exe" -ArgumentList "/k python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory $backendDir

Start-Sleep -Seconds 3

# Start frontend
Start-Process -FilePath "cmd.exe" -ArgumentList "/k npm run dev" -WorkingDirectory $frontendDir

Write-Host "Backend and frontend are starting in separate CMD windows."
