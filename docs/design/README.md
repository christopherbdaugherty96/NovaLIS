# Design Documentation Index

Read this first: `docs/design/DESIGN_AUTHORITY.md`

Purpose:
- `docs/design/` contains intended architecture and phase direction.
- It does not define runtime behavior.
- Cross-phase planning realignments should be captured in explicit planning packets rather than overwriting runtime truth.

Canonical runtime truth:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/PROOFS/`

Current cross-phase planning packet:
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`

Current bounded conversational planning packet:
- `docs/design/CONVERSATIONAL_CORE_PHASE_PLAN_2026-03-19.md`

Current conversational-flow and silent-governor planning packet:
- `docs/design/CONVERSATIONAL_FLOW_AND_SILENT_GOVERNOR_PLAN_2026-03-21.md`

Current bounded style planning packet:
- `docs/design/NOVA_STYLE_LAYER_PLAN_2026-03-20.md`

Current bounded speech/input naturalness planning packet:
- `docs/design/SPEECH_AND_INPUT_NATURALNESS_PLAN_2026-03-20.md`

Current user-observed assistant utility and UI audit packet:
- `docs/design/NOVA_ASSISTANT_UTILITY_AND_UI_AUDIT_2026-03-20.md`

Current user-observed local project and assistant utility audit packet:
- `docs/design/NOVA_LOCAL_PROJECT_AND_ASSISTANT_UTILITY_AUDIT_2026-03-20.md`

Current conversational/style baseline on `main`:
- `39b3d20` - Speech & Input Naturalness Stage 1-2 checkpoint
- `d0a80c3` - Nova Style Layer Stage 2 checkpoint

Current recommended next-step posture:
- pause and evaluate the new baseline in use
- if work resumes, prefer a fresh small branch for a non-chat style consistency audit before broader new conversation behavior
- if the next target is conversation feel rather than surface consistency, use the bounded conversational-flow and silent-governor packet rather than broadening authority or personality work

Canonical design phase folders:
- `Phase 4`
- `Phase 4.2`
- `Phase 4.5`
- `phase 5`
- `Phase 6`
- `Phase 7`
- `Phase 8`
- `Phase 9`
- `Phase 10`

Historical/superseded:
- `archive(phase 4)` (legacy)
- `archive` (new consolidation target)
