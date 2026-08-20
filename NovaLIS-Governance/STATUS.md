# NOVA Governance Status

**Status: SUPERSEDED AS A CURRENT-STATUS SURFACE — 2026-08-20**

This file was originally an April 2026 concise governance snapshot. It accumulated phase, proof, capability, and next-work claims that later diverged from the generated runtime and current operational truth.

Do **not** use this file to answer what Nova's current phase, capability readiness, proof status, or active development lane is.

## Current sources

Use these instead:

1. `docs/current_runtime/CURRENT_RUNTIME_STATE.md` — generated runtime structure/capability/phase evidence for what its generator measures.
2. `docs/current_runtime/GOVERNANCE_MATRIX.md` and `GOVERNANCE_MATRIX_TREE.md` — generated governed-capability structure.
3. `docs/current_runtime/ROUTE_PROTECTION_COVERAGE.md` — generated route-protection classification.
4. `docs/CANONICAL/03_GOVERNANCE_TRUTH.md` — reconciled interpretation of Nova's three control planes and governance boundaries.
5. `docs/status/CURRENT_WORK_STATUS.md` — current human-maintained development state.
6. `docs/status/DAILY_COMMAND_CENTER.md` — current operational lane.
7. `docs/CANONICAL/07_ROADMAP_TRUTH.md` and Issue #343 — current ordering/gates.

## Durable governance principles retained from this historical snapshot

The following principles remain useful, subject to the more precise current control-plane model:

```text
intelligence != authority
capability != authority
memory != authority
recommendation != permission
request acceptance != verified effect
```

For registered governed capabilities, the canonical execution spine remains:

```text
User
-> GovernorMediator
-> Governor
-> CapabilityRegistry
-> SingleActionQueue
-> LedgerWriter
-> ExecuteBoundary
-> Executor
```

Nova also has local operator/administrative and bounded agent/routine planes. They are distinct from the governed-capability plane and must not silently increase one another's authority.

## Why this file is no longer synchronized directly

Duplicating live phase matrices, capability counts, certification state, and current priorities here creates a second manually maintained status authority that can drift again.

Wave A1 therefore retires this file as a **current** status surface instead of copying another transient snapshot into it.

Git history preserves the April 2026 content as historical evidence.
