# AI Ecosystem Operating Rules

Status: Draft
Date: 2026-06-08
Source: User-directed build prompt
Applies to: Obsidian coordination, AI handoffs, business planning, NovaLIS planning

## Purpose

This document defines how multiple AI tools and planning systems can coordinate
around one ecosystem without confusing context, truth, authority, and execution.

The operating model supports:

- Obsidian as shared context and navigation.
- GitHub as implementation workflow and reviewed project documentation.
- Nova governance as execution authority.
- Receipts and logs as proof of actions.
- Human review as the highest business authority.

## Mandatory Principles

1. Obsidian coordinates context.
2. Obsidian does not authorize execution.
3. Intelligence is not authority.
4. Memory does not grant permission.
5. Implementation does not grant execution authority.
6. Human approval remains the highest business authority.
7. Nova governance controls execution authority.
8. Runtime behavior must be provable through receipts and logs.

## Definitions

Context:
Information used to understand work. Context may include notes, transcripts,
drafts, project descriptions, task handoffs, and research.

Truth:
Accepted current state. Truth must be traceable to reviewed documents, merged
code, generated runtime docs, receipts, or logs.

Authority:
Permission to act. Authority comes from the human operator and from Nova's
governed capability path, not from memory or notes.

Execution:
An actual performed action that changes state, opens a governed local surface,
creates an external effect, or produces a receipt/log trail.

No document may simultaneously function as context, truth, authority, and
execution.

## Authority Hierarchy

| Layer | Role |
| --- | --- |
| Human operator | Business authority and final approval |
| Nova governance | Execution authority and capability checks |
| Capability registry and locks | Defines allowed execution surfaces |
| Governor / execution boundary | Mediates governed action |
| Receipts and logs | Evidence of completed or refused actions |
| GitHub repo | Implementation truth and reviewed docs |
| Obsidian vault | Context, planning, handoffs, and navigation |
| AI tools | Analysis, drafting, coding, review, and proposals |

## Context Hierarchy

1. Runtime and receipt-backed facts.
2. Current accepted priorities and locks.
3. Reviewed architecture and decision logs.
4. Draft planning and AI outputs.
5. Archive and historical material.

## Source Ranking

Tier 0:

- Runtime state
- Receipts
- Logs
- Actual code
- Generated runtime docs

Tier 1:

- Current accepted priorities
- Active locks
- Accepted scope

Tier 2:

- Reviewed architecture
- Reviewed decisions
- Approved plans

Tier 3:

- Drafts
- AI outputs
- Brainstorming
- Future planning

Tier 4:

- Archive
- Historical documents
- Superseded material

Lower tiers may never override higher tiers.

## Approval Requirements

Human review is required before:

- Changing active priority.
- Treating a draft as accepted truth.
- Adding or expanding a runtime capability.
- Adding an external write path.
- Adding browser/computer-use expansion.
- Adding scheduler or background work.
- Adding OpenClaw integration or expansion.
- Adding Shopify writes or commerce mutation.
- Changing capability locks.
- Claiming live proof or certification.
- Merging a PR.

## AI Roles

ChatGPT:
Strategic synthesis, review, prompt design, planning review, and final alignment.

Codex:
Repo-grounded implementation, code review, tests, validation, documentation, and
PR preparation.

Claude:
Long-form reasoning, drafting, second-pass critique, and alternate analysis.

OpenClaw:
Only a governed runtime environment when explicitly authorized by Nova's current
capability path. It is not authorized by Obsidian notes or AI plans.

Nova:
Governance-first local AI system. Nova may understand and plan before action,
but execution remains mediated by the Governor, capability registry, execution
boundaries, receipts, and logs.

## Update Protocol

AI may propose updates.

AI may not silently modify accepted truth.

AI-generated content must include:

- Date
- Source
- Status
- Reason

Accepted changes require review.

Stale content must be marked before replacement.

Nothing may be deleted without traceability. Prefer marking superseded content
and linking to the replacement.

## Conflict Resolution

When sources disagree:

1. Runtime truth wins.
2. Current accepted scope wins.
3. Reviewed documents beat drafts.
4. Decision logs beat AI chat output.
5. Drafts never override accepted truth.

If conflict remains unresolved, stop and request human review.

## Branch And PR Rules

- One branch per workstream.
- One PR per reviewed scope.
- Docs-only PRs stay docs-only.
- Runtime PRs require tests or proof appropriate to the risk.
- Baseline CI cleanup stays separate from feature or docs PRs.
- Untracked future docs must not leak into active PRs.
- Capability lock changes require a separate reviewed decision.

## Stale Document Policy

Every operating document should include:

- Status
- Last reviewed date
- Source
- Supersedes, if applicable
- Superseded by, if applicable

Stale documents should be marked as stale or archived. They should not be
quietly deleted.

## Session Handoff Format

Each AI session should end with:

- What changed
- What did not change
- Files touched
- Commands run
- Tests passed
- Tests failed
- Evidence collected
- Known limits
- Next exact action
- Do-not-touch list

## Validation Requirements

Validation must distinguish:

- Document validation
- Repo-state validation
- Runtime validation
- Live proof

No agent may invent unavailable validation, runtime access, receipts, or test
results.

If repository access, Obsidian vault access, runtime access, or required files
are unavailable, explicitly report the limitation and produce the maximum
reviewable implementation package possible without inventing results, tests,
evidence, or completed work.
