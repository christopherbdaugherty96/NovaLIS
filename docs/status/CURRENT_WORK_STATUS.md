# Nova Current Work Status

Last reviewed: 2026-05-07 (proof library progress sync after PR #119)

This is a human-maintained continuity note for the current development slice.

It is not generated runtime truth. For exact runtime fingerprint, capability count, active capabilities, and generated invariants, use [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

Generated runtime docs and actual code win if they conflict with this note.

---

## Priority Lock Status (2026-05-06)

Current active priority lock:

```text
Governed Web / News / Reporting + UI / Commands Proof + Stress Test
```

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md`

Paused prior priority lock:

```text
Trust Review Card MVP / Visible Non-Action Receipt Surface
```

The Trust Review Card MVP lock is paused by user request. No Trust Review Card implementation work should proceed until the active proof/stress-test lock is complete, closed, or explicitly superseded.

The current active workstream is limited to validating and pressure-testing existing governed information/reporting and visible UI/button/command surfaces.

This is not an automation-expansion lock.

PR #119 materially expanded the proof/evidence library, but it did not close the active lock.

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
- **Paused Trust Review Card MVP lock:** selected in PR #112 and paused by the active Web/News/Reporting
  + UI/Commands proof/stress-test lock. It should not be implemented while this proof lock is active.
- **Active Web/News/Reporting + UI/Commands proof lock:** validates existing governed information,
  reporting, dashboard, button, command, widget, confirmation, degraded-state, and blocked-action surfaces.
  It does not approve new capabilities, OpenClaw execution expansion, browser/computer-use expansion,
  external writes, autonomous workflow execution, Google connector runtime expansion, capability registry
  expansion, scheduler expansion, or installer work.
- **PR #119 proof-library expansion:** merged the Web/News proof library index, case-level proof files,
  adversarial prompt suite, master UI/button/command verification matrix, friction logs, blocker logs,
  regression recommendations, and evidence links. Generated MOCs/runtime-doc indexes were refreshed
  through the generator path because proof docs were added to the indexed documentation surface; runtime
  authority/capability behavior was not expanded.
- Cap 64 remains confirmation-bound local `mailto:` draft only. No SMTP, inbox access, or
  autonomous send.
- Cap 65 remains read-only Shopify intelligence. No Shopify writes.

---

## Planning-Only / Future Direction

All future direction outside the active Web/News/Reporting + UI/Commands proof/stress-test lock requires a separate reviewed priority lock before work starts.

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md`

Current lock state:

1. OpenClaw priority-lock sequence is complete and closed.
2. Runtime truth regeneration / audit merged in PR #110 and is complete.
3. Trust Review Card MVP priority lock was selected in PR #112 and is now paused.
4. Web/News/Reporting + UI/Commands proof/stress-test lock is active.
5. PR #119 added the first evidence-backed proof library and UI verification matrix for the active lock.
6. The active lock still remains open because stale-cache/provider-failure fixtures, contradictory-reporting fixtures, source-credibility fixtures, malformed-widget proof, rapid-click/double-submit proof, and Browser Use screenshot/click-path proof still need additional evidence.
7. The active lock allows only proof scaffolding, proof artifacts, simulations, stress-test prompts, and audit work for existing surfaces.
8. Broad OpenClaw automation, browser/computer-use expansion, external writes, email/calendar/Shopify/account actions, direct Cap 63 shortcut use, autonomous workflow execution, Google connector expansion, capability registry expansion, workflow automation expansion, scheduler expansion, installer work, and Trust Review Card implementation remain not approved.
