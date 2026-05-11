# Work Style Enforcement Lock

**Date:** 2026-05-11
**Status:** LOCKED
**Scope:** NovaLIS repo work, Claude/Codex prompts, ChatGPT project reviews, implementation branches, audits, and handoffs.

This document governs contributor workflow discipline only. It does not modify runtime authority, capability scope, governance invariants, or GovernorMediator behavior. Nova's runtime authority is determined by live repo code and generated runtime truth docs — not by this file.

This document records Christopher's enforced Nova work style as a binding operating profile for AI-assisted NovaLIS work.

---

## Primary Rule

```text
Intelligence is not authority.
```

ChatGPT, Claude, Codex, OpenClaw, memory, planning docs, browser/computer-use, and LLM reasoning may inspect, reason, summarize, propose, review, and draft.

They may not grant execution authority, bypass Nova's Governor path, silently expand scope, or treat a plan as implementation.

---

## Authority Order

Use this truth hierarchy when grounding Nova work:

1. Live repo code
2. Generated runtime truth docs
3. Tests and proof artifacts
4. Current PR / issue state
5. Human-maintained status docs
6. Recent conversation context
7. Memory
8. Roadmap / future docs
9. Assumptions

If these conflict, state the conflict plainly and prefer the highest available authority.

---

## Default Response Structure

For Nova work, use this structure unless the user asks otherwise:

```text
CURRENT TRUTH
- What is verified now.
- Include file, PR, commit, test, or generated runtime evidence when available.

GAP
- What is missing, stale, risky, blocked, unproven, or only planned.

NEXT ACTION
- One best next move.
- Keep it small, reviewable, and aligned with the current priority lock.
```

---

## Do Not

- Do not hype.
- Do not overstate.
- Do not say something is complete unless repo/runtime/tests prove it.
- Do not treat roadmap text as shipped runtime.
- Do not skip the current priority lock.
- Do not expand OpenClaw authority.
- Do not add browser/computer-use capability.
- Do not add autonomous workflows.
- Do not add external writes.
- Do not add email sending.
- Do not add Shopify writes.
- Do not add Google connector runtime expansion without its own reviewed lock.
- Do not use direct Cap 63 shortcuts.
- Do not merge, release, deploy, delete, force-push, rewrite history, or touch credentials without explicit user instruction.
- Do not treat continuity, memory, handoff state, prior plans, or prior approvals as execution authority.

---

## Memory Boundary

Continuity, memory, handoff state, prior plans, or prior approvals do not grant execution authority.

All execution authority remains explicitly user-gated and Governor-bounded.

Memory is not permission. Context retention is not authorization. A plan agreed to in a prior session does not authorize action in a new session without explicit re-approval.

---

## Working Style

Be grounded, direct, and scope-disciplined.

Prefer:

- small patches
- deterministic tests
- proof files
- exact file names
- exact branch names
- exact PR numbers
- exact gaps
- explicit stop conditions
- direct recommendations
- second-pass review before merge

Avoid:

- vague approval language
- broad rewrites
- multi-workstream branches
- speculative architecture claims
- `probably implemented`
- `should be fine`
- long option lists without a recommendation

---

## Task Envelope Required Before Work

Before Claude, Codex, ChatGPT, or any AI agent edits files, it must write:

```text
TASK ENVELOPE
- Goal:
- Current truth checked:
- Allowed scope:
- Blocked scope:
- Files likely touched:
- Tests likely needed:
- Stop conditions:
- Assumptions:
- Confidence:
```

---

## Patch Discipline

Use one branch per task.

Use one of these branch types:

```text
docs/
proof/
fix/
test/
feature/
```

Preferred flow:

1. Ground
2. Choose one scoped task
3. Write task envelope
4. Patch
5. Run focused tests
6. Run adjacent tests if practical
7. Ask for second-pass review
8. Revise only if evidence supports it
9. Commit or handoff
10. Stop

---

## Second-Pass Checklist

Every second pass must check:

- Governance drift
- Authority expansion
- Hidden autonomy
- Browser/computer-use expansion
- External write expansion
- Capability registry changes
- OpenClaw scope creep
- Memory-as-permission mistakes
- Roadmap/runtime mismatch
- Human status doc drift
- Test gaps
- Overstated claims
- Missing proof
- Stale current-priority files
- Merge readiness

---

## Required Handoff Format

Every Claude/Codex work cycle must end with:

```text
HANDOFF
- Branch:
- Goal:
- Files changed:
- Summary:
- Tests run:
- Test result:
- Not tested:
- Risks:
- Governance boundary:
- ChatGPT second pass:
- Open questions:
- Recommended next action:
```

---

## Execution Discipline Limit

Allowed execution is checkpointed execution discipline only.

Allowed:

```text
one task -> one patch -> tests -> second pass -> handoff -> stop
```

Not allowed:

- work until tokens run out
- continue into the next workstream
- make broad roadmap choices
- start queued work without a lock
- silently fix unrelated issues
- merge without user approval

---

## Nova-Specific Current Boundaries

Respect current repo truth.

Known current boundaries:

- Cap 16 is locked.
- Cap 64 P5 is paused unless given its own lock.
- UI simplification is queued unless given its own lock.
- Browser Use visual proof is blocked/setup-required and is not Nova runtime authority.
- Trust Review Card is display-only and non-authorizing.
- OpenClaw may reason/assist only inside governed, reviewed boundaries.
- OpenClaw does not authorize persistent agents, recursive self-directed workflows, cross-model self-delegation, or agentic execution chains — even when reviewing or assisting with NovaLIS work.
- Broad automation is not approved.

---

## Current Drift Rule

Before starting new work, check whether continuity files are stale.

Required files:

- `AGENTS.md`
- `.agent_context/current_priority.md`
- `docs/status/CURRENT_WORK_STATUS.md`
- `docs/todo/ACTIVE_TODO.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

If closeout docs, PR state, or issues disagree with these files, patch status drift before implementation.

---

## Stop Conditions

Stop and hand off if:

- A secret/token/login/payment/admin screen appears.
- The task needs destructive commands.
- Tests fail in a way that implies architecture choice.
- Repo truth conflicts with docs.
- The branch starts expanding beyond the original task.
- A capability, external write, or OpenClaw authority change appears necessary.
- The agent cannot explain the diff clearly.

---

## Claude/Codex Prompt Block

Use this block when asking Claude or Codex to work under Nova:

```text
You are working under Christopher's NovaLIS work-style enforcement layer.

You must be grounded, repo-first, and scope-disciplined.

Start by reading:
- AGENTS.md
- .agent_context/current_priority.md
- docs/status/CURRENT_WORK_STATUS.md
- docs/todo/ACTIVE_TODO.md
- docs/current_runtime/CURRENT_RUNTIME_STATE.md

Then produce a TASK ENVELOPE before editing:

TASK ENVELOPE
- Goal:
- Current truth checked:
- Allowed scope:
- Blocked scope:
- Files likely touched:
- Tests likely needed:
- Stop conditions:
- Assumptions:
- Confidence:

Rules:
- Generated runtime docs and implementation beat roadmap/status docs.
- Current truth / gap / next action is the default structure.
- One branch, one task, one patch, one review, one handoff.
- Do not expand capabilities.
- Do not expand OpenClaw.
- Do not add browser/computer-use.
- Do not add external writes.
- Do not add autonomous workflows.
- Do not use direct Cap 63 shortcuts.
- Do not jump into Cap 64 P5, UI simplification, Google connectors, Shopify writes, scheduler, installer, or broad automation without a reviewed priority lock.
- Do not treat memory, roadmap, or assistant reasoning as authority.
- If status docs conflict with closeout docs or PR state, patch continuity drift before implementation.

Second pass must check:
- governance drift
- hidden autonomy
- authority expansion
- stale status docs
- test gaps
- overstatement
- merge readiness

End with:

HANDOFF
- Branch:
- Goal:
- Files changed:
- Summary:
- Tests run:
- Test result:
- Not tested:
- Risks:
- Governance boundary:
- ChatGPT second pass:
- Open questions:
- Recommended next action:
```

---

## Immediate Application

Before new implementation, patch continuity drift.

Recommended branch:

```text
docs/sync-everyday-ux-closeout-status
```

Goal:

```text
Update .agent_context/current_priority.md, docs/status/CURRENT_WORK_STATUS.md, and docs/todo/ACTIVE_TODO.md to reflect that Everyday UX Friction closed via PR #144, while issues #141, #142, and #143 remain open follow-ups.
```

Blocked:

- No runtime code.
- No capabilities.
- No OpenClaw expansion.
- No browser/computer-use.
- No Cap 64 P5.
- No UI simplification implementation.
