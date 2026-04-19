<#
.SYNOPSIS
    Nova Windows bootstrap script.
    Called by the Inno Setup installer's [Run] section, or can be run
    standalone by a user who wants to install Nova without the .exe wrapper.

.DESCRIPTION
    This script:
      1. Checks for Python >= 3.10 (offers to install via winget if missing)
      2. Checks for Ollama (offers to install via winget if missing)
      3. Creates a Python venv inside the Nova install directory
      4. Installs Nova via pip install -e .
      5. Pulls the default Ollama model
      6. Creates a Start Menu shortcut
      7. Launches Nova

    Designed to be idempotent — safe to re-run if a step was interrupted.

.PARAMETER InstallDir
    Root of the Nova installation (where the repo was cloned/extracted).
    Defaults to the parent of this script's directory.

.PARAMETER SkipModel
    Skip the Ollama model pull (useful for offline installs where the
    model will be sideloaded later).

.PARAMETER NoLaunch
    Don't start Nova after installation.

.PARAMETER NonInteractive
    Auto-accept all prompts (used when called from the Inno Setup
    installer with runhidden — Read-Host would hang in a hidden window).
#>
param(
    [string]$InstallDir = "",
    [switch]$SkipModel,
    [switch]$NoLaunch,
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"

function Invoke-ExternalStep {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Description,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command,
        [switch]$AllowFailure
    )

    & $Command
    $exitCode = $LASTEXITCODE
    if ($null -eq $exitCode) {
        $exitCode = 0
    }

    if ($exitCode -ne 0) {
        if ($AllowFailure) {
            Write-Host "       WARNING: $Description failed (exit code $exitCode)." -ForegroundColor Yellow
        } else {
            Write-Host "       ERROR: $Description failed (exit code $exitCode)." -ForegroundColor Red
            exit $exitCode
        }
    }
}

# ------------------------------------------------------------------
# Logging — write transcript so failures are diagnosable
# ------------------------------------------------------------------
$LogFile = Join-Path (if ($InstallDir) { $InstallDir } else { $PSScriptRoot }) "bootstrap.log"
try { Start-Transcript -Path $LogFile -Append -Force } catch { }

# ------------------------------------------------------------------
# Resolve install directory
# ------------------------------------------------------------------
if (-not $InstallDir) {
    $InstallDir = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}
$BackendDir = Join-Path $InstallDir "nova_backend"
$VenvDir = Join-Path $BackendDir "venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$NovaStart = Join-Path $VenvDir "Scripts\nova-start.exe"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Nova — Windows Installer Bootstrap" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Install directory: $InstallDir"
Write-Host ""

# ------------------------------------------------------------------
# Step 1: Python
# ------------------------------------------------------------------
Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow

$pythonCmd = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 10) {
                $pythonCmd = $candidate
                Write-Host "       Found: $ver" -ForegroundColor Green
                break
            }
        }
    } catch { }
}

if (-not $pythonCmd) {
    Write-Host "       Python >= 3.10 not found." -ForegroundColor Red

    # Try bundled Python installer first (ships inside the Nova installer)
    $bundledInstaller = Join-Path $InstallDir "installer\windows\deps\python-3.12.8-amd64.exe"
    $useBundled = Test-Path $bundledInstaller

    if ($useBundled) {
        Write-Host "       Installing Python 3.12 from bundled installer..." -ForegroundColor Yellow
        # /quiet = silent, InstallAllUsers=1 = machine-wide, PrependPath=1 = add to PATH
        $proc = Start-Process -FilePath $bundledInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait -PassThru
        if ($proc.ExitCode -ne 0) {
            Write-Host "       ERROR: Python installation failed (exit code $($proc.ExitCode))." -ForegroundColor Red
            exit 1
        }
        Write-Host "       Python 3.12 installed." -ForegroundColor Green
    } else {
        # Fallback: try winget
        $wingetAvailable = $false
        try { $null = Get-Command winget -ErrorAction Stop; $wingetAvailable = $true } catch { }
        if ($wingetAvailable) {
            if ($NonInteractive) { $install = "Y" } else { $install = Read-Host "       Install Python via winget? (Y/n)" }
            if ($install -ne "n") {
                winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "       ERROR: Python installation via winget failed (exit code $LASTEXITCODE)." -ForegroundColor Red
                    exit 1
                }
            } else {
                Write-Host "       ERROR: Python is required. Install from https://python.org" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "       ERROR: Python is required and no installer is available." -ForegroundColor Red
            Write-Host "       Install Python 3.10+ from https://python.org and re-run this script." -ForegroundColor Red
            exit 1
        }
    }

    # Refresh PATH so we can find the newly installed Python
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    foreach ($candidate in @("python", "python3", "py")) {
        try {
            $ver = & $candidate --version 2>&1
            if ($ver -match "Python 3\.(\d+)") {
                $minor = [int]$Matches[1]
                if ($minor -ge 10) {
                    $pythonCmd = $candidate
                    Write-Host "       Found: $ver" -ForegroundColor Green
                    break
                }
            }
        } catch { }
    }
    if (-not $pythonCmd) {
        Write-Host "       ERROR: Python was installed but could not be found on PATH." -ForegroundColor Red
        Write-Host "       Try restarting your computer, then re-run this script." -ForegroundColor Red
        exit 1
    }
}

# ------------------------------------------------------------------
# Step 2: Ollama
# ------------------------------------------------------------------
Write-Host "[2/6] Checking Ollama..." -ForegroundColor Yellow

$ollamaFound = $false
try {
    $null = & ollama --version 2>&1
    $ollamaFound = $true
    Write-Host "       Found Ollama." -ForegroundColor Green
} catch { }

if (-not $ollamaFound) {
    Write-Host "       Ollama not found." -ForegroundColor Red
    if ($NonInteractive) { $install = "Y" } else { $install = Read-Host "       Install Ollama via winget? (Y/n)" }
    if ($install -ne "n") {
        winget install Ollama.Ollama --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -ne 0) {
            Write-Host "       WARNING: Ollama installation failed (exit code $LASTEXITCODE)." -ForegroundColor Yellow
            Write-Host "       LLM features will not work until Ollama is installed manually." -ForegroundColor Yellow
        } else {
            Write-Host "       Ollama installed." -ForegroundColor Green
        }
    } else {
        Write-Host "       WARNING: Without Ollama, Nova's LLM features won't work." -ForegroundColor Yellow
    }
}

# ------------------------------------------------------------------
# Step 3: Virtual environment
# ------------------------------------------------------------------
Write-Host "[3/6] Setting up Python virtual environment..." -ForegroundColor Yellow

if (-not (Test-Path $VenvPython)) {
    Invoke-ExternalStep -Description "virtual environment creation" -Command { & $pythonCmd -m venv $VenvDir }
    Write-Host "       Created venv at $VenvDir" -ForegroundColor Green
} else {
    Write-Host "       Venv already exists." -ForegroundColor Green
}

# ------------------------------------------------------------------
# Step 4: Install Nova
# ------------------------------------------------------------------
Write-Host "[4/6] Installing Nova (pip install -e .)..." -ForegroundColor Yellow

Invoke-ExternalStep -Description "pip upgrade" -Command { & $VenvPython -m pip install --upgrade pip --quiet 2>&1 | Out-Null }
Invoke-ExternalStep -Description "Nova install (pip install -e .)" -Command { & $VenvPython -m pip install -e $InstallDir --quiet }
Write-Host "       Nova installed." -ForegroundColor Green

# Verify entry point
if (Test-Path $NovaStart) {
    Write-Host "       nova-start command: $NovaStart" -ForegroundColor Green
} else {
    Write-Host "       WARNING: nova-start not found at expected path." -ForegroundColor Yellow
}

# ------------------------------------------------------------------
# Step 5: Pull model
# ------------------------------------------------------------------
if (-not $SkipModel) {
    Write-Host "[5/6] Pulling default Ollama model..." -ForegroundColor Yellow
    Invoke-ExternalStep -Description "default model pull" -Command { & $VenvPython (Join-Path $InstallDir "scripts\fetch_models.py") } -AllowFailure
} else {
    Write-Host "[5/6] Skipping model pull (--SkipModel)." -ForegroundColor Yellow
}

# ------------------------------------------------------------------
# Step 6: Start Menu shortcut
# ------------------------------------------------------------------
Write-Host "[6/6] Creating Start Menu shortcut..." -ForegroundColor Yellow

$startMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Nova"
if (-not (Test-Path $startMenuDir)) {
    New-Item -ItemType Directory -Path $startMenuDir -Force | Out-Null
}

$shortcutPath = Join-Path $startMenuDir "Nova.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $VenvPython
$shortcut.Arguments = "`"$(Join-Path $InstallDir 'scripts\start_daemon.py')`""
$shortcut.WorkingDirectory = $InstallDir
$shortcut.Description = "Launch Nova — Your Local Intelligence System"
$shortcut.IconLocation = "$InstallDir\nova_backend\static\favicon.ico,0"
$shortcut.Save()

Write-Host "       Shortcut created: $shortcutPath" -ForegroundColor Green

# ------------------------------------------------------------------
# Launch
# ------------------------------------------------------------------
if (-not $NoLaunch) {
    Write-Host ""
    Write-Host "Starting Nova..." -ForegroundColor Cyan
    Invoke-ExternalStep -Description "Nova startup" -Command { & $VenvPython (Join-Path $InstallDir "scripts\start_daemon.py") }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Nova installation complete!" -ForegroundColor Cyan
Write-Host "  Open http://localhost:8000 in your browser" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

try { Stop-Transcript } catch { }
