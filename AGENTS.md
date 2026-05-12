# AGENTS.md

Guidance for AI agents working on NovaLIS.

Start here before editing the repo.

## Core Rule

Intelligence is not authority.

Nova's reasoning layers may clarify, plan, search, summarize, and propose. Runtime execution still goes through the Governor, capability registry, execution boundaries, and receipts.

## Current Priority

Read `.agent_context/current_priority.md`.

Current active task:

```text
Generated runtime-doc regeneration after PR #152-#159.
```

Status:

```text
TODO tracked by PR #158.
Generator has not yet been run.
```

Scope:

```text
generated runtime docs / fingerprints / MOC artifacts only
no runtime code
no capability changes
no authority expansion
```

No runtime implementation priority is selected until generated runtime docs are synchronized and runtime-doc drift verification is complete.

Recent repo truth to preserve:

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
```

Current grounded truth:

```text
OpenClaw is implemented runtime code with bounded/manual-first execution surfaces.

The unrestricted freeform-goal registry exposure identified during the audit was narrowed by PR #154 through read-only allowlisting, mutation-tool exclusion, MeteredNetworkProxy enforcement, and governance regression tests.

This does not make OpenClaw broadly autonomous or fully governance-certified.
```

Do not start UI simplification, Cap 64 P5, Google connector runtime work, Shopify writes, ElevenLabs implementation, OpenClaw expansion, browser/computer-use expansion, external writes, finance automation, social posting automation, or autonomous workflow execution without a separate reviewed priority lock.

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
