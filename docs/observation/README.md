# docs/observation — Morning observation logs

**Status:** ACTIVE — this is the current phase's primary evidence stream.
**Authority:** observation logs are recorded evidence (facts about usage), not plans or designs.
They feed the roadmap; they do not authorize builds by themselves.

## Why this folder exists

Phase 3 is closed and engineering is frozen behind the observation gate: **at least 7 real
mornings of logged use before any new feature building.** Behavior generates the roadmap — not
specs, not reference repos, not theory. This folder is where that behavior gets recorded.

The single success metric: **did Nova eliminate at least one uncertainty before you reached for
another app?**

## Launch procedure for the observation week (ONE path, every morning)

1. Confirm Nova is not already running: no python process should own port 8000
   (`netstat -ano | findstr :8000`). If one does, run `stop_nova.bat` first.
2. Launch via `start_nova.bat` (the desktop `Nova.lnk` shortcut points here). It uses the
   backend venv python (`nova_backend\venv\Scripts\python.exe`), which starts uvicorn on
   127.0.0.1:8000 and inherits the User-scope environment variables that carry all live
   config (`OLLAMA_MODEL`, `NOVA_CALENDAR_ICS_PATH`, weather/search keys).
   Do NOT start Nova from a manually opened old shell, and do not use `Start-Nova.ps1`
   (dev/--reload mode) or a bare `python scripts/start_daemon.py` (system python) — mixed
   launch paths caused the Morning-0 port race.
3. After launch, only ONE process should own port 8000; server output goes to
   `scripts\pids\nova.log`.
4. Keep the dashboard closed except when actually reading the brief — while open it
   auto-refreshes the brief (~70s cadence), which contends for the single execution slot and
   can produce false "not configured" labels. Chat questions are the cleaner probe.

Note on config truth: the runtime does **not** read `nova_backend/.env` — it reads process
environment variables only. User-scope env vars (HKCU) are the operative source;
`nova_backend/.env` is kept as a documented mirror (and is read directly by the Cap 65
live-proof test).

## Protocol

1. One file per morning: `MORNING_01_YYYY-MM-DD.md` (02, 03, ...), copied from
   [MORNING_LOG_TEMPLATE.md](MORNING_LOG_TEMPLATE.md).
2. Fill it in **right after** using the Morning Brief, while the experience is fresh.
   Short honest answers beat long polished ones. Always record the config-state and
   condition-log tables (launch path, dashboard open/closed, fresh/warm) — without them the
   7-morning set mixes product behavior with observer-induced load.
3. **Collect before analyzing.** No trend analysis, no roadmap decisions, no builds until at
   least 7 logs exist. A single morning is an anecdote; seven are evidence.
4. Exceptions to the freeze: only critical bugs. If Nova acts without asking, or presents an
   inference as fact, that is a critical bug — log it and it may be fixed immediately.
5. After 7+ logs: analyze for repetition. A wish repeated 3+ mornings is a roadmap candidate.
   A wish appearing once is noise.

## What happens to the results

- Repeated friction/wishes → candidates for the master roadmap
  (`docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`), filtered by decision-relevance
  ("does this change what I should know, decide, or do?") and app-elimination
  ("does this remove another app from my morning?").
- Trust-class violations (inference shown as fact) → Phase-4 candidates for the
  Fact / Reasoning / Inference UI.
- Latency problems → evidence for the model-preset/budget direction.

Related: `docs/CANONICAL/00_INDEX.md` (how to read truth),
`docs/product/PRODUCT_DEFINITION.md` (identity and phases).
