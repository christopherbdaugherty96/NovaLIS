# NOW.md – Current Sprint (Week 1-4)

**Sprint Goal:** Non‑developer installs and runs Nova in 5 minutes.

**Status:** INSTALLER BUILT — `dist/NovaSetup-0.1.0.exe` (214 MB) compiled successfully. Awaiting clean-VM validation.  
**Start Date:** 2026-04-15  
**Target End:** 2026-05-13 (4 weeks)

---

## Active Tasks (Tier 1)

### 1.1 One‑click installer
- [x] Windows `.exe` installer via Inno Setup (`installer/windows/nova_setup.iss`)
- [x] PowerShell bootstrap script (`installer/windows/nova_bootstrap.ps1`) — handles Python, Ollama, venv, pip install, model pull, Start Menu shortcut
- [x] Model fetch script (`scripts/fetch_models.py`) — checks Ollama, pulls default model (`gemma4:e4b`), idempotent
- [x] Daemon start script (`scripts/start_daemon.py`) — ensures Ollama serve, launches Nova background, waits for health, opens browser
- [ ] macOS `.app` bundle or `.pkg` (deferred — validate Windows first)
- [ ] **Test on clean Windows VM** (acceptance criteria: double-click → Nova running in ≤5 min, no terminal)
- [ ] Build and publish `NovaSetup-0.1.0.exe` to GitHub Releases

**Files:** `installer/windows/nova_setup.iss`, `installer/windows/nova_bootstrap.ps1`, `scripts/fetch_models.py`, `scripts/start_daemon.py`, `installer/README.md`  
**Estimate:** 400 lines — **landed ~500 lines across 5 files**

---

### 1.2 Simplify README + GitHub metadata
- [x] Rewrite README for non‑technical user (~45 lines, quickstart, roadmap links)
- [x] Remove outdated claims ("operator", "calm presence", "voice live")
- [x] Create `docs/INTRODUCTION.md` (governance philosophy, non‑technical)
- [x] Create `docs/ARCHITECTURE.md` (technical deep dive, governance spine, capability inventory)
- [ ] Add badges (blocked: CI billing lock on GitHub Actions)
- [ ] Add screenshot or demo GIF
- [ ] Update repo description and tags on GitHub

**Files:** `README.md`, `docs/INTRODUCTION.md`, `docs/ARCHITECTURE.md`  
**Estimate:** 200 lines — **landed ~250 lines across 3 files**

---

### 1.3 Reduce UI overload
- [x] Collapse navigation behind hamburger toggle by default (`dashboard-simplified.css` + `dashboard-simplified.js`)
- [x] Hide non‑essential widgets (weather, morning, search, hints, live-help, news, brief, home-launch, workspace-home, capability-surface, thread-map) behind `nova-simplified` body class
- [x] Hide token budget bar from main UI
- [x] Simplify first‑run experience (`FIRST_RUN_DEFAULT_PROMPT: "Tell me the news"` in config)
- [x] "Show full UI" toggle persists to localStorage so power users keep the old layout

**Files:** `nova_backend/static/index.html`, `nova_backend/static/dashboard-config.js`, `nova_backend/static/dashboard-simplified.css` (new), `nova_backend/static/dashboard-simplified.js` (new)  
**Estimate:** 150 lines — **landed ~180 lines across 4 files**

---

### 1.4 Add `pyproject.toml` + CI
- [x] **Prerequisite:** Add a `def main()` wrapper in `nova_backend/src/brain_server.py` — landed 2026-04-15 (commit `2105777`). Entry point target is `src.brain_server:main` (the `src/` package is the existing import root used by all `from src.X import Y` calls; renaming to a proper `novalis` namespace is deferred to Tier 3).
- [x] Create `pyproject.toml` with dependencies and entry point `nova-start`
- [x] Add `.github/workflows/ci.yml` for basic linting and test run

**Acceptance:**  
- [x] `python -m uvicorn src.brain_server:app` launches the app (existing `start_nova.bat/sh` pattern, verified)
- [x] `pip install -e .` works (verified locally in `nova_backend/venv`; wheel built successfully)
- [x] `nova-start` command created (`nova_backend/venv/Scripts/nova-start.exe` resolves; import smoke test passes)

**Open follow-ups:**
- [ ] Verify `pip install -e .` from a **clean** venv (current verification reused the existing venv — dependencies were already satisfied).
- [ ] Run the new CI workflow on a PR to confirm GitHub Actions passes end-to-end.

**Files:** `nova_backend/src/brain_server.py` (add `main()`), `pyproject.toml`, `.github/workflows/ci.yml`  
**Estimate:** 120 lines

---

### 1.5 Minimal distribution landing page
- [x] Create landing page (`nova_backend/static/landing/index.html`) with hero, bullets, ASCII screenshot placeholder, email waitlist form
- [x] CSS (`styles.css`) — dark-first, responsive, respects `prefers-color-scheme: light`
- [x] Form submission via Formspree (`script.js`) — graceful fallback when endpoint not yet configured
- [x] Mounted at `/landing` in `brain_server.py` via `StaticFiles(html=True)`
- [x] Link from README
- [ ] **Activate waitlist:** sign up at formspree.io, replace `REPLACE_WITH_REAL_ID` in `script.js`
- [ ] (Optional) Host on GitHub Pages or custom domain for public access

**Files:** `nova_backend/static/landing/index.html`, `nova_backend/static/landing/styles.css`, `nova_backend/static/landing/script.js`, `nova_backend/src/brain_server.py`  
**Estimate:** 100 lines — **landed ~280 lines across 4 files**

---

## This Week's Focus (Week 1)

### Must
- [x] **Task 1.0 (preflight):** Baseline established 2026-04-15. `scripts/generate_runtime_docs.py` regenerated cleanly (MOC refresh committed `3e4107a`); `pytest nova_backend/tests/phase45/` passed (36/36). Full suite 1100/1100 passing locally (CI still blocked by billing lock).
- [x] **Task 1.4a (prerequisite to 1.4):** `def main()` added to `nova_backend/src/brain_server.py` (commit `2105777`).
- [x] **Task 1.4:** `pyproject.toml` + CI landed — see section 1.4 above for open follow-ups.

### Should
- [x] **Task 1.2:** README rewritten, INTRODUCTION.md + ARCHITECTURE.md created
- [x] **Task 1.3:** UI simplified — nav collapsed, widgets hidden, token bar hidden, default prompt set
- [x] **Task 1.5:** Landing page with waitlist form deployed at `/landing`

### Remaining
- [x] **Task 1.1:** Windows installer scaffolding shipped — Inno Setup .iss, bootstrap PS1, fetch_models.py, start_daemon.py
- [x] **Task 1.1 build:** `dist/NovaSetup-0.1.0.exe` compiled (214 MB, Inno Setup 6.7.1)
- [ ] **Task 1.1 validation:** Test installer on clean Windows VM (acceptance: double-click → Nova running ≤5 min)
- [ ] Activate Formspree endpoint for landing page waitlist
- [ ] Add CI badges to README (blocked: GitHub Actions billing lock)
- [ ] Add screenshot / demo GIF to README

---

## Done This Week
- [x] Task 1.0 — Preflight baseline (pytest 36/36, MOC refresh)
- [x] Task 1.4a — `def main()` wrapper in brain_server.py
- [x] Task 1.4 — `pyproject.toml` + CI workflow
- [x] Task 1.2 — README rewrite + INTRODUCTION.md + ARCHITECTURE.md
- [x] Task 1.3 — UI simplified (collapsed nav, hidden widgets, token bar removed, default prompt)
- [x] Task 1.5 — Landing page with waitlist form at `/landing`
- [x] Task 1.1 — Windows installer scaffolding (Inno Setup + bootstrap + scripts)
- [x] Deep audit cleanup — removed unverified memory claim
- [x] Doc reorganization — renamed/relocated user docs into docs/future/ and docs/archive/
- [x] Second-pass review — 3 must-fix (favicon, bootstrap hang, start_daemon probe), 5 should-fix, 1 cosmetic — all applied (`96244bc`)
- [x] Test suite fixes — 5 stale test assertions updated (workspace_api LANDING_HTML→LANDING_DIR, landing page copy, skill map web_search, codebase summary README text); full suite 1100/1100 green

---

## Blockers / Dependencies

- **GitHub Actions billing lock** — CI workflow exists but has not run. All three triggered workflows (CI, Governance Check, Fingerprint Clean) failed with "account is locked due to a billing issue." Resolve account status to unblock CI badges and automated testing.

---

## Notes

- **Do not** start refactoring `brain_server.py` or `session_handler.py`. That is Tier 3 work.
- Docker fallback is allowed **only if** native installer path is blocked; it does not replace the Tier 1 goal.
- Test every task completion on a clean Windows VM.

---

*This document is active. Update weekly. Move completed tasks to `CHANGELOG.md` and delete them from this file.*