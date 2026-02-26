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

---

## 7) Amendment — Governance Hardening (Strictness Restoration)

**Date:** 2026-02-25  
**Commit:** See latest governance-hardening commit in git history.  
**Scope:** Enforcement-only hardening (no capability expansion, no authority expansion).

### Changes

- Restored adversarial scan strictness for active source tree by removing broad subtree carve-outs and keeping only archive/quarantine exemptions.
- Tightened timeout fail-closed test to require lifecycle ledger events (`ACTION_ATTEMPTED` + `ACTION_COMPLETED`) and `success=False` result with no partial successful data.
- Added import-surface integrity checks to ensure archive/quarantine modules are not imported by runtime files.
- Added governor bypass coverage and single-request/single-action chain guard tests.

### Verification

- Full suite command:

```bash
cd /workspace/NovaLIS/nova_backend && pytest -q
```

- Result at amendment time: `31 passed`.

### Constitutional Statement

This amendment is enforcement tightening only. It does not alter enabled capabilities, governor authority boundaries, or execution phase state.


---

## 8) Amendment — Phase-4.2 Staging Verification Update

**Date:** 2026-02-25  
**Commit:** See latest Phase-4.2 staging commit in git history.  
**Scope:** Validation/status update for staged escalation path and governance checks.

### Verification

- Full suite command:

```bash
cd /workspace/NovaLIS/nova_backend && pytest -q
```

- Result at amendment time: `35 passed`.

### Notes

- Runtime remains governed by existing authority spine.
- This amendment records verification status and does not reclassify capability authority.

---

## 9) Amendment — Governed TTS (Capability 18) Integration

**Date:** 2026-02-26  
**Commit:** See latest governed-TTS commit in git history.  
**Scope:** Phase-4 governed output modality reflection (voice input → governed speech output).

### Changes

- Capability `18` updated to `speak_text` and enabled in registry.
- Capability `22` reserved for `open_file_folder` and remains disabled.
- Added governed `tts_executor` routed exclusively through `Governor._execute` for capability `18`.
- Added manual invocation parsing for `"speak that"`, `"read that"`, and `"say it"` in `GovernorMediator`.
- Added brain-server channel tracking (`voice` vs `text`), last-response memory, and success-gated auto-speak invocation via Governor after UI response completion.

### Constitutional Statement

This amendment introduces no new autonomy, no new hidden execution paths, and no bypass of the authority spine. Speech output remains fully governed, queue-limited, execute-boundary gated, and ledger-auditable.

---

## 10) Amendment — Scope Fence Verification (Single-PR Merge Fence)

**Date:** 2026-02-26  
**Commit:** See latest scope-fence verification commit in git history.  
**Scope:** Mechanical verification and consistency alignment prior to merge.

### Verifications

- TTS execution path remains Governor-mediated only (`handle_governed_invocation(18)` → `_execute` → `tts_executor`).
- Added adversarial spine checks asserting no direct `TTSEngine.speak()` outside `tts_executor` and no direct TTS execution path in `brain_server`.
- Conversation layer remains non-authorizing (no ActionRequest construction and no direct executor invocation).
- Registry risk semantics documented: `confirm` is treated as a policy-confirmation class distinct from low/high risk levels (no runtime schema changes).
- Runtime truth snapshot documented in `docs/CANONICAL/PHASE_4_RUNTIME_TRUTH.md` with live capabilities 16/17/18.

### Constitutional Statement

This amendment tightens merge-time guarantees and removes classification drift. It does not expand execution authority beyond the already-enabled capability set.
