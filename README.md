# NovaLIS

NovaLIS is a governed local AI system that separates **intelligence** from **execution**.

**Live preview:** [NovaLIS GitHub Pages](https://christopherbdaugherty96.github.io/NovaLIS/)

Nova is built for people who want a useful assistant without surrendering visibility or control. It can reason, summarize, operate bounded local actions, draft messages, and run governed operator workflows, but real actions pass through explicit capability gates, policy checks, and audit logging.

> Intelligence may expand. Authority may not expand without an explicit unlock.

---

## What Nova Is

NovaLIS is not an unrestricted agent. It is a governance-first assistant architecture designed around a simple rule:

**Reasoning can be powerful, but authority must stay bounded, visible, and reviewable.**

The system is designed to keep conversation, capability access, execution, and audit history structurally separated.

---

## Live / Public Surface

- [Live GitHub Pages preview](https://christopherbdaugherty96.github.io/NovaLIS/)
- [Authoritative runtime state](docs/current_runtime/CURRENT_RUNTIME_STATE.md)
- [Docs index](docs/INDEX.md)
- [Quickstart](QUICKSTART.md)

---

## Why It Exists

Most AI assistants blend conversation, tool use, and execution into one opaque surface. NovaLIS treats those as separate responsibilities:

- **Conversation** can explain, plan, draft, and present.
- **Capabilities** define what the system is allowed to do.
- **Governance** checks whether an action is permitted.
- **Execution boundaries** enforce limits before anything runs.
- **The ledger** records what happened and why.
- **The user** keeps final authority over sensitive actions.

That makes Nova less flashy in the wrong places and more trustworthy where it matters.

---

## What Makes It Different

Nova is built around a governance spine instead of a free-running agent loop:

```text
User → Interface → GovernorMediator → CapabilityRegistry → ExecuteBoundary → Executor → Ledger
```

This structure is meant to prevent hidden authority drift. The assistant may become more capable over time, but actions still need to route through explicit capability checks and auditable boundaries.

---

## Current Focus

Nova is early software with a serious governance model. Current work is focused on:

- runtime reliability
- first-use clarity
- public preview quality
- governed operator workflows
- memory and continuity governance
- connector and local-action safety
- documentation alignment with runtime truth

For the authoritative runtime truth, active capability count, enabled phases, and generated fingerprint, see [docs/current_runtime/CURRENT_RUNTIME_STATE.md](docs/current_runtime/CURRENT_RUNTIME_STATE.md).

---

## Documentation

Start here:

- [Docs index](docs/INDEX.md)
- [Quickstart](QUICKSTART.md)
- [Runtime state](docs/current_runtime/CURRENT_RUNTIME_STATE.md)
- [Architecture](docs/reference/ARCHITECTURE.md)
- [Diamond preview release standard](docs/TODO/DIAMOND_PREVIEW_RELEASE_STANDARD_2026-04-23.md)
- [Website LLC priority switch](docs/TODO/PORTFOLIO_PRIORITY_SWITCH_WEBSITE_LLC_2026-04-22.md)

---

## Project Status

NovaLIS is actively evolving. The public-facing surface is being tightened so the first impression better matches the underlying runtime and governance work.

This repository should be treated as an active build, not a finished product.

---

## License

Nova is source-available under the Business Source License 1.1. See [LICENSE](LICENSE).
