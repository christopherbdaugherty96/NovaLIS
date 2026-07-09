# docs/demo_proof — Demo / walkthrough evidence

This folder holds **captured runs of user-facing flows** — daily brief, conversation + search,
OpenClaw read-only workflows, brain dry-runs, request-understanding cards. Each subfolder is a
dated capture of what a flow actually did on that date.

**This is dated evidence, not runtime truth.** A capture proves behavior at its date; it is not a
claim about today. For what is true now, use
[`../CANONICAL/00_INDEX.md`](../CANONICAL/00_INDEX.md) and the generated
[`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

## One of three evidence genres — kept separate

Do not merge these (see [`../CANONICAL/06_TEST_AND_PROOF_TRUTH.md`](../CANONICAL/06_TEST_AND_PROOF_TRUTH.md)):

- **`docs/demo_proof/`** (here) — captured runs of user-facing demo flows.
- **`docs/PROOFS/`** — implementation proof packets (boundaries, gates, capabilities).
- **`docs/capability_verification/`** — live pass/fail against a running build (QA Rule #1).

## Entry points

Each dated subfolder carries its own report(s); read the report inside the capture, and check its
date. The `daily_operating_baseline/` captures are referenced from
[`../product/WHAT_WORKS_TODAY.md`](../product/WHAT_WORKS_TODAY.md) as the latest daily-flow proofs.
