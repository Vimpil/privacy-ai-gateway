#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Run local plagiarism/clone checks for Cipher Oracle.

.DESCRIPTION
  Runs:
    - jscpd (whole repository)
    - copydetect (backend Python code)

  Outputs reports into ./reports/plagiarism.

.EXAMPLE
  .\check-plagiarism.ps1

.EXAMPLE
  .\check-plagiarism.ps1 -ValidateOnly
#>

param(
  [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$reportRoot = Join-Path $root "reports\plagiarism"
$jscpdOut = Join-Path $reportRoot "jscpd"
$copydetectOut = Join-Path $reportRoot "copydetect"

function Write-Step {
  param([string]$Message)
  Write-Host "[STEP] $Message" -ForegroundColor Cyan
}

function Write-Info {
  param([string]$Message)
  Write-Host "[INFO] $Message" -ForegroundColor Yellow
}

function Write-Ok {
  param([string]$Message)
  Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warn {
  param([string]$Message)
  Write-Host "[WARN] $Message" -ForegroundColor Magenta
}

Write-Step "Preparing report directories"
New-Item -ItemType Directory -Path $reportRoot -Force | Out-Null
New-Item -ItemType Directory -Path $jscpdOut -Force | Out-Null
New-Item -ItemType Directory -Path $copydetectOut -Force | Out-Null
Write-Ok "Reports will be written to $reportRoot"

$jscpdCmd = Get-Command jscpd -ErrorAction SilentlyContinue
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if ($ValidateOnly) {
  Write-Step "Validate only"
  if ($jscpdCmd) {
    Write-Ok "Found jscpd: $($jscpdCmd.Source)"
  } else {
    Write-Warn "jscpd not found. Install with: npm install -g jscpd"
  }

  if ($pythonCmd) {
    Write-Ok "Found python: $($pythonCmd.Source)"
  } else {
    Write-Warn "python not found. Install Python to run copydetect checks."
  }

  Write-Info "Validation complete. No checks executed."
  exit 0
}

Write-Step "Running jscpd clone detection"
if ($jscpdCmd) {
  & $jscpdCmd.Source "$root" --reporters console,json --output "$jscpdOut"
  Write-Ok "jscpd report generated"
} else {
  Write-Warn "Skipping jscpd (not installed). Install: npm install -g jscpd"
}

Write-Step "Running copydetect (Python backend)"
if ($pythonCmd) {
  # Ensure copydetect is importable in current environment.
  & $pythonCmd.Source -c "import copydetect" 2>$null
  if ($LASTEXITCODE -ne 0) {
    Write-Warn "copydetect not installed. Install with: python -m pip install copydetect"
  } else {
    $backendPath = Join-Path $root "backend"
    $copydetectReport = Join-Path $copydetectOut "copydetect_report.html"
    & $pythonCmd.Source -m copydetect "$backendPath" --out-file "$copydetectReport"
    Write-Ok "copydetect report generated"
  }
} else {
  Write-Warn "Skipping copydetect (python not found)."
}

Write-Info "Done. Open reports under: $reportRoot"

