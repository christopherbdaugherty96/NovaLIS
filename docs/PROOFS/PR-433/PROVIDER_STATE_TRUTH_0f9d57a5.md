# PR #433 Provider-State Truth Proof

Recorded: 2026-09-24

## Attribution

- Code under test: `0f9d57a5fcf1d22f38a3cd2a1d80e9ae777db263`
- Base: `d2938267dd43504f48d1720714051ff9a7bba5f8`
- Purpose: bounded provider-state truth correction for PR #433.

This record is committed after the listed proof run. It deliberately identifies the
prior code-under-test SHA rather than claiming that the proof-artifact commit itself
was tested. The full package is rerun after this file is committed before any
exact-head review claim is made.

## Consumer impact reviewed

- `ConnectionsStore.snapshot()` and `_provider_snapshot()` now set `connected=true`
  only when a stored credential has `health_ok=true`.
- The Settings API exposes that same snapshot without changing an execution or
  authorization path.
- Capability-help reads `health_ok` directly and already distinguishes verified from
  unverified configuration; its behavior is unchanged.
- Capability truth already projects `health_ok=null` as unknown availability, so the
  snapshot now agrees with that tri-state meaning.
- The affected beta-facing consumers are Settings connection cards, header Quick
  runs, page suggestions, and Intro cards. Canonical and maintained mirror files are
  byte-synchronized.
- No Governor, capability registry, execution boundary, network boundary, provider
  implementation, or persisted provider schema was changed.

## Commands and results

```text
python -m pytest nova_backend/tests/test_beta_readiness_user_facing_truth.py nova_backend/tests/conversation/test_meta_intent_handler.py nova_backend/tests/phase45/test_connections_store.py nova_backend/tests/phase45/test_connections_api.py nova_backend/tests/phase45/test_dashboard_calendar_integration.py nova_backend/tests/phase45/test_dashboard_news_header_weather_widget.py nova_backend/tests/phase45/test_dashboard_header_and_news_refinement.py nova_backend/tests/test_weather_skill.py nova_backend/tests/test_weather_service.py nova_backend/tests/test_weather_location_truth.py nova_backend/tests/test_news_skill.py nova_backend/tests/test_calendar_skill.py nova_backend/tests/executors/test_news_intelligence_executor.py -q
293 passed in 20.66s

python -m ruff check nova_backend/src/connections/connections_store.py nova_backend/tests/phase45/test_connections_store.py nova_backend/tests/test_beta_readiness_user_facing_truth.py
All checks passed!

python scripts/check_frontend_mirror_sync.py
Frontend mirror check passed.

node --check nova_backend/static/dashboard-chat-news.js
node --check nova_backend/static/dashboard.js
node --check Nova-Frontend-Dashboard/dashboard-chat-news.js
node --check Nova-Frontend-Dashboard/dashboard.js
All four commands exited 0.

python scripts/check_frontend_navigation_smoke.py
Frontend navigation smoke check passed.

python scripts/prove_runtime_truth.py
PASS: backend app imports
PASS: dashboard root returns 200
PASS: dashboard root status is 200
PASS: phase-status route returns 200
PASS: phase-status status is 200
PASS: websocket /ws accepts a connection
PASS: capability registry loads
PASS: capability registry loads active capabilities
PASS: cap 16 governed_web_search is active/enabled
PASS: cap 64 requires confirmation before external-effect draft
PASS: Governor evaluates cap 64 without confirmation
PASS: Governor blocks cap 64 without confirmation
PASS: Governor evaluates unknown capability
PASS: Governor blocks unknown capability
PASS: model trust/status snapshot is readable
INFO: model status {"active_model": "gemma2:2b", "current_fingerprint": null, "expected_fingerprint": null, "inference_blocked": true}
SCOPE: structural runtime smoke proof only — not comprehensive runtime truth
SUMMARY: PASS

git diff --check
Exit 0.
```

## Regressions covered

- stored credential plus `health_ok=null`, including the process-environment mirror
  created by `save_key()`, is configured but not connected;
- stored healthy is connected; stored known-failed is unavailable;
- environment-only configuration remains attemptable but is presented as configured,
  not connected, verified, fresh, or live;
- the real Settings card distinguishes configured, needs-verification, connected, and
  known-failed states;
- header Quick runs and Intro cards use the same availability path;
- the real-JS Intro harness records each card's title, badge, and copy;
- canonical and maintained dashboard mirrors remain byte-identical.

## Stopping rule

This proof authorizes neither Ready status nor merge. PR #433 remains Draft and HOLD
pending a fresh independent review of the final exact head.

