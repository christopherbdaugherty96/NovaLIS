# AI Tooling Boundaries

## Purpose

AI tools can accelerate work on NovaLIS. They should not replace judgment, evidence, governance, or truth.

This file defines the boundaries for using external AI systems and generators around the project.

## Boundary Rules

1. Implementation beats documentation when they conflict.
2. Runtime truth beats stale summaries.
3. Tests beat assumptions.
4. Prototypes are not production systems.
5. Mockups are not evidence of runtime capability.
6. Suggestions are not approvals.
7. Intelligence is not authority.
8. Risky actions require visible review and bounded execution.

## What AI Tools Are Good For

- brainstorming
- code suggestions
- documentation drafting
- repo audits
- critique and second-pass review
- summarization
- test ideas
- UI mockups
- content refinement
- workflow design

## What They Must Not Decide Alone

- whether a feature exists
- whether code is secure
n- whether a release is ready
- whether a claim is truthful
- whether an action should bypass governance
- whether user trust has been earned
- whether risky automation is acceptable

## NovaLIS Runtime Boundaries

No external assistant should be represented as equivalent to Nova's governed runtime path.

The governed path exists to keep execution bounded, reviewable, and attributable.

## Documentation Standard

When writing docs:

- separate implemented vs planned vs prototype vs future
- avoid inflated language
- avoid duplicate docs with the same purpose
- prefer clear explanations over internal jargon
- link to evidence when possible
- correct stale claims quickly

## Public Claim Standard

Do not claim:

- consumer readiness if not true
- capabilities not present in code
- autonomous behavior that is not implemented
- security guarantees not validated
- integrations that are only conceptual
- production maturity based only on visuals

## Human Responsibility

The final responsibility for what enters the repo remains human review.

AI assistance can speed work. It does not remove accountability.
