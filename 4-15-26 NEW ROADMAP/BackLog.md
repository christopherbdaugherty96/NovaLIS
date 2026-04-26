# BackLog.md

This file tracks follow-up work that is real, but not allowed to distract from the active close-out path in `Now.md`.

## Trust Receipt Backend Hardening

Context: the minimum viable trust receipt backend/API was added, but a fresh review identified hardening work that should be tracked before treating the receipt system as durable. These are not known regressions; they are reliability, test, and defense-in-depth improvements.

### Highest Priority

- [ ] Harden `receipt_store.py` for fresh-install and corrupted-ledger cases.
  - Missing ledger file should return an empty receipt list instead of raising `FileNotFoundError`.
  - Empty ledger should return an empty receipt list.
  - Malformed or truncated JSONL lines should be skipped safely, with no traceback to the API caller.
  - Unexpected filesystem errors should produce a controlled failure path.

- [ ] Add targeted unit tests for `receipt_store.py`.
  - Missing ledger file.
  - Empty ledger file.
  - Receipt-worthy event filtering.
  - Newest-first ordering.
  - `limit` handling.
  - Malformed/truncated JSONL line handling.
  - Tail-read behavior across chunk boundaries, if `_read_tail_lines` remains custom logic.

### Medium Priority

- [ ] Add prerequisite checks to `scripts/verify_windows.ps1`.
  - Confirm `python` is available.
  - Confirm the command is being run from the project root or fail with a clear message.
  - Confirm `pytest` is importable or explain how to activate/create the virtual environment.
  - Print Python/pip versions for easier Windows troubleshooting.

- [ ] Add a short `ci.yml` comment explaining why simulation tests are excluded from the Windows verification path.
  - Current reason: known pre-existing simulation pathing issue, not caused by trust receipt or Cap 65 work.

- [ ] Add troubleshooting sections to the Cap 64 and Cap 65 live checklists.
  - Cap 64: missing/default mail client, mailto behavior, ledger verification, confirmation gate expectations.
  - Cap 65: missing Shopify domain/token, token scope failures, NetworkMediator refusal, GraphQL errors, empty store data.

### Lower Priority / Design Follow-Up

- [ ] Add router-level loopback dependency to the Trust Receipt API as defense-in-depth.
  - The app-level local/DNS rebinding middleware is the active protection today.
  - A router-level dependency would make the boundary explicit if the router is ever reused elsewhere.

- [ ] Move receipt-worthy event classification out of ad hoc store logic.
  - Short-term acceptable: a named constant such as `RECEIPT_WORTHY_EVENT_TYPES`.
  - Longer-term preferred: event schema or capability metadata, for example `receipt_worthy: true`, derived from governance metadata such as `external_effect`, `persistent_change`, or `confirmation_required`.

## Guardrail

Do not expand this into another broad audit. The active execution path remains:

1. Cap 64 P5 live signoff and lock.
2. Cap 65 P5 live Shopify checklist and lock.
3. Clean Windows VM installer validation and `C:\Program Files\Nova\bootstrap.log` review.
4. Trust receipt dashboard card after backend hardening.
