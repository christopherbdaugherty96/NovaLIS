# Nova-OpenClaw Integration Standard

Updated: 2026-04-14
Status: Active design contract
Purpose: Define how Nova integrates with OpenClaw to minimize friction from upstream changes and keep Nova stable as the product layer

## Core Principle

Nova is the product. OpenClaw is a governed worker engine underneath it.

- Nova owns: UX, trust model, approvals, memory, settings, delivery surfaces, audit language, user-facing summaries
- OpenClaw owns: task envelopes, step execution, tool chaining, run budgets, retries, cancellation checkpoints, per-run state, worker-oriented reasoning loops
- Governor owns: law and boundary system, above both Nova and OpenClaw

## Stable Adapter Layer

Nova should never depend directly on raw OpenClaw internal class structure, exact template naming, storage format, or worker loop internals. Instead, Nova communicates through a stable adapter layer:

### Nova-Owned Contracts

**NovaTaskType** — Nova defines its own task types that map to OpenClaw templates:
- `morning_brief`
- `evening_digest`
- `market_watch`
- `project_snapshot`
- Future: `patch_proposal`, `apply_patch`, `verify_changes`

**NovaRunEnvelope** — Nova-owned purpose, budgets, approval class, allowed paths, allowed hosts, write class. The OpenClaw TaskEnvelope is the implementation detail; Nova presents its own envelope shape.

**NovaRunStatus** — Nova-defined lifecycle states:
- `queued`, `running`, `awaiting_approval`, `completed`, `failed`, `cancelled`

**NovaRunResult** — Nova-owned result shape:
- bottom line, detailed summary, risk notes, suggested next actions, proof/check output

**NovaApprovalBoundary** — Nova-owned approval classes:
- `read_only`, `proposal_only`, `approval_required`, `blocked`

### Anti-Coupling Rules

1. Never let Nova UI depend directly on raw OpenClaw template names or payloads
2. Map OpenClaw tools/templates into Nova capability IDs that Nova owns
3. Keep Nova run records in a Nova schema, even if OpenClaw has its own runtime objects
4. Translate OpenClaw output into Nova presentation objects before it reaches chat/UI
5. Keep Governor decisions above OpenClaw, not inside it
6. Keep provider routing above OpenClaw, or at least policy-controlled by Nova
7. Keep "what is live" defined by Nova runtime docs, not by whatever OpenClaw shipped upstream

## Adoption Layers

OpenClaw capabilities should be adopted in layers, not all at once:

### Layer 1: Read-Only Operator Tasks (Current)
- Briefings, repo analysis, project snapshot, architecture summary, issue review
- No writes, no network, no approval needed beyond "run"

### Layer 2: Proposal Tasks (Next)
- Patch proposal, wording proposal, test plan, cleanup plan
- Generates diffs/suggestions but never applies them

### Layer 3: Approval-Gated Effect Tasks (Future)
- Apply patch, run tests, stage docs changes
- Requires explicit user approval before any write

### Layer 4: Bounded Multi-Step Workflows (Future)
- Inspect -> propose -> apply -> verify
- Each transition requires checkpoint approval

## Provider Policy

- Default to local Gemma/Ollama first for all OpenClaw work
- OpenAI is a narrow optional fallback for task-report summarization only
- Cloud reasoning is optional review, not the default engine
- Token and cost awareness are part of the trust model

## How This Prevents Friction From OpenClaw Updates

When OpenClaw updates upstream:
- Nova's UI stays stable because it maps through Nova-owned contracts
- Nova's test suite stays stable because it tests Nova's adapter, not OpenClaw internals
- Nova's docs stay stable because they describe Nova's task types, not raw OpenClaw templates
- Only the adapter layer needs updating, and only when Nova wants to adopt a new feature

## Relationship to Other Docs

- Phase 8 canonical spec: `PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
- Local code operator roadmap: `NOVA_LOCAL_CODE_OPERATOR_ROADMAP_2026-04-13.md`
- Home agent master reference: `NOVA_OPENCLAW_HOME_AGENT_MASTER_REFERENCE_2026-03-27.md`
