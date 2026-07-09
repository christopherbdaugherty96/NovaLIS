# docs/PROOFS — Implementation proof packets

This folder holds **implementation and verification evidence** — proof that a boundary, gate, or
capability was built and checked. Proofs are **dated artifacts**: each one is evidence of the
state at its date, not a claim about today. For what is true now, use
[`../CANONICAL/00_INDEX.md`](../CANONICAL/00_INDEX.md) and the generated
[`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

## How to read an artifact's currency

- **Generated** — produced from code by a script; regenerating reflects the live surface.
- **Current** — the latest packet for its subject; still the entry point.
- **Historical** — a prior packet kept for the audit trail; superseded by a newer one but not
  wrong about its own date.

When two packets cover the same subject, the newest dated one is current and the rest are
historical. Titles are not enough — check the date in the file.

## Current canonical packet entry points

- `Phase-4/PHASE_4_PROOF_PACKET_INDEX.md`
- `Phase-4.2/PHASE_4_2_PROOF_PACKET_INDEX.md`
- `Phase-4.5/PHASE_4_5_PROOF_PACKET_INDEX.md`
- `Phase-5/PHASE_5_PROOF_PACKET_INDEX.md`
- `Phase-7/PHASE_7_PROOF_PACKET_INDEX.md`

## Latest cross-phase verification

- `CAPABILITY_VERIFICATION_AUDIT_2026-03-25.md` (historical cross-phase snapshot).
- For the **latest live** capability check, leave this folder and read
  [`../capability_verification/LIVE_VERIFICATION_2026-07-07.md`](../capability_verification/LIVE_VERIFICATION_2026-07-07.md).

## This is one of three evidence genres — kept separate

Do not merge these; they answer different questions
(see [`../CANONICAL/06_TEST_AND_PROOF_TRUTH.md`](../CANONICAL/06_TEST_AND_PROOF_TRUTH.md)):

- **`docs/PROOFS/`** (here) — implementation proof packets.
- **`docs/demo_proof/`** — captured runs of user-facing demo flows.
- **`docs/capability_verification/`** — live pass/fail against a running build (QA Rule #1).

## Naming note (recorded, not a discrepancy)

`Trust-Panel/` proves a trust-**page** MVP. The runtime gaps list separately notes the full
Trust **Panel** concept (Phase 4.5) is not implemented. Both are true.
