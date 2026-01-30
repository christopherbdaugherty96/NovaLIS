# REPO_MAP — NovaLIS (AI Navigation)

Purpose: Give humans + AI a deterministic map of this repository and the safe "review order".

Scope: Navigation + review guidance only. No behavior changes.

---

## 0) Canon / North Star (Read First)

The **single authoritative source of truth** for this repository is:

→ **FINAL CANONICAL TRUTH-NovaLIS.txt**

All other documents (including phase locks, governance contracts, and design specs) are authoritative **only insofar as they do not conflict** with the Final Canonical Truth.

If any document conflicts with FINAL CANONICAL TRUTH-NovaLIS.txt, it is **invalid by definition** unless explicitly unlocked.

**Non-negotiables (high-level):**
- Offline-first by default; online only by explicit user request.
- Deterministic behavior; no inferred intent; token-based matching (no substrings).
- No background cognition / no proactive tasks outside explicit contracts.
- Phase gating is a hard safety barrier (Phase 4 remains blocked until Phase 3.5 gates pass).

---

## 1) Repo Top-Level Layout (What Each Folder Is)

### `nova_backend/`
Primary runtime backend (FastAPI / WebSocket brain). This is the main execution surface.

Key subpaths:
- `nova_backend/src/` — main application source
  &nbsp; - `brain_server.py` — server entry + routing/orchestration glue (high attention)
  &nbsp; - `skill_registry.py` — skill registration + dispatch (high attention)
  &nbsp; - `skills/` — skill implementations (system/weather/news/general_chat, etc.)
  &nbsp; - `services/` — service abstractions (e.g., WeatherService)
  &nbsp; - `routers/` — API routes (e.g., STT router)
  &nbsp; - `gates/` and/or `governor/` — governance/confirmation/mediator components (Phase correctness matters)
  &nbsp; - `execution/` / `executors/` / `actions/` — governed action scaffolding (must remain phase-gated)
- `nova_backend/tests/` — tests (unit/contract tests)
- `nova_backend/static/` — static dashboard assets served by backend (if used)

**Important:** Runtime artifacts and large binaries (models, ffmpeg) are NOT committed. See `.gitignore` and `nova_backend/tools/README.md`.

---

### `Nova-Frontend-Dashboard/`
Standalone dashboard/UI (HTML/JS/CSS). Used as an observer/control surface.

Key files:
- `index.html`, `dashboard.js` — main UI
- `style*.css` — styling (Phase constraints may apply)
- `phase1/` — historical frozen phase assets (reference)
- `assets/` / `visuals/` — UI visuals and helpers

---

### `NovaLIS-Governance/`
Governance contracts, phase locks, acceptance gates, and "do not drift" rules.

These documents are **binding only where they align with FINAL CANONICAL TRUTH-NovaLIS.txt**.
If a conflict exists, the Final Canonical Truth prevails.

---

### `Documentation-Architecture-Docs/` and `docs/`
Legacy and supporting documentation. Useful context, not always canonical.

Prefer `NovaLIS-Governance/` for binding constraints.

---

## 2) "Start Here" Review Order (AI + Human)

Use this deterministic review order:

0) **Final Canonical Truth**
   &nbsp;  - `FINAL CANONICAL TRUTH-NovaLIS.txt` — Required reading before any code, governance, or review activity

1) **Governance / locks**
   &nbsp;  - `NovaLIS-Governance/PHASE_*.md`
   &nbsp;  - `NovaLIS-Governance/ARCHITECT_CONTRACT.md`

2) **Backend orchestration**
   &nbsp;  - `nova_backend/src/brain_server.py`
   &nbsp;  - `nova_backend/src/skill_registry.py`

3) **Core skills**
   &nbsp;  - `nova_backend/src/skills/system.py`
   &nbsp;  - `nova_backend/src/skills/weather.py`
   &nbsp;  - `nova_backend/src/skills/news.py`
   &nbsp;  - `nova_backend/src/skills/general_chat.py`

4) **Services + IO**
   &nbsp;  - `nova_backend/src/services/*`
   &nbsp;  - `nova_backend/src/routers/*`
   &nbsp;  - STT chain: `nova_backend/src/stt_manager.py`, `nova_backend/src/services/stt_engine.py`, `nova_backend/src/routers/stt.py`

5) **Governance enforcement layers**
   &nbsp;  - `nova_backend/src/gates/*`
   &nbsp;  - `nova_backend/src/governor/*`
   &nbsp;  - `nova_backend/src/execution/*` and `nova_backend/src/executors/*` (ensure phase-gated; no silent actions)

6) **Frontend parity + schema**
   &nbsp;  - `Nova-Frontend-Dashboard/dashboard.js`
   &nbsp;  - `Nova-Frontend-Dashboard/index.html`
   &nbsp;  - `nova_backend/static/*` (only if backend-served UI is in use)

7) **Tests**
   &nbsp;  - `nova_backend/tests/*`

---

## 3) AI Review Rules (Hard Constraints)

An AI reviewer may:
- Identify mismatches vs governance docs
- Propose minimal diffs
- Add tests that enforce locked behavior
- Add documentation that clarifies setup without adding capability

An AI reviewer must NOT:
- Add new capabilities, new skills, or broaden scope
- "Refactor for style" if it risks behavior drift
- Add background tasks, watchers, telemetry, analytics, or "helpful" auto-actions
- Add silent online behavior or implicit web search
- Introduce probabilistic/ranked intent selection

Preferred output format for AI review:
- Findings grouped by (a) lock violations (b) correctness bugs (c) safety gaps (d) low-risk cleanup
- Provide diff-only patches, smallest change wins
- If uncertain: request a targeted file or log excerpt (no guessing)

---

## 4) Setup Notes (Local-Only by Default)

- Large runtime dependencies (STT models, ffmpeg binaries) are installed locally and are intentionally excluded from Git.
- See: `nova_backend/tools/README.md`
- `.gitignore` defines excluded runtime artifacts.

End of REPO_MAP.