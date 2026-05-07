# Stale Cache / Provider Failure Proof - 2026-05-07

Status: pass / UI fixture follow-up still needed

## Request Coverage

- stale source timestamp fixture
- degraded provider fixture
- malformed provider payload fixture

## What Happened

The focused search evidence regression suite now includes deterministic coverage for freshness and provider degradation:

- stale source timestamps produce `freshness_status: stale`
- stale source timestamps lower overall confidence to `low`
- degraded provider status is preserved as `provider_status: degraded`
- malformed provider payloads return a truthful empty search widget instead of fake success

Focused verification:

```text
24 passed in 5.40s
```

Adjacent news/story verification:

```text
28 passed in 4.55s
```

## What Did Not Happen

- No browser/computer-use was added or invoked.
- No OpenClaw execution was invoked.
- No external write occurred.
- No autonomous workflow was scheduled.
- No direct Cap 63 shortcut was used.
- No live network dependency was required for the fixture tests.

## Governance Boundary

These fixtures add truthfulness metadata and deterministic proof coverage for existing governed search/reporting behavior. They do not add a capability, authorize action, or approve broader automation.

## Evidence

- `docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/stale_provider_credibility_payload.json`
- `docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/stale_provider_credibility_pytest_results.txt`
- `nova_backend/tests/brain/test_search_synthesis.py`
- `nova_backend/tests/executors/test_web_search_executor.py`

## Remaining Follow-Up

- Add a WebSocket/UI fixture that renders stale/degraded state visibly in the dashboard.
- Add malformed-widget UI proof.
- Keep Browser Use screenshot/click-path proof blocked until runtime asset setup works.
