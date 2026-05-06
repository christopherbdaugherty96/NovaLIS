# Nova Current Work Status

Last reviewed: 2026-05-06 (first read-only OpenClaw workflow proof branch started)

This is a human-maintained continuity note for the current development slice.

It is not generated runtime truth. For exact runtime fingerprint, capability count, active capabilities, and generated invariants, use [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

Generated runtime docs and actual code win if they conflict with this note.

---

## Priority Lock (2026-05-04)

Active development is restricted to:

```text
RequestUnderstanding review card
→ capability signoff matrix
→ OpenClawMediator skeleton
→ read-only workflow proof
```

All other workstreams are intentionally paused to prevent premature expansion before execution governance boundaries are proven.

Current next todo: review the first read-only OpenClaw workflow proof.

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
- **Stage 3:** Memory Loop — explicit user-initiated remember / review / update / forget / why-used
  with receipts. No silent autosave. Memory does not authorize action. (PR #82 2026-05-02)
- **Stage 4:** Context Pack — bounded labeled context bridge with source labels, authority labels,
  budget enforcement, stale/conflict warnings; live-wired into general_chat_runtime.py every turn.
  (PRs #83/#87 2026-05-02)
- **Stage 5:** Brain Discipline / Trace — 7 mode contracts, classify_mode(), BrainTrace
  non-authorizing frozen dataclass; stored in session_state["last_brain_trace"] each turn;
  execution_performed and authorization_granted always False. (PRs #85/#88 2026-05-02)
- **Stage 6:** RoutineGraph v0 — RoutineBlock, RoutineGraph, RoutineRun, RoutineReceipt
  non-authorizing frozen dataclasses; DAILY_BRIEF_GRAPH; run_daily_brief_routine(). (PR #93 2026-05-03)
- **Stage 6:** Plan My Week Routine — WeeklyPlan, PlanMyWeekProposal (approval_required=True
  enforced), PlanApprovalRecord; two-phase runner; first RoutineGraph with request_approval block.
  (PR #98 2026-05-03)
- **Stage 6 step 1:** Cost Posture Metadata — cost_posture field (free/free_tier/paid/unknown_cost)
  on all 27 capabilities; validated on load; visible in governance matrix and runtime state doc;
  metadata + visibility only, no runtime enforcement. (PR #99 2026-05-03)
- **Priority lock step 1 foundation:** Planning-task preview runtime handoff proof merged in PR #103
  and RequestUnderstanding review-card payload contract merged in PR #104. This establishes a
  planning-only, non-authorizing payload foundation for the future visible trust surface. No UI render,
  OpenClaw delegation, capability expansion, persistent history store, or execution authority was added.
- **Priority lock step 2:** Local capability signoff matrix merged in PR #105. It records read-only
  evidence and proof requirements for local/runtime surfaces before OpenClaw may rely on them; it does
  not enable capabilities or grant OpenClaw authority.
- **Priority lock step 3:** OpenClawMediator skeleton merged in PR #106. It adds a non-executing
  envelope -> decision -> receipt boundary with hardened blocked-action matching, no runtime routes,
  no OpenClaw execution, and no Governor/capability/filesystem/browser/network calls.
- Cap 64 remains confirmation-bound local `mailto:` draft only. No SMTP, inbox access, or
  autonomous send.
- Cap 65 remains read-only Shopify intelligence. No Shopify writes.

---

## Planning-Only / Future Direction

All future direction remains valid but is currently paused under the priority lock.

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-04.md`

Near-term sequence:

1. Review first read-only OpenClaw workflow proof and proof package.
2. Confirm it remains sample/local, read-only, mediator-gated, and receipt-backed.
3. Do not broaden OpenClaw beyond the reviewed proof path.
