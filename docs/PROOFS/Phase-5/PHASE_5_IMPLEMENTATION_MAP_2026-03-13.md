# Phase-5 Implementation Map
Date: 2026-03-13
Status: Current implementation map
Purpose: Map the active Phase-5 design package to live code, tests, runtime docs, proof docs, and human-language guides.

## Scope Rule
This map covers the closed trust-facing Phase-5 package only.

It does not treat future-direction documents such as delegated autonomy or consolidated APIs as required for current Phase-5 closure.
Thread continuity in the current package is session-scoped. Durable cross-session continuity is provided by explicit governed memory, not by a persistent thread store.

## Design-to-Code Map

| Design Track | Design Source | Runtime Code | Tests | Runtime / Proof Docs | Status |
| --- | --- | --- | --- | --- | --- |
| Memory governance tiers and lifecycle | `docs/design/phase 5/MEMORY GOVERNANCE.md` | `nova_backend/src/memory/governed_memory_store.py`, `nova_backend/src/executors/memory_governance_executor.py`, `nova_backend/src/governor/governor_mediator.py`, `nova_backend/src/brain_server.py` | `nova_backend/tests/phase5/test_memory_governance_executor.py` | `PHASE_5_MEMORY_RUNTIME_SLICE_2026-03-11.md`, `PHASE_5_MEMORY_INSPECTABILITY_RUNTIME_SLICE_2026-03-13.md` | Implemented |
| Working continuity / thread state | `docs/design/phase 5/NOVA_WORKING_CONTEXT_ENGINE.md` | `nova_backend/src/working_context/context_state.py`, `context_builder.py`, `context_store.py`, `project_threads.py`, `nova_backend/src/brain_server.py` | `nova_backend/tests/phase45/test_working_context_store.py`, `nova_backend/tests/phase5/test_project_thread_store.py` | `PHASE_5_PROJECT_CONTINUITY_RUNTIME_NOTE_2026-03-12.md` | Implemented (session-scoped) |
| Thread-memory bridge | Phase-5 continuity + memory package | `nova_backend/src/brain_server.py`, `nova_backend/src/memory/governed_memory_store.py` | `nova_backend/tests/test_governor_mediator_phase4_capabilities.py`, `nova_backend/tests/phase45/test_dashboard_context_insight_widget.py`, `nova_backend/tests/phase5/test_thread_change_summary.py` | `PHASE_5_THREAD_MEMORY_BRIDGE_RUNTIME_SLICE_2026-03-12.md` | Implemented |
| Tone calibration (manual + inspectable) | `docs/design/phase 5/# 🧭 Tonal Calibration Scope – Desi.txt`, `docs/design/phase 5/# 🧭 Tonal Calibration Visibility –.txt` | `nova_backend/src/personality/tone_profile_store.py`, `interface_agent.py`, `nova_backend/src/brain_server.py`, `nova_backend/src/executors/os_diagnostics_executor.py`, `nova_backend/static/dashboard.js` | `nova_backend/tests/phase5/test_tone_profile_store.py`, `test_tone_controls_contract.py`, `nova_backend/tests/phase45/test_dashboard_tone_widget.py` | `PHASE_5_TONE_CONTROLS_RUNTIME_SLICE_2026-03-13.md` | Implemented |
| Notification scheduling boundary | `docs/PROOFS/Phase-5/NOTIFICATION_SCHEDULING_BOUNDARY_SPEC_2026-03-09.md` | `nova_backend/src/tasks/notification_schedule_store.py`, `nova_backend/src/brain_server.py`, `nova_backend/src/governor/governor.py`, `nova_backend/src/executors/os_diagnostics_executor.py`, `nova_backend/src/ledger/event_types.py` | `nova_backend/tests/phase5/test_notification_schedule_store.py`, `test_notification_scheduling_contract.py`, `nova_backend/tests/phase45/test_system_status_reporting_contract.py` | `PHASE_5_NOTIFICATION_SCHEDULING_RUNTIME_SLICE_2026-03-13.md` | Implemented |
| Pattern detection opt-in review | `docs/PROOFS/Phase-5/PATTERN_DETECTION_OPT_IN_GUARDRAILS_SPEC_2026-03-09.md` | `nova_backend/src/patterns/pattern_review_store.py`, `nova_backend/src/brain_server.py`, `nova_backend/static/dashboard.js` | `nova_backend/tests/phase5/test_pattern_review_store.py`, `test_pattern_review_contract.py`, `nova_backend/tests/phase45/test_dashboard_pattern_review_widget.py` | `PHASE_5_PATTERN_REVIEW_RUNTIME_SLICE_2026-03-13.md` | Implemented |

## Deferred / Out-of-Scope Tracks

| Track | Source | Current State | Why |
| --- | --- | --- | --- |
| Declarative identity/preferences | `docs/design/phase 5/📄 Phase 5 Roadmap.txt (corrected).txt` | Deferred to Phase 6 candidate track | No separate canonical design and not part of the ratified current package |
| Persistent cross-session thread substrate / restoration layer | `docs/PROOFS/Phase-6/PHASE_6_DEFERRED_FROM_PHASE_5_2026-03-13.md` | Deferred to Phase 6 candidate track | Current runtime intentionally keeps threads session-scoped; durable continuity is handled through governed memory |
| Delegated autonomy | `docs/design/phase 5/Delegated Autonomy.txt` | Future-direction only | Explicitly outside the current trust-facing Phase-5 runtime package |
| Consolidated APIs | the consolidated API planning note in `docs/design/phase 5/` | Future-direction only | Integration planning reference, not a required closure track |

## Runtime Documentation Entry Points
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/PHASE_5_RUNTIME_SURFACE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## Human-Language Entry Points
- `docs/reference/HUMAN_GUIDES/05_PROJECT_CONTINUITY_AND_MEMORY.md`
- `docs/reference/HUMAN_GUIDES/07_CURRENT_STATE.md`
- `docs/reference/HUMAN_GUIDES/13_BACKEND_RUNTIME_GUIDE.md`
- `docs/reference/HUMAN_GUIDES/20_PHASE_5_EXPLAINED.md`

## Closure Reading Order
1. `PHASE_5_CLOSED_ACT_2026-03-13.md`
2. `PHASE_5_RATIFICATION_ACT_2026-03-13.md`
3. `PHASE_5_ACTIVE_RUNTIME_CERTIFICATION_2026-03-13.md`
4. `PHASE_5_COMPLETION_EVIDENCE_MATRIX_2026-03-13.md`
5. `PHASE_5_IMPLEMENTATION_MAP_2026-03-13.md`
