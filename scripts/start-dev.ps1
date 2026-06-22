# Prisma AI — clean dev startup (kills stale servers, starts V2 backend + frontend)
$ErrorActionPreference = "SilentlyContinue"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

Write-Host "Stopping stale dev servers on ports 3000, 8080..."
foreach ($port in 3000, 8080) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object {
            if ($_ -gt 0) {
                taskkill /F /T /PID $_ 2>$null | Out-Null
            }
        }
}
Start-Sleep -Seconds 2

Write-Host "Starting V3 backend on http://127.0.0.1:8080 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Backend'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080"
) -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "Starting frontend on http://localhost:3000 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Frontend'; npm run dev"
) -WindowStyle Normal

Start-Sleep -Seconds 4
$health = Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -TimeoutSec 5
Write-Host "Backend: $($health.status) v$($health.version)"
Write-Host "Open http://localhost:3000 — upload a new dataset after each restart."
