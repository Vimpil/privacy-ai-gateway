#!/usr/bin/env pwsh
# Cipher Oracle Startup Script
# Usage: .\start.ps1 [-Run]
# Default behavior: setup only (does not start backend/frontend)
# Use -Run to launch dev servers after setup completes.

param(
    [switch]$Run
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

Write-Host "`n=== Cipher Oracle Setup ===" -ForegroundColor Cyan
Write-Host "Project root: $projectRoot`n"

# Setup environment files
Write-Host "=== Step 1: Environment Setup ===" -ForegroundColor Cyan
$backendEnv = Join-Path $backendDir ".env"
$backendEnvExample = Join-Path $backendDir ".env.example"
if (-not (Test-Path $backendEnv) -and (Test-Path $backendEnvExample)) {
    Copy-Item $backendEnvExample $backendEnv
    Write-Host "Created backend/.env" -ForegroundColor Green
}

$frontendEnv = Join-Path $frontendDir ".env"
$frontendEnvExample = Join-Path $frontendDir ".env.example"
if (-not (Test-Path $frontendEnv) -and (Test-Path $frontendEnvExample)) {
    Copy-Item $frontendEnvExample $frontendEnv
    Write-Host "Created frontend/.env" -ForegroundColor Green
}

# Setup backend
Write-Host "`n=== Step 2: Backend Setup ===" -ForegroundColor Cyan
Set-Location $backendDir

# Check Python
$pythonVersion = python --version 2>&1
Write-Host "Found $pythonVersion" -ForegroundColor Green

# Create venv if needed
$venvPath = Join-Path $backendDir ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate and install
& ".\\.venv\\Scripts\\Activate.ps1"
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt
Write-Host "Backend dependencies installed" -ForegroundColor Green

# Setup frontend
Write-Host "`n=== Step 3: Frontend Setup ===" -ForegroundColor Cyan
Set-Location $frontendDir

$nodeVersion = node --version
$npmVersion = npm --version
Write-Host "Found Node.js $nodeVersion, npm $npmVersion" -ForegroundColor Green

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..."
    npm install --silent
    Write-Host "Frontend dependencies installed" -ForegroundColor Green
}

# Done
Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host @"

Next steps:

1. Option A - Manual start (two terminals):
   Terminal 1 (Backend):
     cd backend
     .\.venv\Scripts\Activate.ps1
     python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

   Terminal 2 (Frontend):
     cd frontend
     npx vite --host=127.0.0.1 --port=5173

2. Option B - Parallel start:
   .\run-dev.ps1

3. Option C - Setup + start in one command:
   .\start.ps1 -Run

URLs:
  App:  http://127.0.0.1:5173
  API:  http://127.0.0.1:8000
  Docs: http://127.0.0.1:8000/docs
"@ -ForegroundColor White

if ($Run) {
    Write-Host "`nLaunching dev services via .\run-dev.ps1 ..." -ForegroundColor Cyan
    & "$PSScriptRoot\run-dev.ps1"
}

