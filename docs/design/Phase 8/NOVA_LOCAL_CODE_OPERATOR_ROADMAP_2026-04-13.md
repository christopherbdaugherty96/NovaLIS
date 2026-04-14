# Nova Local Code Operator Roadmap
Date: 2026-04-13
Status: Active design guidance
Scope: Define how Nova should gain Codex-like local coding help through OpenClaw and local Gemma without breaking governance or introducing hidden write authority

## Purpose
This packet answers a practical product question:

How should Nova gain a real "review this project, propose changes, then help apply them" coding workflow while staying local-first, governed, and affordable?

The answer is not:
- unrestricted autonomous coding
- hidden repository mutation
- cloud-first coding dependency

The answer is:
- OpenClaw as the governed worker layer
- local Gemma as the default reasoning lane
- explicit envelopes, diffs, approvals, and verification before any write-capable widening

## Current Grounded Reality
As of 2026-04-13, Nova already has:
- a real OpenClaw home-agent foundation
- manual template execution with strict preflight
- local-first summarization
- a narrow optional OpenAI fallback for task reports
- local project summary, architecture-report, and structure-map flows outside the Agent page

What Nova does not have yet:
- a full coding operator that can inspect a repo, propose a patch, apply it, and verify it end to end through one governed lane
- write-capable OpenClaw envelopes for repo changes
- approval-gated patch execution as a first-class user-facing operator flow

That means the shortest robust path is not "full autonomous coding next."

It is:
- first unify read-only project understanding inside OpenClaw
- then add patch proposal
- then add approval-gated apply
- then add bounded verify-and-repair loops

## Product Goal
Nova should eventually feel like this:

You can say:
- review this project
- summarize what this repo does
- tell me the best next cleanup
- make these changes
- improve this wording
- propose the safest fix

Nova should then:
1. inspect the project
2. explain what it found
3. propose a plan
4. prepare a patch or exact change set
5. ask for approval at the real risk boundary
6. apply the change only within the allowed envelope
7. run checks
8. summarize results, gaps, and follow-up work

## Core Design Rule
The right mental model remains:
- Nova is the face, trust layer, and governing law
- OpenClaw is the worker
- Gemma is the local reasoning brain

This must never collapse into:
- "the model can do whatever it wants in the repo"

Better reasoning is not the same thing as safe execution.

## The Ordered Build Path

## Phase A: Read-only project analyst
This is the first step and should ship first.

Nova gains:
- a manual OpenClaw template for local project analysis
- bounded local file reading inside the current workspace
- a project summary, architecture orientation, and recommended next actions
- local Gemma summarization when available
- deterministic local fallback when it is not

This phase is:
- read-only
- no patching
- no writes
- no cloud dependency

## Phase B: Patch proposal mode
After read-only analysis is stable, Nova should add:
- patch planning
- file-level change proposals
- exact diff previews
- risk notes
- suggested tests

Still no write authority by default.

The output should be:
- "here is the patch I propose"
- "here is why"
- "here is what to test"

## Phase C: Approval-gated apply mode
Only after patch proposal is stable should Nova add:
- explicit apply approval
- allowed-path enforcement
- branch or checkpoint creation before apply
- patch application through one governed path
- write audit continuity

This is the real risk boundary and should never be silent.

## Phase D: Verify-and-repair loop
After apply mode exists, Nova can add:
- allowed test command execution
- bounded retry loops
- error interpretation
- one or two follow-up repair attempts

This phase must stay bounded by:
- run count
- file count
- time
- allowed commands

## Phase E: Everyday coding operator flow
Only after A-D are stable should Nova feel like a daily coding operator.

That later surface should support:
- repo review
- scoped implementation requests
- docs cleanup
- safe refactors
- frontend polish passes
- wording and copy improvements

## Guardrails That Must Stay Non-Negotiable

### 1. Local-first model policy
The default coding lane should stay:
- local Gemma first
- deterministic local fallback second
- optional cloud reasoning only if explicitly enabled later

For early coding-operator work, no metered fallback should be required for read-only repo analysis.

### 2. Envelope-first execution
Every operator run must declare:
- purpose
- allowed files or paths
- allowed tools
- read and write budgets
- duration limit
- escalation conditions

No envelope means no execution.

### 3. Diff before write
Any write-capable future lane must present:
- what will change
- where
- why
- how to verify it

before apply is allowed.

### 4. Stop and recovery
The user must be able to:
- cancel the run
- inspect what happened
- see what completed
- see what failed

### 5. No hidden repo mutation
Nova should never silently:
- rewrite files
- change settings
- commit code
- push code

without an explicit approval moment.

## Gemma's Proper Role
Gemma should handle:
- repo summaries
- architecture explanation
- planning help
- wording and documentation cleanup
- patch rationale
- small to medium local coding tasks

Gemma should not be treated as:
- the governor
- the approval system
- direct execution authority

The best product framing is:
- Local by default
- Strong review before effect
- You stay in control

## What The First Shipping Slice Should Look Like
The first real implementation slice should add a new OpenClaw template that:
- analyzes the current workspace
- reads only a small bounded set of local files
- returns a clear repo summary
- names the main surfaces
- gives safe next-step suggestions

This first slice should appear as:
- a manual Agent page template
- a read-only run
- a low-cost local workflow

It should not yet:
- write code
- mutate docs
- commit changes
- browse broadly
- use OpenAI by default

## Recommended Naming
The clearest user-facing naming is:
- `Project Snapshot`

This is calmer and more truthful than:
- code agent
- autonomous coder
- repo mutation mode

Later phases can introduce stronger terms like:
- Patch Proposal
- Apply Approved Patch
- Verify Changes

## Acceptance Criteria For The First Step
The first shipped step is successful when:
- a user can run a Project Snapshot from the Agent page
- the run stays read-only
- the run stays local-first
- the summary clearly explains the current project
- the output recommends good next steps
- the template appears in status/setup/runtime surfaces without confusing the existing OpenClaw model

## Relationship To Existing Nova Surfaces
This roadmap should be read alongside:
- `docs/design/Phase 8/PHASE_8_DOCUMENT_MAP.md`
- `docs/design/Phase 8/NOVA_OPENCLAW_END_TO_END_EXPANSION_MASTER_TODO_2026-04-02.md`
- `docs/design/Phase 6/NOVA_GEMMA_4_LOCAL_BRAIN_STRATEGY_2026-04-02.md`
- `docs/reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md`

The intended interpretation is:
- current repo-summary tools stay useful
- OpenClaw becomes the unified governed operator lane for future coding help
- local Gemma remains the default brain for this lane
- write authority is later and must be earned

## Short Version
Nova should gain local coding help in this order:
1. read-only project analysis
2. patch proposal
3. approval-gated apply
4. bounded verify-and-repair
5. everyday coding operator polish

That is the clean robust path to a Codex-like Nova without turning Nova into an unsafe silent repo actor.
