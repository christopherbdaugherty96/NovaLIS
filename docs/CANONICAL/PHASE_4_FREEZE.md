# PHASE 4 FREEZE DECLARATION (CANONICAL)

**Status:** ACTIVE (locked)  
**Phase:** 4 (execution kernel stabilization)  
**Repository:** NovaLIS  
**Freeze anchor commit:** `db91e97c4991fe766abbadf43b2a3e3ace144c92`  
**Freeze tag:** `phase-4-freeze-final`

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

## 2) Frozen Runtime State (as of 2026-02-26)

### Enabled capabilities (registry‑authoritative)
- `16` — `governed_web_search` (`enabled: true`)
- `17` — `open_website` (`enabled: true`)
- `18` — `speak_text` (`enabled: true`)

### Declared but disabled
- `19`, `20`, `21`, `22`, `32`, `48` (`enabled: false`)

### Execution gate
- `GOVERNED_ACTIONS_ENABLED = True` (Phase‑4 runtime unlocked but frozen at current scope).

---

## 3) Freeze Assertions

At this checkpoint:

- No hidden execution paths are present.
- No background cognition/autonomous loops exist.
- No multi-step orchestration authority is granted.
- No memory persistence beyond ledger mechanisms.
- DeepSeek is **not** live‑integrated (any cognitive work is non‑authorizing).

---

## 4) Protected Constitutional Files

Changes to any file below require explicit freeze amendment review:

- `nova_backend/src/governor/governor.py`
- `nova_backend/src/governor/network_mediator.py`
- `nova_backend/src/governor/execute_boundary/execute_boundary.py`
- `nova_backend/src/config/registry.json`

All new intelligence/conversation expansion work **must** be isolated under `nova_backend/src/conversation/` and remain non‑authorizing.

---

## 5) Amendment — Governance Hardening (2026-02-25)

**Scope:** Enforcement‑only hardening (no capability expansion).  
**Changes:** Restored adversarial scan strictness, tightened timeout fail‑closed test, added import‑surface integrity checks.  
**Verification:** `31 passed` at amendment time.

---

## 6) Amendment — Phase‑4.2 Staging Verification (2026-02-25)

**Scope:** Validation of staged escalation path.  
**Verification:** `35 passed` at amendment time.  
**Note:** No authority reclassification.

---

## 7) Amendment — Governed TTS (Capability 18) Integration (2026-02-26)

**Scope:** Phase‑4 governed output modality reflection (voice input → governed speech output).  
**Changes:**  
- Capability `18` renamed to `speak_text` and enabled.  
- Capability `22` reserved for `open_file_folder` (disabled).  
- Added `tts_executor` routed exclusively through `Governor._execute`.  
- Added manual invocation parsing (`speak that`, `read that`, `say it`).  
- Added brain‑server channel tracking, last‑response memory, and success‑gated auto‑speak via Governor after UI response.  

**Constitutional Statement:** No new autonomy, no hidden execution paths, no bypass of authority spine. Speech output remains fully governed, queue‑limited, execute‑boundary gated, and ledger‑auditable.

---

## 8) Amendment — Scope Fence Verification (2026-02-26)

**Scope:** Mechanical verification prior to merge.  
**Verifications:**  
- TTS execution path remains Governor‑mediated only.  
- Adversarial spine checks assert no direct `TTSEngine.speak()` outside `tts_executor`.  
- Conversation layer remains non‑authorizing.  
- Registry risk semantics documented (`confirm` as policy‑confirmation marker, not a numeric tier).  
- Runtime truth snapshot updated to reflect live capabilities 16/17/18.

---

## 9) Amendment Rule

Any proposed change that modifies frozen authority behavior must:

1. Add a dated amendment section to this file.
2. Include exact commit hash and rationale.
3. Include explicit before/after capability‑state impact.
4. Include targeted tests proving no unintended authority expansion.

Without this, modifications are out‑of‑constitution for Phase 4 freeze.