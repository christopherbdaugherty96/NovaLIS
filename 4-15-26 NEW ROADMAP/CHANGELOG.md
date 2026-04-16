# Nova — Roadmap Execution Changelog

Rolling log of completed roadmap tasks. Newest at top. Keep entries short
and cite the commit hash(es) that delivered the work.

---

## 2026-04-16 — Third-pass review and hardening (Commit: `8c9e6f2`)
- Corrected capability count: 25 (not 26) across `ARCHITECTURE.md` and
  `MasterRoadMap.md`. Breakdown: 16 read-only + 6 local-device + 3
  persistent-change, zero external effects.
- `start_daemon.py`: Ollama health check now respects `OLLAMA_URL` env var
  instead of hardcoding `127.0.0.1:11434`.
- `fetch_models.py`: replaced substring tag match with exact first-column
  match to avoid false positives on partial model names.
- `nova_bootstrap.ps1`: added `$LASTEXITCODE` checks after `winget install`
  calls — Python failure now exits early, Ollama failure warns explicitly.

## 2026-04-16 — Test suite fixes (Commit: `7f3c574`)
- Fixed `workspace_api.py` `/landing` route: replaced removed `LANDING_HTML`
  reference with `LANDING_DIR / "index.html"`.
- Updated `test_landing_page.py` assertions to match rewritten README copy
  ("private, offline-capable AI assistant" vs old "Local-first AI").
- Updated `test_runtime_governance_docs.py`: `web_search.py` is now correctly
  included in the SKILL_SURFACE_MAP (runtime auditor added it; test was stale).
- Updated `test_brain_server_basic_conversation.py`: codebase summary assertion
  now matches new README paragraph ("private, offline-capable AI assistant").
- Result: full test suite 1100/1100 passing (previously 5 failures).

---

## 2026-04-16 — Second-pass review and fixes (Commit: `96244bc`)
- Created `nova_backend/static/favicon.ico` (16x16 "N" glyph) — unblocks
  Inno Setup .exe compilation.
- Added `-NonInteractive` switch to bootstrap; `.iss` now passes it so
  `Read-Host` cannot hang in a hidden window.
- Replaced `nova-start --help` probe in `start_daemon.py` with
  `shutil.which()` — prevents accidental server start during detection.
- Fixed CHANGELOG placeholder commit hashes; added landing page link to
  README; fixed `ARCHITECTURE.md` uvicorn command; removed dead
  `LANDING_HTML` constant; added News page support in simplified mode
  via `MutationObserver`.

---

## 2026-04-16 — Task 1.1: Windows installer scaffolding

### Task 1.1 — Windows installer (scaffolding DONE, validation pending)
- Commit: `53557cc`
- `installer/windows/nova_setup.iss` — Inno Setup 6 script. Copies source
  tree, runs bootstrap, creates Start Menu + desktop shortcuts, registers
  uninstaller. Outputs `dist/NovaSetup-0.1.0.exe`.
- `installer/windows/nova_bootstrap.ps1` — PowerShell script called by the
  installer (or standalone). Checks Python ≥3.10 and Ollama (offers winget
  install if missing), creates venv, runs `pip install -e .`, pulls default
  model, creates Start Menu shortcut, launches Nova.
- `scripts/fetch_models.py` — checks if the default Ollama model
  (`gemma4:e4b`) is present; pulls it if not. Idempotent.
- `scripts/start_daemon.py` — ensures Ollama is running, launches Nova as
  a background process (no console window on Windows), waits for health
  endpoint, opens browser.
- `installer/README.md` — user-facing install instructions (exe, bootstrap,
  manual).
- Pending: build actual .exe with Inno Setup Compiler, test on clean
  Windows VM (the Tier 1 acceptance criteria).

---

## 2026-04-16 — Tier 1 tasks 1.2, 1.3, 1.5 + doc additions (Commit: `7ad7e26`)

### Task 1.2 — README rewrite + INTRODUCTION + ARCHITECTURE (DONE)
- Rewrote `README.md` from 335-line technical doc to ~45-line non-technical
  landing with quickstart, roadmap links, and "learn more" pointers.
- Created `docs/INTRODUCTION.md` — governance philosophy, what Nova can/cannot
  do, privacy model, target audience. Written for non-engineers.
- Created `docs/ARCHITECTURE.md` — governance spine walkthrough, capability
  inventory, memory layer, ledger, runtime-doc drift check, dev workflow.

### Task 1.3 — UI overload reduction (DONE)
- Added `dashboard-simplified.css` + `dashboard-simplified.js` — new files,
  zero changes to existing JS logic.
- Default first-run: nav collapsed behind hamburger, 12 non-essential widgets
  hidden, token budget bar hidden.
- "Show full UI" toggle persists to `localStorage` so power users can opt out.
- Added `FIRST_RUN_DEFAULT_PROMPT: "Tell me the news"` to `dashboard-config.js`.

### Task 1.5 — Landing page with waitlist (DONE)
- Created `nova_backend/static/landing/` with `index.html`, `styles.css`,
  `script.js`. Dark-first, responsive, `prefers-color-scheme: light` support.
- Formspree integration with graceful fallback when endpoint not yet configured.
- Mounted at `/landing` in `brain_server.py` (`StaticFiles(html=True)`).
- Linked from README.
- Activation step: replace `REPLACE_WITH_REAL_ID` in `script.js` after
  signing up at formspree.io.

### Deep audit cleanup
- Commit: `9898477`
- Removed unverified "fail-silent memory search" claim from
  `DEEP_CODE_AUDIT.md`. Re-grepped `brain_server.py` — zero matches for
  "No memories", "vector_store", "memory_search", "fail.silent".

### New docs added by user (reorganization)
- `docs/future/NovaLIS Portfolio Upgrade Plan.txt` — portfolio packaging
  strategy (backlog, not active roadmap).
- `docs/future/OPENCLAW_INTEGRATION_DESIGN.md` — future OpenClaw integration
  design (cleaned escaped markdown from original draft).
- `docs/archive/openclawintergration.txt` — original OpenClaw draft (archived).
- Moved Phase 4 archive docs from `docs/CANONICAL/archive-phase4/` and
  `docs/archive/` into `docs/archive/phase 4/` subfolder.

---

## 2026-04-15 — Tier 1 foundation work

### Task 1.4 — `pyproject.toml` + CI (DONE)
- Commit: `0593b62`
- Added root `pyproject.toml` with:
  - `novalis` package, Python ≥ 3.10, dependencies pinned to match
    `nova_backend/requirements.txt`.
  - Console script `nova-start = "src.brain_server:main"`.
  - Optional `[dev]` extras (pytest, pytest-asyncio, ruff).
  - Minimal `ruff` and `pytest` configuration.
- Added `.github/workflows/ci.yml` — lint + pytest on push/PR, plus a
  smoke check that the `nova-start` entry point resolves.
- Verified locally: `pip install -e .` succeeds in existing venv,
  `nova-start.exe` is generated, `from src.brain_server import main`
  resolves to the new wrapper.
- Known gap: clean-venv verification and first CI run on a PR still
  pending (tracked in `NOW.md` §1.4 follow-ups).

### Task 1.4a — `main()` wrapper (DONE)
- Commit: `2105777`
- Appended 20-line `main()` + `if __name__ == "__main__":` guard to
  `nova_backend/src/brain_server.py`. Mirrors the `start_nova.bat/sh`
  invocation (`uvicorn src.brain_server:app` on 127.0.0.1:8000) with
  `NOVA_HOST` / `NOVA_PORT` env-var overrides.
- Unblocks Task 1.4 entry point.

### Task 1.0 — Preflight baseline (DONE)
- Commit: `3e4107a` (MOC refresh only)
- Ran runtime-doc generator; drift produced in `_MOCs/*` was committed
  as a separate refresh (indexed the new roadmap folder).
- Spot-ran `pytest nova_backend/tests/phase45/ -x -q` → 36/36 passed.
- Full backend pytest suite deferred to first CI run.

### Roadmap document corrections (DONE)
- Commit: `2ce9c8f`
- Removed fabricated line-range citation for "intent routing monolith"
  in `DEEP_CODE_AUDIT.md` (lines 2100-2190 hold schedule/clock parsing,
  not routing).
- Dropped reference to non-existent `nova_backend/src/api/routes/`.
- Reframed "26 read-only capabilities" as "20 read + 6 local-device
  controls; zero external writes" across `MasterRoadMap.md`.
- Added realistic cadence envelope (24-32 weeks at 2-4 hrs/week).

---

*Entries above are factual records of shipped work. Do not edit history
in place; append corrections as new dated entries.*
