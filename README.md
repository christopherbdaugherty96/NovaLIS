# NovaLIS

NovaLIS is a governed local AI system that separates **intelligence** from **execution**.

Nova is built for people who want a useful assistant without surrendering visibility or control.

> Intelligence may expand. Authority may not expand without an explicit unlock.

---

## Understanding Nova
Start with the non-technical guide:
- [Human Guides](docs/reference/HUMAN_GUIDES/README.md)

The Human Guides explain Nova in plain language. Runtime truth files remain the authority for exact active status.

---

## Why Nova Exists
Most AI tools combine reasoning and authority in one opaque system.

Nova separates them.
Reasoning can improve while real actions still require visible rules, capability checks, and audit trails.

---

## What Nova Can Do
- Research and summarize information
- Help organize projects and workflows
- Maintain governed memory and continuity
- Provide trust and runtime visibility
- Support voice and assistant interactions
- Run bounded operator workflows

---

## Core Specs
- **Backend:** Python 3.10+, FastAPI, Uvicorn, WebSockets
- **Local Models:** Ollama-compatible models with Gemma-focused runtime routes
- **Default Local Model:** Gemma 4 route (32K context where configured)
- **Voice Input:** Vosk + sounddevice
- **Voice Output:** Local TTS path with speech-safe formatting
- **Governance Spine:** GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, Ledger
- **Operator Layer:** OpenClaw home-agent surfaces under Nova governance
- **Memory:** Local governed memory and continuity system
- **UI:** Dashboard, Trust, Workspace, Agent, Settings, runtime surfaces
- **Connectors:** RSS news, ICS calendar, Shopify, optional metered OpenAI lane
- **Runtime Truth:** Generated runtime state, capability reference, and fingerprint docs

---

## What Makes Nova Different
- **Intelligence is not authority** — stronger reasoning does not automatically grant stronger action power.
- **Actions are governed** — real actions route through capability checks and execution boundaries.
- **The user stays in control** — sensitive actions require explicit permission or remain blocked.
- **The system is inspectable** — runtime state, capabilities, and activity are intended to be visible.
- **Local-first matters** — Nova is designed around personal control instead of opaque cloud dependency.

---

## Verification & Sign-Off Status
Nova uses a structured certification model:
1. Unit Tests
2. Routing Tests
3. Integration Tests
4. API Tests
5. Live Human Sign-Off
6. Lock / Regression Protection

### Proven in Repo
- Governance routing and execution boundaries
- Runtime truth generation and drift checks
- Search, reporting, and assistant flows
- Memory, voice, and UI surfaces
- Regression and validation suites

### Current Verified Progress
- Capability 64 `send_email_draft`: P1-P4 passed, awaiting P5 live sign-off
- Certification and lock framework present
- Regression guard process documented

### Still Being Proven
- More capabilities completing full P1-P6 cycles
- Installer and cross-device reliability
- Daily-use polish and onboarding
- End-to-end workflow validation
- Production-style stability at scale

For exact current status, use the generated runtime docs and capability verification status files.

---

## Quick Start
- [Quickstart](QUICKSTART.md)
- [Docs Index](docs/INDEX.md)
- [Authoritative Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md)

---

## For Technical Users
- [Architecture](docs/reference/ARCHITECTURE.md)
- [Runtime Capability Reference](docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md)
- [Runtime Fingerprint](docs/current_runtime/RUNTIME_FINGERPRINT.md)

---

## Project Status
NovaLIS is actively evolving. The repository should be treated as an active build, not a finished product.

## License
Nova is source-available under the Business Source License 1.1. See [LICENSE](LICENSE).
