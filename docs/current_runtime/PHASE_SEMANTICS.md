# NOVA Phase Semantics

## Purpose
This document explains how multiple phase markers can coexist without contradiction.

## The Three Phase Signals

### 1. BUILD_PHASE
Location: `nova_backend/src/build_phase.py`

Meaning:
A static source-level gate used to unlock or constrain code paths at runtime.

Use when asking:
- What phase is intentionally unlocked in source?
- Which compile/runtime gates are enabled?

---

### 2. Registry Phase
Location: `nova_backend/src/config/registry.json`

Meaning:
A configuration epoch / rollout marker for the capability registry and packaged runtime profile.

Use when asking:
- What capability-era config is this registry aligned to?
- What rollout generation is active?

---

### 3. CURRENT_RUNTIME_STATE.md
Location: `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

Meaning:
Generated operator-facing runtime truth derived from code, enabled capabilities, and auditor checks.

Use when asking:
- What is live right now?
- Which phases are operationally complete / active?
- What discrepancies currently exist?

---

## Priority Order
When signals differ:
1. `CURRENT_RUNTIME_STATE.md` = operator truth
2. `BUILD_PHASE` = source gate truth
3. Registry phase = configuration marker

## Example
It is valid for:
- `BUILD_PHASE = 8`
- Registry phase = `8`
- `CURRENT_RUNTIME_STATE.md` to report some Phase 9 surfaces ACTIVE

This means Phase 9 behavior exists in runtime, while the static build gate remains conservative.

## Maintenance Rule
When confusion appears:
1. Check generated runtime truth first.
2. Update stale comments or docs.
3. Expand auditor coverage if probes are outdated.
4. Only change BUILD_PHASE when intentionally widening the static gate.
