# AI Tooling Workflow

## Purpose

NovaLIS may use AI-assisted tools for planning, drafting, implementation support, review, documentation, and prototype exploration.

This document defines how those tools fit into the project without confusing prototypes, generated output, or external helper tools with Nova's actual governed runtime.

The goal is simple: move faster without letting generated polish outrun implementation truth.

## Working Model

| Layer | Role |
| --- | --- |
| GitHub | Durable source of truth for code, documentation, commits, project status, review history, and implementation evidence |
| NovaLIS runtime | Governance/truth layer for bounded local AI execution, mediated capabilities, visible receipts, runtime truth, and auditability |
| ChatGPT / Codex / Claude | Planning, critique, implementation help, code review, documentation review, and repo-audit support |
| Lovable or similar visual builders | Speed/prototype layer for landing pages, dashboards, forms, public demos, and visual workflow drafts |
| Canva / Figma or similar design tools | Optional visual communication layer for diagrams, decks, mockups, and presentation assets |

## Core Rule

GitHub remains the durable source of truth.

AI tools can propose, draft, patch, and prototype, but implementation status is determined by the repository, tests, generated runtime truth docs, and working runtime behavior.

## Acceptable Uses

AI-assisted tools may be used for:

- drafting documentation
- improving README clarity
- auditing docs against code
- generating implementation prompts
- reviewing recent commits
- proposing tests
- creating mockups or landing page drafts
- prototyping trust-facing UI concepts
- exploring user workflows
- summarizing repo state for human review
- converting rough ideas into structured docs

## Prototype Uses

Lovable or similar tools may be useful for:

- public demo pages
- landing page drafts
- onboarding pages
- dashboard mockups
- form workflows
- quote/intake prototypes for related business projects
- visual explanations of Nova's governance model
- trust receipt viewer mockups
- "Try These Commands" style walkthroughs

These surfaces are prototypes until they are reviewed, grounded, and either linked clearly as demos or moved into the durable repo workflow.

## Non-Authoritative Uses

AI-generated output is not authoritative for:

- runtime truth
- capability counts
- implementation status
- security guarantees
- governance claims
- release readiness
- test results
- legal, financial, or operational commitments
- product maturity claims

When generated output conflicts with the repo, trust the implementation and generated runtime truth artifacts first.

## Nova-Specific Boundary

For NovaLIS, external prototype tools must not replace or bypass:

- `GovernorMediator`
- `CapabilityRegistry`
- `ExecuteBoundary`
- `NetworkMediator`
- `LedgerWriter`
- runtime truth generation
- capability gating
- confirmation review
- local execution boundaries
- audit logs or trust receipts

A visual prototype may explain governance. It must not be described as the governance runtime.

## Review Expectations

Before accepting AI-generated work into the repo, check:

- Does it match implementation?
- Does it reduce confusion?
- Does it avoid hype?
- Does it avoid duplicating existing docs?
- Does it clearly distinguish implemented, prototype, planned, and future work?
- Does it preserve the principle that intelligence is not authority?
- Does it help a smart first-time visitor understand the project faster?
- Does it avoid creating claims that tests or runtime evidence do not support?

## Repo Hygiene Rules

1. Merge new guidance into existing docs when a relevant doc already exists.
2. Avoid creating multiple overlapping strategy documents for the same idea.
3. Keep durable decisions in GitHub, not only in chats or prototype tools.
4. Link to live demos only when they exist and are accurate.
5. Label prototypes as prototypes.
6. Do not use polished screenshots to imply finished behavior that is not implemented.
7. Keep current runtime facts aligned with generated runtime truth docs.
8. Prefer clear, plain language over branding-heavy framing.

## Practical Workflow

1. Use chat or coding agents to think through an idea.
2. Convert useful ideas into repo documents or issues.
3. Use visual builders only when a clickable or visual prototype helps clarify the workflow.
4. Review generated code or copy against actual implementation.
5. Commit durable docs/code to GitHub.
6. Re-check docs after runtime changes.
7. Keep public-facing claims conservative until backed by code, tests, screenshots, or generated runtime truth.

## Good Fit Examples

- Draft a Trust Review Card UI spec.
- Prototype a public Nova demo page.
- Create a first-pass onboarding flow.
- Write a README improvement and then verify it against code.
- Generate a diagram explaining intelligence vs. authority.
- Draft test scenarios and then implement them in the repo.

## Poor Fit Examples

- Claiming a prototype is production-ready.
- Treating a generated landing page as proof of runtime capability.
- Replacing governed execution with an external automation path.
- Letting AI-generated copy claim features that are still planned.
- Adding docs because they sound impressive but do not help the user or maintainer.

## Truth-First Standard

A rough but accurate repo is better than a polished misleading one.

The workflow should make Nova clearer, more grounded, and easier to trust without blurring the difference between idea, prototype, implementation, and verified runtime behavior.
