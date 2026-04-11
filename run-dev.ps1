#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Cipher Oracle - Run backend and frontend in parallel.

.DESCRIPTION
    Starts FastAPI backend and Vite frontend in background jobs.

.PARAMETER NoBrowser
    Skip opening the browser automatically.

.PARAMETER ValidateOnly
    Validate script wiring and exit without launching processes.
#>

param(
    [switch]$NoBrowser,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

Write-Header "Cipher Oracle Dev Server"

$venvPath = Join-Path $backendDir ".venv"
$nodeModules = Join-Path $frontendDir "node_modules"

if ($ValidateOnly) {
    Write-Success "ValidateOnly mode: script parsed and paths resolved."
    Write-Host "projectRoot: $projectRoot"
    Write-Host "backendDir : $backendDir"
    Write-Host "frontendDir: $frontendDir"
    exit 0
}

if (-not (Test-Path $venvPath) -or -not (Test-Path $nodeModules)) {
    Write-Warn "Setup not complete. Running .\\start.ps1 first."
    & "$PSScriptRoot\start.ps1"
}

Write-Host "Starting backend and frontend services..." -ForegroundColor Yellow

$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & ".\\.venv\\Scripts\\Activate.ps1"
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
} -ArgumentList $backendDir -Name "CipherOracle-Backend"

Write-Success "Backend started (Job ID: $($backendJob.Id))"

$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npx vite --host=127.0.0.1 --port=5173
} -ArgumentList $frontendDir -Name "CipherOracle-Frontend"

Write-Success "Frontend started (Job ID: $($frontendJob.Id))"

Start-Sleep -Seconds 3

if (-not $NoBrowser) {
    try {
        Start-Process "http://127.0.0.1:5173"
        Write-Success "Opened browser at http://127.0.0.1:5173"
    }
    catch {
        Write-Warn "Could not open browser automatically. Open http://127.0.0.1:5173 manually."
    }
}

Write-Header "Services Running"
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "Backend : http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Docs    : http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Background jobs:" -ForegroundColor Green
Write-Host "  Backend : $($backendJob.Name) (ID: $($backendJob.Id))"
Write-Host "  Frontend: $($frontendJob.Name) (ID: $($frontendJob.Id))"
Write-Host ""
Write-Host "To view logs: Get-Job | Receive-Job -Keep"
Write-Host "To stop all : Get-Job | Stop-Job; Get-Job | Remove-Job"
Write-Host ""

while ($true) {
    Start-Sleep -Seconds 5

    $backendRunning = Get-Job -Id $backendJob.Id -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Running' }
    $frontendRunning = Get-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Running' }

    if (-not $backendRunning) {
        Write-Warn "Backend stopped unexpectedly."
    }

    if (-not $frontendRunning) {
        Write-Warn "Frontend stopped unexpectedly."
    }

    if (-not $backendRunning -and -not $frontendRunning) {
        Write-Host "Both services stopped. Exiting monitor loop." -ForegroundColor Red
        break
    }
}
