# PHASE 3.5 — VERIFICATION CHECKLIST (CANONICAL)

This checklist is the authoritative gate for:
- Phase 3.75
- Phase 4 (Governed Actions)

NO ITEM MAY BE SKIPPED.
EVIDENCE IS REQUIRED FOR EACH SECTION.

--------------------------------------------------
SECTION A — FOUNDATIONAL GUARANTEES (PHASE 0–3)
--------------------------------------------------

A1. No Autonomy
- [ ] Nova does not initiate actions
- [ ] Nova does not self-trigger speech
- [ ] Nova does not advance phases automatically
Evidence:

A2. No Background Cognition
- [ ] No processing without explicit user input
- [ ] No background listeners unless explicitly enabled
- [ ] No idle reasoning loops
Evidence:

A3. Deterministic Routing
- [ ] Token-based matching only
- [ ] No ranking, guessing, or probabilistic intent selection
- [ ] Same input ? same output
Evidence:

A4. Offline-First Default
- [ ] Local reasoning works without internet
- [ ] Online access is explicitly announced
- [ ] Online access is explicitly exited
Evidence:

--------------------------------------------------
SECTION B — CONVERSATION DISCIPLINE
--------------------------------------------------

B1. Entry Discipline
- [ ] First phrase per session is exactly:
      "Hello. How can I help?"
- [ ] Occurs once per session only
Evidence:

B2. Clarification Protocol
- [ ] At most one clarification question
- [ ] No follow-up clarifications
- [ ] Ambiguity fallback is refusal or least-assumptive interpretation
Evidence:

B3. Normalization Rules
- [ ] Deterministic synonym tables only
- [ ] No learning from corrections
- [ ] No cross-session adaptation
Evidence:

--------------------------------------------------
SECTION C — INTERPRETIVE AWARENESS (PHASE-3.5b)
--------------------------------------------------

C1. Ephemeral Only
- [ ] Exists only during response generation
- [ ] No memory writes
- [ ] No logs
- [ ] No UI state changes
Evidence:

C2. No Action Influence
- [ ] Interpretive signals do NOT trigger actions
- [ ] Interpretive signals do NOT alter permissions
Evidence:

--------------------------------------------------
SECTION D — MEMORY GOVERNANCE
--------------------------------------------------

D1. Memory Tier Visibility
- [ ] Locked / Active / Deferred clearly labeled
- [ ] Read-only inspection only
- [ ] No edit, delete, or summarize functions
Evidence:

D2. Correction Mapping
- [ ] "Correction: X" syntax works
- [ ] Literal-only mappings
- [ ] Mappings are inspectable
- [ ] Mappings are deletable
Evidence:

--------------------------------------------------
SECTION E — SAFETY SYSTEMS
--------------------------------------------------

E1. Circuit Breakers
- [ ] Wake >5/min triggers auto-pause
- [ ] Listening >5 min triggers auto-pause
- [ ] Memory >50MB triggers auto-disable
- [ ] Persists across restarts
- [ ] Manual reset required
Evidence:

E2. Safety Dashboard
- [ ] Internet status visible
- [ ] "Data leaving device: NONE" shown when offline
- [ ] Links to audit + memory inspection
- [ ] Read-only
Evidence:

--------------------------------------------------
SECTION F — DIAGNOSTICS & TRACEABILITY
--------------------------------------------------

F1. Nova Doctor
- [ ] Phase displayed
- [ ] Blockers displayed
- [ ] Wake word status shown
- [ ] Circuit breaker state shown
- [ ] No repair or suggestion buttons
Evidence:

F2. Golden Trace
- [ ] Session ID generated
- [ ] Request ID generated
- [ ] Governor decision ID generated
- [ ] Append-only
- [ ] No deletion or mutation
Evidence:

--------------------------------------------------
SECTION G — WAKE WORD (OPT-IN)
--------------------------------------------------

G1. Wake Word Governance
- [ ] Disabled by default
- [ ] Local-only detection
- [ ] No audio retention
- [ ] Activation log append-only
- [ ] Instant disable works
Evidence:

--------------------------------------------------
SECTION H — UX & USER TRUST
--------------------------------------------------

H1. Weather UX
- [ ] Feels-like shown
- [ ] 3–5 day forecast shown
- [ ] Last-updated timestamp shown
- [ ] Spoken only when asked
Evidence:

H2. Morning Briefing
- [ ] User-invoked only
- [ ] Correct greeting by time
- [ ] Headlines only after explicit yes
Evidence:

H3. First-Run Onboarding
- [ ] Skippable
- [ ] Beginner mode default
- [ ] No routines auto-created
Evidence:

--------------------------------------------------
SECTION I — RECOVERY & FAILURE
--------------------------------------------------

I1. Restore & Rollback
- [ ] nova_restore.py tested
- [ ] State restores cleanly
- [ ] No ghost memory
Evidence:

I2. Failure Language
- [ ] Neutral phrasing
- [ ] No blame
- [ ] No alarmist language
Evidence:

--------------------------------------------------
SECTION J — HUMAN TRUST TEST
--------------------------------------------------

J1. Spouse Test
- [ ] Non-technical user
- [ ] Understandable behavior
- [ ] No creepiness
- [ ] Clear limits
Result: PASS / FAIL
Notes referenced in SPOUSE_TEST_NOTES.md

--------------------------------------------------
FINAL GATE
--------------------------------------------------

- [ ] ALL sections above completed
- [ ] ALL Phase-3.5 GitHub issues closed
- [ ] ZERO critical bugs open

SIGN-OFF:
Date:
Verifier:
Commit Hash:
