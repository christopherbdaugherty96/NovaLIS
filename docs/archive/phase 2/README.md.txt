# NovaLIS

NovaLIS is a **governed, local-first household system**.  
It is not an autonomous AI assistant.

This repository represents a deliberately constrained architecture focused on:
- predictability
- explicit control
- refusal-safe behavior
- long-term maintainability

If NovaLIS ever feels “alive,” it has failed its design goals.

---

## Why NovaLIS Exists

Most personal AI projects optimize for:
- novelty
- autonomy
- personality
- background behavior

NovaLIS explicitly rejects those goals.

NovaLIS is designed to behave like a **reliable appliance**:
- it acts only when invoked
- it does nothing in the background
- it never guesses intent
- it never escalates without permission

Trust comes from restraint, not intelligence.

---

## What NovaLIS Is

- A **single-governor system** with deterministic routing
- Event-driven and silence-first
- Local-first and privacy-respecting
- Explicitly permission-based
- Designed for auditability and calm failure

---

## What NovaLIS Is Not

- Not autonomous
- Not proactive
- Not personality-driven
- Not self-improving
- Not a background agent
- Not an intent-guessing assistant

---

## Core Architectural Principles

### 1. Governor Model
All decisions flow through a single authoritative brain.

- Skills do not decide what happens next
- The UI does not decide what happens next
- LLM output never decides what happens next

If responsibility is unclear, the architecture is wrong.

---

### 2. Silence-First Behavior
Silence is a valid and preferred outcome.

If NovaLIS is not explicitly invoked, it does nothing.
No follow-ups. No retries. No background behavior.

---

### 3. Event-Driven Only
NovaLIS responds only to:
- explicit user input
- explicit UI actions
- explicit schedules (ask-first only)

Forbidden:
- background loops
- polling
- silent fetches
- auto-refresh on load or reconnect

---

### 4. LLM as Helper Only
The LLM may:
- clarify user-provided text
- answer bounded informational questions
- support explicit reflective reasoning (user-invoked)

The LLM may NOT:
- route
- plan
- infer intent
- select actions
- execute actions
- retry or escalate automatically

If removing the LLM would make NovaLIS unsafe, NovaLIS is already broken.

---

### 5. Deterministic Skills
Skills are:
- bounded
- stateless
- deterministic
- side-effect free

They return data only.
They never decide what happens next.

---

### 6. Truthful UI
The dashboard is **observer-only**.

- It reflects backend truth
- It does not infer system state
- It does not imply thinking, listening, intent, or emotion

Visuals are presentation-only.

---

## Phase Status (Authoritative)

### Phase-1 — **Frozen**
**Theme:** Information-only, calm presence

- News: headlines-only, whitelisted sources
- Weather: current conditions only
- Deterministic routing
- Silence-safe failures
- No actions, no autonomy

Phase-1 behavior is frozen and reproducible.

---

### Phase-2 — **Gated**
**Theme:** Intentional Action (No Autonomy)

- Explicit `ActionRequest` objects
- Mandatory user confirmation
- One action at a time
- No chaining
- No background execution

Phase-2 features are added only after Phase-1 stability is proven.

---

### Phase-3 — **Future (Locked)**
**Theme:** Governed expansion

Only allowed after Phase-2 exit criteria are met.
No autonomy is introduced at this phase.

---

## Governance & Enforcement

NovaLIS is governed by explicit architectural contracts stored in:














# NovaLIS

NovaLIS is a **local-first, governed assistant system** designed for reliability, predictability, and explicit user control.

It is not an autonomous AI.
It does not learn silently.
It does not act without permission.

This repository contains multiple generations of work, active systems, and frozen references.  
The documents below explain how to navigate it correctly.

---

## Start Here (Required Reading)

If you read nothing else, read these **in order**:

1. **`VISION_CANONICAL.md`**  
   Why NovaLIS exists and what it will never become.

2. **`ARCHITECT_CONTRACT.md`**  
   The non-negotiable architectural rules.

3. **`NovaLIS-CURRENT-STATUS.md`**  
   Where the system is *right now* and what is safe to work on.

These three files define intent, boundaries, and current reality.

---

## Phase Governance

NovaLIS development is governed by explicit phase locks:

- `PHASE_1_LOCK.md` — Foundation (complete, frozen)
- `PHASE_2_LOCK.md` — Intentional Action (current phase)
- `PHASE_3_LOCK.md` — Expansion (locked, not started)

No work should violate an active phase lock.

---

## Repository Orientation

Key directories:

- **`nova_backend/`**  
  Canonical backend (Phase-2+). Active development happens here.

- **`Nova-Backend-AI-Brain/`**  
  Phase-1 backend. Frozen reference only.

- **`Nova-Frontend-Dashboard/`**  
  Observer-only UI and dashboard.

- **`NovaLIS-Governance/`**  
  Architecture contracts, phase locks, environment locks, and status docs.

- **`_archive/`**  
  Historical snapshots and forensic references.

---

## Environment

Canonical runtime environment details are locked in:

- **`ENVIRONMENT_LOCK.md`**

If the environment differs from what is described there, it is considered out of spec.

---

## Important Notes

- NovaLIS prioritizes **stability over novelty**
- Silence is a feature
- Explicit permission gates all actions
- Ideas are cheap; constraints are enforced

If you are unsure whether something should be added, consult the governance documents before writing code.

---

## Status

NovaLIS is currently operating in **Phase-2.1 (UX & dashboard stabilization)**.

Architecture is in place.  
Execution is deliberate.  
Scope is intentionally constrained.

