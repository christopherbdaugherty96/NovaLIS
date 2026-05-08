# Nova Current Work Status

Last reviewed: 2026-05-07 (Trust Review Card MVP closeout review)

This is a human-maintained continuity note for the current development slice.

It is not generated runtime truth. For exact runtime fingerprint, capability count, active capabilities, and generated invariants, use [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

Generated runtime docs and actual code win if they conflict with this note.

---

## Priority Lock Status (2026-05-06)

Most recently active priority lock:

```text
Governed Web / News / Reporting + UI / Commands Proof + Stress Test
```

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md`

Closeout review:

```text
docs/status/WEB_NEWS_UI_PROOF_LOCK_CLOSEOUT_REVIEW_2026-05-07.md
```

Closeout status:

```text
qualified closed / screenshot proof explicitly blocked
```

Most recently completed priority lock:

```text
Trust Review Card MVP / Visible Non-Action Receipt Surface
```

Closeout review:

```text
docs/status/TRUST_REVIEW_CARD_MVP_CLOSEOUT_REVIEW_2026-05-07.md
```

Closeout status:

```text
merged / display-only / non-authorizing / follow-ups tracked
```

Trust Review Card MVP is accepted as a deterministic non-action receipt surface. It renders existing request-understanding review-card state in chat without action buttons, routing, authorization, confirmation acceptance, Governor calls, capability calls, OpenClaw calls, browser/computer-use expansion, external writes, autonomous workflows, or direct Cap 63 shortcut use.

The completed proof/stress-test workstream was limited to validating and pressure-testing existing governed information/reporting and visible UI/button/command surfaces.

This closeout is not an automation-expansion approval.

PR #119 materially expanded the proof/evidence library.

PR #121 added deterministic stress fixtures for contradictory reporting, duplicate/prior-state topic
mapping, and split-topic headline comparison. It reduced those proof gaps.

The current stale/provider/credibility fixture pass adds deterministic search evidence coverage for
stale timestamps, malformed/degraded provider output, and weak/untrusted source credibility signals.
It further reduced proof gaps.

The dashboard stale/degraded rendering pass adds visible search-widget rendering for the new evidence
metadata: provider status, freshness status, source credibility rows, and empty degraded search state.
It further reduced UI truthfulness gaps.

The malformed widget / rapid-submit proof pass adds a visible unsupported dashboard-message fallback and
contract proof for overlapping send blocks, single-use send binding, manual-turn filtering, assistant-text
de-dupe, and pending confirmation isolation. It reduces the rapid-click/double-submit and malformed widget
proof gaps.

The closeout review classifies the lock as qualified closed. Browser Use screenshot/click-path proof,
high-frequency browser event replay, broader visual UI proof, deeper widget-specific fuzzing, and
timeline-drift fixtures remain carried-forward follow-up work rather than reasons to keep this lock
indefinitely open.

---

## Implemented Runtime / Code Truth

- Governance spine remains the strongest runtime truth: GovernorMediator, CapabilityRegistry,
  ExecuteBoundary, NetworkMediator, and ledger discipline are still the authority path.
- Cap 16 governed web search remains the active current-information lane.
- Search Evidence Synthesis is implemented as a deterministic evidence-structuring module for Cap 16
  search output. It does not add a new capability, does not authorize action, does not bypass
  NetworkMediator.
- Daily Brief MVP is implemented as a deterministic, on-demand session brief (PR #68). It synthesizes
  session state, memory, receipts, weather (live via WeatherService), calendar (local ICS via
  CalendarSkill), and email placeholder into 11 sections. Non-authorizing frozen dataclass;
  `execution_performed=False` and `authorization_granted=False` enforced by `__post_init__`.
- **Stage 3:** Memory Loop - explicit user-initiated remember / review / update / forget / why-used
  with receipts. No silent autosave. Memory does not authorize action. (PR #82 2026-05-02)
- **Stage 4:** Context Pack - bounded labeled context bridge with source labels, authority labels,
  budget enforcement, stale/conflict warnings; live-wired into general_chat_runtime.py every turn.
  (PRs #83/#87 2026-05-02)
- **Stage 5:** Brain Discipline / Trace - 7 mode contracts, classify_mode(), BrainTrace
  non-authorizing frozen dataclass; stored in session_state["last_brain_trace"] each turn;
  execution_performed and authorization_granted always False. (PRs #85/#88 2026-05-02)
- **Stage 6:** RoutineGraph v0 - RoutineBlock, RoutineGraph, RoutineRun, RoutineReceipt
  non-authorizing frozen dataclasses; DAILY_BRIEF_GRAPH; run_daily_brief_routine(). (PR #93 2026-05-03)
- **Stage 6:** Plan My Week Routine - WeeklyPlan, PlanMyWeekProposal (approval_required=True
  enforced), PlanApprovalRecord; two-phase runner; first RoutineGraph with request_approval block.
  (PR #98 2026-05-03)
- **Stage 6 step 1:** Cost Posture Metadata - cost_posture field (free/free_tier/paid/unknown_cost)
  on all 27 capabilities; validated on load; visible in governance matrix and runtime state doc;
  metadata + visibility only, no runtime enforcement. (PR #99 2026-05-03)
- **Completed OpenClaw lock step 1 foundation:** Planning-task preview runtime handoff proof merged in
  PR #103 and RequestUnderstanding review-card payload contract merged in PR #104. This establishes a
  planning-only, non-authorizing payload foundation for the future visible trust surface. No UI render,
  OpenClaw delegation, capability expansion, persistent history store, or execution authority was added.
- **Completed OpenClaw lock step 2:** Local capability signoff matrix merged in PR #105 and later
  clarified by PR #112 as accepted only as an evidence baseline for the first read-only OpenClaw proof,
  not authority-granting. It records read-only evidence and proof requirements for local/runtime
  surfaces before any future OpenClaw reliance; it does not enable capabilities or grant OpenClaw authority.
- **Completed OpenClaw lock step 3:** OpenClawMediator skeleton merged in PR #106. It adds a
  non-executing envelope -> decision -> receipt boundary with hardened blocked-action matching, no
  runtime routes, no OpenClaw execution, and no Governor/capability/filesystem/browser/network calls.
- **Completed OpenClaw lock step 4:** First read-only OpenClaw workflow proof merged in PR #107. It
  proves a deterministic Project Foreman Brief proof output through OpenClawMediator using
  caller-provided sample input only, explicit allowed input scope, and receipt/non-action statements.
  No OpenClaw execution, Governor/capability calls, Cap 63 shortcut, filesystem/browser/network action,
  external account action, or workflow automation expansion was added.
- **Completed runtime truth audit lock:** Runtime truth regeneration/audit merged in PR #110. Runtime
  docs were regenerated through the generator path, runtime fingerprint/hash alignment updated, proof
  artifact over-indexing in generated MOCs corrected, and OpenClawMediator/read-only workflow proof
  remained documented as non-executing/non-authorizing.
- **Trust Review Card MVP lock:** selected in PR #112 and paused by the Web/News/Reporting + UI/Commands
  proof/stress-test lock. It may resume after the qualified closeout through a narrow feature branch.
- **Trust Review Card MVP implementation pass:** propagates the existing non-authorizing
  `request_understanding_review_card` payload into chat responses and renders it as a deterministic
  display-only card. Focused tests verify the card has no action buttons, no dispatch/event handlers, no
  capability/Governor/OpenClaw path, no confirmation acceptance, and no state mutation from rendering.
- **Trust Review Card MVP closeout review:** classifies PR #127 as merged / display-only /
  non-authorizing / follow-ups tracked. It records that the MVP did not add capabilities, execution
  authority, OpenClaw expansion, browser/computer-use expansion, external writes, autonomous workflows,
  confirmation acceptance, direct Cap 63 shortcut use, or card-driven state mutation.
- **Qualified-closed Web/News/Reporting + UI/Commands proof lock:** validated existing governed information,
  reporting, dashboard, button, command, widget, confirmation, degraded-state, and blocked-action surfaces.
  It does not approve new capabilities, OpenClaw execution expansion, browser/computer-use expansion,
  external writes, autonomous workflow execution, Google connector runtime expansion, capability registry
  expansion, scheduler expansion, or installer work.
- **PR #119 proof-library expansion:** merged the Web/News proof library index, case-level proof files,
  adversarial prompt suite, master UI/button/command verification matrix, friction logs, blocker logs,
  regression recommendations, and evidence links. Generated MOCs/runtime-doc indexes were refreshed
  through the generator path because proof docs were added to the indexed documentation surface; runtime
  authority/capability behavior was not expanded.
- **PR #121 deterministic stress fixtures:** added test-backed Web/News/Reporting stress fixtures for
  contradictory multi-source reporting, duplicate/prior-state topic-map weighting, and split-topic
  headline comparison. It recorded focused verification of `24 passed` for the news intelligence suite
  and `23 passed` for the adjacent web search/search synthesis/story tracker slice. It did not add a
  capability, OpenClaw expansion, browser/computer-use expansion, external writes, autonomous workflow
  expansion, direct Cap 63 shortcut use, or live-network dependency in the fixture tests.
- **Stale/provider/credibility fixture pass:** adds deterministic search evidence and web search tests
  for stale source timestamps, malformed provider payloads, degraded provider status, and conservative
  source credibility rows. It records `24 passed` for the search evidence/web search slice and `28
  passed` for the adjacent news/story slice. It does not add a capability, OpenClaw expansion,
  browser/computer-use expansion, external writes, autonomous workflow expansion, direct Cap 63 shortcut
  use, or live-network dependency.
- **Dashboard stale/degraded rendering pass:** adds visible search widget evidence rendering for
  `provider_status`, `freshness_status`, `source_credibility`, and empty degraded/malformed search state.
  It records `4 passed` for the dashboard search widget rendering contract, `24 passed` for the adjacent
  search evidence/web search slice, `2 passed` for adjacent dashboard bundle checks, and JS syntax checks
  for served/mirrored dashboard files. It does not add runtime authority, capabilities, browser/computer-use,
  external writes, OpenClaw expansion, autonomous workflow expansion, or direct Cap 63 shortcut use.
- **Malformed widget / rapid-submit proof pass:** adds a visible `Unsupported` fallback for unknown
  dashboard/WebSocket message types and records contract proof for overlapping send blocking, single-use
  send button binding, manual-turn filtering, assistant-text de-dupe, and pending confirmation isolation.
  It records `25 passed` for the focused dashboard/session proof suite and JS syntax checks for served and
  mirrored dashboard files. It does not add runtime authority, capabilities, browser/computer-use, external
  writes, OpenClaw expansion, autonomous workflow expansion, or direct Cap 63 shortcut use.
- **Web/News/UI proof lock closeout review:** classifies the proof/stress-test lock as qualified closed.
  It explicitly carries Browser Use screenshot/click-path proof, high-frequency browser event replay,
  broader visual UI proof, deeper non-search widget fuzzing, and timeline-drift fixtures forward as proof
  follow-up work. It does not add runtime authority or approve browser/computer-use expansion.
- Cap 64 remains confirmation-bound local `mailto:` draft only. No SMTP, inbox access, or
  autonomous send.
- Cap 65 remains read-only Shopify intelligence. No Shopify writes.

---

## Planning-Only / Future Direction

All future direction outside the resumed Trust Review Card MVP scope requires a separate reviewed priority lock before work starts.

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md`

Current lock state:

1. OpenClaw priority-lock sequence is complete and closed.
2. Runtime truth regeneration / audit merged in PR #110 and is complete.
3. Trust Review Card MVP priority lock was selected in PR #112, paused during the proof/stress-test lock, resumed after qualified closeout, implemented in PR #127, and closeout-reviewed as display-only/non-authorizing.
4. Web/News/Reporting + UI/Commands proof/stress-test lock is qualified closed.
5. PR #119 added the first evidence-backed proof library and UI verification matrix for the active lock.
6. PR #121 reduced the contradiction and duplicate/split-topic proof gaps with deterministic fixtures.
7. The stale-cache/provider-failure and source-credibility gaps now have deterministic backend fixture coverage.
8. Dashboard-rendered stale/degraded search evidence state now has contract proof.
9. Rapid-click/double-submit guard behavior and unsupported widget fallback now have contract proof.
10. Browser Use screenshot/click-path proof, broader visual UI/button proof, deeper widget-specific malformed payload fixtures, and timeline-drift fixtures are carried forward as follow-up proof debt.
11. Trust Review Card MVP is accepted as a visible non-action receipt surface with follow-ups tracked.
12. Next recommended branch is Browser Use visual capture recovery as proof infrastructure only.
13. Trust Review Card and Browser Use proof follow-up scope remains non-authorizing and must not expand execution, OpenClaw, browser/computer-use capability, capabilities, external writes, or autonomous workflows.
14. Broad OpenClaw automation, browser/computer-use expansion, external writes, email/calendar/Shopify/account actions, direct Cap 63 shortcut use, autonomous workflow execution, Google connector expansion, capability registry expansion, workflow automation expansion, scheduler expansion, and installer work remain not approved.
