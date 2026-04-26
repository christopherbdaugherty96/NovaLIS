# BackLog.md

This file tracks follow-up work that is real, but not allowed to distract from the active close-out path in `Now.md`.

## Trust Receipt Backend Hardening

Context: the minimum viable trust receipt backend/API was added, but a fresh review identified hardening work that should be tracked before treating the receipt system as durable. These are not known regressions; they are reliability, test, and defense-in-depth improvements.

### Highest Priority

- [x] Harden `receipt_store.py` for fresh-install and corrupted-ledger cases. *(done 2026-04-26, commit 83c7474)*
  - Missing ledger → `[]`; empty ledger → `[]`; malformed/non-dict JSON lines skipped; outer `try/except Exception` prevents propagation.

- [x] Add targeted unit tests for `receipt_store.py`. *(done 2026-04-26, commit 83c7474)*
  - 18 tests in `nova_backend/tests/trust/test_receipt_store.py` covering all scenarios.

### Medium Priority

- [ ] Add prerequisite checks to `scripts/verify_windows.ps1`.
  - Confirm `python` is available before attempting any steps.
  - Confirm the command is being run from the project root or fail with a clear message.
  - Confirm `pytest` is importable or explain how to activate/create the virtual environment.
  - Print Python/pip versions for easier Windows troubleshooting.

- [ ] Add a short `ci.yml` comment explaining why the Windows job runs specific suites rather than the full test suite.
  - Current reason: known pre-existing simulation pathing issue (`test_nova_trial_runner` hardcodes a relative path that fails when `PYTHONPATH=nova_backend`). Not caused by trust receipt or Cap 65 work.

- [ ] Add troubleshooting sections to the Cap 64 and Cap 65 live checklists.
  - Cap 64: missing/default mail client, mailto behavior, ledger verification, confirmation gate expectations.
  - Cap 65: missing Shopify domain/token, token scope failures, NetworkMediator refusal, GraphQL errors, empty store data.

### Lower Priority / Design Follow-Up

- [x] Add router-level loopback dependency to the Trust Receipt API as defense-in-depth. *(done 2026-04-26, commit 83c7474)*
  - `APIRouter(dependencies=[Depends(require_local_http_request)])` applied in `trust_api.py`.
  - `/api/trust` added to `_LOCAL_ONLY_API_PREFIXES` in `local_request_guard.py` so the guard actually fires.

- [ ] Move receipt-worthy event classification out of ad hoc store logic.
  - Short-term acceptable: a named constant such as `RECEIPT_WORTHY_EVENT_TYPES`.
  - Longer-term preferred: event schema or capability metadata, for example `receipt_worthy: true`, derived from governance metadata such as `external_effect`, `persistent_change`, or `confirmation_required`.

## Guardrail

Do not expand this into another broad audit. The active execution path remains:

1. Cap 64 P5 live signoff and lock.
2. Cap 65 P5 live Shopify checklist and lock.
3. Clean Windows VM installer validation and `C:\Program Files\Nova\bootstrap.log` review.
4. Trust receipt dashboard card after backend hardening.
