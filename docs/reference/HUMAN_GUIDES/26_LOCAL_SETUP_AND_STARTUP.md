# Local Setup And Startup
Updated: 2026-03-26

## Purpose
This guide explains the simplest local setup path for Nova today.

It is written for actual use, not for architectural review.

## The Recommended Install Shape
Nova now has:
- a pinned base dependency file
- an optional wake-word dependency file
- startup scripts for Windows and Unix-like systems

That means the safest default install is now smaller and more honest than before.

## Base Install

The canonical base dependency file is:
- `nova_backend/requirements.txt`

This base install is for the current live runtime surface:
- chat
- trust/workspace/settings pages
- governed capabilities
- voice input/output
- screen/context features
- governed external reasoning

It does not pull in wake word by default.

## Optional Wake Word Install

Wake word is still planned, not live runtime truth.

If you want the optional dependency path available for future experimentation, use:
- `nova_backend/requirements-optional-wakeword.txt`

That file exists so Nova can stay honest:
- wake word is not part of the default install
- wake word does not pretend to be a live product surface

## Suggested Local Setup

### 1. Create a virtual environment
Windows:
- `python -m venv nova_backend\\venv`

macOS/Linux:
- `python3 -m venv nova_backend/venv`

### 2. Install the base runtime
Windows:
- `nova_backend\\venv\\Scripts\\python -m pip install -r nova_backend\\requirements.txt`

macOS/Linux:
- `nova_backend/venv/bin/python -m pip install -r nova_backend/requirements.txt`

### 3. Optional: install wake word dependencies later
Windows:
- `nova_backend\\venv\\Scripts\\python -m pip install -r nova_backend\\requirements-optional-wakeword.txt`

macOS/Linux:
- `nova_backend/venv/bin/python -m pip install -r nova_backend/requirements-optional-wakeword.txt`

## Starting Nova

### Windows
Use:
- `start_nova.bat`

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

## Best First Run
Once Nova is running:
1. open the dashboard
2. read the Introduction page
3. try `explain this`
4. open `Trust`
5. open `Settings`

That gives the clearest picture of what Nova can already do today.
