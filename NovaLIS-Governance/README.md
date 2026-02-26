> ## 🔒 PHASE-3.5 STATUS UPDATE — SEALED
>
> **Phase-3.5 is formally COMPLETE, SEALED, and NON-REOPENABLE without explicit constitutional unlock.**  
> All Phase-3.5 acceptance criteria have been mechanically verified and CI-enforced, including execution quarantine, Governor containment, passive confirmation gating, and runtime refusal proofs.
>
> This document may reference Phase-3.5 as "active" for historical context only.  
> **No Phase-3.5 work remains open.** Phase-4 is design‑unlocked but runtime‑locked pending a formal unlock artifact.
>
> **Authoritative closure record:** `docs/PHASE_3.5_CLOSURE.md`
------------------------------------------------

![Phase 3 Complete](https://img.shields.io/badge/Phase--3-COMPLETE-brightgreen?style=flat-square)
![Phase 3.5 Sealed](https://img.shields.io/badge/Phase--3.5-SEALED-blue?style=flat-square)
![Execution Disabled](https://img.shields.io/badge/Execution-DISABLED-red?style=flat-square)
![Local First](https://img.shields.io/badge/Local--First-YES-blue?style=flat-square)
![Governance Text-Sanitizer](https://img.shields.io/badge/Governance-TEXT_SANITIZER-gray?style=flat-square)

## Canonical Identity (Non-Negotiable)

**One-Line Truth**

Nova is a **governor over contained intelligence** — a sovereign household appliance that provides calm, trustworthy access to AI capabilities without surrendering authority.

**Constitutional Invariants (Part I of v1.8)**

- Single Master Governor (no bypass)
- Intelligence–Authority Split (advisory only, execution mediated)
- No Autonomous Execution
- No Background Cognition
- No Predictive Preloading
- No Silent Fallback
- No Environment Override
- No Dynamic Execution Surface
- Orb Non‑Semantic (only message: "There is power here. It is stable.")
- UI Reflective Only
- Calm as Technical Requirement
- No Speculative Execution
- No Self‑Expansion of Authority
- Evolution Kill Switch Absolute
- … and others (see v1.8)

If any code or proposal contradicts the above, it is **invalid by definition** unless an explicit governance unlock exists.

---

## Phase Status (v1.8-Aligned)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0–2 | ✅ **Frozen** | Historical foundations, permanently locked |
| Phase 3 | ✅ **Frozen** | Core functionality complete and locked |
| Phase 3.5 | 🔒 **SEALED** | No execution authority, GovernorMediator only |
| Phase 4 | 🚫 **Design‑Unlocked, Runtime‑Locked** | Design phase only; requires explicit unlock |
| Phase 4.5 | 🔓 **Proposed** | Experience Elevation (awaiting ratification) |
| Phase 5A | 🔒 **Design‑Locked** | Explicit Memory & Continuity (future) |
| Phase 5B | 🔒 **Design‑Locked** | Experience Maturation (future) |
| Phase 6 | 🔒 **Design‑Locked** | Policy‑Bound Operation (requires proven household value) |
| Phase 7–10 | 🔒 **Design‑Locked** | Conditional on experience foundation |

**Important:**

Phase progression is enforced as a **hard safety barrier**, not a roadmap suggestion. Current Phase 3.5 is SEALED with proven guarantees.

---

## What Exists in This Repository

This repository contains:

- A **FastAPI + WebSocket backend** implementing the Nova brain
- A **deterministic skill registry** (system / weather / news / general_chat)
- A **text mediation layer** (GovernorMediator only, not enforcement engine)
- A **static dashboard UI** (observer/control surface)
- **Governance verification tooling**
- **Execution surface proof documentation**

Large runtime artifacts (models, binaries) are intentionally excluded from version control.

---

## What This Repository Does *Not* Do

Nova explicitly does **not**:

- Execute actions (`execute_action = None`)
- Act autonomously or proactively
- Perform background reasoning or monitoring
- Infer user intent
- Adapt behavior based on history or habits
- Enable governed agent execution (Phase 4 is design‑only)
- Provide "helpful" escalation beyond defined contracts
- Use DeepSeek, DEG, or agent architectures **in runtime** (Phase 4+ designs only)

**Deep Thought (external analysis) is advisory only.** When invoked, Nova is completely dormant: it does not receive the message, does not respond, and performs no background processing. Deep Thought outputs are visible in chat history but carry no authority and do not influence Nova’s decision‑making unless explicitly referenced by the user in a subsequent Nova‑mode message.

If a feature requires Nova to **decide, assume, or initiate**, it is **illegal** under the current canon.

---

## Repository Navigation (Required for Review)

This repository must be reviewed using the deterministic order defined in:

➡ **REPO_MAP.md**

That document specifies:

- Canonical governance sources
- Safe review order for humans and AI
- Phase-sensitive files
- Explicit review constraints

Any review or change proposal that ignores REPO\_MAP.md is considered **unsafe**.

---

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

---

## Runtime Dependencies

Runtime dependencies such as STT models or media tools are **installed locally** and excluded from Git.

See:

- `nova_backend/tools/README.md`
- `.gitignore`

This repository is intentionally **not self-contained** at runtime.

---

## Status Disclaimer

Nova is **acceptance-gated** and **not production-complete**.

Claims of capability are valid **only** where explicitly implemented and verified.

Specification does not imply availability.

**Current Runtime Truth:**
- Phase 3.5: SEALED (no execution authority)
- Governor: GovernorMediator (text sanitizer only)
- Execution: Disabled (`execute_action = None`, `GOVERNED_ACTIONS_ENABLED = false` hard‑coded)
- Skills: Read-only weather, news, system, general chat
- No DeepSeek, DEG, agents, or device control

---

## Canonical References

- **`NOVA COMPLETE CONSTITUTIONAL BLUEPRINT 1.8.md`** — Single source of truth ✅
- **`docs/PHASE_3.5_CLOSURE.md`** — Formal closure record
- **`REPO_MAP.md`** — Deterministic repository navigation
- **`CONTRIBUTING.md`** — Governance-aligned contribution rules

These documents together define the **authoritative reference set**, governed by v1.8 as the supreme document.

---

## Core Philosophical Context

The following documents are **non-authoritative context** and do not grant capability, permission, or roadmap intent. They provide background on Nova's governance-first mindset:

- **`CorePhilosophy.md`** - Foundational philosophical framing
- **`NOVA_AGENT_IDENTITY_v3.0.md`** - Non-autonomous coordination definition
- **`NOVA_DEEP_MEMORY_SAVED_UNLOCK_REQUIRED_v1.0.md`** - Memory governance design

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
- **Phase-3.5:** 🔒 SEALED (no execution authority)  
- **Speech-to-Text (STT):** ✅ Final  
- **Execution Authority:** 🚫 Disabled (`execute_action = None`, `GOVERNED_ACTIONS_ENABLED = false`)  
- **Phase-4:** ⛔ Design‑Unlocked, Runtime‑Locked

For formal attestations, see:  
`docs/PHASE_3.5_CLOSURE.md`

**Reference Authority:** Nova Complete Constitutional Blueprint v1.8