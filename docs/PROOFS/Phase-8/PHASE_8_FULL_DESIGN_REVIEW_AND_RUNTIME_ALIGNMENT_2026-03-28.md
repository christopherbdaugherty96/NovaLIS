# Phase 8 Full Design Review And Runtime Alignment
Updated: 2026-03-28
Status: Full Phase-8 design review refresh

## Purpose
This packet closes the remaining wording drift between the live Phase-8 runtime and the Phase-8 design folder.

The runtime already had:
- a manual OpenClaw home-agent foundation
- a narrow scheduled briefing lane behind explicit settings control
- a persistent delivery inbox
- a narrow local-first metered OpenAI fallback for task-report summarization
- bounded assistive noticing with handled state and Trust review

The main remaining mismatch was in the design wording:
- parts of the master reference and home-agent plan still spoke as if no scheduler existed yet
- the generated runtime note did not mention bounded assistive noticing even though the Phase-8 map treated it as part of the current live slice

## What Changed
- refreshed the Phase-8 master reference so the scheduler boundary now reads truthfully:
  - only the explicit narrow briefing scheduler carve-out is live
  - broader background automation still remains deferred
- refreshed the home-agent and personality-layer plan so it now names the live scheduler, `market_watch`, and the narrow metered OpenAI task-report fallback
- updated the runtime auditor so the generated Phase-8 note now includes bounded assistive noticing
- added an Assistive Noticing system entry to the generated runtime systems section
- added Phase-8 design-gate assertions so stale pre-scheduler wording fails fast in tests

## Why This Matters
Phase 8 is now doing real work in runtime, but only in a narrow, inspectable, operator-visible sense.

That only stays trustworthy if the design folder says exactly that:
- narrow scheduler live
- bounded noticing live
- manual foundation live
- full canonical envelope-governed automation still deferred

## Verification
Run these commands from `nova_backend/`.

Passed:
- `python -m pytest tests\phase8 -q`
- `python -m pytest tests\openclaw\test_agent_runner.py tests\openclaw\test_agent_runtime_store.py tests\openclaw\test_agent_scheduler.py tests\openclaw\test_openai_responses_lane.py tests\openclaw\test_strict_preflight.py tests\openclaw\test_task_envelope.py tests\test_openclaw_agent_api.py tests\test_openclaw_bridge_api.py tests\test_runtime_settings_api.py tests\test_runtime_auditor.py -q`
- `python -m py_compile src\audit\runtime_auditor.py src\openclaw\agent_runner.py src\openclaw\agent_runtime_store.py src\providers\openai_responses_lane.py`
- `python ..\scripts\generate_runtime_docs.py`
- `python ..\scripts\check_runtime_doc_drift.py`
- `python ..\scripts\check_frontend_mirror_sync.py`

## Bottom Line
This refresh does not widen Nova's authority.

It makes the Phase-8 design folder match the actual live runtime more cleanly:
- the scheduler is described honestly
- bounded assistive noticing is called out in runtime truth
- the full canonical automation model still stays clearly ahead of what is live today
