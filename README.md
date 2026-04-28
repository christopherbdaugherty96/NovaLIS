# NovaLIS

![Alpha](https://img.shields.io/badge/stage-alpha-blue) ![Active Build](https://img.shields.io/badge/status-active_build-brightgreen) ![Local First](https://img.shields.io/badge/model-local--first-purple) ![Trust First](https://img.shields.io/badge/focus-trust--first-orange)

## The AI assistant you can actually trust.

**Version:** 0.4 Alpha  
**Status:** Active Build  
**Model:** Local-first / Trust-first  
**Last Major Update:** 2026-04-28  
**Next Milestone:** Trust Review Card

NovaLIS is a governed local AI system designed to help with real daily work while keeping execution under clear control.

Nova separates **intelligence** from **authority**: AI can reason and assist, but important actions remain bounded, visible, and reviewable.

> Intelligence may expand. Authority may not expand without an explicit unlock.

![Nova dashboard home](docs/product/assets/dashboard-home.png)

---

## Start Here
1. Read [What Works Today](docs/product/WHAT_WORKS_TODAY.md)
2. Follow [Quickstart](QUICKSTART.md)
3. Review [Known Limitations](docs/product/KNOWN_LIMITATIONS.md)
4. Check [Authoritative Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md)

---

## Who Nova Is For Right Now
- People who want a private daily-use AI assistant
- Builders who want visible boundaries around actions
- Early adopters comfortable with local tools
- Users who value control over hidden automation

---

## What Nova Helps With

### Understand & Organize
- Notes
- Memory
- Summaries
- Context carryover

### Help With Work
- Research
- Drafts
- Planning
- Explanations

### Safe Actions
- Approval-gated actions
- Visible decisions
- Action history
- Logged execution events

### Daily Utility
- Weather
- News
- Calendar snapshots
- Local tools

---

## Why Nova Exists
Most AI tools combine reasoning and authority in one opaque system.

Nova separates them. Reasoning can improve while real actions still require visible rules, capability checks, and audit trails.

---

## Core Specs
- **Backend:** Python 3.10+, FastAPI, Uvicorn, WebSockets
- **Local Models:** Ollama-compatible models with Gemma-focused runtime routes
- **Voice:** Optional local speech input/output surfaces
- **Governance Spine:** GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, Ledger
- **Memory:** Local governed memory and continuity system
- **UI:** Dashboard, Trust, Workspace, Agent, Settings, runtime surfaces
- **Connectors:** RSS news, ICS calendar, Shopify, optional metered OpenAI lane
- **Runtime Truth:** Generated runtime state, capability reference, and fingerprint docs

---

## What Makes Nova Different
- **Intelligence is not authority**
- **Actions are governed**
- **The user stays in control**
- **The system is inspectable**
- **Local-first matters**

---

## Current Focus
Build the best trustworthy daily-use personal AI assistant first.

Long-term platform ambitions remain possible, but current work is focused on clarity, trust, and usefulness.

---

## Explore Next
- [Use Cases](USE_CASES.md)
- [Why Nova](docs/product/WHY_NOVA.md)
- [Demo Walkthrough](docs/product/DEMO_WALKTHROUGH.md)
- [Docs Index](docs/INDEX.md)
- [Changelog](CHANGELOG.md)

## License
Nova is source-available under the Business Source License 1.1. See [LICENSE](LICENSE).
