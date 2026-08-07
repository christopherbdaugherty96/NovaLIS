# docs/observation - Morning observation logs

**Status:** ACTIVE evidence stream; no open-ended morning gate is active.
**Authority:** observation logs are recorded evidence (facts about usage), not plans or designs.
They feed the roadmap; they do not authorize builds by themselves.

## Why This Folder Exists

Phase 3 is closed. The seven-morning threshold was completed and synthesized on 2026-07-22, and
its rank-1 grounded-routing repair shipped through PR #312. The targeted post-#312 owner-use
session is recorded in
[OWNER_ACCEPTANCE_POST_312_2026-08-07.md](OWNER_ACCEPTANCE_POST_312_2026-08-07.md). That record
closed the pending product-selection input and selected `Commitment Truth + Natural Reminder
Handoff` under a separate owner-approved priority lock.

Observation remains an evidence stream: behavior generates product priorities, not speculative
architecture. There is no new open-ended morning gate. Future normal use may discover defects
without automatically restarting a formal observation phase.

Current posture update (2026-08-07): when real use exposes a trust, truth, or daily-use blocker,
record it first and require an explicit bounded owner decision before implementation. The August 7
record followed that rule. Do not treat normal use or this folder as permission to resume
speculative roadmap implementation or activate a secondary candidate.

The single success metric: **did Nova eliminate at least one uncertainty before you reached for
another app?**

## Launch Procedure For A Live Observation Session

1. Confirm Nova is not already running: no python process should own port 8000
   (`netstat -ano | findstr :8000`). If one does, run `stop_nova.bat` first.
2. Launch via `start_nova.bat` (the desktop `Nova.lnk` shortcut points here). It uses the
   backend venv python (`nova_backend\venv\Scripts\python.exe`), which starts uvicorn on
   `127.0.0.1:8000` and inherits the User-scope environment variables that carry all live
   config (`OLLAMA_MODEL`, `NOVA_CALENDAR_ICS_PATH`, weather/search keys).
   Do not start Nova from a manually opened old shell, and do not use `Start-Nova.ps1`
   (dev/`--reload` mode) or a bare `python scripts/start_daemon.py` (system python). Mixed
   launch paths caused the Morning-0 port race.
3. After launch, only one process should own port 8000; server output goes to
   `scripts\pids\nova.log`.
4. Keep the dashboard closed except when actually reading the brief. While open, it auto-refreshes
   the brief (~70s cadence), which contends for the single execution slot and can produce false
   "not configured" labels. Chat questions are the cleaner probe.

Note on config truth: the runtime does **not** read `nova_backend/.env`; it reads process
environment variables only. User-scope env vars (HKCU) are the operative source;
`nova_backend/.env` is kept as a documented mirror and is read directly by the Cap 65 live-proof
test.

## Protocol

1. For a formal morning record, copy [MORNING_LOG_TEMPLATE.md](MORNING_LOG_TEMPLATE.md) and fill
   it in immediately while the experience is fresh.
2. Record config and condition metadata, especially the exact running commit, branch, launch path,
   dashboard state, and fresh/warm state. Missing provenance limits commit-level attribution.
3. Distinguish a single-session finding from a repeated trend. A severe trust/correctness defect
   may support a bounded repair; ordinary wishes remain candidates until repeated evidence earns
   priority.
4. Exceptions to the freeze remain critical bugs and owner-approved evidence-fired trust repairs. If
   Nova acts without asking, presents inference as fact, fabricates source-like output, or an
   observed daily-use blocker makes the product misleading, log it first; it may be fixed
   immediately only when the owner explicitly calls that lane.
5. Do not restart the completed seven-morning phase or require another post-#312 acceptance morning
   unless the owner explicitly creates a new evidence gate.

## What Happens To The Results

- Repeated friction/wishes become candidates for the master roadmap
  (`docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`), filtered by decision-relevance
  ("does this change what I should know, decide, or do?") and app-elimination
  ("does this remove another app from my morning?").
- Trust-class violations (inference shown as fact) become Phase-4 candidates for the
  Fact / Reasoning / Inference UI.
- Latency problems become evidence for the model-preset/budget direction.

Related: `docs/CANONICAL/00_INDEX.md` (how to read truth),
`docs/product/PRODUCT_DEFINITION.md` (identity and phases).
