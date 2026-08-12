# AGENTS.md

Guidance for AI agents working on NovaLIS.

Start here before editing the repo.

## Core Rule

Intelligence is not authority.

Nova's reasoning layers may clarify, plan, search, summarize, and propose. Runtime execution still goes through the Governor, capability registry, execution boundaries, and receipts.

## Project Positioning

Nova is a governance-first local AI system that separates intelligence from execution authority.

Nova prioritizes visible authority boundaries, inspectable execution, and user-controlled AI operation.

Nova is NOT:

```text
- "AI employee" / "fully autonomous agent" / "universal orchestrator" / "AGI coworker"
```

Nova's strongest differentiator is: governed local-first execution with visible authority boundaries.

---

## Active Direction

Read these documents before starting any task, in this order (a reading order, not an
authority ranking — for runtime-existence claims, generated runtime docs win):

1. `docs/CANONICAL/00_INDEX.md` — how to read repo truth (defines the authority model)
2. `docs/status/DAILY_COMMAND_CENTER.md` — where the project is right now
3. `.agent_context/current_priority.md` — active state and safety boundaries
4. `docs/capability_verification/CAPABILITY_INVENTORY.md` — what verifiably works
5. `docs/current_runtime/CURRENT_RUNTIME_STATE.md` — generated runtime truth

Current active product state:

```text
Phase 3 observation: SEVEN-MORNING THRESHOLD COMPLETE (2026-07-22 synthesis).
The seven-morning gate is CLOSED. Its rank-1 defect — grounded brief/category
routing — was repaired, merged as PR #312 (2026-07-23), and verified on fresh
`main` (docs/status/GROUNDED_BRIEF_ROUTING_CLOSEOUT_2026-07-23.md).
No additional seven-morning or open-ended observation gate is required.

The August 7 owner-use defect is CLOSED on merged main. PR #330 implemented
Commitment Truth + Natural Reminder Handoff; PR #332 fixed notification-schedule
command precedence. Fresh-main proof at `dfef1db5...` confirmed the exact natural
handoff, real reminder persistence, `show schedules`, `reminders`, fresh-session
retrieval, and preservation of calendar-query routing.

The local-action outcome-truth lane is also CLOSED. PR #331 is merged and its
Cap 17/19/22 behavior was live-proven on merged main.

PR #333 merged the roadmap/current-state reconciliation. PR #334 merged Semantic
Substrate Slice 1 as durable provider-neutral contract/test infrastructure. Current
merged `main` is `c44b6d0cd72f0f91a6ec517427ad3fe2076beb30`.

PR #335 contains the implemented Google Workspace identity-only foundation, but it
remains DRAFT / UNMERGED at `befb69e...`. It is paused behind two P1 truth repairs
selected by the 2026-08-12 fresh-main real-user acceptance record:
  A. user-visible commitment/capability truth;
  B. receipt-correlated action/outcome history.
The 25-step golden regression was covered; the full 36-section stress catalog was
not completed. Repair and prove P1-A before beginning the separately bounded P1-B;
after both P1 proofs, address the recorded P2 groups and remaining stress-test gaps
before resuming #335 review. This text ORDERS that work but does not authorize either
repair or proof, modification of #335, or activation of Google domain-data access.

Authorization Integrity Slice 2A remains separately approved, not implemented on
main, and paused; it is neither cancelled nor silently active.
Runtime recovery remains historical/accepted context, deferred until
observation evidence reactivates it.
```

Not authorized without a separate reviewed priority lock:

```text
New implementation lanes, capability expansion, modification/expansion of PR #335,
Google domain-data connector work,
Shopify writes, ElevenLabs implementation, OpenClaw expansion,
browser/computer-use expansion, external writes, finance automation, social
posting automation, autonomous workflow execution, multi-agent expansion,
enterprise orchestration work.
```

---

## Current Task Status

```text
Phase 3 build lanes — COMPLETE (2026-07-07). Merged #262-#272, tagged
  phase-3-complete. Live verification recorded in PR #273.
Docs truth reconciliation — COMPLETE (2026-07-09). PRs #276-#283.
Runtime proof harness — LANDED (2026-07-09, PR #284).
  Run python scripts/prove_runtime_truth.py before every merge.
Observation scaffold — LANDED (2026-07-09, PR #285).
Seven mornings logged and synthesized — COMPLETE (2026-07-22,
  docs/observation/SEVEN_MORNING_SYNTHESIS_2026-07-22.md).
Grounded brief/category routing (synthesis rank-1 defect) — COMPLETE
  (PR #312, merged 2026-07-23; 205 focused tests, runtime proof PASS).
Timeout containment (Morning 6-7 cross-turn blocking) — COMPLETE (PR #311).
Post-#312 owner-use evidence - RECORDED (2026-08-07; suitable for product
  prioritization, with incomplete exact runtime provenance).
Commitment Truth + Natural Reminder Handoff — COMPLETE (PR #330 plus PR #332;
  fresh-main closeout PASS at dfef1db5 on 2026-08-09).
Local Action Outcome Truth — COMPLETE (PR #331; merged-main live proof PASS).
Semantic Substrate Slice 1 — COMPLETE (PR #334; merged in current main c44b6d0).
2026-08-12 fresh-main real-user acceptance — RECORDED for planning; 25-step golden
  regression covered, full 36-section catalog incomplete.
Current planning priority: P1-A user-visible commitment/capability truth, its targeted
  fresh-main live proof, then the separately bounded P1-B receipt-correlated action/outcome
  history and its targeted live proof. Neither implementation nor either proof is authorized by this
  documentation sync. PR #335 remains draft/unmerged and must not be modified, marked ready,
  or merged from this ordering text. Google Tasks remains unstarted.
Authorization Integrity Slice 2A remains separately approved, paused, and
  unimplemented on main.
Do not select implementation work from any document dated before 2026-07-07
  without checking docs/CANONICAL/07_ROADMAP_TRUTH.md first.
```

For full merge-by-merge continuity, use `docs/status/CURRENT_WORK_STATUS.md`.

Current grounded truth:

```text
OpenClaw is implemented runtime code with bounded/manual-first execution surfaces.

The unrestricted freeform-goal registry exposure identified during the audit was
narrowed by PR #154 through read-only allowlisting, mutation-tool exclusion,
MeteredNetworkProxy enforcement, and governance regression tests.

This does not make OpenClaw broadly autonomous or fully governance-certified.

Phase 8 envelope execution is PARTIAL — broader envelope-governed execution
remains deferred. Phase 9 surfaces are ACTIVE but built on an incomplete Phase 8
foundation. These are human-layer annotations; CURRENT_RUNTIME_STATE.md is the
authoritative machine-generated runtime truth.
```

## Required Context Files

Read these before making brain/governance changes:

- `docs/brain.md`
- `docs/brain/README.md`
- `.agent_context/brain_loop.md`
- `.agent_context/environments.md`
- `.agent_context/governance.md`
- `.agent_context/current_priority.md`

## Do Not

- add execution capabilities without explicit request
- bypass GovernorMediator
- treat memory as permission
- claim conceptual docs are implemented runtime behavior
- treat Cap 64/65 certification locks (both P1-P5 locked, 2026-05) as permission
  to expand scope — locked means bounded, not expandable
- add Shopify writes or email sending under existing read/draft capabilities

## Repo Truth Rule

Generated runtime docs and implementation beat roadmap language.

When exact current status matters, verify against code and generated runtime truth.
