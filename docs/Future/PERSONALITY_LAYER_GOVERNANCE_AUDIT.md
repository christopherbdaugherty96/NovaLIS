# Personality Layer Architecture — Governance Audit

Status: governance audit (no code, no runtime changes)
Date: 2026-06-04
Auditing: docs/future/PERSONALITY_LAYER_ARCHITECTURE.md
Grounded in: CURRENT_RUNTIME_STATE.md, registry.json,
  assistive_noticing.py, personality subsystem source

---

## CURRENT TRUTH

### Verified Against Runtime

- Governance spine confirmed: GovernorMediator → Governor →
  CapabilityRegistry → SingleActionQueue → LedgerWriter →
  ExecuteBoundary → Executor
- 27 capabilities active, 2 require confirmation (Cap 22
  open_file_folder, Cap 64 send_email_draft)
- Personality subsystem (`src/personality/`) has zero imports of
  GovernorMediator, ExecuteBoundary, or any executor — confirmed
  presentation-only
- AssistiveNoticing (`src/working_context/assistive_noticing.py`)
  has zero imports of GovernorMediator, ExecuteBoundary, or any
  executor — confirmed advisory-only
- AssistiveNoticing suggested_actions contain command strings (e.g.,
  "project status ThreadName"), not capability invocations — these
  are chat-input suggestions, not execution triggers
- Runtime fingerprint hash:
  2066f96926e9ffaf2e07621d12e010ed23fb0c17f35875e97082fcc11284f4b9

### Design Doc Accuracy

The design document correctly describes the existing architecture.
No factual mismatches found between the design document and current
runtime truth.

---

## SAFE PARTS

### 1. Stack Position (SAFE)

The personality layer sits above governance and has no downward
execution path. This is confirmed by source: neither personality
nor assistive noticing imports any governance or execution
component. The design document correctly states this.

### 2. Prohibited Inputs (SAFE)

The prohibited inputs list is correct and comprehensive. The
personality subsystem has no mechanism to access raw network data,
executors, registry write methods, or credentials.

### 3. Forbidden Outputs (SAFE)

The forbidden outputs list is correct. No code path exists today
for personality to issue commands to executors, modify capability
state, or write ledger entries.

### 4. Initiative vs Authority Framework (SAFE)

The bright line ("the question mark is the governance boundary")
is clear and testable. The examples are well-chosen and
unambiguous.

### 5. Governance Review Gate (SAFE)

The initiative ↑ / authority unchanged → approve matrix is a
sound design criterion. It is simple enough to be applied
consistently and strict enough to catch real violations.

### 6. Failure Rules (SAFE)

Failure behavior is advisory-only. All failure responses in the
design present options without taking action. No failure path
grants emergency authority.

### 7. Voice Rules (SAFE)

Voice routes through Cap 18 (speak_text), which is already
governed. The requirement for text confirmation on high-authority
actions prevents voice-as-authority-shortcut.

### 8. Trust UI Rules (SAFE)

"Nova never frames governance as a limitation. Governance is the
product." This is the correct framing and prevents the most
common trust erosion pattern.

---

## UNSAFE / RISKY PARTS

### Finding 1: BriefingComposer Data Access Path (MEDIUM-HIGH)

**Section:** Implementation Recommendation, Phase 1, item 4

**Problem:** The design says BriefingComposer "reads from
capability results already in session" and "reads from memory,
calendar, project threads." But it does not specify the
enforcement mechanism that prevents BriefingComposer from calling
capabilities directly.

The existing personality subsystem is safe because it has no
imports of governance or execution code. But the BriefingComposer
is a new component. Nothing in the design mandates that it inherit
this isolation. A future developer could add a GovernorMediator
import to "make briefings more useful" and create a hidden
execution path inside the personality layer.

**Required patch:** The design must specify a structural
enforcement rule: BriefingComposer MUST NOT import GovernorMediator,
ExecuteBoundary, NetworkMediator, or any executor class. This
should be a testable invariant (import audit test), not just a
design intention.

### Finding 2: Tier 4 "Prepare" Ambiguity (MEDIUM)

**Section:** Proactive Suggestion Framework

**Problem:** Tier 4 says: "I've prepared a draft production
ticket for order #1902. Ready for your review." The design doc's
own authority leak analysis (Risk 2) correctly identifies this
risk and says Tier 4 "must only use data already available in the
current session or cached from prior governed calls."

But "cached from prior governed calls" is ambiguous. How stale
can cached data be? If the personality layer uses data from a
Shopify call made 6 hours ago to "prepare" a production ticket
suggestion, the suggestion may be based on outdated inventory or
order state. The user might approve based on stale data without
realizing it.

More critically: the phrase "I've prepared a draft production
ticket" implies that some artifact was created. Was it? Did
personality write a draft to a store? If so, that is a write
operation — authority, not initiative.

**Required patch:**
- Define maximum cache staleness for Tier 4 suggestions (e.g.,
  suggestions based on data older than N minutes must disclose
  the data age).
- Clarify that "prepared" means "composed a preview in memory"
  not "written a draft to persistent storage." Tier 4 preparation
  must be ephemeral and display-only until the user approves,
  at which point the actual write goes through governance.

### Finding 3: Pattern-Derived Reminders as Behavioral Profiling
(MEDIUM)

**Section:** Reminder Framework

**Problem:** "Pattern-derived: You usually review Shopify orders
on Monday mornings." This requires Nova to observe, record, and
analyze the user's behavioral patterns over time. While the
reminder itself is advisory-only (initiative, not authority),
the underlying pattern detection creates a behavioral profile.

This is not an authority leak, but it is a governance concern:
- Who owns the behavioral profile data?
- Where is it stored? Through Cap 61 (memory_governance)?
  Or in a separate, ungovened store?
- Can the user see, edit, and delete their behavioral patterns?
- Can patterns be used for purposes beyond reminders?

If pattern data is stored outside the governed memory system
(Cap 61), it creates an ungoverned data store — which violates
the design doc's own rule: "No personality-owned data stores
(use existing governed stores)."

**Required patch:** Specify that all behavioral pattern data
must be stored through Cap 61 (memory_governance) and is
subject to the same visibility, edit, and delete controls as
any other memory item. Patterns are governed memory, not hidden
telemetry.

### Finding 4: Mode Detection Auto-Switching (LOW-MEDIUM)

**Section:** Home Rules, Mode Transition

**Problem:** "Business hours + Shopify mention → business mode."
Auto-switching modes based on time and topic is convenient, but
mode affects initiative patterns (different suggestion types,
different tone). If mode detection is wrong, the user gets
mismatched suggestions.

This is not an authority leak (mode never affects authority
boundaries), but it creates a subtler issue: if business mode
is more "action-oriented" and home mode is "calmer," an
incorrect mode detection could make Nova feel pushy (business
mode at home) or unresponsive (home mode during work).

**Required patch:** Mode detection should have an explicit
override ("I'm working" / "I'm done for the day") and the
current detected mode should be visible to the user (in
dashboard or Trust Panel). Auto-detection is a default, not
a hidden state.

### Finding 5: Approval Gate Wrapping May Obscure Gate Identity
(MEDIUM)

**Section:** Approval Gate Interaction Rules

**Problem:** The "before and after" example transforms:
```
"Action 'send_email_draft' requires confirmation. Confirm? [y/n]"
```
into:
```
"I've drafted the email to Sarah about the Q3 timeline.
Want me to open this in your mail client?"
```

The personality-wrapped version is better UX, but it no longer
identifies which governance gate is being triggered. A user who
wants to understand Nova's governance model cannot tell from the
wrapped message that Cap 64 (send_email_draft) is being invoked,
or what authority_class it has, or whether it's reversible.

This matters because "governance should feel natural" must not
become "governance should be invisible." The design doc's own
Trust UI section says "governance is the product." If the
personality wrapping makes governance invisible, it contradicts
the trust principle.

**Required patch:** Personality-wrapped gate messages must
include a machine-readable or expandable reference to the
underlying governance gate. Options:
- A subtle "Cap 64 · send_email_draft · reversible" footer
- An expandable "Why am I being asked?" link
- A Trust Panel cross-reference
The user should be able to see the governance truth behind
every personality-wrapped confirmation, even if they usually
don't need to.

### Finding 6: Escalation "Security Anomaly" Claim (LOW-MEDIUM)

**Section:** Escalation Behavior

**Problem:** "I noticed an unusual login pattern. You should
check your Shopify admin." This implies Nova is monitoring login
patterns. Currently, Cap 65 (shopify_intelligence_report) is
read-only and fetches order metrics, product catalog, and
inventory. It does not fetch login or security data.

If Nova cannot actually detect login anomalies, this escalation
example is aspirational, not grounded in current truth. Including
unimplementable examples in a governance design document creates
a gap between design and reality that could lead to shortcuts
during implementation.

**Required patch:** Either:
- Remove the security anomaly example and replace with one
  grounded in current capabilities (e.g., "Shopify API has
  returned errors 3 times today"), or
- Mark it explicitly as "future capability required" and note
  that it requires a new governed capability for security
  monitoring.

### Finding 7: "Decides What Deserves Attention" is Soft Authority
(LOW)

**Section:** Chief of Staff Model, Three Internal Roles

**Problem:** "Personality Layer = Chief of Staff (decides what
deserves the user's attention)." The word "decides" here is
doing real work. Prioritization is a form of soft authority —
what Nova surfaces first affects what the user acts on first.
If Nova consistently deprioritizes certain information, the
user may never see it.

This is not a hard authority leak (no gates are bypassed), but
it is an information-filtering risk. A chief of staff who
controls the briefing controls the agenda.

**Required patch:** Add an explicit rule: "The user may always
request a full, unprioritized view of all available information.
Personality prioritization is a convenience default, not an
information filter. No data source may be excluded from the
full view based on personality-layer prioritization logic."

---

## AUTHORITY LEAKS

### Confirmed Leaks: 0

No direct authority leak exists in the design. The personality
layer has no execution path, no governance imports, and no
mechanism to bypass gates. This is structurally sound.

### Potential Leak Vectors: 3

1. **BriefingComposer import creep** (Finding 1) — future
   developer adds execution imports. Mitigated by import audit
   test.

2. **Tier 4 "prepared" ambiguity** (Finding 2) — "prepared"
   could be interpreted as "wrote to store." Mitigated by
   clarifying ephemeral-only.

3. **Pattern data stored outside governance** (Finding 3) —
   ungoverned behavioral profile. Mitigated by requiring Cap 61
   for all pattern storage.

---

## MEMORY-AS-PERMISSION RISKS

### Design Doc Coverage: GOOD

The design document's memory rules are the strongest section.
The rule "Memory informs suggestions. Memory never grants
authority." is clear and correct.

### Residual Risk: 1

**Implicit frequency escalation from memory.** If Nova remembers
that the user has approved Shopify data pulls 10 times, the
personality layer might increase the confidence and frequency of
Shopify-related suggestions, making the user feel pressured to
approve. This is not memory-as-permission (the gate still
fires), but it is memory-as-persuasion.

**Required patch:** Add a rule: "Suggestion frequency and
confidence for a given action type must not escalate based on
prior approval count. The personality layer treats each approval
as independent. Memory may inform content (what to suggest) but
not pressure (how urgently to suggest it)."

---

## APPROVAL-GATE RISKS

### Finding 5 (above): Gate identity obscured by wrapping

### Additional Risk: Confirmation Fatigue by Design

The design proposes Tier 3 and Tier 4 suggestions that end with
"Would you like me to...?" If each of these triggers a
governance gate, the user faces two confirmation steps:

1. Personality layer: "Would you like me to investigate?"
2. Governance gate: "This action requires confirmation. Confirm?"

This double-confirmation could cause fatigue faster than the
current system. Users may learn to approve both steps
reflexively.

**Required patch:** Clarify the interaction between personality
suggestions and governance gates. Options:
- Personality "Would you like me to...?" IS the governance gate
  (personality wraps the gate, not a separate step before it)
- Or: personality suggestion is a pre-gate advisory, and the
  gate fires only if the user says yes — making it a single
  confirmation, not two

The design doc's gate interaction example implies the first
option (wrapping), but this should be stated explicitly as a
rule.

---

## ASSISTIVE-NOTICING RISKS

### Current State: SAFE

AssistiveNoticing has no execution imports. Its suggested_actions
are chat-input command strings, not capability invocations. The
user must still type or click the suggestion, which enters the
normal conversation router → governance path.

### Extension Risk: Tier Mapping

The design proposes mapping suggestion tiers onto
AssistiveNoticing:
- Tier 1 → current notice types
- Tier 2 → anomaly detection
- Tier 3 → actionable suggestions
- Tier 4 → preparation notices

Tiers 3 and 4 are new territory for AssistiveNoticing. The
current system surfaces observations ("A blocker is recorded
without a next step"). Tiers 3-4 surface calls to action
("Want me to investigate?"). This shifts AssistiveNoticing from
an awareness system to a suggestion system.

**Required patch:** When extending AssistiveNoticing with
Tiers 3-4, maintain the structural guarantee: suggested_actions
remain chat-input command strings. No Tier 3 or Tier 4 notice
may contain a direct capability invocation. The user's
acceptance of a suggestion must re-enter the conversation
router, not bypass it.

---

## TRUST UI RISKS

### Finding 5 (above): Gate wrapping may obscure governance truth

### Additional Risk: Chief of Staff Framing May Set Wrong
Expectations

"Nova's role is Chief of Staff" is a useful internal design
metaphor. But if surfaced to the user as-is, it may set
expectations that Nova has more agency than it does. A human
chief of staff can make phone calls, send emails, and schedule
meetings independently. Nova cannot.

**Required patch:** The user-facing personality should not use
the phrase "Chief of Staff" literally. The internal design
uses it as an architectural metaphor. The user should experience
the behavior (proactive, organized, transparent) without the
title (which implies agency). This prevents a trust gap between
what the metaphor promises and what governance permits.

---

## REQUIRED PATCHES TO DESIGN DOC

Summary of all required patches, ordered by priority:

### Priority 1 (Must Fix Before Implementation)

**P1-A: BriefingComposer structural isolation (Finding 1)**
Add: "BriefingComposer MUST NOT import GovernorMediator,
ExecuteBoundary, NetworkMediator, or any executor. Enforce with
an import audit test."

**P1-B: Tier 4 "prepared" clarification (Finding 2)**
Add: "'Prepared' means composed an ephemeral preview in
working memory. No persistent artifact is created until the
user approves, at which point the write routes through
governance."

**P1-C: Personality suggestion IS the governance gate
(Approval-Gate Risk)**
Add: "When personality wraps an approval gate, the personality
message IS the gate — not a separate step before it. The user
confirms once. The confirmation routes directly to governance."

### Priority 2 (Should Fix Before Implementation)

**P2-A: Pattern data must go through Cap 61 (Finding 3)**
Add: "All behavioral pattern data is governed memory. Stored
through Cap 61. Subject to user visibility, edit, and delete."

**P2-B: Gate identity must remain visible (Finding 5)**
Add: "Personality-wrapped confirmations must include an
expandable governance reference (capability ID, authority class,
reversibility)."

**P2-C: Full unprioritized view always available (Finding 7)**
Add: "User may request full unprioritized data at any time.
Personality prioritization is convenience, not a filter."

**P2-D: Memory must not escalate suggestion pressure
(Memory Risk)**
Add: "Suggestion frequency and confidence must not increase
based on prior approval count."

### Priority 3 (Should Fix Before or During Implementation)

**P3-A: Mode detection visible and overridable (Finding 4)**
Add: "Current mode displayed in dashboard. User can override
with explicit command."

**P3-B: Remove or mark aspirational escalation examples
(Finding 6)**
Add: Ground all examples in current capabilities, or mark
future-dependent examples explicitly.

**P3-C: Tier 3-4 suggested_actions remain chat-input strings
(Noticing Risk)**
Add: "No Tier 3 or 4 notice may contain a direct capability
invocation. Acceptance re-enters conversation router."

**P3-D: "Chief of Staff" is internal-only terminology
(Trust UI Risk)**
Add: "The Chief of Staff model is an internal architecture
metaphor. User-facing personality does not use this title."

---

## IMPLEMENTATION READINESS

### Structural Safety: READY

The architecture is structurally sound. The personality layer
has no execution path, no governance bypass mechanism, and no
authority expansion vector. The existing codebase confirms this
isolation.

### Design Completeness: NOT READY (patches required)

The design document has 11 patches needed across 3 priority
levels. The 3 Priority-1 patches address ambiguities that could
lead to authority leaks during implementation. These must be
resolved before any code is written.

### Test Strategy: NOT SPECIFIED

The design document does not include a test strategy. Before
implementation, define:
- Import audit tests (BriefingComposer isolation)
- Authority boundary tests (personality never triggers execution)
- Gate-wrapping tests (confirmation still routes through
  governance)
- Suggestion tier tests (Tier 3-4 remain advisory-only)

---

## FINAL VERDICT

```text
SAFE WITH PATCHES
```

The personality layer architecture is governance-safe in
structure. No direct authority leaks exist. The governance
review gate (initiative ↑ / authority unchanged → approve) is
a sound design criterion.

However, 11 design patches are required before implementation
can begin safely. Three are Priority 1 (must fix): BriefingComposer
isolation enforcement, Tier 4 artifact ambiguity, and
double-confirmation risk. These address ambiguities that could
become authority leaks during implementation if not resolved
in the design.

The design is the right architecture for Nova's personality
layer. It needs tightening, not rethinking.
