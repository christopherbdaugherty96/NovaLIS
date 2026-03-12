# Docs Authority Remediation Log
Date: 2026-03-12
Scope: Documentation-only remediation for runtime-truth and traceability findings
Status: Applied (no runtime code changes)

## Findings Addressed in Docs

### P0 - Conflicting runtime-truth authority docs
Applied:
- `docs/PHASE_4_RUNTIME_TRUTH.md` downgraded to historical status.
- Removed claim that it is the single authoritative runtime source.
- Added explicit authority pointers to current runtime/proof artifacts.

Authoritative runtime references now:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/current_runtime/RUNTIME_TRUTH_ADDENDUM_2026-03-12.md`
- `docs/PROOFS/Phase-5/PHASE_5_PROOF_PACKET_INDEX.md`

### P2 - Broken internal doc references
Applied path/link repairs:
- `docs/NOVA_PHASE4_MASTER_STATUS.md`
  - fixed stale upper-case canonical matrix path references
  - fixed stale legacy runtime-truth path references
- `docs/Master Capability Matrix.md`
  - fixed comparison-doc path to `docs/NOVA_PHASE4_PHASE7_CODE_COMPARISON.md`
- `docs/NOVA_CAPABILITY_MASTER.md`
  - fixed comparison-doc path to `docs/NOVA_PHASE4_PHASE7_CODE_COMPARISON.md`
- `docs/NOVA_PHASE4_PHASE7_CODE_COMPARISON.md`
  - fixed stale references to `docs/NOVA_CAPABILITY_MASTER.md`
  - replaced non-existent runtime-feature-flags suggestion with current runtime fingerprint reference
- `docs/canonical/archive-phase4/PHASE_4_REVIEW_PACKET.md`
  - fixed stale capability-master reference path

## Documentation Clarification Added for Auditor Blind Spots
Created:
- `docs/current_runtime/RUNTIME_TRUTH_ADDENDUM_2026-03-12.md`

This addendum documents known generated-auditor blind spots without changing code:
- calendar false-negative risk in generated runtime status
- phase table hardcoded `Phase 5 | DESIGN` mismatch risk
- BYPASS scan scope under-reporting risk

## Pending (Code/Auditor Work - Not changed in this pass)
- runtime auditor calendar detection logic
- runtime auditor phase-5 derivation logic
- BYPASS scan allowlist/scope update
- media executor success/failure semantics

## Governance Note
This remediation intentionally changes documentation only. No runtime behavior, capability routing, or execution authority logic was modified.
