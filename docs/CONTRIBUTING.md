# CONTRIBUTING — NovaLIS (Governance-First Rules)

This repository does **not** follow conventional open-source contribution norms.

NovaLIS is a **governed system** with phase-locked behavior, strict authority boundaries, and an offline-first safety model.

Contributions are permitted **only** within the constraints defined here.

---

## 1) Canonical Authority

The following documents are binding and override all other guidance:

- `NOVA CANONICAL SYNTHESIS v5.1` — Phase-Aligned Truth (primary authority)
- `NovaLIS-Governance/PHASE_3.5_FROZEN_STATUS.md` — Current phase status
- `NovaLIS-Governance/ARCHITECT_CONTRACT.md`
- Any document explicitly marked **LOCKED** in `NovaLIS-Governance/`

If a proposed change conflicts with a lock, the change is invalid unless an explicit unlock is recorded.

---

## 2) Phase Discipline (Hard Rule)

- Current operational state: **Phase 3.5 FROZEN** (Execution Surface Guarantee Proven)
- **Phase 4 is hard blocked** and design-only
- Governor is **GovernorMediator** (text sanitizer only)
- Execution is **disabled** (`execute_action = None`)
- Documentation must never imply capabilities that runtime cannot perform

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
- Phase alignment corrections (to match v5.1)

All changes must be:

- Deterministic
- Explicit
- Reviewable via diff
- Reversible
- Phase-compliant with v5.1

---

## 4) What Contributions Are NOT Allowed

The following are forbidden unless explicitly unlocked in governance:

- Adding new skills or commands
- Implicit intent inference or ranking
- Substring or fuzzy matching
- Background threads, daemons, or schedulers
- Telemetry, analytics, or tracking
- Silent network access or auto-fallbacks
- Self-modifying or self-expanding behavior
- "Helpful" automation that bypasses user intent
- DeepSeek, DEG, or agent integration (Phase 4+ design only)
- Device control or execution capability
- Any capability beyond Phase 3.5 frozen state

If a change feels "smart" or "convenient," it is likely invalid.

---

## 5) AI-Assisted Contributions

AI may be used **only** as a constrained reviewer or editor.

AI may:

- Audit code against phase locks (v5.1)
- Propose minimal diffs
- Identify inconsistencies or unsafe assumptions
- Generate tests that enforce existing rules
- Verify phase alignment

AI must NOT:

- Design new features
- Reinterpret intent
- "Improve UX" by adding autonomy
- Optimize behavior in ways that affect authority or scope
- Suggest capabilities beyond Phase 3.5 frozen state

All AI-generated changes must be reviewed as if written by an untrusted junior contributor.

---

## 6) Review Expectations

Every contribution must:

- State the phase it affects
- Declare whether behavior changes (expected: "no")
- Reference the relevant governance lock(s)
- Prefer smallest possible change
- Align with v5.1 phase-aligned truth

If uncertain, stop and ask for clarification rather than guessing.

---

## 7) Non-Goals (Explicit)

NovaLIS is **not**:

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

- Phase 3.5: FROZEN (Execution Surface Guarantee Proven)
- Governor: GovernorMediator (text sanitizer only)
- Execution: Disabled (execute_action = None)
- External data: User/UI-triggered only
- Design documents: Marked as Phase 4+ only

Any contribution that implies capabilities beyond this reality is rejected.

---

**End of CONTRIBUTING rules.**

**Reference Authority:** Nova Canonical Synthesis v5.1 - Phase-Aligned Truth