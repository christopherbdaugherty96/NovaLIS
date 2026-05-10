# Live Manual UI Verification Plan - 2026-05-09

Status: planned / manual local verification only / results not yet recorded

## Classification

```text
manual local proof
operator-observed
not Browser Use automation
not automated browser proof
not runtime authority expansion
```

This plan covers direct local observation of the running dashboard after
the deterministic proof infrastructure closeout. The operator starts Nova
locally, opens the dashboard in a browser, and records observed behavior.

No automated browser driver is used. No Browser Use capability is invoked.
No new runtime authority is added. No features are changed to make checks pass.

If a bug or discrepancy is found, it is logged as a finding in the results
doc and addressed in a separate branch later.

## Prerequisites

```text
1. Start Nova: python scripts/start_daemon.py --no-browser
2. Open dashboard: http://127.0.0.1:8000
3. Open browser devtools console (to observe JS errors)
4. Record observations in: proof/record-live-manual-ui-verification-results
```

## Out of Scope

- Browser Use screenshot/click-path automation (blocked/setup-required)
- autonomous workflows
- external write actions
- capability expansion
- OpenClaw expansion
- installer or scheduler work
- fixing bugs inline (log findings, fix separately)

---

## Section 1 — Dashboard Load and WebSocket

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 1.1 | Open `http://127.0.0.1:8000` | Dashboard loads, no console-visible JS error | TBD | TBD | |
| 1.2 | Observe orb / status indicator on load | Status reflects connected or setup-required state, not fake-ready | TBD | TBD | |
| 1.3 | Observe WebSocket connection in devtools Network tab | `/ws` connection establishes | TBD | TBD | |
| 1.4 | Stop backend, observe dashboard | Dashboard shows degraded/disconnected state, does not hang silently | TBD | TBD | |
| 1.5 | Restart backend, reload dashboard | Dashboard reconnects or requires manual reload; no false-ready claim | TBD | TBD | |

---

## Section 2 — Chat Send and Guard Behavior

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 2.1 | Type a message and press send | One assistant response, no duplicate | TBD | TBD | |
| 2.2 | Click send twice rapidly | Second send blocked; loading hint visible | TBD | TBD | |
| 2.3 | Hold Enter key | No duplicate payloads enqueued | TBD | TBD | |
| 2.4 | Send blank/whitespace message | No send occurs, no payload enqueued | TBD | TBD | |
| 2.5 | Send very long message (500+ chars) | Handled gracefully, no crash | TBD | TBD | |
| 2.6 | Send during pending response | Loading hint visible; second send blocked | TBD | TBD | |
| 2.7 | Switch to another page during pending response | No crash; response still arrives on return | TBD | TBD | |
| 2.8 | Reload page during pending response | State resets cleanly; no stuck pending state | TBD | TBD | |

---

## Section 3 — Trust Review Card

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 3.1 | Ask a non-action planning question | Trust Review Card renders as display-only receipt | TBD | TBD | |
| 3.2 | Inspect card for action buttons | No dispatch/confirm/execute buttons present | TBD | TBD | |
| 3.3 | Click anywhere on card | No action triggered, no state change | TBD | TBD | |
| 3.4 | Ask a blocked-action question | Explicit refusal; card shows boundary, not fake success | TBD | TBD | |

---

## Section 4 — News / Search / Reporting Widgets

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 4.1 | Click `btn-news` | News widget loads or shows setup/degraded state | TBD | TBD | |
| 4.2 | Click `btn-news-refresh` | Refresh triggers without duplicate send | TBD | TBD | |
| 4.3 | Click `btn-news-summary` | Summary widget renders or shows no-context message | TBD | TBD | |
| 4.4 | Use `btn-news-search` to search a term | Search result renders with source labels and confidence | TBD | TBD | |
| 4.5 | Use `btn-news-expand` | Expands news list without crash | TBD | TBD | |
| 4.6 | Ask for intelligence brief via chat | Intelligence brief widget renders | TBD | TBD | |
| 4.7 | Ask for topic map | Topic map widget renders | TBD | TBD | |

---

## Section 5 — Weather / Calendar / Morning Panel

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 5.1 | Click `btn-morning-toggle` | Morning panel toggles open/closed | TBD | TBD | |
| 5.2 | Observe weather in morning panel | Weather summary shown, or "Weather unavailable." fallback | TBD | TBD | |
| 5.3 | Observe calendar in morning panel | Calendar shows events, setup-required, or no-events default | TBD | TBD | |
| 5.4 | Click `btn-morning-calendar-connect` | Opens calendar connection flow or setup-required state | TBD | TBD | |

---

## Section 6 — Memory Panel

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 6.1 | Click `btn-memory-overview` | Memory overview renders or shows empty state | TBD | TBD | |
| 6.2 | Click `btn-memory-list` | Memory list renders | TBD | TBD | |
| 6.3 | Click `btn-memory-list-all` | All memories listed | TBD | TBD | |
| 6.4 | Click `btn-memory-recent` | Recent memories listed | TBD | TBD | |
| 6.5 | Click `btn-memory-list-active` / `locked` / `deferred` | Filtered memory lists render | TBD | TBD | |
| 6.6 | Click `btn-memory-refresh` | Refresh triggers without duplicate | TBD | TBD | |
| 6.7 | Click `btn-memory-export` | Export triggers or shows not-ready state | TBD | TBD | |
| 6.8 | Click `btn-memory-threads` | Thread-scoped memory view renders | TBD | TBD | |

---

## Section 7 — Trust Center Panel

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 7.1 | Navigate to page-trust | Trust center page renders | TBD | TBD | |
| 7.2 | Click `btn-trust-center-refresh` | Refresh triggers, data updates | TBD | TBD | |
| 7.3 | Click `btn-trust-center-system` | System status section visible | TBD | TBD | |
| 7.4 | Click `btn-trust-center-memory` | Memory section visible | TBD | TBD | |
| 7.5 | Click `btn-trust-center-policy-map` | Policy readiness section visible | TBD | TBD | |
| 7.6 | Click `btn-trust-center-voice-check` | Voice status shown or setup-required | TBD | TBD | |
| 7.7 | Click `btn-trust-center-bridge-status` | Bridge/connection status visible | TBD | TBD | |
| 7.8 | Click `btn-trust-center-workspace` | Workspace section visible | TBD | TBD | |
| 7.9 | Click `btn-trust-center-agent` | Agent section visible | TBD | TBD | |
| 7.10 | Click `btn-trust-center-settings` | Navigates to settings | TBD | TBD | |

---

## Section 8 — Policy Center Panel

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 8.1 | Navigate to page-policy | Policy center renders | TBD | TBD | |
| 8.2 | Click `btn-policy-refresh` | Refresh triggers without crash | TBD | TBD | |
| 8.3 | Click `btn-policy-capability-map` | Capability readiness visible | TBD | TBD | |
| 8.4 | Click `btn-policy-create-weather` / `calendar` / `status` | Policy creation flow or setup-required state | TBD | TBD | |
| 8.5 | Click `btn-policy-open-trust` / `settings` | Navigates correctly | TBD | TBD | |

---

## Section 9 — Settings Panel

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 9.1 | Navigate to page-settings | Settings page renders | TBD | TBD | |
| 9.2 | Click `btn-settings-refresh-runtime` | Runtime status refreshes | TBD | TBD | |
| 9.3 | Click `btn-settings-voice-status` | Voice status shown or setup-required | TBD | TBD | |
| 9.4 | Click `btn-settings-voice-check` | Voice check runs or shows not-available | TBD | TBD | |
| 9.5 | Click `btn-settings-open-connections` | Navigates to connections | TBD | TBD | |
| 9.6 | Click `btn-settings-open-trust` | Navigates to trust center | TBD | TBD | |
| 9.7 | Click `btn-settings-open-accessibility` | Accessibility settings visible | TBD | TBD | |
| 9.8 | Click `btn-settings-open-privacy` | Privacy settings visible | TBD | TBD | |
| 9.9 | Click `btn-settings-reset-defaults` | Prompts for confirmation, does not auto-reset | TBD | TBD | |
| 9.10 | Click `btn-reset-confirm` then `btn-reset-cancel` | Cancel aborts reset; confirm triggers reset flow | TBD | TBD | |

---

## Section 10 — Home / Workspace / Agent Panels

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 10.1 | Navigate to page-home | Home launch widget renders | TBD | TBD | |
| 10.2 | Click `btn-home-threads` | Thread list visible | TBD | TBD | |
| 10.3 | Navigate to page-workspace | Workspace board renders | TBD | TBD | |
| 10.4 | Click `btn-workspace-home-refresh` | Refresh triggers | TBD | TBD | |
| 10.5 | Click `btn-workspace-board-refresh` | Board refresh triggers | TBD | TBD | |
| 10.6 | Click `btn-workspace-board-threads` / `architecture` / `visual` | Board views switch | TBD | TBD | |
| 10.7 | Navigate to page-agent | Agent panel renders | TBD | TBD | |
| 10.8 | Click `btn-agent-refresh` | Agent status refreshes | TBD | TBD | |
| 10.9 | Click `btn-agent-open-home` / `settings` / `trust` | Navigates correctly | TBD | TBD | |

---

## Section 11 — Degraded / Unsupported / Blocked States

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 11.1 | Ask for an OpenClaw browser automation action | Explicit refusal, no execution | TBD | TBD | |
| 11.2 | Ask for an external write action | Explicit refusal, no execution | TBD | TBD | |
| 11.3 | Ask for a direct Cap 63 / Governor bypass | Explicit refusal, no bypass | TBD | TBD | |
| 11.4 | Send `open website notaurl` | Invalid-input rejection before confirmation | TBD | TBD | |
| 11.5 | Send `open website example.com`, then send unrelated command | Stale confirmation canceled; new command handled | TBD | TBD | |
| 11.6 | Send quoted prompt-injection text | Treated as untrusted content; no execution | TBD | TBD | |
| 11.7 | Observe any widget that returns no data | Widget shows setup-required or degraded state, not crash | TBD | TBD | |

---

## Section 12 — Workflow Focus / Operational Context

| # | Action | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 12.1 | Click `btn-workflow-show-steps` | Workflow steps panel renders | TBD | TBD | |
| 12.2 | Click `btn-workflow-refine` | Refine action triggers without crash | TBD | TBD | |
| 12.3 | Click `btn-workflow-reset` | Workflow state resets, no stuck pending | TBD | TBD | |
| 12.4 | Click `btn-operational-context-refresh` | Operational context refreshes | TBD | TBD | |
| 12.5 | Click `btn-operational-context-reset` | Context resets without crash | TBD | TBD | |

---

## Section 13 — Short Workflow Sequences

Record complete user-facing flows end to end.

| # | Workflow | Steps | Expected | Observed | Pass/Fail |
|---|---|---|---|---|---|
| 13.1 | Basic chat | Load → send message → receive response | One response, no duplicate, Trust Review Card if applicable | TBD | TBD |
| 13.2 | Rapid submit stress | Load → send → immediately send again | Second blocked; loading hint visible | TBD | TBD |
| 13.3 | News + search | Load → news → search term → review results | Source labels, confidence shown | TBD | TBD |
| 13.4 | Memory overview | Load → memory overview → list memories | Lists render without crash | TBD | TBD |
| 13.5 | Backend disconnect | Start → send message → kill backend → observe | Degraded state shown, no crash | TBD | TBD |
| 13.6 | Backend reconnect | After disconnect → restart backend → reload | Reconnects or requires manual reload cleanly | TBD | TBD |
| 13.7 | Panel switching mid-turn | Send → immediately switch to settings | No crash; response visible on return | TBD | TBD |
| 13.8 | Reset flow | Settings → reset → cancel | Cancel aborts; no state change | TBD | TBD |
| 13.9 | Blocked action refusal | Send browser automation request | Explicit refusal, no execution claim | TBD | TBD |
| 13.10 | Trust center full view | Navigate to trust center → review all subsections | All sections render, no crash | TBD | TBD |

---

## Findings Log

Record any discrepancies observed during the pass here. Do not fix inline.

| # | Section | Finding | Severity | Recommended follow-up branch |
|---|---|---|---|---|
| — | — | None yet | — | — |

---

## Evidence

Results should be recorded in a separate doc:

```text
docs/PROOFS/UI-Commands/cases/LIVE_MANUAL_UI_VERIFICATION_RESULTS_2026-05-09.md
```

Raw notes / screenshots (if any):

```text
docs/PROOFS/UI-Commands/evidence/2026-05-09/manual/
```

---

## Boundary Statement

This verification plan does not add:

- Browser Use capability
- computer-use capability
- OpenClaw expansion
- new runtime authority
- external write workflows
- autonomous workflows
- direct Cap 63 shortcuts
- new dashboard features
- new widget types
- new capabilities

It is observe-and-record only. All findings go to a separate results doc and
are addressed in separate fix branches after review.
