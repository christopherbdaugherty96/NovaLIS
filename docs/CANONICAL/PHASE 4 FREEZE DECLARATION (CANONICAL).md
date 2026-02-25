# PHASE 4 FREEZE DECLARATION (CANONICAL)

**Status:** ACTIVE (locked)  
**Phase:** 4 (execution kernel stabilization)  
**Repository:** NovaLIS  
**Freeze anchor commit:** `db91e97c4991fe766abbadf43b2a3e3ace144c92`  
**Declaration commit:** This document-introducing commit (`git log -- docs/CANONICAL/PHASE_4_FREEZE.md`).  
**Tag reference:** `phase-4-kernel-stable` (not present in current local refs at declaration time)  
**Freeze tag (this declaration):** `phase-4-freeze-final`

---

## 1) Constitutional Freeze Scope

This freeze seals the Phase 4 authority/kernel surface. While ACTIVE, the following are prohibited:

- No new capabilities enabled.
- No new execution routes.
- No Governor authority expansion.
- No NetworkMediator surface expansion.
- No phase reclassification or stealth unlock.

Allowed during freeze:

- Documentation alignment.
- Tests and CI enforcement.
- Refactors with zero behavioral change.

---

## 2) Frozen Runtime State

### Enabled capabilities (registry-authoritative)

- `16` — `governed_web_search` (`enabled: true`)
- `17` — `open_website` (`enabled: true`)

### Declared but disabled capabilities

- `18`, `19`, `20`, `21`, `32`, `48` (`enabled: false`)

### Execution gate

- `GOVERNED_ACTIONS_ENABLED = True` (Phase 4 runtime unlocked but frozen at current scope).

---

## 3) Freeze Assertions (explicit lock confirmations)

At this checkpoint:

- No hidden execution paths are intentionally introduced by this declaration.
- No background cognition/autonomous loops are introduced by this declaration.
- No multi-step orchestration authority is introduced by this declaration.
- No memory persistence authority beyond existing ledger mechanisms is introduced by this declaration.
- No DeepSeek live integration is activated by this declaration.

---

## 4) Protected Constitutional Files During Freeze

Changes to any file below are considered constitutional modifications and require explicit freeze amendment review:

- `nova_backend/src/governor/governor.py`
- `nova_backend/src/governor/network_mediator.py`
- `nova_backend/src/governor/execute_boundary/execute_boundary.py`
- `nova_backend/src/config/registry.json`

All new intelligence/conversation expansion work should be isolated under:

- `nova_backend/src/conversation/`

---

## 5) Verification Snapshot at Freeze Declaration

Executed command:

```bash
cd /workspace/NovaLIS/nova_backend && pytest -q
```

Result summary at declaration time:

- Test suite does **not** fully pass in current repo state.
- Failures are primarily pre-existing invariant/test-drift issues (Invocation unpacking assumptions, legacy phase-3.5 seal expectation, and policy-test findings in adversarial suite).

This declaration freezes the Phase 4 authority surface; it does not claim full red-to-green conversion of all historical tests.

---

## 6) Amendment Rule

Any proposed change that modifies frozen authority behavior must:

1. Add a dated amendment section to this file.
2. Include exact commit hash and rationale.
3. Include explicit before/after capability-state impact.
4. Include targeted tests proving no unintended authority expansion.

Without this, modifications are out-of-constitution for Phase 4 freeze.
