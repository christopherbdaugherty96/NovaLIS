> ## 🔒 PHASE-3.5 STATUS UPDATE — SEALED
>
> **Phase-3.5 is formally COMPLETE and SEALED.**  
> All Phase-3.5 acceptance criteria have been mechanically verified and CI-enforced, including execution quarantine, Governor containment, passive confirmation gating, and runtime refusal proofs.
>
> This document may reference Phase-3.5 as "active" for historical context only.  
> **No Phase-3.5 work remains open.** Phase-4 is design‑unlocked but runtime‑locked pending a separate unlock artifact.
>
> **Authoritative closure record:** `docs/PHASE_3.5_CLOSURE.md`
------------------------------------------------

# REPO_MAP — Nova (AI Navigation)

Purpose: Give humans + AI a deterministic map of this repository and the safe "review order".

Scope: Navigation + review guidance only. No behavior changes.

---

## 0) Canon / North Star (Read First)

The **single authoritative source of truth** for this repository is:

→ **`NOVA COMPLETE CONSTITUTIONAL BLUEPRINT 1.8.md`**

All other documents (including phase locks, governance contracts, and design specs) are authoritative **only insofar as they do not conflict** with v1.8.

If any document conflicts with v1.8, it is **invalid by definition** unless explicitly unlocked.

**Non-negotiables (high-level):**
- Phase 3.5: **SEALED** (no execution authority, GovernorMediator only)
- Phase-3.5 closure is recorded in `docs/PHASE_3.5_CLOSURE.md` and is authoritative for execution status
- Governor: GovernorMediator (text sanitizer only)
- Execution: Disabled (`execute_action = None`, `GOVERNED_ACTIONS_ENABLED = false` hard‑coded)
- Phase 4: Design‑Unlocked, Runtime‑Locked (no implementation)
- Agent Identity: Nova is non-autonomous coordinator (Intelligence–Authority Split)
- Memory Governance: Memory is filing system, not learning system
- Offline-first by default; online only by explicit user request
- Deterministic behavior; no inferred intent; literal word‑boundary triggers
- No background cognition / no proactive tasks outside explicit contracts

---

## 1) Repo Top-Level Layout (What Each Folder Is)

### `nova_backend/`
Primary runtime backend (FastAPI / WebSocket brain). This is the main execution surface.

Key subpaths:
- `nova_backend/src/` — main application source
  &nbsp; - `brain_server.py` — server entry + routing/orchestration glue (high attention)
  &nbsp; - `skill_registry.py` — skill registration + dispatch (high attention)
  &nbsp; - `skills/` — skill implementations (system/weather/news/general_chat, etc.)
  &nbsp; - `services/` — service abstractions (e.g., WeatherService using Visual Crossing)
  &nbsp; - `routers/` — API routes (e.g., STT router)
  &nbsp; - `governor/` — GovernorMediator (text sanitizer only, not enforcement engine)
  &nbsp; - `execution/` — execution disabled (`execute_action = None`)
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
*Note: This folder may contain legacy documents; the canonical truth is v1.8.*

**Key documents:**
- `PHASE_3.5_FROZEN_STATUS.md` — Current phase status (SEALED; should be updated to match v1.8)
- Phase completion certificates (archival)

---

### `Documentation-Architecture-Docs/` and `docs/`
Legacy and supporting documentation. Useful context, not always canonical.

**Note:** For current phase status, refer to `docs/PHASE_3.5_CLOSURE.md` and v1.8.

---

## 2) "Start Here" Review Order (AI + Human)

Use this deterministic review order:

0) **Final Canonical Truth**
   &nbsp;  - `NOVA COMPLETE CONSTITUTIONAL BLUEPRINT 1.8.md` — Required reading before any code, governance, or review activity

1) **Current Phase Status**
   &nbsp;  - `docs/PHASE_3.5_CLOSURE.md` — Current operational reality

2) **Governance / locks**
   &nbsp;  - `NovaLIS-Governance/PHASE_*.md` (verify against v1.8)
   &nbsp;  - `NovaLIS-Governance/ARCHITECT_CONTRACT.md`

3) **Backend orchestration**
   &nbsp;  - `nova_backend/src/brain_server.py`
   &nbsp;  - `nova_backend/src/skill_registry.py`

4) **Core skills**
   &nbsp;  - `nova_backend/src/skills/system.py`
   &nbsp;  - `nova_backend/src/skills/weather.py` (Visual Crossing provider)
   &nbsp;  - `nova_backend/src/skills/news.py` (RSS, user-initiated)
   &nbsp;  - `nova_backend/src/skills/general_chat.py`

5) **Services + IO**
   &nbsp;  - `nova_backend/src/services/*`
   &nbsp;  - `nova_backend/src/routers/*`
   &nbsp;  - STT chain: `nova_backend/src/stt_manager.py`, `nova_backend/src/services/stt_engine.py`, `nova_backend/src/routers/stt.py`

6) **Governance mediation layer**
   &nbsp;  - `nova_backend/src/governor/` (GovernorMediator only)

7) **Frontend parity + schema**
   &nbsp;  - `Nova-Frontend-Dashboard/dashboard.js`
   &nbsp;  - `Nova-Frontend-Dashboard/index.html`
   &nbsp;  - `nova_backend/static/*` (only if backend-served UI is in use)

8) **Tests**
   &nbsp;  - `nova_backend/tests/*`

---

## 3) AI Review Rules (Hard Constraints)

An AI reviewer may:
- Identify mismatches vs governance docs (especially v1.8)
- Propose minimal diffs
- Add tests that enforce locked behavior
- Add documentation that clarifies setup without adding capability
- Verify phase alignment with v1.8

An AI reviewer must NOT:
- Add new capabilities, new skills, or broaden scope
- "Refactor for style" if it risks behavior drift
- Add background tasks, watchers, telemetry, analytics, or "helpful" auto-actions
- Add silent online behavior or implicit web search
- Introduce probabilistic/ranked intent selection
- Suggest capabilities beyond Phase 3.5 sealed state
- Reinterpret "design documents" as approval for implementation

Preferred output format for AI review:
- Findings grouped by (a) lock violations (b) correctness bugs (c) safety gaps (d) low-risk cleanup
- Provide diff-only patches, smallest change wins
- If uncertain: request a targeted file or log excerpt (no guessing)

---

## 4) Setup Notes (Local-Only by Default)

- Large runtime dependencies (STT models, ffmpeg binaries) are installed locally and are intentionally excluded from Git.
- See: `nova_backend/tools/README.md`
- `.gitignore` defines excluded runtime artifacts.

---

## 5) Phase Documentation Reference

**Current Operational Status:**
- `docs/PHASE_3.5_CLOSURE.md` — Phase 3.5 is SEALED (no execution authority)

**Historical Completion Certificates:**
- `docs/PHASE_3_COMPLETION.md` — Phase 3 was COMPLETE & LOCKED

**Canonical Truth:**
- `NOVA COMPLETE CONSTITUTIONAL BLUEPRINT 1.8.md` — Single source of truth

**Design Documents (Phase 4+ only - NOT IMPLEMENTED):**
- Nova Orthogonal Cognition Stack.txt (Phase 4.2+)
- Nova Personal Intelligence Hub Arch.txt (Phase 5+)
- NOVA MIND ARCHITECTURE WITH DEEPSEEK.txt (Phase 4+)

**Audit & Governance Frameworks (Phase 4+):**
- `DEEPSEEK INTEGRATION AUDIT.md` - Constitutional audit requirements for DeepSeek integration

**Philosophical Context (Reference Only):**
- `CorePhilosophy.md` - Project philosophy and governance-first mindset

**Note:** Phase-10+ documents describe speculative, non-binding end-state ideas. They do **not** imply roadmap intent, prioritization, or inevitability.

**Important:** Design documents describe future architecture only. No implementation exists in current runtime.

---

**End of REPO_MAP.**