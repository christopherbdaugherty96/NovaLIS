@echo off
setlocal enableextensions

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%nova_backend"
set "START_SCRIPT=%ROOT_DIR%scripts\start_daemon.py"

set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  set "PYTHON_EXE=python"
)

if not exist "%START_SCRIPT%" (
  echo [Nova] Missing start script: "%START_SCRIPT%"
  exit /b 1
)

"%PYTHON_EXE%" "%START_SCRIPT%"
exit /b %ERRORLEVEL%
