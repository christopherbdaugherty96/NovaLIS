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
Engineering remains frozen except for explicitly approved proof/truth-sync work
and critical bugs.
The seven-morning gate is CLOSED. Its rank-1 defect — grounded brief/category
routing — was repaired, merged as PR #312 (2026-07-23), and verified on fresh
`main` (docs/status/GROUNDED_BRIEF_ROUTING_CLOSEOUT_2026-07-23.md).
No additional seven-morning or open-ended observation gate is required.
The targeted post-#312 owner-use session occurred on 2026-08-07 and is recorded
in docs/observation/OWNER_ACCEPTANCE_POST_312_2026-08-07.md. It is prospective
owner-use evidence suitable for product prioritization; exact commit-level
attribution is limited because the running SHA was not captured.
Active owner-selected product repair: Commitment Truth + Natural Reminder
Handoff (lock: docs/status/PRIORITY_LOCK_2026-08-07_COMMITMENT_TRUTH_REMINDER_HANDOFF.md).
Do not start another acceptance cycle or select another product lane until this
repair closes or is explicitly superseded. Authorization Integrity Slice 2A
remains separately approved but is temporarily paused behind this observed P1
correctness/trust repair. Do not mix the two implementations or PRs.
Runtime recovery remains historical/accepted context, deferred until
observation evidence reactivates it.
```

Not authorized without a separate reviewed priority lock:

```text
New implementation lanes, capability expansion, Google connector runtime work,
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
Current activity: land and implement only Commitment Truth + Natural Reminder
  Handoff. No additional acceptance morning or secondary product lane is active.
Authorization Integrity Slice 2A remains separately approved and temporarily
  paused behind this observed P1 correctness/trust repair.
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
