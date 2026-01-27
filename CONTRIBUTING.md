\# CONTRIBUTING — NovaLIS (Governance-First Rules)



This repository does \*\*not\*\* follow conventional open-source contribution norms.



NovaLIS is a \*\*governed system\*\* with phase-locked behavior, strict authority boundaries, and an offline-first safety model.



Contributions are permitted \*\*only\*\* within the constraints defined here.



---



\## 1) Canonical Authority



The following documents are binding and override all other guidance:



\- `NovaLIS-Governance/PHASE\_1\_LOCK.md`

\- `NovaLIS-Governance/PHASE\_2\_LOCK.md`

\- `NovaLIS-Governance/PHASE\_3\_LOCK.md`

\- `NovaLIS-Governance/ARCHITECT\_CONTRACT.md`

\- Any document explicitly marked \*\*LOCKED\*\* in `NovaLIS-Governance/`



If a proposed change conflicts with a lock, the change is invalid unless an explicit unlock is recorded.



---



\## 2) Phase Discipline (Hard Rule)



\- Current operational ceiling: \*\*Phase 3 / Phase 3.5\*\*

\- \*\*Phase 4 is blocked\*\* until Phase 3.5 acceptance gates are complete.

\- No contribution may:

&nbsp; - Introduce new capabilities

&nbsp; - Expand authority

&nbsp; - Enable background execution

&nbsp; - Add proactive or inferred behavior



Phase boundaries are safety barriers, not suggestions.



---



\## 3) What Contributions ARE Allowed



Allowed changes include:

\- Bug fixes that preserve behavior

\- Clarifying comments and documentation

\- Tests that enforce existing constraints

\- Refactoring \*\*only\*\* when behavior is provably unchanged

\- Removal of dead code or unused artifacts

\- Tooling that improves verification without adding power



All changes must be:

\- Deterministic

\- Explicit

\- Reviewable via diff

\- Reversible



---



\## 4) What Contributions Are NOT Allowed



The following are forbidden unless explicitly unlocked in governance:



\- Adding new skills or commands

\- Implicit intent inference or ranking

\- Substring or fuzzy matching

\- Background threads, daemons, or schedulers

\- Telemetry, analytics, or tracking

\- Silent network access or auto-fallbacks

\- Self-modifying or self-expanding behavior

\- “Helpful” automation that bypasses user intent



If a change feels “smart” or “convenient,” it is likely invalid.



---



\## 5) AI-Assisted Contributions



AI may be used \*\*only\*\* as a constrained reviewer or editor.



AI may:

\- Audit code against locks

\- Propose minimal diffs

\- Identify inconsistencies or unsafe assumptions

\- Generate tests that enforce existing rules



AI must NOT:

\- Design new features

\- Reinterpret intent

\- “Improve UX” by adding autonomy

\- Optimize behavior in ways that affect authority or scope



All AI-generated changes must be reviewed as if written by an untrusted junior contributor.



---



\## 6) Review Expectations



Every contribution must:

\- State the phase it affects

\- Declare whether behavior changes (expected: “no”)

\- Reference the relevant governance lock(s)

\- Prefer smallest possible change



If uncertain, stop and ask for clarification rather than guessing.



---



\## 7) Non-Goals (Explicit)



NovaLIS is \*\*not\*\*:

\- A chatbot platform

\- An autonomous agent

\- A learning system

\- A surveillance system

\- A growth-at-all-costs product



It is a \*\*governed, household-safe assistant\*\* that values predictability over cleverness.



---



End of CONTRIBUTING rules.



