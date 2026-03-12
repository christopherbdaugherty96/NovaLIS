# Nova Phase-5 Capability Summary and Sellability Brief
Date: 2026-03-12
Status: Runtime-capability summary (current implementation baseline)
Classification: Product positioning artifact (governance-safe)

## Positioning
Nova is moving from a prompt-response assistant to a governed personal intelligence workspace for ongoing projects.

Core distinction:
- Conventional assistants: `Question -> Answer`
- Nova runtime: `Context -> Continuity -> Reasoned Guidance -> Explicit Governed Persistence`

Constitution preserved:
- Intelligence may expand.
- Authority does not expand without explicit unlock.

## What Nova Can Do Now

### 1) Explain Anything (Invocation-Bound Perception)
- Analyze visible screen context when asked.
- Explain pages, errors, and file content.
- Provide practical next-step guidance for common issues.

### 2) Working Context Engine (Session-Scoped)
- Maintains temporary task context for follow-up coherence.
- Supports natural follow-up prompts (`help me do this`, `what should I click next`).
- Remains non-persistent and non-autonomous.

### 3) Project Continuity Threads
- Create/resume/list project threads.
- Attach updates and decisions.
- Generate continuity briefs with goal, artifacts, blockers, and next actions.

### 4) Continuity Reasoning Layer
- Thread Health classification (`blocked`, `at-risk`, `on-track`) with score + rationale.
- Project status summaries.
- Biggest blocker extraction.
- Cross-thread prioritization via `which project is most blocked right now`.
- Recommendation transparency via `why this recommendation`.

### 5) Governed Memory + Thread Bridge
- Explicit governed memory operations via capability `61` (`memory_governance`).
- Thread bridge commands:
  - `memory save thread <name>`
  - `memory save decision for <thread>: <text>`
  - `memory list thread <name>`
- Memory linkage fields on saved items:
  - `links.project_thread_name`
  - `links.project_thread_key`

### 6) UX Surface Maturity
- Dashboard thread map with blocker/status/health context.
- Thread row memory badge (`Memory: N`) and memory actions.
- Inline decision save from thread row.
- Read-only `Changed: ...` mini-diff (since last viewed thread-map payload).
- Read-only thread detail panel:
  - goal
  - latest blocker
  - latest decision
  - recent decisions list
  - recent linked memory with timestamps
  - clearer blocked/next-step rationale wording

## Why This Is Sellable
Nova now directly answers daily workflow questions:
- "Where am I in my work?"
- "What is blocked right now?"
- "What changed since I last looked?"
- "What decision did we already make on this?"

This shifts product value from one-off answers to ongoing project continuity intelligence.

## Differentiators

### Governance as Product Value
- Governor-mediated execution path.
- Invocation-bound behavior.
- No hidden autonomy loops.
- Ledger visibility for governed actions.

### Context + Continuity + Persistence
- Perception-powered explanation.
- Threaded continuity reasoning.
- Explicit governed persistence linked to project workstreams.

### Trust and Legibility
- Explainable "why" outputs.
- No silent persistence.
- Read-only insight surfaces separated from explicit write actions.

## Everyday Usage Pattern
1. User asks: `which project is most blocked right now`
2. Nova identifies the most blocked thread and why.
3. User asks: `thread detail deployment issue`
4. Nova returns focused blocker/decision/memory context.
5. User asks: `save decision` inline in thread row or command form.
6. Nova persists the decision through governed memory capability `61`.
7. User checks `memory list thread deployment issue` for durable linked history.

## Verification Snapshot (2026-03-12)
- `nova_backend/tests/phase5`: `25 passed`
- `nova_backend/tests/phase45`: `33 passed`
- Full backend suite (`nova_backend/tests`): `344 passed`
- Runtime docs drift check: passed
- Frontend mirror sync check: passed

## Next Sellability Milestone (No Autonomy Expansion)
- Cross-thread planning clarity:
  - "What should I work on first today?"
  - "Which project is closest to unblocked?"
  - "What changed since yesterday?"
  - "Which project has highest stall risk?"
