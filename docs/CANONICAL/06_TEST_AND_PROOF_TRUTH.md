# 06 — Test and Proof Truth (what evidence exists)

**Status: mixed.** Tests are runtime-backed; proof packets are dated artifacts whose currency
varies. Read each artifact's own date, not just its title.

## Three distinct evidence genres (kept separate on purpose)

Per `docs/todo/DOC_CLEANUP.md`, these are **not merged** — they are different kinds of evidence:

| Folder | Genre | What it is |
| --- | --- | --- |
| [`../PROOFS/`](../PROOFS/) | Implementation proof packets | Per-phase/per-capability proof that a boundary or feature was built and checked. |
| [`../demo_proof/`](../demo_proof/) | Demo / walkthrough evidence | Captured runs of user-facing flows (daily brief, memory loop, conversation+search). |
| [`../capability_verification/`](../capability_verification/) | Live verification | Observed pass/fail against a running build, following QA Rule #1. |

## Current vs historical proofs

- **Proof index / currency map:** [`../PROOFS/README.md`](../PROOFS/README.md) — lists the
  current canonical packet entry points and which artifacts are historical vs generated.
- **Latest live verification:**
  [`../capability_verification/LIVE_VERIFICATION_2026-07-07.md`](../capability_verification/LIVE_VERIFICATION_2026-07-07.md).
- Older per-phase proof packets (Phase-4 … Phase-8) are **historical** records of the state at
  their date. They remain valid as evidence of *what was proven then*, not as a claim about today.

## Tests as living proof

- `nova_backend/tests/` holds runtime, governance, phase, and regression coverage — this is the
  strongest continuously-checked evidence.
- Root **structural runtime smoke proof**: `python scripts/prove_runtime_truth.py` checks app
  import, local routes, `/ws`, capability registry loading, and Governor confirmation/unknown-
  capability blocking. It is a structural smoke proof only — a PASS is NOT comprehensive runtime
  truth and does NOT prove response validity, inference, model-lock enforcement, receipt
  persistence, live providers, or authorization integrity. See the script docstring for full
  non-goals.
- Approval-gate certification (Cap 22 / Cap 64) closeout:
  [`../status/APPROVAL_GATE_CERTIFICATION_CLOSEOUT_2026-05-19.md`](../status/APPROVAL_GATE_CERTIFICATION_CLOSEOUT_2026-05-19.md).

## Naming reconciliation (recorded, not a bug)

`PROOFS/Trust-Panel/` contains a proven trust-*page* MVP, while the runtime gaps list "Trust
Panel not implemented." Both are true: the trust **page** MVP was proven; the full Trust
**Panel** concept (Phase 4.5) remains open. Do not read this as a contradiction.

## Full-suite verification status

[VERIFIED CLEAN 2026-07-27] The complete test suite passed on merged main after PRs #315 and
#316: 3799 passed in 6:46, exit code 0, with no pytest timeout and no external browser or
email-client launch. The historical high-completion stall did not reproduce. Targeted suites
remain useful for bounded development checks, but are no longer a substitute for the full suite —
which now completes. The 180-second pytest-timeout guard remains enabled.
