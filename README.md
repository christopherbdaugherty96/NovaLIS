# NovaLIS

NovaLIS is a governed local AI system that separates intelligence from execution.

**Live preview:** [NovaLIS GitHub Pages](https://christopherbdaugherty96.github.io/NovaLIS/)

It is built for people who want a useful assistant without surrendering visibility or control. Nova can reason, summarize, operate bounded local actions, draft messages, and run governed operator workflows, but real actions pass through explicit capability gates, policy checks, and audit logging.

> Intelligence may expand. Authority may not expand without an explicit unlock.

For the authoritative runtime truth, active capability count, enabled phases, and generated fingerprint, see [docs/current_runtime/CURRENT_RUNTIME_STATE.md](docs/current_runtime/CURRENT_RUNTIME_STATE.md).

---

## Why It Exists

Most AI assistants blend conversation, tool use, and execution into one opaque surface. NovaLIS treats those as separate responsibilities:

- conversation can explain, plan, and present
- capabilities define what the system is allowed to do
- governance checks whether an action is permitted
- the ledger records what happened and why
- the user keeps final authority over sensitive actions

That makes Nova less flashy in the wrong places and more trustworthy where it matters.

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

Nova is early software with a serious governance model. It is actively evolving across runtime reliability, routing quality, memory governance, operator workflows, connector support, and public documentation.

Current documentation work is also tightening first-use clarity and preview quality so the public-facing surface better matches the underlying runtime quality.

## License

Nova is source-available under the Business Source License 1.1. See [LICENSE](LICENSE).
