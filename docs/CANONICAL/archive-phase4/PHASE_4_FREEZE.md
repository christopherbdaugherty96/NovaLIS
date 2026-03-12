> STATUS (2026-03-12): HISTORICAL PHASE-4 ARTIFACT
> This file is retained for traceability and historical audit context.
> For current canonical runtime truth, use:
> - docs/current_runtime/CURRENT_RUNTIME_STATE.md
> - docs/PROOFS/Phase-5/PHASE_5_PROOF_PACKET_INDEX.md
> - docs/canonical/CANONICAL_DOCUMENT_MAP.md
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

## 2) Frozen Runtime State (as of 2026-02-26, amended 2026-03-03)

### Enabled capabilities (registryâ€‘authoritative)
- `16` â€” `governed_web_search` (`enabled: true`)
- `17` â€” `open_website` (`enabled: true`)
- `18` â€” `speak_text` (`enabled: true`)
- `19` â€” `volume_up_down` (`enabled: true`) *(see Section 10)*
- `20` â€” `media_play_pause` (`enabled: true`) *(see Section 10)*
- `21` â€” `brightness_control` (`enabled: true`) *(see Section 10)*
- `32` â€” `os_diagnostics` (`enabled: true`) *(see Section 10)*

### Declared but disabled
- `22` (`open_file_folder`), `48` (`multi_source_reporting`) (`enabled: false`)

### Execution gate
- `GOVERNED_ACTIONS_ENABLED = True` (Phaseâ€‘4 runtime unlocked but frozen at current scope).

---

## 3) Freeze Assertions

At this checkpoint:

- No hidden execution paths are present.
- No background cognition/autonomous loops exist.
- No multi-step orchestration authority is granted.
- No memory persistence beyond ledger mechanisms.
- DeepSeek is **not** liveâ€‘integrated (any cognitive work is nonâ€‘authorizing).

---

## 4) Protected Constitutional Files

Changes to any file below require explicit freeze amendment review:

- `nova_backend/src/governor/governor.py`
- `nova_backend/src/governor/network_mediator.py`
- `nova_backend/src/governor/execute_boundary/execute_boundary.py`
- `nova_backend/src/config/registry.json`

All new intelligence/conversation expansion work **must** be isolated under `nova_backend/src/conversation/` and remain nonâ€‘authorizing.

---

## 5) Amendment â€” Governance Hardening (2026-02-25)

**Scope:** Enforcementâ€‘only hardening (no capability expansion).  
**Changes:** Restored adversarial scan strictness, tightened timeout failâ€‘closed test, added importâ€‘surface integrity checks.  
**Verification:** `31 passed` at amendment time.

---

## 6) Amendment â€” Phaseâ€‘4.2 Staging Verification (2026-02-25)

**Scope:** Validation of staged escalation path.  
**Verification:** `35 passed` at amendment time.  
**Note:** No authority reclassification.

---

## 7) Amendment â€” Governed TTS (Capability 18) Integration (2026-02-26)

**Scope:** Phaseâ€‘4 governed output modality reflection (voice input â†’ governed speech output).  
**Changes:**  
- Capability `18` renamed to `speak_text` and enabled.  
- Capability `22` reserved for `open_file_folder` (disabled).  
- Added `tts_executor` routed exclusively through `Governor._execute`.  
- Added manual invocation parsing (`speak that`, `read that`, `say it`).  
- Added brainâ€‘server channel tracking, lastâ€‘response memory, and successâ€‘gated autoâ€‘speak via Governor after UI response.  

**Constitutional Statement:** No new autonomy, no hidden execution paths, no bypass of authority spine. Speech output remains fully governed, queueâ€‘limited, executeâ€‘boundary gated, and ledgerâ€‘auditable.

---

## 8) Amendment â€” Scope Fence Verification (2026-02-26)

**Scope:** Mechanical verification prior to merge.  
**Verifications:**  
- TTS execution path remains Governorâ€‘mediated only.  
- Adversarial spine checks assert no direct `TTSEngine.speak()` outside `tts_executor`.  
- Conversation layer remains nonâ€‘authorizing.  
- Registry risk semantics documented (`confirm` as policyâ€‘confirmation marker, not a numeric tier).  
- Runtime truth snapshot updated to reflect live capabilities 16/17/18.

---

## 9) Amendment Rule

Any proposed change that modifies frozen authority behavior must:

1. Add a dated amendment section to this file.
2. Include exact commit hash and rationale.
3. Include explicit before/after capabilityâ€‘state impact.
4. Include targeted tests proving no unintended authority expansion.

Without this, modifications are outâ€‘ofâ€‘constitution for Phase 4 freeze.

---

## 10) Amendment â€” Device Control Capabilities Enablement (2026-03-03)

**Scope:** Documentation correction â€” capabilities 19, 20, 21, 32 were enabled in `registry.json` prior to this amendment. This section documents that enablement.

**Capabilities enabled:**

| ID | Name | Executor | Parser |
|----|------|----------|--------|
| 19 | `volume_up_down` | `src/executors/volume_executor.py` (`VolumeExecutor`) | `governor_mediator.py` â€” `volume up/down`, `set volume <level>` |
| 20 | `media_play_pause` | `src/executors/media_executor.py` (`MediaExecutor`) | `governor_mediator.py` â€” `play`, `pause`, `resume` |
| 21 | `brightness_control` | `src/executors/brightness_executor.py` (`BrightnessExecutor`) | `governor_mediator.py` â€” `brightness up/down`, `set brightness <level>` |
| 32 | `os_diagnostics` | `src/executors/os_diagnostics_executor.py` (`OSDiagnosticsExecutor`) | `governor_mediator.py` â€” `system check`, `system status` |

**Constitutional Statement:**

- All four capabilities execute through the same Governor spine (`Governor._execute()`) as capabilities 16, 17, 18.
- Same authority chain: GovernorMediator â†’ Governor â†’ ExecuteBoundary â†’ CapabilityRegistry â†’ SingleActionQueue â†’ LedgerWriter â†’ Executor.
- Same ledger audit: `ACTION_ATTEMPTED` before execution, `ACTION_COMPLETED` after.
- Same execute boundary: SingleActionQueue prevents concurrent execution.
- No new authority surface: these are low-risk, local-only, non-networked capabilities. No outbound network calls.
- No new autonomy, no hidden execution paths, no bypass of authority spine.

**Capabilities remaining disabled:**
- `22` (`open_file_folder`) â€” `enabled: false`
- `48` (`multi_source_reporting`) â€” `enabled: false`
