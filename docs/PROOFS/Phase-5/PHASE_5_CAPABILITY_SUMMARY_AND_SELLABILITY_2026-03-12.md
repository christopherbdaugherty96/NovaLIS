# Nova Phase-5 Capability Summary and Sellability Brief
Date: 2026-03-12  
Status: Runtime-capability summary (post continuity reasoning pass)  
Classification: Product positioning artifact (governance-safe)

## Positioning
Nova is now transitioning from an assistant that answers prompts into a governed personal intelligence workspace that helps users understand ongoing work.

Core distinction:
- Conventional assistants: `Question -> Answer`
- Nova model: `Work Context -> Continuity -> Reasoned Guidance`

Constitution preserved:
- Intelligence may expand.
- Authority does not expand without explicit unlock.

## What Nova Can Do Now

### 1) Explain Anything (Invocation-Bound Perception)
- Analyze visible screen context when asked.
- Explain pages, errors, and file content.
- Provide practical next-step guidance for common issues (for example dependency/import failures).

### 2) Working Context Engine (Session-Scoped)
- Maintains temporary task context for follow-up coherence.
- Supports natural follow-up prompts (`help me do this`, `what should I click next`).
- Remains non-persistent and non-autonomous.

### 3) Project Continuity Threads
- Create and resume project threads.
- Attach updates and decisions.
- Generate continuity briefs with:
  - goal
  - artifacts
  - blockers
  - next actions

### 4) Continuity Reasoning Layer
- Thread Health classification (`blocked`, `at-risk`, `on-track`) with score and rationale.
- Project status summaries.
- Biggest blocker extraction.
- Cross-thread prioritization via `most blocked project` view.
- Recommendation transparency via `why this recommendation`.

### 5) UX Surfaces
- Dashboard context insight panel.
- Dashboard project thread map with active thread, blocker preview, and status actions.
- Quick actions for explain mode and continuity workflows.

## Why This Is Sellable

Nova now solves a daily user pain that generic assistants often miss:
- “Where am I in my work?”
- “What is currently stuck?”
- “What should I do next?”

This shifts value from one-off answers to ongoing project intelligence.

## Differentiators (Product-Level)

### Governance as Product Value
- Governor-mediated execution path.
- Invocation-bound behavior.
- No hidden autonomy loops.
- Ledger visibility for governed actions.

### Context + Continuity
- Perception-powered explanations.
- Threaded project continuity.
- Cross-thread blocker reasoning.
- Transparent recommendation rationale.

### User Trust
- Explainable “why” output.
- No silent action execution.
- Calm and controlled interaction model.

## Everyday Usage Pattern
1. User asks: `Which project is most blocked right now?`
2. Nova identifies the most blocked thread with reason.
3. User asks: `Continue that.`
4. Nova returns a continuity brief.
5. User asks: `Why this recommendation?`
6. Nova explains rationale.
7. User says: `Save this fix attempt.`
8. Nova updates the active thread.

This is a clean Phase-5 personal intelligence workflow.

## Readiness Snapshot
- Runtime behavior remains invocation-bound.
- No governor bypass introduced.
- No background monitoring introduced.
- Test status at time of writing:
  - `nova_backend/tests/phase5`: `13 passed`
  - full backend suite: `332 passed`

## Next Sellability Milestone
Highest-value next increment (without autonomy expansion):
- Cross-thread planning clarity:
  - “What should I work on first today?”
  - “Which project is closest to unblocked?”
  - “What changed since yesterday?”
  - “Which project has highest stall risk?”

This would strengthen Nova’s role as a trusted personal intelligence workspace while staying within governance constraints.
