# Local Setup And Startup
Updated: 2026-04-20

## Purpose
This guide explains Nova's current local setup paths.

It is written for actual use, not for architectural review.

## Current Honest Setup Posture
For Windows end users, Nova now has a real installer path under `installer/`.
That installer path is not fully signed off yet because clean-VM validation is still open.

For source-based local setup, Nova has:
- packaging metadata in `pyproject.toml`
- a pinned base dependency file
- an optional wake-word dependency file
- startup scripts for Windows and Unix-like systems

That means the practical honest split is:
- installer path for intended non-developer Windows setup, still in validation
- source/manual path for developers and local operators who want to run Nova directly from the repo

## Installer Path (Windows)
If you are testing the Windows installer path, use:
- `installer/README.md`
- `installer/windows/nova_bootstrap.ps1`

Important truth:
- the installer path is real
- it is not yet fully closed as a finished install experience
- `C:\Program Files\Nova\bootstrap.log` is the main failure log when installer setup breaks
- installed code should live under `C:\Program Files\Nova`, but changing runtime state should live under `%LOCALAPPDATA%\Nova`

## Runtime State Location
Nova now separates code from mutable runtime state.

When Nova runs from a writable source checkout, such as `C:\Nova-Project`, it can keep runtime state with that checkout.

When Nova runs from a protected Windows install path, such as `C:\Program Files\Nova`, it should write mutable state under:
- `%LOCALAPPDATA%\Nova`

This includes:
- ledger entries
- model version lock state
- settings
- memory
- usage tracking
- profile state
- policy state
- notification schedules
- OpenClaw runtime state
- screen captures

Why this matters:
- Windows normally blocks regular user writes inside `C:\Program Files`
- Nova must not depend on write access to the installed-code directory
- model confirmation, memory, settings, and ledger writes must survive restart

## Source Install

The simplest current source install path is:

### 1. Create a virtual environment
Windows:
- `python -m venv .venv`

macOS/Linux:
- `python3 -m venv .venv`

### 2. Install Nova from the repo
Windows:
- `.venv\\Scripts\\python -m pip install -e .`

macOS/Linux:
- `.venv/bin/python -m pip install -e .`

### 3. Fetch local models
Windows:
- `.venv\\Scripts\\python scripts\\fetch_models.py`

macOS/Linux:
- `.venv/bin/python scripts/fetch_models.py`

### 4. Start Nova
Windows:
- `.venv\\Scripts\\nova-start`

macOS/Linux:
- `.venv/bin/nova-start`

This is the simplest source-based start path after `pip install -e .`.

If you prefer the repo startup scripts instead, note that they look first for:
- `nova_backend\\venv\\Scripts\\python.exe` on Windows
- `nova_backend/venv/bin/python` on macOS/Linux

If that backend-local venv does not exist, the scripts fall back to `python` or `python3` on PATH.

## Optional Pinned Requirements Path

The canonical pinned dependency file is:
- `nova_backend/requirements.txt`

If you want the direct requirements-based route instead of `pip install -e .`, use that file.
It stays aligned with the current live runtime surface.

## Optional Wake Word Install

Wake word is still planned, not live runtime truth.

If you want the optional dependency path available for future experimentation, use:
- `nova_backend/requirements-optional-wakeword.txt`

That file exists so Nova can stay honest:
- wake word is not part of the default install
- wake word does not pretend to be a live product surface

### Optional: install wake word dependencies later
Windows:
- `.venv\\Scripts\\python -m pip install -r nova_backend\\requirements-optional-wakeword.txt`

macOS/Linux:
- `.venv/bin/python -m pip install -r nova_backend/requirements-optional-wakeword.txt`

## Starting Nova

### Windows
Use:
- `start_nova.bat`

On Windows, `start_nova.bat` delegates to `scripts/start_daemon.py`.
That keeps startup behavior in one Python-owned path and avoids fragile batch
parsing of `.env` files.

### macOS/Linux
Use:
- `./start_nova.sh`

Both scripts:
- start the backend
- wait for `/phase-status`
- write logs to `scripts/pids/`
- open the dashboard URL when possible

## Stopping Nova

### Windows
Use:
- `stop_nova.bat`

### macOS/Linux
Use:
- `./stop_nova.sh`

## Logs And PID Files

Runtime logs and PID state live under:
- `scripts/pids/`

The main files are:
- `nova_backend.out.log`
- `nova_backend.err.log`
- `nova_backend.pid`
- `nova.log` when started through `scripts/start_daemon.py`

For installed Windows builds, also check:
- `%LOCALAPPDATA%\Nova\data\ledger.jsonl`
- `%LOCALAPPDATA%\Nova\models\current_model_hash.txt`

## Important Clarifications

### Wake word
Wake word is still:
- designed
- documented
- optional

It is not yet:
- active runtime truth
- part of the current base install promise

### Startup scripts
The scripts help with local startup, but they do not replace:
- model downloads
- OS-level audio permissions
- browser permissions
- any future connector/provider setup

They also do not mean the Windows installer flow is already fully validated.

## Best First Run
Once Nova is running:
1. open the dashboard
2. read the Introduction page
3. use the in-app Setup Readiness checklist on Intro or Settings
4. try `explain this`
5. open `Trust`
6. open `Settings`

That gives the clearest picture of what Nova can already do today.

## What The In-App Setup Surfaces Now Show
The dashboard itself now carries more of the setup burden instead of leaving it only in docs.

The Intro and Settings pages now show:
- current setup mode
- runtime connection readiness
- local model route readiness
- recommended voice-check status
- optional-provider and bridge status
- the next best setup action for the current device

That means a user should be able to tell:
- what is required right now
- what is only recommended
- what can stay optional until later
