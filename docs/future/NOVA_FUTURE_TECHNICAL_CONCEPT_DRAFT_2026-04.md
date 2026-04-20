# Nova Future Technical Concept Draft

**Status:** Future Concept Reserve - Not Implementation-Ready  
**Last Updated:** 2026-04-20  
**Provenance:** Derived from a broader architectural scan, then reshaped to align with Nova's governance model. Not an original Nova roadmap document.

> **Future concept draft**
> This document is a forward-looking architecture and implementation concept, not a drop-in build spec for the current Nova repo.
> Several examples, module paths, capability names, and dependency assumptions below do **not** match Nova's current codebase one-to-one.
> Before implementing anything from this document, reconcile it with `4-15-26 NEW ROADMAP/Now.md`, `docs/current_runtime/`, current capability verification docs, and the live `nova_backend/src/` structure.

---

## Revision Status

This document has already been through distinct second-pass, third-pass, and polish work. Pass-level tracking lives in [docs/future/README.md](C:/Nova-Project/docs/future/README.md) so this file can stay focused on the future design itself.

---

## Banner: This Is Not a Current Implementation Plan

This document exists to preserve promising long-term ideas **without** letting them masquerade as current authority. It describes what Nova *might* become, not what it is obligated to build next.

**Do not use this document for:**

- sprint planning
- current capability design
- installer or runtime decisions
- overriding `Now.md` or `STATUS.md`

**Use this document only for:**

- understanding possible future directions
- evaluating whether a new idea aligns with Nova's long-term trajectory
- informing *future* roadmap discussions after current proof-of-trust work is complete

---

## Purpose

This document captures possible future technical directions for Nova based on the broader strategic roadmap. It is meant to preserve promising ideas while separating them from current operational truth.

Use this document for:

- future architecture exploration
- identifying promising capability areas
- comparing larger strategic options
- collecting implementation ideas that may later be translated into repo-accurate tasks

Do **not** use this document as:

- the authoritative current roadmap
- the source of truth for current repo structure
- a direct implementation checklist without reconciliation work
- proof that a concept has already been approved for implementation

---

## Non-Goals

This document does **not** do the following:

- authorize new scope in the current sprint
- override `Now.md`, runtime truth, or capability certification state
- replace concrete engineering design notes for a chosen feature
- force Nova into a new package layout, install strategy, or orchestration model
- commit Nova to every idea listed below

If a reader needs immediate execution guidance, this is the wrong document.

---

## Current Alignment Snapshot (2026-04-20)

This draft exists in parallel with Nova's actual operating truth. Before any concept here is considered for implementation, it must be reconciled against:

| Live Truth Source | Purpose |
| :--- | :--- |
| `4-15-26 NEW ROADMAP/Now.md` | Current sprint priorities |
| `docs/capability_verification/STATUS.md` | Capability status surface and current verification snapshot |
| `docs/current_runtime/` | Runtime architecture and governance spine |
| `docs/capability_verification/` | Capability contracts, checklists, and signoff evidence |
| `nova_backend/src/` | Actual code organization |

**Any concept that cannot be translated cleanly into this structure is not ready.**

---

## Current System Mapping

To prevent drift, future concepts must map to **real Nova components**, not imaginary ones.

| Generic Concept | Nova Equivalent (Current) | Notes |
| :--- | :--- | :--- |
| Governance spine | `GovernorMediator -> Governor -> CapabilityRegistry -> ExecuteBoundary -> LedgerWriter` | Implemented through `nova_backend/src/governor/` and `nova_backend/src/ledger/` |
| Capability registry | `registry.json` + `capability_locks.json` | Not `capability_registry.json` |
| Capability verification | `docs/capability_verification/` + `scripts/certify_capability.py` | Certification and live signoff, not just abstract contracts |
| Memory stores | Current governed memory/runtime flows | Not yet a vector-first architecture |
| Installer | `installer/windows/` + `pyproject.toml` entry point | Not `pipx` or `get.nova.local` |
| Audit ledger | Append-only local ledger subsystem | Avoid assuming a single `ledger.json` file as the design center |
| First governed external-effect capability | `cap_64` (`send_email_draft`) | Implemented, awaiting live signoff and lock |

**Rule:** Any future concept that assumes a different structure must include translation notes before promotion.

---

## Concept Maturity Guide

To keep this document operationally safe, treat each concept in one of these buckets:

- **Near-term candidate**: plausible after current trust-surface work closes; should still be rewritten into repo-accurate tasks before implementation
- **Mid-term concept**: promising, but depends on stabilization of current runtime, certification, and packaging work
- **Research track**: architecture exploration only; not suitable for roadmap activation yet
- **Deferred**: intentionally out of current scope

Examples:

- **Near-term candidate**: structured evaluation expansion, graceful recovery improvements, bounded onboarding polish
- **Mid-term concept**: MCP integration, bounded workflows, richer memory transparency surfaces
- **Research track**: sandboxing experiments, semantic retrieval upgrades, broader execution isolation
- **Deferred**: multi-agent orchestration

Unless explicitly promoted later, concepts in this document should default to **mid-term concept** or **research track**.

Promotion into active roadmap work should require:

- a real implementation owner
- repo-accurate file targets
- explicit acceptance criteria
- an explanation of how the concept interacts with the ledger, runtime docs, and certification flow
- confirmation that it does not derail the current trust-surface priorities

---

## Failure Modes to Avoid

Historically, future-planning documents become dangerous when they create one of these failure modes:

- a parallel source of truth that competes with runtime docs or `Now.md`
- a new abstraction stack that ignores existing Nova systems
- a package/layout rewrite hidden inside a feature proposal
- a "future maybe" dependency treated as if it were already approved
- a broad architecture jump that arrives before current trust surfaces are stable

This draft should be used in a way that avoids all five.

---

## Phase Concepts Overview

### Phase A: Evaluation and Regression Hardening

**Objective:** Make governance measurable and behavior predictable.

**Maturity:** Near-term candidate

**Current caution:** This work must stay grounded in the **actual** `nova_backend/src` structure and current capability inventory (`registry.json`, `capability_locks.json`). Near-term work here should emphasize evaluation quality, regression coverage, and repo-accurate verification around the existing system, not a new abstract contract framework that runs ahead of runtime truth.

**Promotion gate:** Installer validation complete + cap 64 live signoff and lock.

**Key concepts:**

- stronger capability verification derived from `STATUS.md` and live capability definitions
- structured evaluation and conversation quality checks
- stronger regression protection for the governance spine

### Phase B: Recovery and Failure Handling

**Objective:** Ensure tool failures do not break user trust.

**Maturity:** Near-term candidate

**Current caution:** Recovery loops must be integrated into the existing execution and governance paths, not bolted on as a separate system. All meaningful recovery events should remain auditable through the ledger/trust surfaces. Generalized recovery architecture belongs later; current installer/startup diagnostics and visibility work can still continue now as part of present hardening.

**Promotion gate:** Same as Phase A.

**Key concepts:**

- bounded retries
- circuit breaker behavior for persistent failures
- user-visible fallback messaging

### Phase C: Memory Transparency and Retrieval

**Objective:** Make memory useful without making it opaque.

**Maturity:** Mid-term concept

**Current caution:** The current memory surfaces are not yet a vector-first architecture. Any retrieval upgrade must either coexist with or transparently migrate the current system. Semantic/vector retrieval remains a design-heavy item, not a near-term requirement.

**Promotion gate:** After Phase A/B are stable and user feedback confirms memory retrieval is a real friction point.

**Key concepts:**

- short-term vs long-term memory separation
- "memory used" transparency in the UI
- memory management surfaces (inspect, edit, delete)
- possible future semantic retrieval, but only after stronger design validation

### Phase D: MCP Integration

**Objective:** Unlock ecosystem tools under governed control.

**Maturity:** Mid-term concept

**Current caution:** MCP tools are untrusted by default. Nova should require explicit approval per server or tool class, and all invocations must remain visible in the ledger/trust model. This is a major trust-surface expansion and should not begin before core proof-of-trust work is solid.

**Promotion gate:** Phase A/B complete + at least one additional governed capability beyond cap 64 is live-signed.

**Key concepts:**

- MCP client that discovers tools
- capability mapping with explicit external-source labeling
- user approval flow per server
- ledger logging of all MCP tool calls

### Phase E: Execution Sandboxing

**Objective:** Protect the user's system from risky commands.

**Maturity:** Research track

**Current caution:** The WASM/Docker sandbox sketch is an architecture placeholder, not an implementation spec. Any sandboxing work should start with a narrow, well-defined target such as third-party or externally sourced execution.

**Promotion gate:** Only after a concrete, bounded use case is identified.

**Key concepts:**

- policy-based sandboxing
- filesystem/network restrictions
- phased rollout beginning with the riskiest execution lanes

### Phase F: Bounded Workflows

**Objective:** Enable multi-step tasks without open-ended autonomy.

**Maturity:** Mid-term concept

**Current caution:** Workflows should be deterministic and predefined, not dynamically improvised by the LLM as open-ended plans. Each step must still pass through the existing governance spine.

**Promotion gate:** After multiple single-turn capabilities are proven and user demand for multi-step tasks is evident.

**Key concepts:**

- workflow definitions
- trigger phrase matching
- governed step-by-step execution with ledger logging

### Phase G: Multi-Agent Orchestration

**Objective:** Coordinate specialized agents for complex tasks.

**Maturity:** Deferred

**Current caution:** This is explicitly deferred. Multi-agent systems raise coordination complexity and trust-verification burden. Nova should not consider this until single-agent plus workflows are demonstrably insufficient.

**Promotion gate:** Only if a concrete, high-value use case cannot be solved any other way, and after all prior phases are stable and well-understood.

**Key concepts:**

- supervisor-agent pattern
- full audit logging of inter-agent communication

---

## Current Priority Filter

If Nova needs to choose only a few concepts from this document later, the strongest current candidates are:

1. structured evaluation expansion
2. tighter recovery and graceful failure handling
3. memory transparency improvements
4. bounded onboarding/first-run polish that extends the installer-first path

The weakest current candidates for activation are:

- broad packaging replacement via a new pipx-first install channel
- full MCP capability expansion before present trust surfaces are closed
- sandbox runtime work before there is a narrower execution target
- multi-agent orchestration

---

## Packaging and Onboarding Alignment

**Current reality:** Nova already has a Windows installer path (`installer/windows/`) and a packaged entry point defined in `pyproject.toml`.

**Future concept note:** Any onboarding or packaging improvements must **extend the existing installer-first path**, not replace it with a `pipx`-based flow unless there is a clear, validated reason to switch. The current priority is installer validation and diagnostic clarity, not a new distribution channel.

**Promotion gate for packaging changes:** Installer validation on a clean VM passes consistently.

---

## What Would Make This Draft Obsolete

This document should be retired, replaced, or heavily rewritten if any of the following become true:

- Nova adopts a materially different runtime architecture than the current governance spine
- a newer future-architecture draft supersedes these concepts with repo-accurate plans
- the strongest concepts here are promoted into the roadmap and rewritten as concrete implementation notes
- the assumptions in this document drift far enough from runtime truth that the cautionary framing is no longer sufficient

Future-thinking is useful, but stale future-thinking becomes drag. This document should earn its place by staying clearly subordinate to live truth.

---

## Translation Rules Before Implementation

Before any concept from this document becomes active work, rewrite it into a repo-accurate implementation note that:

1. names the real current files or modules in `nova_backend/src/`
2. names the real current capability IDs or runtime surfaces
3. states how it interacts with certification, runtime docs, and the ledger
4. defines acceptance criteria and what counts as live signoff
5. states what existing system it extends instead of inventing a parallel one

If a concept cannot survive that translation pass, it should remain a future draft rather than entering the roadmap.

For especially risky concepts, add one more step:

6. define what must be proven in a spike or experiment before implementation begins

---

## Promotion Requirements

Before any concept in this document is moved into the active roadmap (`Now.md`) or treated as near-term work, it must satisfy:

1. **Translation to current repo structure:** the concept is rewritten using actual Nova paths and modules
2. **Capability inventory alignment:** capability examples use real Nova capabilities or are clearly marked hypothetical
3. **Runtime truth consistency:** the concept does not contradict `CURRENT_RUNTIME_STATE.md` or the existing governance spine
4. **Signoff gate satisfaction:** the concept's stated promotion gate is actually met
5. **Ledger impact assessment:** the effect on auditability or trust surfaces is documented

---

## Recommended Use

If Nova returns to this document later, the safest process is:

1. choose one concept only
2. translate it into current repo terms
3. define acceptance and verification criteria
4. attach it to the active roadmap only when it becomes near-term work
5. verify it does not contradict `Now.md`, current runtime truth, or active capability certification state

This keeps the document useful as a design reserve without letting it compete with operational truth.

Keep this document inside `docs/future/` and out of top-level product entry points such as [README.md](C:/Nova-Project/README.md) unless it is being referenced explicitly as non-authoritative future context.

If a concept is promoted out of this file, leave a short historical note here with the promotion date and where the concept moved.

---

## Bottom Line

This document preserves useful future-thinking around evals, capability contracts, memory quality, MCP integration, sandboxing, and workflows.

It should be treated as a **future architecture draft**, not as the current implementation plan for Nova.

