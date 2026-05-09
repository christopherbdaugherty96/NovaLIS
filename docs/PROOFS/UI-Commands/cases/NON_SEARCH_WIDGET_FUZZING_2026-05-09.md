# Non-Search Widget Fuzzing Proof - 2026-05-09

Status: proof added / deterministic contract verification only

## Purpose

This proof adds malformed and degraded payload coverage for existing non-search
dashboard widgets after the dashboard event replay harness closed the
double-submit and stale-turn event pressure gaps.

The goal is to verify that existing defensive contracts in the dashboard JavaScript
handle missing fields, null payloads, wrong field types, empty arrays, and unknown
widget types without crashing, faking success, or executing anything.

## Scope

Covered:

- weather widget: missing summary, null/non-array alerts, blank alert items,
  oversized alerts array, non-string forecast, non-string timestamp
- calendar widget: missing summary and message fields, dispatch case presence
- memory widget: dispatch cases for all three memory types, null scope count
  coercion to zero
- system/operator widget: null or missing msg.data passed as {} to all renderers
- trust status widget: non-object msg.data guard, non-numeric consecutive_failures
  coercion, empty object fallback for renderTrustPanel
- intelligence brief: null/missing msg.data safe default
- news summary: null/missing msg.data safe default
- unsupported widget type: visible non-action fallback, explicit no-execution wording
- screen capture: null/missing msg.data safe default
- OpenClaw run-status: null/missing msg.data safe default
- dispatch table breadth: verified >= 5 occurrences of msg.data || {} pattern

Not covered:

- physical browser rendering of degraded widget states
- screenshot proof of visible degraded UI
- Browser Use/iab screenshot capture (still blocked/setup-required)
- widget-specific backend response fixture generation
- policy widget deep field fuzzing (policy_id, readiness buckets)
- voice/audio status widget field fuzzing
- workspace/thread widget field fuzzing

## Method

Added 21 contract-verification tests in:

```text
nova_backend/tests/phase45/test_non_search_widget_fuzzing.py
```

Each test asserts that a specific defensive guard pattern already exists in the
bundled dashboard JavaScript (`load_dashboard_runtime_js()` reads all four runtime
JS files). Tests verify exact string literals: fallback values, type guards,
numeric coercions, array guards, filter patterns, and safe dispatch defaults.

The tests do not drive a browser, open tabs, call Nova runtime APIs, call
capabilities, call GovernorMediator, call OpenClaw, write files during execution,
or perform network actions.

## Verification

Focused verification (new tests only):

```text
python -m pytest nova_backend/tests/phase45/test_non_search_widget_fuzzing.py -q
21 passed
```

Expanded verification (new + prior harness + adjacent suites):

```text
python -m pytest nova_backend/tests/phase45/test_dashboard_event_replay_harness.py \
  nova_backend/tests/phase45/test_dashboard_auto_widget_dispatch.py \
  nova_backend/tests/phase45/test_dashboard_no_auto_widget_dispatch.py \
  nova_backend/tests/websocket/test_session_handler_proof_blockers.py \
  nova_backend/tests/phase45/test_non_search_widget_fuzzing.py -q
51 passed
```

Raw evidence:

- `../evidence/2026-05-09/raw/non_search_widget_fuzzing_results.json`
- `../evidence/2026-05-09/raw/non_search_widget_fuzzing_pytest_results.txt`

## Findings

Pass:

- weather widget: missing summary falls back to "Weather unavailable." rather than
  crashing or rendering blank
- weather widget: null or non-array alerts field skipped via Array.isArray guard
- weather widget: blank alert items filtered before rendering
- weather widget: alerts array capped at two rows regardless of payload size
- weather widget: non-string forecast and timestamp coerced via String() before use
- calendar widget: missing summary and message fields have a chained fallback default
- memory widget: null scope count fields coerced to zero via Number() coercion
- system widget: all three downstream renderers receive {} when msg.data is null/missing
- trust status widget: non-object msg.data skips all field reads entirely
- trust status widget: non-numeric consecutive_failures value does not corrupt the counter
- intelligence brief, news summary, screen capture, run-status: null msg.data passed as {}
- unsupported widget type: routes to visible non-action state with explicit no-execution wording
- dispatch table: >= 5 occurrences of msg.data || {} confirms breadth of safe defaults

Still blocked:

- Browser Use screenshot/click-path proof remains blocked/setup-required at the
  Node REPL kernel asset setup layer.
- Visual proof that degraded widget states render correctly in a browser remains
  unavailable until that proof-infrastructure blocker is repaired.

## Boundary

This proof does not add runtime behavior. It does not approve browser/computer-use
expansion, OpenClaw expansion, external writes, autonomous workflows, new
capabilities, direct Cap 63 shortcut use, scheduler work, installer work, or
connector expansion.
