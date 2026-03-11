@echo off
setlocal enableextensions

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

set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  set "PYTHON_EXE=python"
)

if exist "%PID_FILE%" (
  for /f "usebackq delims=" %%P in ("%PID_FILE%") do set "NOVA_PID=%%P"
  if defined NOVA_PID (
    powershell -NoProfile -Command "if (Get-Process -Id %NOVA_PID% -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
    if not errorlevel 1 (
      echo [Nova] Backend already running ^(PID %NOVA_PID%^).
      start "" "%DASHBOARD_URL%"
      exit /b 0
    )
  )
)

echo [Nova] Starting backend...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p = Start-Process -FilePath '%PYTHON_EXE%' -ArgumentList '-m','uvicorn','src.brain_server:app','--host','127.0.0.1','--port','8000' -WorkingDirectory '%BACKEND_DIR%' -RedirectStandardOutput '%OUT_LOG%' -RedirectStandardError '%ERR_LOG%' -PassThru; Set-Content -Path '%PID_FILE%' -Value $p.Id"

if errorlevel 1 (
  echo [Nova] Failed to start backend.
  exit /b 1
)

timeout /t 2 >nul
echo [Nova] Backend started.
echo [Nova] Dashboard: %DASHBOARD_URL%
start "" "%DASHBOARD_URL%"
exit /b 0
