\# REPO\_MAP — NovaLIS (AI Navigation)



Purpose: Give humans + AI a deterministic map of this repository and the safe “review order”.

Scope: Navigation + review guidance only. No behavior changes.



---



\## 0) Canon / North Star (Read First)



If you are reviewing code or proposing changes, you must treat these as authoritative:

\- `NovaLIS-Governance/PHASE\_1\_LOCK.md`

\- `NovaLIS-Governance/PHASE\_2\_LOCK.md`

\- `NovaLIS-Governance/PHASE\_3\_LOCK.md`

\- `NovaLIS-Governance/ARCHITECT\_CONTRACT.md`

\- Any additional “LOCKED” governance docs in `NovaLIS-Governance/`



\*\*Non-negotiables (high-level):\*\*

\- Offline-first by default; online only by explicit user request.

\- Deterministic behavior; no inferred intent; token-based matching (no substrings).

\- No background cognition / no proactive tasks outside explicit contracts.

\- Phase gating is a hard safety barrier (Phase 4 remains blocked until Phase 3.5 gates pass).



---



\## 1) Repo Top-Level Layout (What Each Folder Is)



\### `nova\_backend/`

Primary runtime backend (FastAPI / WebSocket brain). This is the main execution surface.



Key subpaths:

\- `nova\_backend/src/` — main application source

&nbsp; - `brain\_server.py` — server entry + routing/orchestration glue (high attention)

&nbsp; - `skill\_registry.py` — skill registration + dispatch (high attention)

&nbsp; - `skills/` — skill implementations (system/weather/news/general\_chat, etc.)

&nbsp; - `services/` — service abstractions (e.g., WeatherService)

&nbsp; - `routers/` — API routes (e.g., STT router)

&nbsp; - `gates/` and/or `governor/` — governance/confirmation/mediator components (Phase correctness matters)

&nbsp; - `execution/` / `executors/` / `actions/` — governed action scaffolding (must remain phase-gated)

\- `nova\_backend/tests/` — tests (unit/contract tests)

\- `nova\_backend/static/` — static dashboard assets served by backend (if used)



\*\*Important:\*\* Runtime artifacts and large binaries (models, ffmpeg) are NOT committed. See `.gitignore` and `nova\_backend/tools/README.md`.



---



\### `Nova-Frontend-Dashboard/`

Standalone dashboard/UI (HTML/JS/CSS). Used as an observer/control surface.



Key files:

\- `index.html`, `dashboard.js` — main UI

\- `style\*.css` — styling (Phase constraints may apply)

\- `phase1/` — historical frozen phase assets (reference)

\- `assets/` / `visuals/` — UI visuals and helpers



---



\### `NovaLIS-Governance/`

Governance contracts, phase locks, acceptance gates, and “do not drift” rules.



This folder is the canonical constraints layer.

If code conflicts with governance docs, code must be corrected (not the other way around) unless an explicit unlock exists.



---



\### `Documentation-Architecture-Docs/` and `docs/`

Legacy and supporting documentation. Useful context, not always canonical.

Prefer `NovaLIS-Governance/` for binding constraints.



---



\## 2) “Start Here” Review Order (AI + Human)



Use this deterministic review order:



1\) \*\*Governance / locks\*\*

&nbsp;  - `NovaLIS-Governance/PHASE\_\*.md`

&nbsp;  - `NovaLIS-Governance/ARCHITECT\_CONTRACT.md`



2\) \*\*Backend orchestration\*\*

&nbsp;  - `nova\_backend/src/brain\_server.py`

&nbsp;  - `nova\_backend/src/skill\_registry.py`



3\) \*\*Core skills\*\*

&nbsp;  - `nova\_backend/src/skills/system.py`

&nbsp;  - `nova\_backend/src/skills/weather.py`

&nbsp;  - `nova\_backend/src/skills/news.py`

&nbsp;  - `nova\_backend/src/skills/general\_chat.py`



4\) \*\*Services + IO\*\*

&nbsp;  - `nova\_backend/src/services/\*`

&nbsp;  - `nova\_backend/src/routers/\*`

&nbsp;  - STT chain: `nova\_backend/src/stt\_manager.py`, `nova\_backend/src/services/stt\_engine.py`, `nova\_backend/src/routers/stt.py`



5\) \*\*Governance enforcement layers\*\*

&nbsp;  - `nova\_backend/src/gates/\*`

&nbsp;  - `nova\_backend/src/governor/\*`

&nbsp;  - `nova\_backend/src/execution/\*` and `nova\_backend/src/executors/\*` (ensure phase-gated; no silent actions)



6\) \*\*Frontend parity + schema\*\*

&nbsp;  - `Nova-Frontend-Dashboard/dashboard.js`

&nbsp;  - `Nova-Frontend-Dashboard/index.html`

&nbsp;  - `nova\_backend/static/\*` (only if backend-served UI is in use)



7\) \*\*Tests\*\*

&nbsp;  - `nova\_backend/tests/\*`



---



\## 3) AI Review Rules (Hard Constraints)



An AI reviewer may:

\- Identify mismatches vs governance docs

\- Propose minimal diffs

\- Add tests that enforce locked behavior

\- Add documentation that clarifies setup without adding capability



An AI reviewer must NOT:

\- Add new capabilities, new skills, or broaden scope

\- “Refactor for style” if it risks behavior drift

\- Add background tasks, watchers, telemetry, analytics, or “helpful” auto-actions

\- Add silent online behavior or implicit web search

\- Introduce probabilistic/ranked intent selection



Preferred output format for AI review:

\- Findings grouped by (a) lock violations (b) correctness bugs (c) safety gaps (d) low-risk cleanup

\- Provide diff-only patches, smallest change wins

\- If uncertain: request a targeted file or log excerpt (no guessing)



---



\## 4) Setup Notes (Local-Only by Default)



\- Large runtime dependencies (STT models, ffmpeg binaries) are installed locally and are intentionally excluded from Git.

\- See: `nova\_backend/tools/README.md`

\- `.gitignore` defines excluded runtime artifacts.



End of REPO\_MAP.



