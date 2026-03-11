# Phase 4.5 Runtime Alignment Note (2026-03-09)

Status: Runtime implementation addendum.

Runtime alignment update:

- Trust Panel and failure-ladder runtime signals remain active.
- Morning dashboard now includes concrete calendar integration (`CalendarSkill` + websocket/UI updates).
- Media (`id: 20`) and brightness (`id: 21`) capabilities are enabled in registry and routed through system-control execution paths.

Runtime truth source:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

Required interpretation rule:

- If roadmap language conflicts with runtime behavior, runtime truth wins.
- Design docs remain directional until ratified and reflected in runtime truth artifacts.

Governance hierarchy (authoritative order):

1. Constitution and canonical Tier-1 invariants.
2. Ratified phase locks, closure acts, and constitutional addenda.
3. Runtime truth artifacts and governed runtime behavior.
4. Design/reference documents.

Conflict rule:

- If runtime behavior and design text diverge, runtime is authoritative only when it remains within the constitutional and lock constraints and passes governance tests.
- Design documents must then be updated to reflect runtime truth.
