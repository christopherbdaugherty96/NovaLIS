# Nova Current Work Status

Last reviewed: 2026-05-03

This is a human-maintained continuity note for the current development slice.

It is not generated runtime truth. For exact runtime fingerprint, capability count, active capabilities, and generated invariants, use [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

Generated runtime docs and actual code win if they conflict with this note.

---

## Current Truth

At this review baseline, the alignment branch includes:

- PR #64 Brain Planning Preview scaffold, merged earlier.
- PR #66 Search Evidence Synthesis, merged in this alignment pass.
- PR #68 Daily Brief MVP, merged 2026-05-01.
- Free-first cost governance design docs, merged in this alignment pass.
- Auralis and YouTubeLIS planning docs already present on `main`.
- OpenClaw robust hardening audit added as a future implementation recommendation, not runtime truth.
- Governed Workflow Workspace Architecture added as a product/architecture planning note for everyday
  workflows, independent automation, and business-owner use cases.
- Stage 3 Memory Loop merged 2026-05-02.
- Stage 4 Context Pack merged 2026-05-02.

Generated runtime truth still reports the authoritative capability inventory and governance invariants. This note should not be used as a replacement for generated runtime docs.

---

## Implemented Runtime / Code Truth

- Governance spine remains the strongest runtime truth: GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, and ledger discipline are still the authority path.
- Cap 16 governed web search remains the active current-information lane.
- Search Evidence Synthesis is implemented as a deterministic evidence-structuring module for Cap 16 search output. It does not add a new capability, does not authorize action, and does not bypass NetworkMediator.
- Daily Brief MVP is implemented as a deterministic, on-demand session brief (PR #68). It synthesizes session state, memory, receipts, weather (live via WeatherService), calendar (local ICS via CalendarSkill), and email placeholder into 11 sections. Non-authorizing frozen dataclass; `execution_performed=False` and `authorization_granted=False` are enforced by `__post_init__`. No new capability, no LLM calls, no Governor path.
- Daily Brief robustness is improved on the `daily-brief-continuity-hardening` branch. It degrades cleanly on malformed session, memory, receipt, weather, calendar, and email-placeholder inputs; surfaces session continuity fields; and uses deterministic next-action recommendations. Proof notes live under [`../demo_proof/daily_operating_baseline/`](../demo_proof/daily_operating_baseline/).
- Stage 3 Memory Loop is implemented as an explicit user-initiated conversational memory skill: remember / review-list / update / forget / why-used, with memory receipts. It does not silently autosave, does not authorize action, and does not register a new capability.
- Stage 4 Context Pack is implemented as a bounded, labeled context bridge with ContextItem, ContextPackWarning, ContextPack, source labels, authority labels, budget enforcement, stale/conflict warnings, warning cap, deleted-memory filtering, legacy format output, and render_context_block. It does not authorize action. As of Stage 6, it is live-wired into general_chat_runtime.py — raw memory items now pass through compose_context_pack() before prompt assembly on every general-chat turn.
- Cap 64 remains confirmation-bound local `mailto:` draft only. It does not use Gmail API, SMTP, inbox access, or autonomous send.
- Cap 65 remains read-only Shopify intelligence. No Shopify writes are implemented.

---

## Merged Scaffold / Planning State

- Task Understanding, Task Envelope, and Simple Task Mode exist as planning-only Brain scaffolds.
- Conversation fallback can attach a planning-only Task Understanding preview for task-like requests.
- RunManager exists as an in-memory planning-only scaffold.
- Conversation fallback can create a session-local planning Run Preview.
- These Brain layers do not execute, authorize, call OpenClaw, add capabilities, or bypass Governor.

---

## Planning-Only / Future Direction

- Google connector work is future read/context connector planning. There is no Google OAuth, Gmail, Calendar, Drive, or Google account runtime connector unless generated runtime truth later proves it.
- Free-first cost governance is now a design policy and implementation plan. Runtime enforcement does not exist until registry metadata, generator output, tests, and UI/proof paths exist.
- Auralis Website Coworker is a future business workflow / production discipline layer. It is not an autonomous website builder and has no publish, deploy, domain, DNS, or client-send authority.
- Auralis Social Content Workflow Pack is a future/manual validation workflow. It has no autonomous posting, ad spend, client-account access, or customer messaging authority.
- YouTubeLIS is a planning-only tool folder. It has no upload, publish, account automation, or YouTube Studio control.
- OpenClaw remains governed/constrained and is not broad autonomy. Future expansion must require Run/Task Envelope/Governor/receipts.
- The OpenClaw robust hardening audit recommends mandatory EnvelopeFactory issuance, disabling or preview-gating freeform goal execution, replacing action auto-allow, centralizing execution guards, adding boundary detection, and adding run/step receipts before any browser/computer-use expansion.
- Governed Workflow Workspace is product planning for everyday workflows, independent automation, and business-owner workflows. It does not mean workflow templates, object models, onboarding wizard, or complete personal SaaS behavior are implemented.

---

## Stage 1 Proof — Closed 2026-05-02

All four Stage 1 proof docs verified against `main @ f82cc9c`:

- Daily Brief: PASS — 114 tests, 1877 full suite, 6 functional degradation cases
- Conversation Continuity: PASS — 412 tests, continuity roundtrip verified
- Search Evidence Synthesis: PASS — 222 brain+executors tests, 3 evidence path cases
- Memory Loop: partial at Stage 1; full loop completed in Stage 3

Stage 2 (status update) is complete.

---

## Stage 3 Memory Loop — Closed 2026-05-02

Implemented:

- `remember` — explicit user-initiated memory save
- `review` / `list` — show what is saved
- `update` — change a saved item
- `forget` — delete a saved item
- `why-used` — explain why a memory item was activated
- memory receipts for create / update / forget / use

Proof: [`../demo_proof/daily_operating_baseline/MEMORY_LOOP_PROOF.md`](../demo_proof/daily_operating_baseline/MEMORY_LOOP_PROOF.md) — PASS.

Required invariants proven by the Stage 3 proof package:

- no silent autosave
- memory is not used before user confirmation/review
- forgotten memory is not reused
- memory never authorizes action

---

## Stage 4 Context Pack — Closed 2026-05-02

Implemented:

- `ContextItem`
- `ContextPackWarning`
- `ContextPack`
- `compose_context_pack()`
- source labels and authority labels
- budget enforcement
- stale/conflict warnings
- warning cap
- deleted-memory filtering
- legacy format output
- `render_context_block()`

Proof: [`../demo_proof/daily_operating_baseline/CONTEXT_PACK_PROOF.md`](../demo_proof/daily_operating_baseline/CONTEXT_PACK_PROOF.md) — PASS.

Required invariants proven by the Stage 4 proof package:

- candidate items are not treated as confirmed
- runtime truth outranks memory
- budgets are enforced
- Context Pack is non-authorizing

Boundary: Context Pack is implemented and proven, but live prompt wiring and Brain mode/trace behavior are Stage 5 work.

---

## Stage 5 — Brain Discipline / Trace — Closed 2026-05-02

Implemented:

- 7 mode contracts: brainstorm, repo_review, implementation, merge, planning, action_review, casual
- classify_mode() — lightweight regex classifier, no LLM call, confidence 0.0–1.0
- BrainTrace — non-authorizing frozen dataclass; execution_performed, authorization_granted,
  private_reasoning_exposed always False; enforced in __post_init__
- Context Pack wired into general_chat_runtime.py — every general-chat turn now passes raw memory
  items through compose_context_pack() before prompt assembly; packed_context replaces
  relevant_memory_context in skill_state; brain trace stored in session_state["last_brain_trace"]

Proof: `docs/demo_proof/daily_operating_baseline/BRAIN_MODE_PROOF.md` — PASS.
Merged: PRs #85, #87, #88, #89 — all 2026-05-02.

---

## Stage 6 — Routine Surfaces (Active)

### RoutineGraph v0 — Closed 2026-05-03

Implemented:

- `RoutineBlock` — named step definition (frozen dataclass)
- `RoutineGraph` — ordered sequence of blocks (frozen dataclass)
- `RoutineRun` — record of a single execution; execution_performed=False and
  authorization_granted=False enforced via __post_init__, not settable by callers
- `RoutineReceipt` — non-authorizing proof artifact; same invariant enforcement
- `DAILY_BRIEF_GRAPH` — 8-block Daily Brief RoutineGraph definition
- `run_daily_brief_routine()` — wraps compose_daily_brief() with named blocks, produces
  (RoutineRun, RoutineReceipt)
- 60 tests: test_routine_graph.py (27) + test_daily_brief_routine.py (33)
- Merged: PR #93 2026-05-03

Boundary: RoutineGraph is planning and record-keeping vocabulary. It does not add
new capabilities, does not call an LLM, and does not grant execution authority.

### Plan My Week Routine — Closed 2026-05-03

Implemented:

- `WeeklyPlanItem` — single plan item (frozen dataclass)
- `WeeklyPlan` — assembled plan with focus_items, tasks, calendar_events, open_loops,
  recommended_actions; execution_performed/authorization_granted enforced False
- `PlanMyWeekProposal` — approval boundary surface; approval_required=True enforced,
  not settable by callers; execution_performed/authorization_granted enforced False
- `PlanApprovalRecord` — records user decision (approved/rejected/modified); validates
  decision; execution_performed/authorization_granted enforced False
- `PLAN_MY_WEEK_GRAPH` — 8-block RoutineGraph; first to include request_approval block
- `run_plan_my_week_routine()` — Phase 1: gathers data, assembles plan, surfaces proposal;
  nothing saved or executed until user approves
- `record_plan_approval(proposal, decision=...)` — Phase 2: records decision; non-authorizing
- 52 tests
- Merged: PR #98 2026-05-03

### Remaining Active Scope:

- Governance boundaries for routine execution (workflow workspace shell, template schema)
- Brain mode surfaced in UI per turn

Immediate continuation order:

1. Plan cost posture metadata as the next free-first implementation step.
2. Continue doc/status alignment as work progresses.
5. Plan Google read-only connector foundations only after cost posture and connector governance are clear.
6. Keep OpenClaw expansion frozen until envelope issuance, approval, execution-guard, and receipt gaps are closed.

Do not start new write/action capabilities in this sprint.

---

## Governed Workflow Workspace Direction

Canonical product planning note: [`../product/GOVERNED_WORKFLOW_WORKSPACE_ARCHITECTURE.md`](../product/GOVERNED_WORKFLOW_WORKSPACE_ARCHITECTURE.md).

The broadened product direction is:

```text
A governed AI workspace for everyday workflows and independent automation.
```

This includes everyday personal workflows, household/life admin workflows, creator workflows, independent contractor workflows, small business workflows, research and learning workflows, content/media workflows, local-first assistant workflows, and approved automation routines.

Independent business owners remain a major use case, but not the only use case.

---

## OpenClaw Hardening Priority

Canonical audit note: [`../future/OPENCLAW_ROBUST_HARDENING_AUDIT_2026-05-01.md`](../future/OPENCLAW_ROBUST_HARDENING_AUDIT_2026-05-01.md).

Current recommended order:

1. Make EnvelopeFactory mandatory for all OpenClaw runs.
2. Disable or strictly envelope-gate freeform goal execution.
3. Replace `/api/openclaw/approve-action` auto-allow with allow / pause / block decisions.
4. Add centralized OpenClaw execution guard for tool, network, file, action, and budget checks.
5. Add browser/computer-use boundary detection before any browser expansion.
6. Add run, step, boundary, failure, cancel, completion, and cleanup receipts.
7. Add visible active-run approval UI.
8. Only then implement a read-only isolated-browser slice.

---

## Do Not Overstate

Do not claim these are finished unless verified against code/runtime truth:

- Full Task Environment Router.
- Governor-driven live contract lookup.
- Dry Run / Plan Preview API.
- Brain Trace UI.
- Google OAuth/Gmail/Calendar runtime connectors.
- Gmail send/write authority.
- Shopify write authority.
- Broad autonomous execution.
- OpenClaw Run-based execution.
- OpenClaw mandatory EnvelopeFactory enforcement.
- OpenClaw real human approval gate.
- OpenClaw browser/computer-use readiness.
- Governed workflow workspace runtime shell.
- Workflow object model.
- Workflow template system.
- First-run workspace onboarding wizard.
- Free-first runtime enforcement.
- One-click consumer installer.
- Full Daily Operating System / scheduled background routines.
- Brain mode surfaced in UI (classify_mode exists in code; not yet shown per-turn in the UI).

---

## Branch / Workstream Map

For the branch and workstream alignment snapshot from this pass, see [`REPO_BRANCH_AND_WORKSTREAM_STATUS_2026-05-01.md`](REPO_BRANCH_AND_WORKSTREAM_STATUS_2026-05-01.md).
