@echo off
setlocal enableextensions

set "ROOT_DIR=%~dp0"
set "PID_FILE=%ROOT_DIR%scripts\pids\nova_backend.pid"

if not exist "%PID_FILE%" (
  echo [Nova] No backend PID file found.
  exit /b 0
)

for /f "usebackq delims=" %%P in ("%PID_FILE%") do set "NOVA_PID=%%P"

if not defined NOVA_PID (
  echo [Nova] PID file is empty. Cleaning up.
  del "%PID_FILE%" >nul 2>&1
  exit /b 0
)

echo [Nova] Stopping backend ^(PID %NOVA_PID%^)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Process -Id %NOVA_PID% -ErrorAction SilentlyContinue) { Stop-Process -Id %NOVA_PID% -Force; exit 0 } else { exit 0 }"

del "%PID_FILE%" >nul 2>&1
echo [Nova] Backend stopped.
exit /b 0
