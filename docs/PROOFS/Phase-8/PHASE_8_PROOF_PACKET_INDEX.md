# Phase 8 Proof Packet Index
Updated: 2026-04-05
Status: Current proof index

## Current canonical live Phase-8 foundation packet
- `docs/PROOFS/Phase-8/PHASE_8_MANUAL_FOUNDATION_AND_DELIVERY_INBOX_RUNTIME_SLICE_2026-03-27.md`
- `docs/PROOFS/Phase-8/PHASE_8_5_NARROW_SCHEDULER_RUNTIME_SLICE_2026-03-27.md`
- `docs/PROOFS/Phase-8/PHASE_8_LOCAL_FIRST_OPENAI_ROUTING_AND_VISIBILITY_RUNTIME_SLICE_2026-03-27.md`
- `docs/PROOFS/Phase-8/PHASE_8_SYSTEM_MAP_AND_METERED_OPENAI_TASK_REPORT_RUNTIME_SLICE_2026-03-27.md`
- `docs/PROOFS/Phase-8/PHASE_8_DEDICATED_VERIFICATION_AND_PROOF_ALIGNMENT_2026-03-28.md`
- `docs/PROOFS/Phase-8/PHASE_8_FULL_DESIGN_REVIEW_AND_RUNTIME_ALIGNMENT_2026-03-28.md`
- `docs/PROOFS/Phase-8/PHASE_8_5_SCHEDULER_POLICY_SUPPRESSION_AND_END_TO_END_VALIDATION_2026-03-28.md`

## Adjacent Phase-8 companion slices
- `docs/PROOFS/Phase-8/PHASE_8_OPENCLAW_REMOTE_BOUNDARY_AND_SETUP_READINESS_RUNTIME_SLICE_2026-03-27.md`
- `docs/PROOFS/Phase-8/PHASE_8_BOUNDED_ASSISTIVE_NOTICING_RUNTIME_SLICE_2026-03-27.md`
- `docs/PROOFS/Phase-8/PHASE_8_ASSISTIVE_NOTICE_RATE_LIMITING_AND_HANDLING_RUNTIME_SLICE_2026-03-27.md`
- `docs/PROOFS/Phase-8/PHASE_8_ASSISTIVE_NOTICE_HISTORY_AND_TYPE_COOLDOWNS_RUNTIME_SLICE_2026-03-27.md`

## Scope captured across the current packets
- manual OpenClaw home-agent foundation with delivery inbox and operator-visible review
- strict manual preflight before a home-agent task can run
- explicit TaskEnvelope scope and budget preview on runnable templates
- measured narrow-lane usage surfaced on active and completed runs
- narrow scheduler behavior behind explicit settings control
- quiet-hours and rate-limit suppression for the narrow scheduler
- local-first metered OpenAI fallback for narrow task-report summarization only
- current system-map and end-to-end explanation packet for Nova and OpenClaw
- project-level end-to-end validation checklist for core Nova journeys
- remote boundary and setup-readiness truth for the governed bridge and agent inputs
- bounded assistive noticing with cooling windows, handled state, and Trust review surfaces

Interpretation note:
- the canonical live Phase-8 core is still the narrow home-agent foundation plus its scheduler, metered-reporting fallback, and dedicated verification package
- remote-boundary hardening and bounded assistive noticing are real runtime work, but they should be read as companion slices instead of redefining the canonical Phase-8 shipping line

## Read with
- `docs/design/Phase 8/PHASE_8_DOCUMENT_MAP.md`
- `docs/design/Phase 8/NOVA_OPENCLAW_HOME_AGENT_MASTER_REFERENCE_2026-03-27.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_HOME_AGENT_AND_PERSONALITY_LAYER_PLAN_2026-03-26.md`
- `docs/design/Phase 8.5/PHASE_8_5_SCHEDULER_AND_PROACTIVE_DELIVERY_PLAN_2026-03-27.md`
- `docs/design/Phase 5/NOVA_CROSS_SYSTEM_MEMORY_AND_GOVERNED_AWARENESS_DIRECTION_2026-03-27.md`

## Verification Commands (Current)
Run these commands from `nova_backend/`.

- `python -m pytest tests\phase8 -q`
- `python -m pytest tests\openclaw\test_agent_runner.py tests\openclaw\test_agent_runtime_store.py tests\openclaw\test_agent_scheduler.py tests\openclaw\test_openai_responses_lane.py tests\openclaw\test_strict_preflight.py tests\openclaw\test_task_envelope.py tests\test_openclaw_agent_api.py tests\test_openclaw_bridge_api.py tests\test_runtime_settings_api.py tests\test_runtime_auditor.py -q`
- `python -m pytest tests\phase45\test_dashboard_trust_center_widget.py tests\phase45\test_dashboard_workspace_home_widget.py tests\phase45\test_brain_server_memory_and_continuity.py -q`
- `python -m py_compile src\audit\runtime_auditor.py src\openclaw\agent_runner.py src\openclaw\agent_runtime_store.py src\providers\openai_responses_lane.py`
- `python ..\scripts\generate_runtime_docs.py`
- `python ..\scripts\check_runtime_doc_drift.py`
- `python ..\scripts\check_frontend_mirror_sync.py`

## Latest Verification Snapshot (2026-03-28)
- phase8 dedicated verification package: `20 passed`
- OpenClaw / agent API / runtime-auditor bundle: `62 passed`
- dashboard continuity / Trust widget bundle: `24 passed`
- runtime documentation drift check: passed
- frontend mirror parity check: passed

## Notes
- Do not read this folder as proof that full canonical Phase-8 automation is complete.
- Runtime truth still lives in `docs/current_runtime/CURRENT_RUNTIME_STATE.md`.
