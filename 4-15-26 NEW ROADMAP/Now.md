# NOW.md – Current Sprint (Week 1-4)

**Sprint Goal:** Non‑developer installs and runs Nova in 5 minutes.

**Status:** IN PROGRESS  
**Start Date:** 2026-04-15  
**Target End:** 2026-05-13 (4 weeks)

---

## Active Tasks (Tier 1)

### 1.1 One‑click installer
- [ ] Windows `.exe` installer (Inno Setup or similar)
- [ ] macOS `.app` bundle or `.pkg`
- [ ] Model fetch script bundled with installer
- [ ] Start daemon/service after installation

**Files:** `installer/windows/*.iss`, `scripts/fetch_models.py`, `scripts/start_daemon.py`  
**Estimate:** 400 lines

---

### 1.2 Simplify README + GitHub metadata
- [ ] Rewrite README for non‑technical user (60‑second install promise)
- [ ] Remove outdated claims ("operator", "calm presence", "voice live")
- [ ] Add badges, clear screenshot, quickstart section
- [ ] Update repo description and tags

**Files:** `README.md`, `docs/INTRODUCTION.md`, `docs/ARCHITECTURE.md`  
**Estimate:** 200 lines

---

### 1.3 Reduce UI overload
- [ ] Collapse navigation sidebar by default
- [ ] Hide non‑essential widgets from home view
- [ ] Remove token budget bar from main UI
- [ ] Simplify first‑run experience (default prompt: "Tell me the news")

**Files:** `nova_backend/static/index.html`, `nova_backend/static/dashboard-config.js`  
**Estimate:** 150 lines

---

### 1.4 Add `pyproject.toml` + CI
- [ ] Create `pyproject.toml` with dependencies and entry point `nova-start`
- [ ] Add `.github/workflows/ci.yml` for basic linting and test run

**Acceptance:**  
- [ ] `pip install -e .` works in a clean virtual environment  
- [ ] `nova-start` command launches the application

**Files:** `pyproject.toml`, `.github/workflows/ci.yml`  
**Estimate:** 100 lines

---

### 1.5 Minimal distribution landing page
- [ ] Create simple HTML landing page with email waitlist form
- [ ] Host on GitHub Pages or similar free service
- [ ] Add link from README and repo

**Files:** `landing/index.html` (or separate repo)  
**Estimate:** 100 lines

---

## This Week's Focus (Week 1)

### Must
- [ ] **Task 1.4:** `pyproject.toml`

### Should
- [ ] **Task 1.1:** Windows installer scaffolding

### Could
- [ ] **Task 1.2:** README first pass

---

## Done This Week
- [ ] (Move completed tasks here at week end)

---

## Blockers / Dependencies

- None yet.

---

## Notes

- **Do not** start refactoring `brain_server.py` or `session_handler.py`. That is Tier 3 work.
- Docker fallback is allowed **only if** native installer path is blocked; it does not replace the Tier 1 goal.
- Test every task completion on a clean Windows VM.

---

*This document is active. Update weekly. Move completed tasks to `CHANGELOG.md` and delete them from this file.*