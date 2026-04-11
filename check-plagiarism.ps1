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
$venvPython = Join-Path $root "backend\.venv\Scripts\python.exe"
$pythonCmd = $null
if (Test-Path $venvPython) {
  $pythonCmd = @{ Source = $venvPython }
} else {
  $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
}

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
  # Use default reporters for portability across jscpd versions.
  & $jscpdCmd.Source "$root" --output "$jscpdOut"
  if ($LASTEXITCODE -eq 0) {
    Write-Ok "jscpd scan completed"
  } else {
    Write-Warn "jscpd exited with code $LASTEXITCODE"
  }
} else {
  Write-Warn "Skipping jscpd (not installed). Install: npm install -g jscpd"
}

Write-Step "Running copydetect (Python backend)"
if ($pythonCmd) {
  # Check install via pip metadata to avoid traceback noise.
  $oldErr = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  & $pythonCmd.Source -m pip show copydetect *> $null
  $copydetectInstalled = ($LASTEXITCODE -eq 0)
  $ErrorActionPreference = $oldErr

  if (-not $copydetectInstalled) {
    Write-Warn "copydetect not installed. Install with: python -m pip install copydetect"
  } else {
    $backendAppPath = Join-Path $root "backend\app"
    $backendTestsPath = Join-Path $root "backend\tests"
    $copydetectReport = Join-Path $copydetectOut "copydetect_report.html"

    $ErrorActionPreference = "Continue"
    # Scan only authored source + tests (avoid backend/.venv and other large runtime folders).
    & $pythonCmd.Source -m copydetect -t "$backendAppPath" "$backendTestsPath" -e py -O "$copydetectReport"
    $copydetectExit = $LASTEXITCODE
    $ErrorActionPreference = $oldErr

    if ($copydetectExit -eq 0) {
      Write-Ok "copydetect report generated"
    } else {
      Write-Warn "copydetect exited with code $copydetectExit"
    }
  }
} else {
  Write-Warn "Skipping copydetect (python not found)."
}

Write-Info "Done. Open reports under: $reportRoot"





