@echo off
setlocal enabledelayedexpansion enableextensions

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%nova_backend"
set "PID_DIR=%ROOT_DIR%scripts\pids"
set "PID_FILE=%PID_DIR%\nova_backend.pid"
set "OUT_LOG=%PID_DIR%\nova_backend.out.log"
set "ERR_LOG=%PID_DIR%\nova_backend.err.log"
set "DASHBOARD_URL=http://127.0.0.1:8000"

if not exist "%BACKEND_DIR%" (
  echo [Nova] Missing backend directory: "%BACKEND_DIR%"
  exit /b 1
)

if not exist "%PID_DIR%" (
  mkdir "%PID_DIR%" >nul 2>&1
)

rem -- Load .env if present (skip comments and blank lines) --
if exist "%BACKEND_DIR%\.env" (
  echo [Nova] Loading environment from .env...
  for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%BACKEND_DIR%\.env") do (
    set "ENVKEY=%%A"
    set "ENVVAL=%%B"
    if defined ENVKEY if defined ENVVAL (
      set "ENVKEY=!ENVKEY: =!"
      if not "!ENVKEY!"=="" (
        set "!ENVKEY!=!ENVVAL!"
      )
    )
  )
)

set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  set "PYTHON_EXE=python"
)

if exist "%PID_FILE%" (
  for /f "usebackq delims=" %%P in ("%PID_FILE%") do set "NOVA_PID=%%P"
  if defined NOVA_PID (
    powershell -NoProfile -Command "if (Get-Process -Id %NOVA_PID% -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
    if not errorlevel 1 (
      powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$ready = $false; " ^
        "for ($i = 0; $i -lt 6; $i++) { " ^
        "  if (-not (Get-Process -Id %NOVA_PID% -ErrorAction SilentlyContinue)) { exit 4 }; " ^
        "  try { $resp = Invoke-WebRequest -UseBasicParsing '%DASHBOARD_URL%/phase-status' -TimeoutSec 2; if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300) { $ready = $true; break } } catch { }; " ^
        "  Start-Sleep -Milliseconds 500; " ^
        "} " ^
        "if ($ready) { exit 0 } else { exit 5 }"
      if not errorlevel 1 (
        echo [Nova] Backend already running (PID %NOVA_PID%).
        start "" "%DASHBOARD_URL%"
        exit /b 0
      )
      echo [Nova] Existing backend process (PID %NOVA_PID%) is running but not ready.
      echo [Nova] Check logs:
      echo [Nova]   stdout: %OUT_LOG%
      echo [Nova]   stderr: %ERR_LOG%
      exit /b 1
    )
  )
)

echo [Nova] Starting backend...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p = Start-Process -FilePath '%PYTHON_EXE%' -ArgumentList '-m','uvicorn','src.brain_server:app','--host','127.0.0.1','--port','8000' -WorkingDirectory '%BACKEND_DIR%' -RedirectStandardOutput '%OUT_LOG%' -RedirectStandardError '%ERR_LOG%' -PassThru -WindowStyle Hidden; Set-Content -Path '%PID_FILE%' -Value $p.Id"

if errorlevel 1 (
  echo [Nova] Failed to start backend.
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$pid = (Get-Content -Path '%PID_FILE%' -ErrorAction SilentlyContinue | Select-Object -First 1); " ^
  "if (-not $pid) { exit 3 }; " ^
  "$ready = $false; " ^
  "for ($i = 0; $i -lt 20; $i++) { " ^
  "  if (-not (Get-Process -Id $pid -ErrorAction SilentlyContinue)) { exit 4 }; " ^
  "  try { $resp = Invoke-WebRequest -UseBasicParsing '%DASHBOARD_URL%/phase-status' -TimeoutSec 2; if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300) { $ready = $true; break } } catch { }; " ^
  "  Start-Sleep -Milliseconds 500; " ^
  "} " ^
  "if ($ready) { exit 0 } else { exit 5 }"

set "START_STATUS=%ERRORLEVEL%"
if not "%START_STATUS%"=="0" (
  if "%START_STATUS%"=="4" (
    echo [Nova] Backend process exited before readiness completed.
  ) else (
    echo [Nova] Backend did not become ready at %DASHBOARD_URL%/phase-status.
  )
  echo [Nova] Check logs:
  echo [Nova]   stdout: %OUT_LOG%
  echo [Nova]   stderr: %ERR_LOG%
  exit /b 1
)

echo [Nova] Backend started.
echo [Nova] Dashboard:       %DASHBOARD_URL%
echo [Nova] Bridge endpoint: http://127.0.0.1:8000/api/openclaw/bridge/message
start "" "%DASHBOARD_URL%"
exit /b 0
