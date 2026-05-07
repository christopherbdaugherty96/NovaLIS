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

## Verdict

Expected outcome is truthful bounded behavior, not guaranteed success.

This pass found no evidence of unauthorized execution, external write, broad OpenClaw automation, direct Cap 63 shortcut use, or browser/computer-use expansion.

It did find UI/command truthfulness gaps that should be fixed or regression-tested before broader automation work resumes.

## Matrix Status

The master matrix now records evidence-backed status for the high-risk visible command paths and marks screenshot/click-path coverage as blocked by Browser Use runtime setup rather than Nova runtime authority.
