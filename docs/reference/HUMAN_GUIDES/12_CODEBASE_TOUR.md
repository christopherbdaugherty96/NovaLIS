# Codebase Tour
Updated: 2026-04-20

## Purpose
This guide explains the shape of the repository in plain language.

It is the fastest way to understand where things live before opening code files.

## Top-Level Repository Areas

### `README.md`
The plain-language front door for the whole project.

### `REPO_MAP.md`
The engineer/reviewer map that points people into the right parts of the repository.

### `docs/`
The full documentation system.
This includes:
- human guides
- runtime truth
- design docs
- proof packets
- canonical governance material

### `installer/`
The Windows installer path, bootstrap script, and packaging assets.
This is real repo surface today, but installer validation is still open rather than fully closed.

### `nova_backend/`
The live backend runtime.
This is where the governor path, executors, cognition, voice, memory, and tests live.

### `Nova-Frontend-Dashboard/`
A maintained mirror copy of the frontend.
The runtime-served canonical frontend lives in `nova_backend/static/`.

### `installer/`
Windows installer assets, bootstrap script, and end-user install documentation.
The installer is built but still in validation — not yet closed for non-developer use.

### `scripts/`
Utility scripts for runtime docs, checks, and other project maintenance tasks.

## Inside `nova_backend/`

### `src/`
The main backend code.
This is the most important source directory in the project.

### `tests/`
The main automated validation surface.
This includes governance tests, executor tests, and phase-specific tests.

### `static/`
The runtime-served frontend files.
This is the browser UI Nova actually uses at runtime.
The frontend is modular: `dashboard.js` (shared shell/state), `dashboard-chat-news.js`, `dashboard-control-center.js`, `dashboard-workspace.js`, `dashboard-config.js`, `style.phase1.css`, and `dashboard-surfaces.css`.

### `models/`
Local model-related assets or configuration surfaces.

### `tools/`
Supporting runtime tools, such as local bundled utilities.

### `memory/`
Persistent memory storage area related to governed memory.

## Inside `nova_backend/src/`
The source tree is organized by responsibility.

Some of the most important directories are:
- `api/`
- `governor/`
- `executors/`
- `conversation/`
- `openclaw/`
- `settings/`
- `skills/`
- `websocket/`
- `working_context/`
- `memory/`
- `perception/`
- `personality/`
- `providers/`
- `ledger/`
- `rendering/`
- `voice/`

## Fastest Review Path
If you want the quickest useful understanding of the codebase, a good order is:
1. human guides
2. runtime truth docs
3. `brain_server.py`
4. `src/websocket/`
5. `src/governor/`
6. `src/executors/`
7. `src/openclaw/`
8. `src/working_context/`
9. `src/memory/`
10. `src/personality/`
11. tests

## What This Repository Is Trying To Be
The repo is not organized like a simple chat app.
It is organized like a governed system with separate layers for:
- execution authority
- cognitive analysis
- perception/context
- continuity/memory
- user experience

That separation is one of the defining traits of Nova.
