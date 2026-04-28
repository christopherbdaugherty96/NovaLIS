# NovaLIS

![Alpha](https://img.shields.io/badge/stage-alpha-blue) ![Active Build](https://img.shields.io/badge/status-active_build-brightgreen) ![Local First](https://img.shields.io/badge/model-local--first-purple) ![Trust First](https://img.shields.io/badge/focus-trust--first-orange)

**Version 0.4 Alpha**

NovaLIS is a governance-first local AI system designed to separate intelligence from execution.

Most AI systems focus on what the model can generate. Nova focuses on what the system is allowed to do, how decisions are routed, and how actions stay visible, bounded, and reviewable.

## Why Nova Exists

Reasoning power should not automatically equal authority.

Modern AI products are moving from simple answering toward systems that can search, remember, route, open tools, draft, automate, and connect to outside services. That shift makes the authority problem more important, not less important.

Nova exists to make that boundary explicit:

```text
Useful intelligence under visible control.
```

The goal is not hidden autonomy. The goal is a local assistant runtime where useful actions pass through governed capability checks, execution boundaries, and audit trails.

## The Nova Flow

Nova should be understood as a layered system, not as a single chatbot box:

```text
User input
  -> intelligence / interpretation
  -> governance check
  -> approved capability
  -> bounded execution
  -> trust output / receipt
```

This framing is important. A normal agent diagram often says: input -> AI brain -> execution. Nova inserts the governance layer as the central product feature.

## What Makes It Different

- Capability-based authority model
- Governed action routing
- Local-first architecture
- Execution boundaries
- Reviewable action history
- Runtime truth documentation
- Honest limitations
- Trust-first product direction

Nova should not be evaluated only by raw feature count. It should be evaluated by whether its actions remain understandable, bounded, reviewable, and grounded in runtime truth.

## What Works Today

See: [`docs/product/WHAT_WORKS_TODAY.md`](docs/product/WHAT_WORKS_TODAY.md)

For the exact live capability surface, use the generated runtime truth docs:

- [`docs/current_runtime/CURRENT_RUNTIME_STATE.md`](docs/current_runtime/CURRENT_RUNTIME_STATE.md)
- [`docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`](docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md)
- [`docs/current_runtime/GOVERNANCE_MATRIX.md`](docs/current_runtime/GOVERNANCE_MATRIX.md)

## Start Here

1. [What Works Today](docs/product/WHAT_WORKS_TODAY.md)
2. [Quickstart](QUICKSTART.md)
3. [Governed System Architecture](docs/product/GOVERNED_SYSTEM_ARCHITECTURE.md)
4. [Trust Review Card Plan](docs/product/TRUST_REVIEW_CARD_PLAN.md)
5. [Known Limitations](docs/product/KNOWN_LIMITATIONS.md)
6. [Runtime Truth](docs/current_runtime/CURRENT_RUNTIME_STATE.md)

## Try These 5 Commands

- What works today?
- Weather in Belleville
- Summarize today’s news
- Draft an email to John about tomorrow
- Explain what Nova can do

## Current Status

Nova is an **alpha build** intended for technical users and early adopters.
It is real software under active development, not a finished consumer product.

Current public framing should stay honest:

- Real governed runtime work exists.
- Setup still expects technical users.
- Some capabilities depend on local environment and credentials.
- Broad autonomous execution is not the current product promise.
- The Trust Review Card / Trust Panel is the highest-value missing proof layer.

## Core Principle

**Intelligence is not authority.**

Nova may reason, suggest, draft, summarize, search, and route. Real actions should remain bounded by capability checks, user-visible review, execution boundaries, and ledgered receipts.

## Explore Next

- [Use Cases](USE_CASES.md)
- [Why Nova](docs/product/WHY_NOVA.md)
- [Governed System Architecture](docs/product/GOVERNED_SYSTEM_ARCHITECTURE.md)
- [Trust Review Card Plan](docs/product/TRUST_REVIEW_CARD_PLAN.md)
- [Demo Walkthrough](docs/product/DEMO_WALKTHROUGH.md)
- [Docs Index](docs/INDEX.md)
- [Changelog](CHANGELOG.md)

## License

Nova is source-available under the Business Source License 1.1. See [LICENSE](LICENSE).
