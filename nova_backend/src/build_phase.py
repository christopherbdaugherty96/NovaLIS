from __future__ import annotations

# Compile-time style phase gate. This constant is intentionally static in source
# so 4.2 remains runtime-locked unless a build updates the value.
BUILD_PHASE = 9
PHASE_4_2_ENABLED = BUILD_PHASE >= 5
