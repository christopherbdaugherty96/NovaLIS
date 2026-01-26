# NovaLIS

NovaLIS is a **local-first, governed assistant system** built for reliability, predictability, and explicit user control.

It is not an autonomous AI.
It does not act without permission.
It does not learn or operate in the background.

This repository is governed by explicit contracts and phase locks.
Nothing here should be interpreted without them.

---

## Start Here (Required Reading)

Read these files **in this order**. They are authoritative.

1. **VISION_CANONICAL.md**  
   Defines why NovaLIS exists and what it will never become.

2. **ARCHITECT_CONTRACT.md**  
   Non-negotiable architectural rules and safety boundaries.

3. **NovaLIS-CURRENT-STATUS.md**  
   The factual, current state of the system and what is safe to work on.

---

## Phase Governance

Development is governed by explicit phase locks:

- **PHASE_1_LOCK.md** — Foundation (complete, frozen)
- **PHASE_2_LOCK.md** — Intentional Action (current phase)
- **PHASE_3_LOCK.md** — Expansion (locked, not started)

No work may violate an active phase lock.

---

## Repository Orientation

Key directories:

- **nova_backend/**  
  Canonical backend (Phase-2+). Active development happens here.

- **Nova-Backend-AI-Brain/**  
  Phase-1 backend. Frozen reference only.

- **Nova-Frontend-Dashboard/**  
  Observer-only UI and dashboard.

- **NovaLIS-Governance/**  
  Architecture contracts, phase locks, environment locks, and governance docs.

- **_archive/**  
  Historical snapshots and reference material.

---

## Environment

Canonical runtime assumptions are locked in:

- **ENVIRONMENT_LOCK.md**

If the runtime environment differs from what is defined there, it is considered out of spec.

---

## Process Discipline

Before committing changes, consult:

- **PRE_COMMIT_CHECKLIST.md**
- **SENIOR_REVIEW_DO_NOTS.md**

These exist to prevent scope creep, autonomy drift, and accidental violations.

---

## Current Phase

NovaLIS is currently operating in **Phase-2.1 — UX & dashboard stabilization**.

Architecture is complete.  
Actions are governed.  
Remaining work is UI wiring and presentation only.

---

## Rule of Thumb

If you are unsure whether something should be added:

**Stop.  
Read the governance documents.  
Do not guess.**
