# docs/capability_verification — Live verification

This folder holds **live pass/fail checks against a running build** — the strongest "does it
actually work right now" evidence genre. It follows **QA Rule #1**: confirm the running process
matches current `main` before testing; restart if not.

**Dated checks are evidence at their date, not a standing claim.** For what is true now, use the
generated [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

## Entry points

- **Canonical inventory (current):** [`CAPABILITY_INVENTORY.md`](CAPABILITY_INVENTORY.md) — the
  single evidence-backed "what works" file. Verification updates this rather than spawning
  scattered docs.
- **Latest live check:** [`LIVE_VERIFICATION_2026-07-07.md`](LIVE_VERIFICATION_2026-07-07.md).
- **Method:** [`FRAMEWORK.md`](FRAMEWORK.md) (P1–P5) and [`STATUS.md`](STATUS.md) (certification
  progress; use `python scripts/certify_capability.py status` for exact pass/fail).
- **Live checklists:** [`live_checklists/`](live_checklists/) — per-capability manual checklists.

Older dated `*_2026-04-2x.md` simulations and smoke reports are **historical** — kept for the
audit trail, superseded by the current inventory and the latest live check.

## One of three evidence genres — kept separate

Do not merge with [`../PROOFS/`](../PROOFS/) (implementation proof packets) or
[`../demo_proof/`](../demo_proof/) (demo-flow captures). See
[`../CANONICAL/06_TEST_AND_PROOF_TRUTH.md`](../CANONICAL/06_TEST_AND_PROOF_TRUTH.md).
