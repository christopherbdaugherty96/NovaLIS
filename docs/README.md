> ## 🔒 PHASE-3.5 STATUS UPDATE — CLOSED
>
> **Phase-3.5 is formally COMPLETE and CLOSED.**  
> All Phase-3.5 acceptance criteria have been mechanically verified and CI-enforced, including execution quarantine, Governor containment, passive confirmation gating, and runtime refusal proofs.
>
> This document may reference Phase-3.5 as “active” for historical context only.  
> **No Phase-3.5 work remains open.** Phase-4 remains hard-locked pending a separate unlock artifact.
>
> **Authoritative closure record:** `docs/PHASE_3.5_CLOSURE.md`
------------------------------------------------

![Phase 3 Complete](https://img.shields.io/badge/Phase--3-COMPLETE-brightgreen?style=flat-square)
![Phase 3.5 Frozen](https://img.shields.io/badge/Phase--3.5-FROZEN-blue?style=flat-square)
![Execution Disabled](https://img.shields.io/badge/Execution-DISABLED-red?style=flat-square)
![Local First](https://img.shields.io/badge/Local--First-YES-blue?style=flat-square)
![Governance Text-Sanitizer](https://img.shields.io/badge/Governance-TEXT_SANITIZER-gray?style=flat-square)

## Canonical Identity (Non-Negotiable)

**One-Line Truth**

NovaLIS is a sealed governance vessel with proven execution surface safety. Current runtime has zero execution capability and minimal text mediation.

**Constitutional Invariants**

- No autonomy (user → Nova → GovernorMediator → response → user)
- No execution capability (execute_action = None)
- No background cognition or silent execution
- Deterministic behavior (same input → same output)
- Offline-first by default; online only by explicit request
- Explicit invocation only (no inferred intent)
- Full inspectability (logs, traces, ledgers, manifests)

If any code or proposal contradicts the above, it is **invalid by definition** unless an explicit governance unlock exists.

## Phase Status (v5.1-Aligned)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0–2 | ✅ **Frozen** | Historical foundations, permanently locked |
| Phase 3 | ✅ **Frozen** | Core functionality complete and locked |
| Phase 3.5 | 🔒 **Frozen** | Execution Surface Guarantee Proven |
| Phase 4 | 🚫 **Hard Blocked** | Design phase only; requires explicit unlock |
| Phase 4.2+ | 🔒 **Locked** | Design documents only |
| Phase 5+ | 🔒 **Locked** | Architecture specifications only |
| Phase 10+ | 🔒 **Deep Locked** | Requires unanimous constitutional amendment |

**Important:**

Phase progression is enforced as a **hard safety barrier**, not a roadmap suggestion. Current Phase 3.5 is FROZEN with proven guarantees.

## What Exists in This Repository

This repository contains:

- A **FastAPI + WebSocket backend** implementing the NovaLIS brain
- A **deterministic skill registry** (system / weather / news / general_chat)
- A **text mediation layer** (GovernorMediator only, not enforcement engine)
- A **static dashboard UI** (observer/control surface)
- **Governance verification tooling**
- **Execution surface proof documentation**

Large runtime artifacts (models, binaries) are intentionally excluded from version control.

## What This Repository Does *Not* Do

NovaLIS explicitly does **not**:

- Execute actions (execute_action = None)
- Act autonomously or proactively
- Perform background reasoning or monitoring
- Infer user intent
- Adapt behavior based on history or habits
- Enable governed agent execution (Phase 4 is design-only)
- Provide "helpful" escalation beyond defined contracts
- Use DeepSeek, DEG, or agent architectures (Phase 4+ designs only)

If a feature requires Nova to **decide, assume, or initiate**, it is **illegal** under the current canon.

## Repository Navigation (Required for Review)

This repository must be reviewed using the deterministic order defined in:

➡ **REPO_MAP.md**

That document specifies:

- Canonical governance sources
- Safe review order for humans and AI
- Phase-sensitive files
- Explicit review constraints

Any review or change proposal that ignores REPO\_MAP.md is considered **unsafe**.

## Contribution Rules (Binding)

All contributions are governed by:

➡ **CONTRIBUTING.md**

Key rules include:

- No scope expansion without explicit unlock
- No refactors that risk behavioral drift
- No background tasks, telemetry, or adaptive behavior
- Smallest possible diffs
- Governance always overrides convenience
- Documentation must never imply capabilities that runtime cannot perform

If you are unsure whether a change is allowed: **do not implement it**.

## Runtime Dependencies

Runtime dependencies such as STT models or media tools are **installed locally** and excluded from Git.

See:

- nova\_backend/tools/README.md
- .gitignore

This repository is intentionally **not self-contained** at runtime.

## Status Disclaimer

NovaLIS is **acceptance-gated** and **not production-complete**.

Claims of capability are valid **only** where explicitly implemented and verified.

Specification does not imply availability.

**Current Runtime Truth:**
- Phase 3.5: FROZEN (Execution Surface Guarantee Proven)
- Governor: GovernorMediator (text sanitizer only)
- Execution: Disabled (execute_action = None)
- Skills: Read-only weather, news, system, general chat
- No DeepSeek, DEG, agents, or device control

## Canonical References

- **NOVA CANONICAL SYNTHESIS v5.1** — Phase-Aligned Truth ✅
- **REPO_MAP.md** — Deterministic repository navigation
- **CONTRIBUTING.md** — Governance-aligned contribution rules
- **NovaLIS-Governance/PHASE_3.5_FROZEN_STATUS.md** — Current phase status
- **docs/PHASE_3_COMPLETION.md** — Phase 3 completion certificate

These documents together define the **single source of truth** for NovaLIS.

---

## What Phase-3 Means

Phase-3 establishes Nova as a **stable, local, input-driven assistant** with **no execution authority**.

At this phase, Nova is intentionally limited to ensure safety, determinism, and trust. All capabilities are explicit, inspectable, and reversible.

### Nova **CAN**:

- Accept user input (text or speech)
- Perform local speech-to-text (STT)
- Route requests deterministically
- Respond conversationally
- Fail gracefully without crashing
- Run fully offline by default

### Nova **CANNOT**:

- Execute OS, app, or file actions
- Modify system state
- Act autonomously or proactively
- Perform background processing
- Learn, adapt, or infer intent
- Write to memory without explicit future unlocks

### Why This Matters

Phase-3 proves that Nova's core promise is **structurally true**:

> Nova is helpful **without** being powerful.

All system-changing authority is **architecturally impossible** at this stage, not merely "disabled by convention."  
This guarantees that future capability expansion (Phase-4+) happens only through explicit governance, not drift.

### Status

- **Phase-3:** ✅ Complete & Locked  
- **Phase-3.5:** 🔒 Frozen (Execution Surface Guarantee Proven)  
- **Speech-to-Text (STT):** ✅ Final  
- **Execution Authority:** 🚫 Disabled (execute_action = None)  
- **Phase-4:** ⛔ Hard-blocked (Design Only, no implementation)

For formal attestations, see:  
`docs/PHASE_3_COMPLETION.md` and `NovaLIS-Governance/PHASE_3.5_FROZEN_STATUS.md`

**Reference Authority:** Nova Canonical Synthesis v5.1 - Phase-Aligned Truth