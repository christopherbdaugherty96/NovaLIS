from __future__ import annotations

# Compile-time style phase gate. This constant is intentionally static in source
# so 4.2 remains runtime-locked unless a build updates the value.
#
# Phase semantics:
#   BUILD_PHASE is a source-level compile/runtime gate marker.
#   It is NOT the authoritative statement of every live runtime surface.
#
# Current interpretation:
#   - BUILD_PHASE = highest phase intentionally unlocked by static source gate
#   - registry.json phase = configuration / rollout epoch marker
#   - CURRENT_RUNTIME_STATE.md = generated authoritative runtime truth
#
# Runtime grounding (updated 2026-04-22):
#   Phase 3.5–7: complete
#   Phase 8: active source gate and canonical build marker
#   Phase 9: some live runtime surfaces may appear in generated runtime truth
#            when implemented capabilities and auditor checks detect them,
#            even while BUILD_PHASE remains 8
#
# If these surfaces diverge unexpectedly, treat CURRENT_RUNTIME_STATE.md as the
# operator-facing source of truth and update stale comments or probe coverage.
BUILD_PHASE = 8
PHASE_4_2_ENABLED = BUILD_PHASE >= 5
