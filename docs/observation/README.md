# docs/observation - Morning observation logs

**Status:** ACTIVE - this is the current phase's primary evidence stream.
**Authority:** observation logs are recorded evidence (facts about usage), not plans or designs.
They feed the roadmap; they do not authorize builds by themselves.

## Why This Folder Exists

Phase 3 is closed and engineering is frozen behind the observation gate: **at least 7 real
mornings of logged use before broad feature building.** Behavior generates the roadmap, not specs,
reference repos, or theory. This folder is where that behavior gets recorded.

Current posture update (2026-07-15): the default remains collect-before-building, but a narrower
exception exists when a real morning exposes a trust, truth, or daily-use blocker and the owner
explicitly fires a lane from that evidence. Morning 4/5 repairs followed that pattern: observation
named the problem first, then fixes stayed scoped to the observed failure. Do not treat this as
permission to resume speculative roadmap implementation.

The single success metric: **did Nova eliminate at least one uncertainty before you reached for
another app?**

## Launch Procedure For The Observation Week

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

1. One file per morning: `MORNING_01_YYYY-MM-DD.md` (02, 03, ...), copied from
   [MORNING_LOG_TEMPLATE.md](MORNING_LOG_TEMPLATE.md).
2. Fill it in **right after** using the Morning Brief, while the experience is fresh.
   Short honest answers beat long polished ones. Always record the config-state and condition-log
   tables (launch path, dashboard open/closed, fresh/warm); without them the 7-morning set mixes
   product behavior with observer-induced load.
3. **Collect before analyzing.** No trend analysis, no speculative roadmap decisions, no broad
   builds until at least 7 logs exist. A single morning is an anecdote; seven are evidence.
4. Exceptions to the freeze: critical bugs and owner-approved evidence-fired trust repairs. If
   Nova acts without asking, presents inference as fact, fabricates source-like output, or an
   observed daily-use blocker makes the product misleading, log it first; it may be fixed
   immediately only when the owner explicitly calls that lane.
5. After 7+ logs: analyze for repetition. A wish repeated 3+ mornings is a roadmap candidate.
   A wish appearing once is noise.

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
