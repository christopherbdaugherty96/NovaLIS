# docs/audits — Dated review evidence

This folder holds **dated audit and review passes** — repo alignment audits, live-simulation
results, conversation-quality benchmarks, and workflow verifications. Each file is evidence of
what a review found **on its date**.

**Not runtime truth.** An audit reflects the repo at its date and can be stale now. For what is
true today use the generated
[`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md) and
[`../CANONICAL/00_INDEX.md`](../CANONICAL/00_INDEX.md).

## How to read

Titles carry the date — trust the newest for a given subject. Rough currency:

- **Current custody input:** `EGRESS_INVENTORY_2026-10-08.md` maps outbound runtime and
  delegated-egress paths on `main@bab4a6c`; it is an implementation design input, not proof
  that provider-neutral Data-Out enforcement exists.
- **More recent signals:** `USER_SIMULATION_RESULTS_2026-07-06.md`,
  `PERSONALITY_GATE_WRAPPING_LIVE_VALIDATION_2026-06-05.md`,
  `UI_SIMPLIFICATION_AUDIT_2026-05-26.md`, and the 2026-05-19 conversation-model / simulation
  result set.
- **Historical passes:** the 2026-04 review series (`SESSION_DEEP_AUDIT_2026-04-22.md`, the
  `2026-04-24/25/26` subfolders, `PASS1/PASS3/PASS4` alignment audits) — kept for the audit
  trail, superseded by later work.

This is a review-evidence genre, distinct from implementation proofs
([`../PROOFS/`](../PROOFS/)) and live verification
([`../capability_verification/`](../capability_verification/)).
