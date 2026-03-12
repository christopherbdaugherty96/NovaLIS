# Canonical Document Map
Updated: 2026-03-12
Status: Active

## Purpose
This map classifies documents under `docs/canonical` so reviewers can quickly identify what is authoritative now vs historical context.

## Authority Order
1. Constitutional canon (identity + invariant law)
2. Ratified phase locks/closure acts in `docs/PROOFS`
3. Runtime truth (`docs/current_runtime`) + verified tests
4. Design docs (`docs/design`) and planning artifacts

## Active Canonical Core
- `docs/canonical/NOVA COMPLETE CONSTITUTIONAL BLUEPRINT v1.9.txt`
  - Constitutional law source for identity/invariants
  - Runtime capability counts/statuses inside this file may be historical snapshots

## Current Runtime Canon References
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/PROOFS/Phase-4/`
- `docs/PROOFS/Phase-4.5/`
- `docs/PROOFS/Phase-5/PHASE_5_PROOF_PACKET_INDEX.md`
- `docs/PROOFS/Phase-5/PHASE_5_CUMULATIVE_IMPLEMENTATION_STATE_2026-03-12.md`

## Historical Canonical Artifacts (Keep for Traceability)
- `docs/canonical/archive-phase4/# 🧬 NOVA PHASE 4 ROADMAP(updated).txt`
- `docs/canonical/archive-phase4/NOVA-PHASE4-ACTION-PLAN-v1.0.txt`
- `docs/canonical/archive-phase4/PHASE4_CONSTITUTIONAL_MISMATCH_AUDIT.md`
- `docs/canonical/archive-phase4/PHASE_4_FREEZE.md`
- `docs/canonical/archive-phase4/PHASE_4_FREEZE1.md`
- `docs/canonical/archive-phase4/PHASE_4_REVIEW_PACKET.md`
- `docs/canonical/archive-phase4/full code audit 2-19-26.txt`

These are valid historical evidence/working artifacts, but they are not the source of current runtime truth.

## Cleanup Actions Applied (2026-03-12)
- Added status banners to historical artifacts to reduce accidental misuse.
- Added canonical pointer updates in `docs/canon/README.md`.
- Added this map for explicit canonical vs historical separation.

## Maintenance Rule
When runtime behavior changes:
1. Update runtime/proof artifacts first.
2. Update this map if artifact classification changes.
3. Keep historical artifacts, but ensure they carry a clear status banner.
