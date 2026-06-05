# Implementation Plan — Governance Audit

Status: governance audit of implementation plan
Date: 2026-06-04
Auditing: docs/future/PERSONALITY_LAYER_IMPLEMENTATION_PLAN.md
Architecture status: SAFE
Governance audit status: SAFE
Implementation status: NOT STARTED

---

## 20-POINT AUDIT

### Phase 1 Audit

#### 1. Authority Expansion — SAFE

No Phase 1 component creates new capabilities, executors, or
authority paths. ChiefOfStaffProfile is pure configuration.
BriefingComposer is presentation-only. AssistiveNoticing
extensions add tiers but not execution. PersonalityInterfaceAgent
extensions add wrapping but not gate modification.

#### 2. Hidden Autonomy — SAFE

No Phase 1 component operates autonomously. All output is
triggered by user interaction or existing notification surfaces.
No new background processing loops.

#### 3. Capability Bypass — SAFE

No Phase 1 component invokes capabilities. BriefingComposer
receives data as arguments, never fetches. Import boundary
tests enforce this.

#### 4. GovernorMediator Bypass — SAFE WITH FINDING

See Finding 1 below.

#### 5. ExecuteBoundary Bypass — SAFE

No Phase 1 component imports or references ExecuteBoundary.

#### 6. Memory-as-Permission — SAFE

Plan explicitly states memory informs content, never grants
authority. Prior-approval independence rule documented.
Test `test_memory_informs_not_grants` covers this.

#### 7. Pattern-Profile Accumulation — SAFE

Plan requires all pattern data through Cap 61. Test
`test_pattern_data_stored_via_cap61` covers this.

#### 8. AssistiveNoticing Authority Drift — SAFE

New tiers produce chat-input command strings only. Test
`test_suggested_actions_are_chat_strings` covers this.
Acceptance re-enters ConversationRouter.

#### 9. BriefingComposer Authority Drift — SAFE

Hard structural isolation with import audit test. Eight
import boundary tests defined.

#### 10. Confirmation Ambiguity — SAFE

Single-confirmation rule documented. Test
`test_gate_wrapping_single_confirmation` covers this.

#### 11. Double-Confirmation Risk — SAFE

Plan explicitly states personality wrapping IS the gate.
Test `test_single_confirmation_maintained` covers this.

#### 12. Trust UI Visibility Loss — SAFE

Gate wrapping preserves governance identity. Test
`test_gate_wrapping_includes_governance_id` covers this.

#### 13. Mode-Based Authority Changes — SAFE

Plan states mode affects tone only, never authority.
Test `test_mode_does_not_affect_gates` covers this.

#### 14. Reminder Authority Escalation — SAFE

Plan prohibits calendar events without approval, recurring
obligations without request, escalation based on dismissal.
Tests cover each.

#### 15. Voice Authority Escalation — SAFE

Plan requires text confirmation for high-authority voice
actions. Test `test_high_authority_requires_text_confirm`
covers this.

#### 16. Simulation Coverage Gaps — FINDING

See Finding 3 below.

#### 17. Test Coverage Gaps — FINDINGS

See Findings 2, 4, 5 below.

#### 18. Import-Boundary Weaknesses — FINDING

See Finding 1 below.

#### 19. Rollback Weaknesses — FINDING

See Finding 6 below.

#### 20. Future-Maintainer Drift Risk — FINDING

See Finding 7 below.

---

## SAFE PARTS

The plan is structurally sound. The component designs are
correct. The governance boundaries are well-defined. The
test strategy covers the most important boundaries. The
rollback plan is phase-independent and clean.

The plan correctly:
- Prohibits new capabilities and executors
- Enforces import boundary isolation
- Requires single-confirmation rule
- Routes pattern data through Cap 61
- Keeps suggestions as chat-input strings
- Preserves governance identity in gate wrapping
- Makes mode detection visible and overridable
- Prohibits memory-as-permission
- Prohibits suggestion pressure escalation

---

## RISKY PARTS

### Finding 1: core.py Already Imports from src.governor (MEDIUM)

**Section affected:** Current Truth, Import Boundary Tests

**Problem:** The plan states "Zero imports of GovernorMediator,
ExecuteBoundary, NetworkMediator, or any executor in any
personality file." This is incorrect.

`core.py` (PersonalityAgent) imports `AgentOrchestrator` from
`src.governor.agent_orchestrator`. While AgentOrchestrator is
documented as "non-authorizing," it lives in the governor
package and creates an import chain from personality → governor.

Additionally, `ProjectThreadStore` (which BriefingComposer
will read from) imports `LedgerWriter` from `src.ledger.writer`.
If BriefingComposer imports ProjectThreadStore directly, it
inherits a transitive dependency on LedgerWriter.

**Risk:** The import boundary tests as currently specified scan
for direct imports only. They would miss transitive imports.
A developer could import ProjectThreadStore into
BriefingComposer and technically satisfy all 8 import boundary
tests while gaining indirect access to LedgerWriter.

**Required patch:**
- Acknowledge core.py's existing governor import in the
  Current Truth section. Note that it predates the personality
  layer design and is scoped to non-authorizing orchestration.
- Add transitive import tests: verify that BriefingComposer's
  full import tree contains no governance, execution, or
  ledger imports. Not just direct imports — full resolution.
- Specify that BriefingComposer receives a ProjectThreadStore
  snapshot (a plain dict or frozen dataclass), not the
  ProjectThreadStore instance itself. This breaks the
  transitive dependency.

### Finding 2: Missing Test for Tier 4 Data Staleness (LOW-MEDIUM)

**Section affected:** Phase 1 Test Plan, BriefingComposer Tests

**Problem:** The architecture doc (patched) requires that
Tier 4 suggestions based on stale data must disclose data age.
The implementation plan has no test for this.

A Tier 4 suggestion like "I can put together a draft production
ticket from today's data" implies the data is current. If the
underlying Shopify data is from 6 hours ago, the user might
approve based on outdated information.

**Required patch:** Add test:

```
test_tier4_discloses_data_age
  Description: Tier 4 suggestion from stale data includes
    age disclosure
  Pass criteria: If source data is older than configured
    threshold, suggestion text includes data age
```

### Finding 3: Missing Simulation for Personality-Off Baseline
(MEDIUM)

**Section affected:** Phase 1 Simulation Plan

**Problem:** The plan defines 5 simulation scenarios for
personality-on behavior. It does not define a baseline
comparison for personality-off behavior. Without a baseline,
you cannot verify that personality changes only presentation
(initiative) and not behavior (authority).

**Required patch:** Add a 6th simulation scenario:

```
Scenario 6: Personality-Off Baseline

Run the same 5 scenarios with personality layer disabled
(CHIEF_OF_STAFF_ENABLED = False).

Expected: Same governance gates fire. Same confirmation
requirements. Same capability invocations. Only presentation
text differs.

Authority check: Governance behavior identical with and
without personality.
```

This is the strongest possible test of "personality may
increase initiative, personality may never increase authority."

### Finding 4: Missing Test for Existing PersonalityAgent
Compatibility (LOW-MEDIUM)

**Section affected:** Phase 1 Test Plan

**Problem:** `core.py` contains `PersonalityAgent` (Phase 4.2
facade) which uses `AgentOrchestrator`. The implementation
plan creates `ChiefOfStaffProfile` and extends
`PersonalityInterfaceAgent` but does not specify how the new
Chief of Staff components interact with the existing
`PersonalityAgent` class.

If the new code modifies `PersonalityInterfaceAgent.present()`
behavior, it could affect `PersonalityAgent` callers. The plan
says "extend, don't replace" but has no regression test for
existing PersonalityAgent behavior.

**Required patch:** Add test:

```
test_existing_personality_agent_unchanged
  Description: PersonalityAgent.run() produces same output
    structure as before Phase 1
  Pass criteria: Output format, validation, deep-mode
    behavior all unchanged
```

### Finding 5: Import Boundary Tests Need Transitive Scan
(MEDIUM)

**Section affected:** Phase 1 Test Plan, Import Boundary Tests

**Problem:** The 8 import boundary tests scan for direct
imports (string matching in source files). This catches
`from src.governor.governor_mediator import GovernorMediator`
but misses transitive imports through intermediate modules.

Example: if BriefingComposer imports a utility that imports
an executor, the direct-import scan passes but the isolation
is broken.

**Required patch:** Add a 9th import boundary test:

```
test_briefing_composer_transitive_isolation
  Description: Resolve full import tree of BriefingComposer.
    Verify no module in the tree is in src.governor,
    src.executors, src.ledger, or src.governor.network_mediator
  Pass criteria: Zero governance/execution/ledger modules
    in resolved import tree
  Implementation: Use importlib or AST walking to resolve
    transitive imports
```

This is the strongest form of the isolation test.

### Finding 6: Rollback Verification Missing Personality-Off
Simulation (LOW)

**Section affected:** Rollback Plan, Phase 1

**Problem:** Rollback verification says "run full test suite"
and "verify runtime fingerprint." It does not say "run
simulation scenarios to verify personality-off behavior
matches pre-Phase-1 behavior."

If rollback is needed, the most important verification is
that the system behaves identically to before Phase 1 — not
just that tests pass but that user-facing behavior is
unchanged.

**Required patch:** Add to Phase 1 rollback verification:

```
- Run simulation baseline (20 personas, 33 turns)
- Results must match pre-Phase-1 baseline within existing
  tolerances
```

### Finding 7: No CONTRIBUTING Guidance for Personality PRs
(LOW)

**Section affected:** Implementation Risks, Governance Risks

**Problem:** The plan identifies "future features bypass review
gate because 'it's just UX'" as a governance risk. The
mitigation says "governance review gate criterion documented,
review required for all personality PRs." But no
CONTRIBUTING guidance or PR template is specified.

Without explicit process, the governance review gate is a
design principle, not an enforced practice.

**Required patch:** Add to Phase 1 deliverables:

```
Add CONTRIBUTING note or PR checklist for personality changes:
- [ ] Does this feature increase initiative?
- [ ] Does this feature increase authority?
- [ ] If authority ↑, REJECT
- [ ] Import boundary tests pass
- [ ] No new capability IDs
- [ ] No new executors
```

This turns the design principle into a process gate.

---

## MISSING TESTS

| # | Missing Test | Phase | Priority |
|---|---|---|---|
| 1 | Transitive import isolation for BriefingComposer | 1 | HIGH |
| 2 | Tier 4 data staleness disclosure | 1 | MEDIUM |
| 3 | Existing PersonalityAgent compatibility | 1 | MEDIUM |
| 4 | Personality-off baseline simulation | 1 | HIGH |
| 5 | Rollback simulation verification | 1 | LOW |

---

## MISSING SIMULATIONS

| # | Missing Simulation | Phase | Priority |
|---|---|---|---|
| 1 | Personality-off baseline (same 5 scenarios, personality disabled) | 1 | HIGH |
| 2 | Escalation scenario (repeated failures, verify no authority change) | 1 | MEDIUM |

---

## MISSING IMPORT GUARDS

| # | Missing Guard | Phase | Priority |
|---|---|---|---|
| 1 | Transitive import resolution for BriefingComposer | 1 | HIGH |
| 2 | Acknowledgment of core.py's existing governor import | 1 | MEDIUM |
| 3 | BriefingComposer receives snapshot not instance of ProjectThreadStore | 1 | HIGH |

---

## MISSING ROLLBACK PROTECTIONS

| # | Missing Protection | Phase | Priority |
|---|---|---|---|
| 1 | Simulation baseline comparison on rollback | 1 | LOW |

---

## REQUIRED PATCHES

### Priority 1 (Must Fix Before Implementation)

**P1-A: Fix Current Truth — core.py governor import**
Acknowledge that `personality/core.py` imports
`AgentOrchestrator` from `src.governor`. Note this predates
personality layer design and is scoped to non-authorizing
orchestration. New personality components (ChiefOfStaffProfile,
BriefingComposer) must not follow this pattern.

**P1-B: Add transitive import boundary test**
Add `test_briefing_composer_transitive_isolation` to resolve
full import tree and verify zero governance/execution/ledger
modules.

**P1-C: BriefingComposer receives snapshots, not instances**
Specify that BriefingComposer receives plain dicts or frozen
dataclasses as inputs, not live instances of
ProjectThreadStore (which imports LedgerWriter) or other
components with governance dependencies.

**P1-D: Add personality-off baseline simulation**
Add Scenario 6: run same 5 scenarios with personality disabled.
Verify governance behavior identical with and without
personality.

### Priority 2 (Should Fix Before Implementation)

**P2-A: Add Tier 4 data staleness test**
Add `test_tier4_discloses_data_age` to verify stale-data
disclosure.

**P2-B: Add existing PersonalityAgent compatibility test**
Add `test_existing_personality_agent_unchanged` to verify
Phase 4.2 facade behavior is unaffected.

**P2-C: Add personality PR checklist**
Define CONTRIBUTING guidance or PR template with governance
review gate questions for all personality changes.

### Priority 3 (Should Fix Before or During Implementation)

**P3-A: Add escalation simulation scenario**
Add a simulation for repeated failures to verify escalation
increases urgency of presentation but never changes authority.

**P3-B: Add rollback simulation verification**
Add simulation baseline comparison to rollback verification
procedure.

---

## IMPLEMENTATION READINESS

| Criterion | Status |
|---|---|
| Architecture | SAFE (audited, patched, re-audited) |
| Implementation plan structure | SOUND |
| Component designs | CORRECT |
| Governance boundaries | WELL-DEFINED |
| Test strategy | GOOD — needs 5 additions |
| Simulation strategy | GOOD — needs 2 additions |
| Import boundary strategy | NEEDS STRENGTHENING (transitive) |
| Rollback strategy | ADEQUATE — minor addition |
| Current Truth accuracy | NEEDS CORRECTION (core.py import) |

---

## FINAL VERDICT

```text
SAFE WITH PATCHES → SAFE (patches applied 2026-06-04)
```

All 9 patches applied to PERSONALITY_LAYER_IMPLEMENTATION_PLAN.md:
- 4 Priority 1: core.py truth correction, transitive import
  test, snapshot-only rule, personality-off baseline simulation
- 3 Priority 2: staleness test, compatibility test, PR checklist
- 2 Priority 3: escalation simulation, rollback simulation

Post-patch status: The implementation plan is governance-safe.
No component design introduces authority expansion. Test
strategy covers critical boundaries including transitive
imports. Rollback plan includes simulation verification.
Snapshot-only rule prevents indirect governance dependencies.

Implementation readiness: READY for Phase 1A.
