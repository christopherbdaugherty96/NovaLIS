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

- [x] Add prerequisite checks to `scripts/verify_windows.ps1`. *(done 2026-04-26, commit b1434e2)*
  - Python ≥ 3.10 check, project-root check, pytest importable check, Python/pip/pytest version printout.

- [x] Add a short `ci.yml` comment explaining why the Windows job runs specific suites rather than the full test suite. *(done 2026-04-26, commit b1434e2)*
  - Comment added above `test-windows:` job.

- [x] Add troubleshooting sections to the Cap 64 and Cap 65 live checklists. *(done 2026-04-26, commit b1434e2)*
  - Cap 64: mail client setup, `@` encoding, blank body, Trust page not built, confirmation gate, certify errors.
  - Cap 65: domain format, token scopes, NetworkMediator refusal, GraphQL/empty data, Test 3 restart, period defaults, certify errors.

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
