# Phase 3 Personality — Design Scope

Status: design (no code, no runtime changes)
Date: 2026-06-05
Prerequisite: Phase 2 complete (f001589)
Governing rule: initiative ↑, authority unchanged

---

## 1. CURRENT TRUTH

### Delivered State

**Phase 1 (fd9ba33 → 294cfa6):**

- ChiefOfStaffProfile — frozen behavioral model configuration
- BriefingComposer — snapshot-only briefing aggregation
- PersonalityInterfaceAgent extensions — gate wrapping,
  failure humanization, mode-aware presentation
- AssistiveNoticing tiers 2-4 — flag, recommend, prepare
  with staleness disclosure
- Import boundary tests — build-blocking governance isolation
- Phase 1 simulation — 28 tests, 7 scenarios, all green

**Phase 2 (47b8ea9 → f001589):**

- ModeDetector — context-aware mode inference (home, business,
  development) with explicit override support
- ReminderFramework — user-created and pattern-derived reminder
  suggestions as plain dicts, no persistence
- Initiative template refinement — mode-specific templates and
  chat guidance using permitted suggestion language
- Authority neutrality tests — 11 tests proving mode cannot
  affect permissions
- Phase 2 simulation — 38 tests, 10 scenarios, all green

**Runtime baseline:**

```
Active capabilities: 27
Executors: 22
Confirmation-required: Cap 22, Cap 64
Fast suite: 2911 passing
Governance imports in personality: 0
Working tree: clean
```

### Not Yet Wired

- ModeDetector → not connected to ConversationRouter
- ReminderFramework → not connected to live session flow
- BriefingComposer → no live caller
- Initiative templates → not selected by ModeDetector
- Voice → no personality integration
- Trust Panel → no personality integration
- Proactive briefing → no triggers

---

## 2. PHASE 3 GOAL

Phase 3 connects the personality layer to Nova's voice surface,
trust transparency surfaces, and briefing delivery. Phases 1-2
built the personality infrastructure. Phase 3 makes it tangible
to the user.

```
Phase 1: personality exists
Phase 2: personality is context-aware
Phase 3: personality reaches the user through voice, trust, and briefings
```

Three components:

```
Component 8:  Voice Personality Rules
Component 9:  Trust Panel Integration
Component 10: Proactive Briefing Framework
```

---

## 3. COMPONENT 8 — VOICE PERSONALITY RULES

**File:** `src/personality/voice_personality.py` (new)

### Purpose

Applies Chief of Staff personality to voice (TTS) output.
Voice makes Nova sound more natural without lowering
confirmation requirements.

### Voice Wording Rules

1. Voice output is shorter than text output by default.
   Target: 1-3 sentences for informational responses.
2. Voice strips markdown, code blocks, and structural
   formatting before TTS rendering.
3. Voice preserves meaning — shortening must not drop
   the core answer or actionable next step.
4. Voice applies mode-aware tone from ChiefOfStaffProfile:
   - Home: conversational, calm, warm but not performative
   - Business: structured, metric-first, direct
   - Development: technical, concise, task-scoped

### Voice Confirmation Clarity

1. Voice-initiated confirmation requests must include the
   action description and a clear question.
2. Voice confirmation ("yes, do it") routes through the
   same governance gate as text confirmation.
3. High-authority actions (Cap 22, Cap 64) require visual
   confirmation even when initiated by voice. Voice surfaces
   the action; the user confirms via text/dashboard.
4. Voice never implies confirmation is optional.

### Voice Failure Handling

1. Voice failures use `humanize_failure()` from Phase 1B.
2. Voice failure messages are shorter than text failures.
3. Voice failures offer a verbal next step: "Want me to
   try again, or should we look at alternatives?"
4. Voice never says "ERROR", "CRITICAL", "ALERT", or
   "FAILURE" aloud.

### Voice Mode Behavior

1. Voice mode is determined by ModeDetector from Phase 2.
2. Voice mode affects tone and length, not authority.
3. Home mode: "Here's what I found. Want me to go deeper?"
4. Business mode: "47 orders today, revenue is up 12%.
   Want the full breakdown?"
5. Development mode: "Tests are green. Two threads have
   open blockers. Want the details?"

### What Voice Must Never Do

- Execute actions from voice commands without governance
- Bypass approval gates via voice
- Lower confirmation requirements because voice "feels faster"
- Access capabilities directly
- Call executors
- Write to ledger
- Invoke GovernorMediator

```
Voice may make Nova sound more natural.
Voice may not lower confirmation requirements.
```

### Interface

```python
@dataclass(frozen=True)
class VoicePersonalityResult:
    spoken_text: str
    display_text: str
    requires_visual_confirmation: bool
    mode: str

class VoicePersonality:
    def format_for_voice(
        self,
        text: str,
        *,
        mode: str = "home",
        is_confirmation: bool = False,
        is_failure: bool = False,
        profile: ChiefOfStaffProfile | None = None,
    ) -> VoicePersonalityResult: ...
```

### Governance Boundaries

- Allowed inputs: text strings, mode string, profile config
- Allowed outputs: `VoicePersonalityResult` (frozen dataclass)
- Prohibited outputs: capability invocations, executor calls,
  ledger writes, confirmation bypass flags
- Authority risk: voice feels faster → user expects less
  confirmation → personality layer silently drops gates
- Mitigation: `requires_visual_confirmation` flag for
  high-authority actions; import boundary test; no gate
  logic in VoicePersonality

---

## 4. COMPONENT 9 — TRUST PANEL INTEGRATION

**File:** `src/personality/trust_presenter.py` (new)

### Purpose

Provides natural-language descriptions of governance state
for Trust Panel surfaces. Makes governance visible through
personality rather than raw system data.

### How Personality Outputs Appear in Trust UI

1. Each personality-wrapped gate includes a governance
   identity reference: capability name, ID, authority class.
2. Trust Panel surfaces show the same governance identity
   in a human-readable format.
3. Personality framing enhances — never replaces — the
   underlying receipt data.

### How Governance Identity Remains Visible

1. Every `wrap_gate()` call includes the governance footer
   from `ChiefOfStaffProfile.confirmation_template`.
2. Trust receipts (`/api/trust/receipts`) are not modified
   by personality. They reflect raw ledger truth.
3. Dashboard trust widgets show personality-wrapped summaries
   alongside raw receipt data.

### How Suggestions Link to Capabilities

1. Each suggestion references the capability it relates to
   by name (not ID) in natural language.
2. An "expand" or "why" action reveals the governance identity
   (cap name, cap ID, authority class, reversibility).
3. Suggestions never hide which capability would be invoked.

### What Personality Must Not Obscure

- Ledger truth: receipts are raw, never personality-wrapped
- Capability identity: cap name and ID always retrievable
- Confirmation state: pending/confirmed/rejected always visible
- Failure reasons: original error available alongside
  humanized version
- Cost posture: free/paid/unknown always visible

### Interface

```python
class TrustPresenter:
    def describe_capability(
        self,
        cap_name: str,
        cap_id: int,
        authority_class: str,
        *,
        profile: ChiefOfStaffProfile | None = None,
    ) -> dict[str, str]: ...

    def describe_receipt(
        self,
        receipt: dict[str, Any],
        *,
        profile: ChiefOfStaffProfile | None = None,
    ) -> dict[str, str]: ...

    def explain_boundary(
        self,
        action_description: str,
        reason: str,
        *,
        profile: ChiefOfStaffProfile | None = None,
    ) -> str: ...
```

### Governance Boundaries

- Allowed inputs: capability metadata (name, ID, class),
  receipt dicts, boundary descriptions
- Allowed outputs: plain dicts with `summary` and `detail`
  strings, explanation strings
- Prohibited outputs: modified receipts, hidden capability
  data, trust-escalation language
- Authority risk: personality framing obscures what Nova
  actually did, creating false trust
- Mitigation: receipts never modified; capability identity
  always present; "governance is the product" framing
  enforced; trust-escalation language prohibited

---

## 5. COMPONENT 10 — PROACTIVE BRIEFING FRAMEWORK

**File:** `src/personality/proactive_briefing.py` (new)

### Purpose

Defines when and how BriefingComposer output reaches the
user. Phase 1 built BriefingComposer (composes from snapshots).
Phase 3 defines the trigger and delivery rules.

### Briefing Triggers

1. **Morning briefing:** triggered by first session of the
   day (detected by session timestamp vs last briefing
   timestamp). Not a background timer.
2. **Data arrival:** triggered when new capability result
   data enters the session (e.g., fresh Cap 65 Shopify data).
   The session handler detects fresh data; the briefing
   framework does not poll for it.
3. **Explicit request:** user says "brief me" or "what did
   I miss."

Triggers are session events, not background loops.

### Allowed Briefing Inputs

Snapshot-only rule from Phase 1 applies unchanged:

- Session data (dict of capability results)
- Project thread snapshot (list of dicts)
- Active notices snapshot (list of dicts)
- ChiefOfStaffProfile configuration (frozen dataclass)

Prohibited inputs:
- Live store instances (ProjectThreadStore, etc.)
- Capability invocations to gather data
- Network calls
- File system reads

### Cooldowns

1. Morning briefing: once per calendar day per session.
2. Data-arrival briefing: once per data source per
   `ChiefOfStaffProfile.default_staleness_threshold_seconds`
   (default 1800s / 30 minutes).
3. Explicit request: no cooldown (user asked for it).

### Full Unprioritized View Requirement

BriefingComposer already implements `as_unprioritized_text()`.
The proactive briefing framework must surface this as an
option: "Want the full view?" or equivalent.

### Opt-Out Behavior

1. User can dismiss a proactive briefing.
2. Dismissed briefing type respects cooldown before
   re-surfacing.
3. User can disable proactive briefings entirely via
   settings (assistive_notice_mode = "silent").
4. Opt-out does not affect explicit "brief me" requests.

### How Briefings Remain Advisory-Only

1. Briefings are surfaced as chat messages or dashboard
   widgets — never as background actions.
2. Briefings contain observations and suggestions, never
   confirmations or executions.
3. Suggested actions in briefings are chat-input command
   strings that re-enter ConversationRouter.
4. Briefings never trigger capability invocations.

### Interface

```python
@dataclass(frozen=True)
class BriefingTrigger:
    trigger_type: str       # "morning" | "data_arrival" | "explicit"
    source_label: str
    data_timestamp: float | None

class ProactiveBriefing:
    def should_trigger(
        self,
        *,
        trigger: BriefingTrigger,
        last_briefing_timestamp: float | None,
        assistive_notice_mode: str = "suggestive",
        cooldown_seconds: int | None = None,
    ) -> bool: ...

    def compose_and_format(
        self,
        *,
        trigger: BriefingTrigger,
        session_data: dict[str, Any] | None = None,
        thread_snapshot: list[dict[str, Any]] | None = None,
        notice_snapshot: list[dict[str, Any]] | None = None,
        mode: str = "home",
        profile: ChiefOfStaffProfile | None = None,
    ) -> dict[str, Any] | None: ...
```

### Governance Boundaries

- Allowed inputs: trigger metadata, session snapshots, profile
- Allowed outputs: briefing dicts with text and metadata
- Prohibited outputs: capability invocations, persistence,
  calendar writes, Shopify writes, background threads
- Authority risk: proactive briefings create the feeling of
  an autonomous agent
- Mitigation: triggers are session events (not timers);
  snapshot-only rule; no background loops; opt-out available;
  all suggested actions are chat-input strings

---

## 6. GOVERNANCE BOUNDARIES SUMMARY

| Component | Allowed Inputs | Allowed Outputs | Prohibited | Risk | Mitigation |
|---|---|---|---|---|---|
| VoicePersonality | text, mode, profile | VoicePersonalityResult | Cap invocations, gate bypass, ledger writes | Voice lowers confirmation | `requires_visual_confirmation` for high-auth; import test |
| TrustPresenter | cap metadata, receipts | description dicts, explanation strings | Modified receipts, hidden cap data, trust-escalation language | False trust from framing | Raw receipts unmodified; identity always present |
| ProactiveBriefing | trigger metadata, session snapshots | briefing dicts | Cap invocations, persistence, background loops | Feels autonomous | Session-event triggers only; snapshot rule; opt-out |

### Cross-Component Rules

1. No imports from `src.governor`, `src.executors`, `src.ledger`
2. No capability IDs in personality output
3. No `confirmed=True` or `approved=True` in any output
4. No calendar event creation
5. No Shopify writes
6. No background agent loops
7. All suggested actions are chat-input command strings
8. Enforced by import boundary tests (build-blocking)

---

## 7. PHASE 3 TEST STRATEGY

Tests first, then implementation.

### Voice Authority Tests

File: `test_voice_personality.py`

| Test | Pass Criteria |
|---|---|
| `test_voice_output_shorter_than_text` | Voice text length < input text length |
| `test_voice_mode_aware` | Home/business/dev produce different voice text |
| `test_voice_high_authority_requires_visual_confirm` | Cap 22, Cap 64 → `requires_visual_confirmation=True` |
| `test_voice_result_is_frozen` | Immutable dataclass |
| `test_voice_no_alarm_words` | No ERROR/CRITICAL/ALERT in spoken text |
| `test_voice_failure_uses_humanize_failure` | Failure output is calm |
| `test_voice_confirmation_includes_action_description` | Spoken confirmation describes what will happen |
| `test_voice_never_emits_confirmed_true` | No confirmation bypass |
| `test_voice_yes_for_high_authority_routes_to_visual_gate` | Voice "yes" for Cap 22/64 sets `requires_visual_confirmation=True` |

### Trust UI Truth Preservation Tests

File: `test_trust_presenter.py`

| Test | Pass Criteria |
|---|---|
| `test_describe_capability_includes_governance_identity` | Cap name, ID, authority class present |
| `test_describe_receipt_does_not_modify_original` | Input receipt dict unchanged |
| `test_explain_boundary_uses_positive_framing` | No "can't"/"limited" without "by design" |
| `test_no_trust_escalation_language` | No "just trust me" / "if you let me" |
| `test_receipts_are_raw_truth` | Description accompanies, never replaces receipt |

### Proactive Briefing Advisory-Only Tests

File: `test_proactive_briefing.py`

| Test | Pass Criteria |
|---|---|
| `test_morning_trigger_respects_daily_cooldown` | Second trigger same day returns False |
| `test_data_arrival_trigger_respects_staleness_cooldown` | Within threshold returns False |
| `test_explicit_request_has_no_cooldown` | Always returns True |
| `test_silent_mode_suppresses_proactive_triggers` | Morning/data triggers suppressed |
| `test_compose_returns_advisory_dict` | No confirmed/approved/execute fields |
| `test_compose_includes_full_view_option` | "Full view" or equivalent in output |
| `test_compose_stale_data_discloses_age` | Stale timestamp → age disclosure |
| `test_suggested_actions_are_chat_strings` | All commands are plain strings |
| `test_compose_does_not_invoke_capabilities` | No capability invocations |

### Personality-Off Baseline Tests

File: `test_phase3_personality_off_baseline.py`

| Test | Pass Criteria |
|---|---|
| `test_routing_identical_with_voice_personality` | Same capability sequences |
| `test_governor_decisions_identical` | Same decisions |
| `test_capability_count_unchanged` | 27 |
| `test_executor_count_unchanged` | 22 |

### Import Boundary Tests

Extend: `test_personality_import_boundary.py`

| Test | Pass Criteria |
|---|---|
| `test_voice_personality_no_governance_imports` | AST scan clean |
| `test_trust_presenter_no_governance_imports` | AST scan clean |
| `test_proactive_briefing_no_governance_imports` | AST scan clean |
| `test_voice_personality_transitive_isolation` | No governance in import tree |
| `test_trust_presenter_transitive_isolation` | No governance in import tree |
| `test_proactive_briefing_transitive_isolation` | No governance in import tree |

---

## 8. PHASE 3 SIMULATION STRATEGY

### Simulation Scenarios

| # | Scenario | What It Tests |
|---|---|---|
| 1 | Voice confirmation (Cap 22) | Voice surfaces action, requires visual confirm |
| 2 | Voice confirmation (Cap 64) | Email draft voice confirm, visual gate required |
| 3 | Voice failure handling | Calm voice failure, next-step suggestion |
| 4 | Trust Panel capability description | Governance identity visible in description |
| 5 | Trust Panel receipt preservation | Raw receipt unchanged by personality |
| 6 | Trust Panel boundary explanation | Positive framing, no trust escalation |
| 7 | Proactive morning briefing | Trigger fires, snapshot data used, advisory only |
| 8 | Proactive business briefing | Shopify data in briefing, mode-aware tone |
| 9 | Stale briefing data warning | Old timestamp → age disclosure |
| 10 | Briefing opt-out behavior | Dismissed → respects cooldown |
| 11 | Personality-off baseline | Routing/governor identical |

### Simulation Pass Criteria

| Criterion | Requirement |
|---|---|
| Governance leaks | 0 |
| Authority expansions | 0 |
| Voice confirmation bypasses | 0 |
| Receipt modifications | 0 |
| Trust escalation language | 0 |
| Background capability invocations | 0 |
| Persistent artifacts from briefings | 0 |
| Calendar/Shopify writes | 0 |
| Personality-off governance diff | 0 |

---

## 9. NON-GOALS

The following are explicitly prohibited in Phase 3:

| Non-Goal | Reason |
|---|---|
| Voice-triggered execution without confirmation | Voice surfaces and waits; governance gates unchanged |
| New capability IDs | Personality is not a capability |
| New executors | Personality has no execution path |
| Persistent briefing store | Briefings are ephemeral session output |
| Shopify writes | Read-only personality layer |
| Calendar writes | Read-only personality layer |
| Autonomous reminders | Reminders are surfaced, never acted upon |
| Device control from personality | All device control through existing governed executors |
| Background agent loops | No background execution from personality |
| Hidden execution | All execution visible in ledger |
| Voice recording/transcription changes | Voice personality is output-only (TTS formatting) |
| Trust Panel data modification | Personality describes trust data, never modifies it |
| Memory writes from personality | All memory through governed Cap 61 |

---

## 10. IMPLEMENTATION READINESS CRITERIA

Nothing may be implemented until ALL items are checked.

### Architecture Readiness

- [ ] Phase 3 design scope reviewed (this document)
- [ ] Governance audit of Phase 3 design scope complete
- [ ] No authority expansion identified in any component

### Pre-Code Verification

- [ ] Phase 1 + Phase 2 test suites green (2911+ tests)
- [ ] Runtime fingerprint current
- [ ] Working tree clean
- [ ] Main branch up to date with origin

### Component-Level Readiness

- [ ] VoicePersonality interface agreed
- [ ] TrustPresenter interface agreed
- [ ] ProactiveBriefing interface agreed
- [ ] Snapshot-only rule understood for briefing inputs
- [ ] `requires_visual_confirmation` semantics agreed
- [ ] Receipt-preservation rule understood

### Governance Readiness

- [ ] Import boundary test list finalized
- [ ] No new capability IDs planned
- [ ] No new executors planned
- [ ] No authority expansion in any feature
- [ ] Voice confirmation clarity rule understood
- [ ] Trust escalation language checklist defined

---

## 11. NEXT ACTION

```
1. Run governance audit on this design scope
2. Address any findings
3. Check all readiness items
4. Write tests (tests first, then implementation)
5. Implement components
6. Run import boundary tests
7. Run Phase 3 simulation
8. Phase 3 completion report
```

The design scope preserves the rule that has survived
every prior phase:

```
Personality may increase initiative.
Personality may never increase authority.
```

No code until the governance audit clears this document.
