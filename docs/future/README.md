# Future Docs Guide

**Status:** Reference guide for the `docs/future/` folder  
**Purpose:** Explain what these documents are for, how much authority they carry, and how they relate to Nova's live project state.

---

## What This Folder Is

The `docs/future/` folder is Nova's **design reserve**.

These documents preserve:

- long-term vision
- strategic options
- future technical directions
- optional expansion paths
- portfolio and packaging ideas

They are **not** the active roadmap and they are **not** implementation authority.

The best way to think about this folder is:

> not now, but maybe later

---

## Pass Tracking

The current cleanup of the future-doc system is intentionally split into three separate tasks:

### Task 1: Second Pass

Goal: make the future-doc set understandable as a coherent system.

Focus:

- explain what the folder is for
- explain that future docs are not equal-weight
- point readers back to live truth sources
- state the immediate current priorities clearly

### Task 2: Third Pass

Goal: make the main future technical concept draft governance-safe.

Focus:

- add current-system mapping
- add maturity levels and promotion gates
- add failure modes to avoid
- add obsolescence logic
- require translation into current repo truth before implementation

### Task 3: Polish Pass

Goal: tighten language, path accuracy, and operational clarity without changing authority boundaries.

Focus:

- align terms with the real Nova repo structure
- remove misleading generic wording
- keep future docs subordinate to `Now.md`, runtime truth, and capability verification
- preserve useful ideas while reducing ambiguity

These are separate tasks on purpose. They should not be treated as one undifferentiated documentation sweep.

The technical concept draft should not carry the full revision ledger inside the artifact itself. This guide is the right place to record the distinction between second-pass, third-pass, and polish work.

---

## Important: Not All Future Docs Carry the Same Weight

The files in this folder are not equal-priority and should not be treated as if they all have the same authority.

### 1. Strategic Anchors

These express Nova's long-term identity and differentiators.

- `NOVA_STRATEGIC_VISION.md`
- `NOVA_MARKET_POSITION.md`
- `ARCHITECTURAL_POSITIONING.md`

### 2. Packaging / Presentation Guidance

These focus on how Nova should present working value more clearly.

- `2026-04-15_portfolio_transformation_vision.txt`
- `2026-04-15_portfolio_upgrade_plan.txt`
- `2026-04-15_architecture_assessment_portfolio_plan.txt`

### 3. Business / Monetization Options

These describe possible sustainability paths if Nova becomes stable and useful enough.

- `BUSINESS_OPTIONS.md`

### 4. Optional Integration Branches

These explore expansions Nova could take, but does not need in order to succeed.

- `OPENCLAW_INTEGRATION_DESIGN.md`
- `OPENCLAW_INTEGRATION_REVIEW.md`

### 5. Technical Concept Reserve

These preserve future technical ideas while keeping them subordinate to live repo truth.

- `NOVA_FUTURE_TECHNICAL_CONCEPT_DRAFT_2026-04.md`

---

## What These Docs Are Trying to Say Together

Taken as a group, the future docs say:

- Nova should become a governed, user-owned AI operating layer
- its durable moat is trust, local control, approval gates, and auditability
- richer workflows and business value matter more than generic chatbot imitation
- future expansion should be careful, phased, and subordinate to governance
- complexity is only justified when it produces concrete usefulness

In short:

> Nova's future is carefully expanded usefulness built on trust, ownership, and governed execution.

---

## Live Truth Still Lives Elsewhere

Future docs must never outrank current reality.

**Current truth lives in:**

- `4-15-26 NEW ROADMAP/Now.md`
- `docs/current_runtime/`
- `docs/capability_verification/`
- `nova_backend/src/`

If a future doc conflicts with those sources, the future doc loses.

Future docs also should not be promoted through casual visibility drift. In practice, that means they should stay out of top-level product entry points such as the root `README.md` unless they are being referenced explicitly as non-authoritative future context.

---

## Immediate Focus Still Matters More Than Future Theory

No matter how good a future idea is, Nova's immediate execution priorities remain:

- installer validation
- cap 64 live signoff and lock
- demo / README surface
- conversational and first-run polish

The future folder should support those priorities indirectly, not compete with them.

---

## How To Use This Folder Safely

Before promoting any future idea into active work:

1. Identify which kind of document it came from
2. Check whether it is a vision anchor, an option, or a technical concept
3. Reconcile it with `Now.md`, runtime truth, and capability verification
4. Translate it into the real current repo structure
5. Define acceptance and verification criteria

If that translation step fails, the idea should stay in `docs/future/`.

One more rule matters here:

6. Do not let a future doc silently become a "maybe-soon" architecture memo without an explicit promotion step into the active roadmap or a repo-accurate design note

---

## One-Sentence Truth

**This folder preserves future optionality for Nova, but live authority still belongs to the roadmap, runtime truth, capability verification, and current code.**
