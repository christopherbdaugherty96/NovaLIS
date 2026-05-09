# UI / Commands Proof Report - 2026-05-06

Status: draft / review required

## Purpose

This proof pass tests existing Nova UI, button, command, and visible boundary behavior under the active Web/News/Reporting + UI/Commands proof/stress-test lock.

This pass is read-only with respect to runtime authority. It does not add capabilities, does not expand browser/computer-use, does not add external writes, does not add autonomous workflows, and does not use direct Cap 63 shortcuts.

## Method

- Started Nova through `scripts/start_daemon.py --no-browser`.
- Attempted in-app browser/computer-use against `http://127.0.0.1:8000`.
- Browser runtime failed before page interaction; this is recorded as a proof blocker.
- Verified dashboard HTML and static button inventory through local HTTP/static inspection.
- Exercised representative visible commands through the same `/ws` WebSocket channel used by the dashboard.
- Corrected the first probe after discovering pending website confirmation contaminated later commands.

## Evidence

- `MASTER_UI_VERIFICATION_MATRIX_2026-05-07.md`
- `evidence/2026-05-06/raw/start_daemon_output.txt`
- `evidence/2026-05-06/raw/browser_use_failure.txt`
- `evidence/2026-05-06/raw/static_button_inventory.json`
- `evidence/2026-05-06/raw/websocket_command_probe.json`
- `evidence/2026-05-06/raw/websocket_command_probe_corrected.json`
- `evidence/2026-05-06/raw/websocket_command_probe_summary.json`
- `evidence/2026-05-07/raw/ui_blocker_fix_probe.json`
- `evidence/2026-05-07/raw/focused_pytest_results.txt`
- `evidence/2026-05-07/raw/ui_followup_probe.json`
- `evidence/2026-05-07/raw/followup_pytest_results.txt`
- `evidence/2026-05-07/raw/followup_combined_pytest_results.txt`
- `evidence/2026-05-07/raw/browser_screenshot_followup_attempt.txt`
- `cases/DASHBOARD_STALE_DEGRADED_RENDERING_PROOF_2026-05-07.md`
- `evidence/2026-05-07/raw/dashboard_stale_degraded_rendering_contract.json`
- `evidence/2026-05-07/raw/dashboard_stale_degraded_rendering_pytest_results.txt`
- `cases/MALFORMED_WIDGET_PAYLOAD_PROOF_2026-05-07.md`
- `cases/RAPID_CLICK_DOUBLE_SUBMIT_PROOF_2026-05-07.md`
- `evidence/2026-05-07/raw/ui_malformed_rapid_click_contract.json`
- `evidence/2026-05-07/raw/ui_malformed_rapid_click_pytest_results.txt`
- `VERIFICATION_MATRIX.md`
- `FRICTION_LOG.md`

## Summary

Pass / usable:

- backend readiness
- dashboard static load
- chat send
- weather status
- calendar setup-required state
- news load
- daily brief / intelligence brief
- governed web search with source labels and caveats
- memory overview
- structure map / analysis docs
- voice status
- email draft boundary
- Shopify read-only/setup-dependent boundary

Needs correction:

- browser/computer-use screenshot capture was unavailable in this environment.

## 2026-05-07 Blocker-Fix Validation

Targeted fixes and proof rerun covered the highest-value truthfulness blockers:

- Pending website confirmation no longer monopolizes later unrelated commands. The stale pending open request is canceled before the new command is handled; the same turn then processed `weather`.
- Broad OpenClaw automation, browser/computer-use, external-write, GovernorMediator bypass, and direct Cap 63 shortcut attempts now return short explicit refusals with no execution or authority claim.
- Headline summary routing and low-relevance search confidence are validated in the Web/News proof report.
- Focused regression suite passed: `65 passed`.

Remaining friction is still recorded rather than hidden:

- browser/computer-use screenshot capture remains unavailable in this environment.

## 2026-05-07 Follow-Up Validation

The follow-up branch closed the remaining UI command truthfulness gaps that did not require browser screenshots:

- `open website notaurl` now returns an invalid-input message before confirmation: Nova could not verify it as a valid website.
- Quoted prompt-injection/article text is treated as untrusted local content, summarized locally, and explicitly says no web search or command execution occurred.
- Focused follow-up regression suite passed: `20 passed`.
- Combined follow-up regression suite passed: `75 passed`.
- Browser screenshot capture was attempted again with Browser Use/iab and remained blocked by `failed to write kernel assets`; no screenshot was captured or substituted.

## 2026-05-07 Dashboard Stale / Degraded Rendering Validation

The dashboard rendering pass connected PR #123 evidence metadata to visible search widget state:

- search widgets now render an `Evidence state` panel when evidence metadata is present
- `provider_status` appears when not `ok`
- `freshness_status` appears when not `unknown`
- `source_credibility` appears as conservative source-signal rows
- empty degraded/malformed search widgets remain visible as `Search state` rather than disappearing
- focused dashboard rendering suite passed: `4 passed`
- adjacent search evidence/web search suite passed: `24 passed`
- adjacent dashboard bundle checks passed: `2 passed`
- JS syntax checks passed for the served static dashboard and mirrored frontend dashboard file

## 2026-05-07 Malformed Widget / Rapid Submit Validation

The malformed/rapid-interaction pass reduced two remaining UI proof gaps without adding authority:

- unsupported dashboard/WebSocket message types now render a visible `Unsupported` response rather than disappearing silently
- the unsupported fallback explicitly says Nova did not treat the payload as success or execute anything
- backend and mirrored frontend dashboard copies carry the same unsupported-widget fallback
- malformed/degraded search widget behavior remains covered by the PR #124 `Search state` / `Evidence state` contract
- overlapping manual chat sends remain blocked while Nova is answering
- send button listener binding remains single-use through `sendBtn.dataset.bound`
- repeated assistant text within the same manual turn remains deduped
- pending website confirmation resolution remains limited to explicit yes/no/cancel style responses

Focused verification passed:

```text
25 passed
node --check passed
```

Remaining friction is still recorded rather than hidden:

- Browser Use screenshot/click-path proof remains blocked by runtime asset setup.
- High-frequency browser click replay remains unproven.
- Known non-search widget field fuzzing remains partial beyond unsupported-message and safe-default contract coverage.

## 2026-05-08 Browser Use Visual Capture Recovery Attempt

The proof-infrastructure recovery branch attempted Browser Use/iab screenshot capture through the required Browser Use skill path.

Result:

```text
blocked / setup-required
```

Observed failure:

```text
failed to write kernel assets: The system cannot find the path specified. (os error 3)
```

The blocker occurs before JavaScript execution in the Node REPL kernel asset setup layer. No tab was created, no page was loaded, no DOM was inspected, no screenshot was captured, and no click-path proof was recorded.

Evidence:

- `cases/BROWSER_USE_VISUAL_CAPTURE_RECOVERY_2026-05-08.md`
- `evidence/2026-05-08/raw/browser_use_visual_capture_recovery_attempt.txt`
- `evidence/2026-05-08/raw/browser_use_visual_capture_diagnostics.json`

Boundary:

- no Nova browser/computer-use capability was added
- no Browser Use path was added to Nova runtime
- no OpenClaw expansion occurred
- no external write path was added
- no autonomous workflow path was added
- no screenshot was substituted or faked

## 2026-05-08 Dashboard Event Replay Harness Validation

After Browser Use visual capture remained blocked below Nova, this branch added deterministic dashboard event replay proof for existing UI interaction guards:

- repeated manual sends / double submits do not enqueue duplicate payloads
- stale `turn_id` chat and `chat_done` events are ignored
- early `chat_done` without assistant output does not fake completion
- active-turn widget messages can complete a manual turn
- repeated assistant text in the same manual turn is deduped
- unsupported dashboard/WebSocket message types produce a visible non-action response
- socket error/close cleanup clears pending manual-turn state without sending extra payloads

Focused verification passed:

```text
22 passed
node --check passed
```

Evidence:

- `cases/DASHBOARD_EVENT_REPLAY_HARNESS_2026-05-08.md`
- `evidence/2026-05-08/raw/dashboard_event_replay_harness_results.json`
- `evidence/2026-05-08/raw/dashboard_event_replay_pytest_results.txt`

Boundary:

- deterministic replay only
- no browser/computer-use capability added
- no OpenClaw expansion
- no external write path added
- no autonomous workflow path added
- no screenshot/click-path proof claimed

## Verdict

Expected outcome is truthful bounded behavior, not guaranteed success.

This pass found no evidence of unauthorized execution, external write, broad OpenClaw automation, direct Cap 63 shortcut use, or browser/computer-use expansion.

It did find UI/command truthfulness gaps that should be fixed or regression-tested before broader automation work resumes.

## Matrix Status

The master matrix now records evidence-backed status for the high-risk visible command paths, malformed/unsupported widget fallback, and rapid-submit contract guards. Screenshot/click-path coverage remains blocked/setup-required by Browser Use / Node REPL runtime asset setup rather than Nova runtime authority.
