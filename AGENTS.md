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

Read these documents before starting any task:

- `.agent_context/current_priority.md` — active task and safety boundaries
- `docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md` — post-audit
  stabilization/productization sequencing
- `docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md` — consolidated roadmap and
  positioning update

Current priority order:

```text
1. Approval gate wiring priority lock — scope the next execution-blocking lane cleanly
2. Approval gate wiring — make approval flow genuinely execution-blocking after the reviewed lock exists
3. Installer & bootstrap reliability
4. Live workflow demonstrations
5. CI stabilization
6. Envelope execution completion
7. Runtime cost enforcement
```

Not authorized without a separate reviewed priority lock:

```text
UI simplification, Cap 64 P5, Google connector runtime work, Shopify writes,
ElevenLabs implementation, OpenClaw expansion, browser/computer-use expansion,
external writes, finance automation, social posting automation, autonomous workflow
execution, multi-agent expansion, enterprise orchestration work.
```

---

## Current Task Status

```text
Runtime-doc regeneration — COMPLETE (2026-05-12).
Second-pass review and roadmap sync — COMPLETE (2026-05-12).
#141 live proof — COMPLETE (2026-05-14).
Trust Panel MVP — COMPLETE / merged / live-proven (2026-05-15).
Approval gate wiring priority lock — ACTIVE (2026-05-15).
Next: review the lock, then implement approval gate wiring in a separate scoped branch.
```

Recent repo truth:

```text
PR #134 — Cap 16 governed_web_search certification locked.
PR #144 — Everyday UX Friction workstream closed.
PR #145 — Work Style Enforcement Lock merged.
PR #146 — Creator-led Shopify/POD future model merged.
PR #147 — Nova two-domain product direction merged.
PR #148 — Piper-first voice direction merged.
PR #149 — Current status / continuity synchronization merged.
PR #150 — Audit-first safety boundary merged.
PR #152 — Full repo/doc/code alignment audit artifacts merged.
PR #153 — PASS4 OpenClaw freeform-goal inspection merged.
PR #154 — OpenClaw PATCH A-D hardening merged.
PR #156 — Search stopword cleanup merged.
PR #157 — Post-audit continuity/status synchronization merged.
PR #158 — Runtime-doc regeneration TODO tracking merged.
PR #159 — Current priority/status synchronization merged.
PR #167 — Trust Panel MVP receipt surface merged.
PR #169 — Approval gate next-sequence correction merged.
```

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
- mark Cap 64 or Cap 65 complete without live proof
- add Shopify writes or email sending under existing read/draft capabilities

## Repo Truth Rule

Generated runtime docs and implementation beat roadmap language.

When exact current status matters, verify against code and generated runtime truth.
