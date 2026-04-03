from __future__ import annotations

# Compile-time style phase gate. This constant is intentionally static in source
# so 4.2 remains runtime-locked unless a build updates the value.
#
# Runtime grounding (2026-04-02):
#   Phase 3.5–7: complete
#   Phase 8: active, narrow — OpenClaw home-agent foundation shipped, full
#             envelope execution still deferred
#   Phase 9: design and isolated prep slices merged (token budget gate,
#             cap 63 wire-up), but NOT yet the live runtime state
#   BUILD_PHASE reflects the highest phase with merged prep work.
#   CURRENT_RUNTIME_STATE.md is the authoritative runtime truth.
BUILD_PHASE = 8
PHASE_4_2_ENABLED = BUILD_PHASE >= 5
