#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Cipher Oracle - Run backend and frontend in parallel

.DESCRIPTION
    Starts both FastAPI backend and Vite frontend in background jobs,
    opens browser, and displays logs.

.EXAMPLE
    .\run-dev.ps1
#>

param()

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

# Get project root
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

Write-Header "Cipher Oracle Dev Server"

# Check if setup has been run
$venvPath = Join-Path $backendDir ".venv"
$nodeModules = Join-Path $frontendDir "node_modules"

if (-not (Test-Path $venvPath) -or -not (Test-Path $nodeModules)) {
    Write-Host "⚠️  Setup not complete. Run '.\start.ps1' first.`n" -ForegroundColor Yellow
    & $PSScriptRoot\start.ps1
}

Write-Host "Starting backend and frontend services...`n" -ForegroundColor Yellow

# Start backend in background
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & ".\\.venv\\Scripts\\Activate.ps1"
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
} -ArgumentList $backendDir -Name "CipherOracle-Backend"

Write-Success "Backend started (Job: $($backendJob.Id))"

# Start frontend in background
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npx vite --host=127.0.0.1 --port=5173
} -ArgumentList $frontendDir -Name "CipherOracle-Frontend"

Write-Success "Frontend started (Job: $($frontendJob.Id))"

# Wait for services to start
Write-Host "`nWaiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Try to open browser
try {
    Start-Process "http://127.0.0.1:5173"
    Write-Success "Opened browser"
} catch {
    Write-Host "⚠️  Could not open browser. Visit http://127.0.0.1:5173 manually." -ForegroundColor Yellow
}

Write-Header "Services Running"

Write-Host @"
Frontend: http://127.0.0.1:5173
Backend:  http://127.0.0.1:8000
Docs:     http://127.0.0.1:8000/docs

Background jobs:
  Backend:  $($backendJob.Name) (ID: $($backendJob.Id))
  Frontend: $($frontendJob.Name) (ID: $($frontendJob.Id))

To view logs:
  Get-Job | Receive-Job -Keep

To stop:
  Get-Job | Stop-Job
  Get-Job | Remove-Job

Press Ctrl+C to exit this script (services will continue running).
"@ -ForegroundColor Green

# Keep script running and display job updates
while ($true) {
    Start-Sleep -Seconds 5

    # Check if jobs are still running
    $backendRunning = Get-Job -Id $backendJob.Id -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Running" }
    $frontendRunning = Get-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Running" }

    if (-not $backendRunning) {
        Write-Host "⚠️  Backend stopped unexpectedly" -ForegroundColor Red
    }

    if (-not $frontendRunning) {
        Write-Host "⚠️  Frontend stopped unexpectedly" -ForegroundColor Red
    }

    if (-not $backendRunning -and -not $frontendRunning) {
        Write-Host "Both services stopped. Exiting..." -ForegroundColor Red
        break
    }
}

