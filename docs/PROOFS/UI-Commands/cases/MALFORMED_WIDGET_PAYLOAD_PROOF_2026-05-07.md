# Malformed Widget Payload Proof - 2026-05-07

Status: partial pass / screenshot proof blocked

## Purpose

This proof records the dashboard behavior for malformed, empty, degraded, or unsupported widget payloads under the active Web/News/Reporting + UI/Commands proof/stress-test lock.

This proof does not add a capability, does not expand browser/computer-use, does not perform external writes, and does not create runtime authority.

## What Was Tested

- Search widget evidence payloads with degraded/empty search state.
- Search widget evidence metadata with missing or malformed source credibility fields.
- Unsupported dashboard/WebSocket message types.
- Mirrored dashboard frontend/backend copy consistency for unsupported widget fallback text.

## Expected Behavior

- No crash.
- No fake success.
- No hidden execution.
- No silent disappearance where a degraded state should remain visible.
- Unsupported widget/message types should be visibly marked unsupported rather than ignored as success.

## Evidence

- `../evidence/2026-05-07/raw/dashboard_stale_degraded_rendering_contract.json`
- `../evidence/2026-05-07/raw/ui_malformed_rapid_click_contract.json`
- `../evidence/2026-05-07/raw/ui_malformed_rapid_click_pytest_results.txt`

## Result

Pass for the covered contract layer.

Covered behavior:

- Empty degraded search widgets remain visible as `Search state`.
- Search evidence metadata renders as `Evidence state`.
- Provider/freshness/source-signal evidence remains visible when present.
- Malformed source credibility rows fall back to safe text defaults.
- Unsupported dashboard messages now produce a visible `Unsupported` assistant message saying Nova did not treat the payload as success or execute anything.

## Remaining Gap

This is not a full browser screenshot/click-path proof. Browser Use screenshot capture remains blocked by runtime asset setup, so visual pixel-level proof is still unavailable.

Known widget-specific fuzzing beyond the search/unsupported-message contract should continue later for weather, calendar, memory, policy, and system-control widgets.
