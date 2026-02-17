# CONTRIBUTING — Nova (Governance-First Rules)

This repository does **not** follow conventional open-source contribution norms.

Nova is a **governed system** with phase-locked behavior, strict authority boundaries, and an offline-first safety model. The single source of truth is the **Nova Complete Constitutional Blueprint v1.8**.

Contributions are permitted **only** within the constraints defined here.

---

## 1) Canonical Authority

The following document is binding and overrides all other guidance:

- **`NOVA COMPLETE CONSTITUTIONAL BLUEPRINT 1.8.md`** — The single source of truth (immutable)

All other documents (including phase locks, governance contracts, and design specs) are authoritative **only insofar as they do not conflict** with v1.8.

If a proposed change conflicts with a constitutional invariant or phase lock, the change is invalid unless an explicit unlock is ratified.

---

## 2) Phase Discipline (Hard Rule)

- Current operational state: **Phase 3.5 SEALED** (no execution authority, GovernorMediator only)
- **Phase 4 is HARD‑LOCKED** at runtime; design activity is unlocked but no implementation.
- Governor is **GovernorMediator** (text sanitizer only, non-authoritative)
- Execution is **disabled** (`execute_action = None`, `GOVERNED_ACTIONS_ENABLED = false` hard‑coded)
- Documentation must never imply capabilities that runtime cannot perform.

Phase boundaries are safety barriers, not suggestions.

---

## 3) What Contributions ARE Allowed

Allowed changes include:

- Bug fixes that preserve behavior
- Clarifying comments and documentation
- Tests that enforce existing constraints
- Refactoring **only** when behavior is provably unchanged
- Removal of dead code or unused artifacts
- Tooling that improves verification without adding power
- Phase alignment corrections (to match v1.8 and closure documentation)

All changes must be:

- Deterministic
- Explicit
- Reviewable via diff
- Reversible
- Phase-compliant with v1.8

---

## 4) What Contributions Are NOT Allowed

The following are forbidden unless explicitly unlocked in governance:

- Adding new skills or commands
- Implicit intent inference or ranking
- Substring or fuzzy matching (beyond defined skill triggers)
- Background threads, daemons, or schedulers
- Telemetry, analytics, or tracking
- Silent network access or auto-fallbacks
- Self-modifying or self-expanding behavior
- "Helpful" automation that bypasses user intent
- Any capability beyond Phase 3.5 sealed state (unless a phase unlock is ratified)
- Interpreting "design documents" as implementation approval
- Device control or execution capability

If a change feels "smart" or "convenient," it is likely invalid.

---

## 5) AI-Assisted Contributions

AI may be used **only** as a constrained reviewer or editor.

AI may:

- Audit code against phase locks (v1.8)
- Propose minimal diffs
- Identify inconsistencies or unsafe assumptions
- Generate tests that enforce existing rules
- Verify phase alignment

AI must **NOT**:

- Design new features
- Reinterpret intent
- "Improve UX" by adding autonomy
- Optimize behavior in ways that affect authority or scope
- Suggest capabilities beyond Phase 3.5 sealed state

All AI-generated changes must be reviewed as if written by an untrusted junior contributor.

---

## 6) Review Expectations

Every contribution must:

- State the phase it affects
- Declare whether behavior changes (expected: "no")
- Reference the relevant constitutional invariant(s) (Part I of v1.8)
- Prefer smallest possible change
- Align with v1.8 phase‑aligned truth

If uncertain, stop and ask for clarification rather than guessing.

---

## 7) Non-Goals (Explicit)

Nova is **not**:

- A chatbot platform
- An autonomous agent
- A learning system
- A surveillance system
- A growth-at-all-costs product
- An execution engine (Phase 3.5 has zero execution)

It is a **sealed governance vessel** with proven safety, awaiting explicit phase unlocks for future capability.

---

## 8) Phase-Alignment Mandate

All contributions must respect:

- **Phase 3.5**: SEALED (no execution authority, GovernorMediator only)
- **Governor**: GovernorMediator (text sanitizer only, non-authoritative)
- **Execution**: Disabled (`execute_action = None`, no runtime path exists)
- **External data**: User/UI-triggered only, no background polling
- **Design documents**: Marked as Phase 4+ only, not interpretable as implementation approval
- **Closure documentation**: Phase 3.5 closure recorded in `docs/PHASE_3.5_CLOSURE.md`

Any contribution that implies capabilities beyond this reality is rejected.

---

## 9) Reference Documents (Non-Negotiable Truths)

All contributions must align with these canonical documents:

- **`NOVA COMPLETE CONSTITUTIONAL BLUEPRINT 1.8.md`** - Primary phase-aligned truth
- **`docs/PHASE_3.5_CLOSURE.md`** - Formal closure record

Any contribution that contradicts these documents is invalid by definition.

---

**End of CONTRIBUTING rules.**

**Reference Authority:** Nova Complete Constitutional Blueprint v1.8