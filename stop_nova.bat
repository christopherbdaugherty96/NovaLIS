@echo off
setlocal enableextensions

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%nova_backend"
set "STOP_SCRIPT=%ROOT_DIR%scripts\stop_daemon.py"

set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  set "PYTHON_EXE=python"
)

if not exist "%STOP_SCRIPT%" (
  echo [Nova] Missing stop script: "%STOP_SCRIPT%"
  exit /b 1
)

"%PYTHON_EXE%" "%STOP_SCRIPT%"
exit /b %ERRORLEVEL%
