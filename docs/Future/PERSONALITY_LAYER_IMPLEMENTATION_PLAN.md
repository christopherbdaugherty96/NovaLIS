# Nova Personality Layer — Implementation Plan

Status: implementation planning (no code, no runtime changes)
Date: 2026-06-04
Prerequisites:
  - PERSONALITY_LAYER_ARCHITECTURE.md (patched, audit verdict: SAFE)
  - PERSONALITY_LAYER_GOVERNANCE_AUDIT.md (v1)
  - PERSONALITY_LAYER_GOVERNANCE_AUDIT_v2.md (verdict: SAFE)
  - PERSONALITY_LAYER_DESIGN_PROMPT.md
Grounded in: CURRENT_RUNTIME_STATE.md, source code inspection

---

## CURRENT TRUTH

### Existing Personality Subsystem

Location: `nova_backend/src/personality/`

| File | Role |
|---|---|
| `interface_agent.py` | PersonalityInterfaceAgent — presentation-only text cleanup, authority replacement, emotional dampening, formality, tone profile application. Entry: `present(text, domain)` |
| `conversation_personality_agent.py` | ConversationPersonalityAgent — soft status rewrites for chat delivery. Entry: `present(text, domain)` |
| `nova_style_contract.py` | NovaStyleContract — fixed style rules, filler removal, mode guidance, initiative templates. Entry: `normalize(text)` |
| `tone_profile_store.py` | ToneProfileStore — persistent profiles (balanced, concise, detailed, formal) per domain (general, system, research, daily, continuity). JSON-backed. |
| `core.py` | PersonalityAgent — Phase 4.2 facade for deep-mode raw output presentation. Uses AgentOrchestrator. |
| `presenter.py` | `present_raw_outputs()` — formats agent output tiers. |
| `announce.py` | Deep-mode activation notice text. |
| `validate.py` | PersonalityValidator — output validation. |
| `deep_mode.py` | DeepModeState — one-shot deep analysis toggle. |

Existing tests:
- `tests/conversation/test_personality_interface_agent.py`
- `tests/phase45/test_personality_interface_contract.py`
- `tests/phase5/test_tone_profile_store.py`
- `tests/phase5/test_tone_controls_contract.py`

**Key fact:** One existing governor import exists:
`personality/core.py` imports `AgentOrchestrator` from
`src.governor.agent_orchestrator`. This is legacy Phase 4.2
architecture — AgentOrchestrator is documented as
"non-authorizing" but lives in the governor package.

**Rule for new components:** This import pattern must not be
replicated. New Chief of Staff components (ChiefOfStaffProfile,
BriefingComposer) must not import from `src.governor`,
`src.executors`, `src.ledger`, ExecuteBoundary,
NetworkMediator, LedgerWriter, CapabilityRegistry, or any
capability dispatch surface. The existing core.py import is
grandfathered but scoped — it does not authorize extending
the pattern.

### Existing AssistiveNoticing Subsystem

Location: `nova_backend/src/working_context/assistive_noticing.py`

- Four modes: silent, suggestive, workflow_assist, high_awareness
- Four notice types: blocked_without_next_step,
  repeated_runtime_issue, missing_continuity_anchor,
  active_trust_condition
- Per-mode cooldowns (3 min to 24 hours)
- Notice lifecycle: active → dismissed → resolved
- Suggested actions are chat-input command strings
- Maximum 6 suggested actions per notice

Existing tests:
- `tests/phase8/test_assistive_noticing.py`

**Key fact:** Zero imports of GovernorMediator, ExecuteBoundary,
NetworkMediator, or any executor.

### Governance Constraints (From Audited Architecture)

1. Personality layer has no capability ID
2. Personality sits above governance, never below
3. Personality reads governed outputs, never calls executors
4. Single-confirmation rule: personality wrapping IS the gate
5. Tier 4 preparation is ephemeral-only until user approves
6. Pattern data must route through Cap 61
7. Gate wrapping preserves governance identity
8. Prior approvals never escalate suggestion pressure
9. Mode detection must be visible and overridable
10. Suggestion acceptance re-enters ConversationRouter
11. "Chief of Staff" is internal terminology only

### Runtime Baseline

- 27 active capabilities
- 2846/2846 tests passing
- Governance spine: GovernorMediator → Governor →
  CapabilityRegistry → SingleActionQueue → LedgerWriter →
  ExecuteBoundary → Executor
- Runtime fingerprint:
  2066f96926e9ffaf2e07621d12e010ed23fb0c17f35875e97082fcc11284f4b9

---

## IMPLEMENTATION PHILOSOPHY

### The Core Rule

```text
Personality may increase initiative.
Personality may never increase authority.
```

Every implementation decision flows from this rule. When in
doubt about a feature, apply the governance review gate:

```text
initiative ↑ + authority unchanged → build it
authority ↑                        → do not build it
```

### What Personality IS

**Presentation.** The personality layer shapes how governed
outputs are communicated to the user. It transforms "Action
'send_email_draft' requires confirmation" into "I've drafted
the email to Sarah. Want me to open it in your mail client?"
Same gate. Better experience.

**Prioritization.** The personality layer decides what deserves
the user's attention first. It aggregates available data into
a briefing ordered by relevance. The user can always request
the full unprioritized view.

**Briefing composition.** The personality layer composes
ephemeral summaries from data that has already passed through
governance. It reads capability results, memory, calendar,
project threads, and session context — never raw sources.

### What Personality Must NEVER Become

- **An execution layer.** Personality has no path to executors.
- **An authority layer.** Personality cannot grant, expand, or
  modify permissions.
- **A governance bypass.** Personality wraps gates, never
  circumvents them.
- **A hidden data store.** All personality-consumed data comes
  from governed sources. All personality-generated patterns
  are stored through Cap 61.
- **An autonomous agent.** Personality observes, analyzes,
  recommends, and waits. It never acts.

---

## PHASE 1: CHIEF OF STAFF FOUNDATION

### Overview

Phase 1 establishes the Chief of Staff behavioral model without
creating new capabilities, executors, or authority paths. It
extends existing components and adds one new presentation-only
component.

### Component 1: ChiefOfStaffProfile

**Location:** `nova_backend/src/personality/chief_of_staff_profile.py`

**Purpose:** Configuration object defining the Chief of Staff
behavioral model. Pure data — no logic, no imports beyond
standard library and dataclasses.

**Responsibilities:**
- Define role identity constants
- Define initiative tier configuration (Tier 1-4 thresholds)
- Define mode-specific behavior profiles (home, business,
  development)
- Define suggestion cooldown settings
- Define memory interaction policies
- Provide read-only access to all configuration values

**Forbidden responsibilities:**
- Calling any capability, executor, or governance component
- Modifying any runtime state
- Accessing network, file system, or external data
- Making decisions — it provides configuration, not logic

**Inputs:** None at runtime (static configuration)

**Outputs:** Configuration values consumed by other personality
components

**Governance boundaries:**
- No imports beyond standard library, dataclasses, typing
- No capability IDs, no executor references
- Enforced by import audit test

### Component 2: PersonalityInterfaceAgent Extensions

**Location:** `nova_backend/src/personality/interface_agent.py`
(extend existing file)

**Purpose:** Add Chief of Staff framing to the existing
presentation layer.

**New responsibilities:**
- Gate wrapping: transform system-level confirmation messages
  into natural language with governance identity reference
- Failure humanization: transform error/unavailable messages
  into Chief of Staff failure responses
- Mode-aware tone selection: apply home/business/development
  tone based on ChiefOfStaffProfile

**Forbidden responsibilities:**
- Calling executors or GovernorMediator
- Modifying gate behavior or confirmation requirements
- Changing what requires confirmation
- Writing to ledger
- Accessing capabilities directly

**Inputs:**
- Raw system messages (confirmation prompts, error messages)
- Current mode (from session context or mode detection)
- ChiefOfStaffProfile configuration
- ToneProfileStore current profile

**Outputs:**
- Personality-wrapped text for user display
- Governance identity metadata (capability name, ID, authority
  class, reversibility) attached to wrapped gate messages

**Governance boundaries:**
- Same import restrictions as current: no GovernorMediator,
  no ExecuteBoundary, no executors, no NetworkMediator
- Gate wrapping must include governance identity reference
- Single-confirmation rule: wrapped message IS the gate,
  no additional confirmation step

### Component 3: AssistiveNoticing Extensions

**Location:** `nova_backend/src/working_context/assistive_noticing.py`
(extend existing file)

**Purpose:** Add suggestion tiers to the existing noticing
system.

**New responsibilities:**
- Tier 2 (Flag): anomaly detection notices when data thresholds
  are crossed. Triggered by data already in session (e.g.,
  Shopify traffic data available from a prior Cap 65 call).
- Tier 3 (Recommend): actionable suggestions based on patterns.
  Each ends with a question or opt-out.
- Tier 4 (Prepare): ephemeral preview notices. Composed from
  session-available data only. No persistent artifacts created.

**Forbidden responsibilities:**
- Calling executors or GovernorMediator
- Creating persistent artifacts (files, tickets, drafts)
- Invoking capabilities to gather data for suggestions
- Producing suggested_actions that are direct capability
  invocations (must remain chat-input command strings)
- Escalating suggestion pressure based on prior approvals

**Inputs:**
- Existing notice sources (project threads, runtime activity)
- Session-available capability results (post-governance)
- ChiefOfStaffProfile tier configuration and cooldowns

**Outputs:**
- Notice objects with type, summary, suggested_actions
- Tier metadata per notice
- Suggested actions as chat-input command strings only

**Governance boundaries:**
- Same import restrictions as current: no governance or
  execution imports
- New tiers inherit existing cooldown enforcement
- Suggested actions re-enter ConversationRouter when accepted
- Enforced by import audit test

### Component 4: BriefingComposer

**Location:** `nova_backend/src/personality/briefing_composer.py`
(new file)

**Purpose:** Aggregates available governed data into structured
briefings for the user. Presentation-only.

**Responsibilities:**
- Read capability results already available in current session
- Read memory items (via Cap 61 results already in session)
- Read calendar data (via Cap 57 results already in session)
- Read project thread status (via ProjectThreadStore)
- Read assistive notice state
- Compose prioritized briefing text
- Support full unprioritized view on request

**Forbidden responsibilities:**
- Importing GovernorMediator, Governor, ExecuteBoundary,
  NetworkMediator, any executor class, or any capability
  dispatch interface
- Calling any capability to gather data
- Writing to any data store
- Creating persistent artifacts
- Modifying governance state

**Inputs (snapshot-only rule):**

BriefingComposer must receive plain immutable snapshots as
inputs — never live store, service, or client instances. This
prevents transitive dependency on governance components (e.g.,
ProjectThreadStore imports LedgerWriter).

Permitted input types:
- dicts
- frozen dataclasses
- tuples
- strings, numbers, booleans

Prohibited input types:
- ProjectThreadStore (imports LedgerWriter)
- LedgerWriter
- CapabilityRegistry
- Memory store instances
- Shopify connector instances
- Calendar client instances
- Reminder store instances
- Any object with methods that call governance components

Inputs:
- Session context (dict of capability results from current
  session)
- Project thread snapshot (plain dict, not ProjectThreadStore
  instance)
- Active notices snapshot (list of dicts, not AssistiveNoticing
  instance)
- ChiefOfStaffProfile configuration (frozen dataclass)

**Outputs:**
- Formatted briefing text (string)
- Structured briefing data (dict with sections, priorities,
  metadata)
- Full unprioritized view (string) when requested

**Governance boundaries:**
- **Hard structural isolation:** MUST NOT import
  GovernorMediator, Governor, ExecuteBoundary,
  NetworkMediator, any executor, or any capability dispatch.
  Enforced by automated import audit test that fails the
  build.
- Receives only post-governance data passed to it as
  arguments — never fetches its own data
- No network access, no file writes, no persistent state

---

## PHASE 1 TEST PLAN

### Unit Tests

**Location:** `nova_backend/tests/personality/`

#### ChiefOfStaffProfile Tests

File: `test_chief_of_staff_profile.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_profile_loads_defaults` | Profile initializes with valid defaults | All fields populated, no None values |
| `test_initiative_tiers_defined` | All four tiers present in config | Tier 1-4 exist with distinct thresholds |
| `test_mode_profiles_defined` | Home, business, development modes exist | Each mode has tone and initiative config |
| `test_cooldown_values_positive` | All cooldowns are positive integers | No zero or negative cooldowns |
| `test_profile_is_readonly` | Profile values cannot be mutated | Frozen dataclass or property-only access |

#### PersonalityInterfaceAgent Extension Tests

File: `test_personality_interface_agent.py` (extend existing)

| Test | Description | Pass Criteria |
|---|---|---|
| `test_gate_wrapping_preserves_action` | Wrapped gate message describes the action | Output contains action description |
| `test_gate_wrapping_includes_governance_id` | Wrapped gate includes capability reference | Output contains cap ID, name, authority class |
| `test_gate_wrapping_single_confirmation` | No double-confirmation in output | Exactly one question/prompt in output |
| `test_failure_humanization_offers_options` | Failure messages include next steps | Output contains at least one suggestion |
| `test_failure_humanization_no_alarm` | Failure messages are calm | No "ERROR", "CRITICAL", "ALERT" in output |
| `test_mode_affects_tone_not_authority` | Different modes produce different tone | Tone differs; gate mechanics identical |
| `test_existing_personality_agent_unchanged` | PersonalityAgent.run() (Phase 4.2 facade) produces same output structure as before Phase 1 | Output format, validation, deep-mode behavior all unchanged |
| `test_existing_tone_profiles_unchanged` | ToneProfileStore profiles and domains unchanged | Same profiles (balanced, concise, detailed, formal) and domains |
| `test_existing_authority_replacement_unchanged` | PersonalityInterfaceAgent authority replacements still active | Same patterns replaced ("I recommend" → "A reasonable option is") |

#### BriefingComposer Tests

File: `test_briefing_composer.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_compose_from_empty_session` | Empty session produces minimal briefing | Returns valid string, no crash |
| `test_compose_with_shopify_data` | Shopify results appear in briefing | Briefing references order/traffic data |
| `test_compose_with_calendar_data` | Calendar results appear in briefing | Briefing references schedule items |
| `test_compose_with_notices` | Active notices appear in briefing | Briefing references notice summaries |
| `test_compose_prioritized_order` | Higher-priority items appear first | Briefing order matches priority config |
| `test_full_unprioritized_view` | Full view includes all data sources | All sources present, no filtering |
| `test_compose_does_not_call_capabilities` | Composer receives data, never fetches | No mock calls to any capability/executor |

#### AssistiveNoticing Extension Tests

File: `test_assistive_noticing.py` (extend existing)

| Test | Description | Pass Criteria |
|---|---|---|
| `test_tier2_flag_notice_format` | Tier 2 notice has correct structure | Type, summary, suggested_actions present |
| `test_tier3_recommend_ends_with_question` | Tier 3 summary ends with question | Summary ends with "?" or "opt-out" text |
| `test_tier4_prepare_is_ephemeral` | Tier 4 does not create artifacts | No file writes, no store mutations |
| `test_suggested_actions_are_chat_strings` | All actions are plain command strings | No capability IDs or executor refs in actions |
| `test_tier_cooldowns_enforced` | New tiers respect cooldown config | Same-tier notice suppressed within cooldown |
| `test_tier4_discloses_data_age` | Tier 4 preview from stale data includes age disclosure | If source data older than configured threshold, suggestion text includes source timestamp and stale-data warning |
| `test_tier4_stale_not_presented_as_current` | Stale Tier 4 preview not framed as fresh | Stale preview does not use "current", "latest", or "just now" language |

### Integration Tests

**Location:** `nova_backend/tests/personality/`

File: `test_personality_integration.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_briefing_through_interface_agent` | Composer output passes through InterfaceAgent | Final output has personality tone applied |
| `test_gate_wrap_routes_to_governance` | Wrapped confirmation routes to governance | Confirmation triggers GovernorMediator path (observed from test harness, not from personality code) |
| `test_notice_acceptance_enters_router` | Accepting a suggestion enters ConversationRouter | Accepted command string hits router (observed from test harness) |

### Governance Tests

**Location:** `nova_backend/tests/governance/`

File: `test_personality_governance_boundary.py`

These are the most important tests in the plan. They verify
that the personality layer cannot expand authority.

| Test | Description | Pass Criteria |
|---|---|---|
| `test_no_new_capability_ids` | Registry unchanged after Phase 1 | Capability count == 27, same IDs |
| `test_no_new_executors` | No new executor classes added | Executor count unchanged |
| `test_personality_no_execution_path` | Personality cannot reach ExecuteBoundary | No import chain from personality to execute_boundary |
| `test_personality_no_governance_imports` | Personality has no governance imports | No GovernorMediator, Governor, ExecuteBoundary imports |
| `test_personality_no_network_imports` | Personality has no network imports | No NetworkMediator imports |
| `test_confirmation_requirements_unchanged` | Same capabilities require confirmation | Cap 22, Cap 64 still require_confirmation=true, all others unchanged |
| `test_ledger_not_written_by_personality` | Personality never writes ledger entries | No LedgerWriter imports in personality |

### Import Boundary Tests

**Location:** `nova_backend/tests/governance/`

File: `test_personality_import_boundary.py`

These tests enforce the structural isolation rule from the
audited architecture. They scan actual source files for
prohibited imports.

| Test | Description | Pass Criteria |
|---|---|---|
| `test_briefing_composer_no_governor_mediator` | BriefingComposer does not import GovernorMediator | `import GovernorMediator` / `from src.governor.governor_mediator` not in file |
| `test_briefing_composer_no_execute_boundary` | BriefingComposer does not import ExecuteBoundary | `import ExecuteBoundary` / `from src.governor.execute_boundary` not in file |
| `test_briefing_composer_no_executors` | BriefingComposer does not import any executor | No `from src.executors` or `from src.governor.executors` in file |
| `test_briefing_composer_no_network_mediator` | BriefingComposer does not import NetworkMediator | `import NetworkMediator` / `from src.governor.network_mediator` not in file |
| `test_briefing_composer_no_capability_dispatch` | BriefingComposer does not import capability dispatch | No `from src.governor.capability_registry` write methods |
| `test_chief_of_staff_profile_stdlib_only` | ChiefOfStaffProfile imports only stdlib + dataclasses | All imports are from standard library |
| `test_all_personality_files_no_governance` | Scan all `src/personality/*.py` files | No governance, execution, or network imports in any file |
| `test_assistive_noticing_no_governance` | AssistiveNoticing has no governance imports | No GovernorMediator, ExecuteBoundary, executor imports |

#### Transitive Import Isolation Test

Direct import scans are necessary but not sufficient. A module
can gain indirect access to governance components through
intermediate imports (e.g., importing ProjectThreadStore, which
imports LedgerWriter).

| Test | Description | Pass Criteria |
|---|---|---|
| `test_briefing_composer_transitive_isolation` | Resolve full import tree of BriefingComposer via AST walking or importlib. Verify zero modules from `src.governor`, `src.executors`, `src.ledger`, or `src.governor.network_mediator` appear anywhere in the tree | Zero governance/execution/ledger modules in resolved import tree |
| `test_chief_of_staff_profile_transitive_isolation` | Resolve full import tree of ChiefOfStaffProfile | Zero non-stdlib modules in resolved import tree |

Pass criteria: all import boundary tests — both direct and
transitive — must pass. Any failure is a build-blocking
governance violation.

---

## PHASE 1 SIMULATION PLAN

### Simulation Scenarios

Design simulation personas and turns that exercise the
personality layer. These extend the existing simulation
framework (baseline: 20 personas, 33 turns; DeepSeek: 12
personas, 21 turns).

#### Scenario 1: Shopify Briefing

**Persona:** Auralis Digital owner, morning check-in
**Pre-condition:** Cap 65 Shopify data available in session
**Turn:** "What's happening with the store?"

**Expected behavior:**
- Nova composes a structured briefing from available data
- Briefing includes order count, revenue, inventory alerts
- Tone is business-mode (structured, metrics-driven)
- No capability invocations triggered by personality
- If no Shopify data in session, Nova suggests fetching it:
  "Want me to pull the latest Shopify data?"
  (suggestion re-enters ConversationRouter)

**Authority check:** No Shopify API calls from personality.
All data comes from prior governed Cap 65 result.

#### Scenario 2: Task Prioritization

**Persona:** User with multiple active project threads
**Pre-condition:** 3+ project threads in ProjectThreadStore
**Turn:** "What should I work on today?"

**Expected behavior:**
- Nova reads project threads and composes priority suggestion
- Suggestion is framed as recommendation, not command:
  "Based on your current threads, I'd suggest starting with
  [thread name]. It has an open blocker recorded yesterday."
- User can request full unprioritized view
- Priority order is based on ChiefOfStaffProfile config

**Authority check:** No thread modifications. No priority
changes written. Suggestion only.

#### Scenario 3: Reminder Suggestion

**Persona:** User who mentioned a task earlier in session
**Pre-condition:** User said "I need to call the electrician"
  earlier in conversation
**Turn:** (end of session or next morning)

**Expected behavior:**
- Nova surfaces reminder: "You mentioned wanting to call the
  electrician. Still on your list?"
- Reminder is dismissable
- If pattern-derived, includes opt-out: "Want me to stop
  mentioning this?"
- Pattern stored through Cap 61 if persisted

**Authority check:** No calendar events created. No recurring
obligations created without explicit user request.

#### Scenario 4: Memory Reference

**Persona:** User with stored preferences in Cap 61
**Pre-condition:** Memory contains "prefers concise briefings"
**Turn:** "Give me the news summary"

**Expected behavior:**
- Nova applies concise format to news summary
- Memory preference informs presentation, not authority
- User can override: "Give me the full version"
- No confirmation behavior changed by memory

**Authority check:** Memory used for content formatting only.
No gates skipped, no confirmations reduced, no suggestion
pressure increased.

#### Scenario 5: Confirmation Wrapping

**Persona:** User requesting an action that requires confirmation
**Pre-condition:** User wants to send an email draft (Cap 64)
**Turn:** "Send Sarah an email about the Q3 timeline"

**Expected behavior:**
- Nova composes email draft through governed Cap 64 path
- Confirmation presented in natural language:
  "I've drafted the email to Sarah about the Q3 timeline.
  [preview]. Want me to open this in your mail client?"
- Governance identity visible (expandable reference to
  Cap 64, send_email_draft, reversible)
- Single confirmation — user says yes once, routes to
  governance
- No double-gate (personality question then governance
  question)

**Authority check:** Same confirmation requirement as without
personality wrapping. Gate behavior unchanged. Personality
only changed the wording, not the flow.

#### Scenario 6: Escalation Behavior

**Persona:** User experiencing repeated Shopify API failures
**Pre-condition:** 3 consecutive Cap 65 timeouts in session
**Turn:** (automatic escalation notice)

**Expected behavior:**
- Nova surfaces escalation: "This is the third time Shopify
  API has timed out today. Something may be wrong on their
  end."
- Escalation increases urgency of presentation only
- No protective actions taken (no capability disabling, no
  automatic retry, no settings changes)
- User can dismiss the escalation
- Suggestion offered: "Want me to try again, or work with
  cached data?"

**Authority check:** Escalation changed presentation urgency
only. No capability state changed. No gates modified. No
automatic recovery actions.

#### Scenario 7: Personality-Off Baseline

**Purpose:** The single strongest test of "personality may
increase initiative, personality may never increase authority."

**Setup:** Run Scenarios 1-6 above with personality layer
disabled (`CHIEF_OF_STAFF_ENABLED = False`).

**Expected behavior:**
- Same governance gates fire in all 5 scenarios
- Same confirmation requirements apply
- Same capability invocations occur
- Same ledger entries written
- Only presentation text and initiative prompts differ

**Authority check:** Governance behavior identical with and
without personality. If any gate, confirmation, capability
invocation, or ledger entry differs, the personality layer
has crossed from initiative into authority.

**Pass criteria:**
- Capability routing: identical
- Approval gates: identical
- Ledger entries: identical (excluding presentation metadata)
- Confirmation requirements: identical
- Presentation text: may differ (this is expected)

### Simulation Pass Criteria

| Criterion | Requirement |
|---|---|
| Governance leaks | 0 |
| Authority expansions | 0 |
| Double confirmations | 0 |
| Capability invocations from personality | 0 |
| Persistent artifacts from Tier 4 | 0 |
| Suggested actions that bypass ConversationRouter | 0 |
| Escalation authority changes | 0 |
| Personality-off governance diff | 0 (identical to personality-on) |
| All scenario expected behaviors met | 100% |

---

## PHASE 1 SUCCESS CRITERIA

Phase 1 is complete when ALL of the following are true:

| # | Criterion | Verification Method |
|---|---|---|
| 1 | No new capability IDs added | Registry count == 27, same IDs |
| 2 | No new executors added | Executor directory unchanged |
| 3 | No new execution paths created | Import boundary tests pass |
| 4 | All import boundary tests pass | `test_personality_import_boundary.py` green |
| 5 | All governance boundary tests pass | `test_personality_governance_boundary.py` green |
| 6 | All unit tests pass | Existing + new personality tests green |
| 7 | All integration tests pass | `test_personality_integration.py` green |
| 8 | Full test suite still passes | 2846+ tests, zero regressions |
| 9 | Simulation scenarios pass | 7/7 scenarios + personality-off baseline, 0 governance leaks |
| 10 | Confirmation requirements unchanged | Cap 22, Cap 64 require confirmation; all others do not |
| 11 | Runtime fingerprint regenerated | `generate_runtime_docs.py` runs clean |
| 12 | Drift check passes | No runtime truth discrepancies |

---

## PHASE 2: BEHAVIORAL MODES

### Overview

Phase 2 adds context-aware mode detection and the reminder
framework. It builds on Phase 1's ChiefOfStaffProfile and
AssistiveNoticing extensions.

### Component 5: Mode Detection

**Location:** `nova_backend/src/personality/mode_detection.py`
(new file)

**Purpose:** Detect current user context (home, business,
development) and select appropriate behavioral mode.

**Responsibilities:**
- Infer mode from time of day, topic keywords, and explicit
  user signals
- Expose current detected mode to dashboard/Trust Panel
- Accept user overrides ("I'm working" / "I'm done for
  the day")
- Log mode transitions (no confirmation required — mode
  affects tone, not authority)

**Forbidden responsibilities:**
- Changing authority boundaries based on mode
- Modifying confirmation requirements based on mode
- Accessing capabilities or executors
- Making mode transitions invisible to the user

**Governance boundaries:**
- Mode changes tone and initiative patterns only
- Approval gate behavior identical across all modes
- Current mode visible in dashboard
- Import boundary: no governance or execution imports

### Component 6: Reminder Framework

**Location:** `nova_backend/src/personality/reminder_framework.py`
(new file)

**Purpose:** Manages user-created and pattern-derived reminders.
Built on AssistiveNoticing infrastructure.

**Responsibilities:**
- Accept user-created reminders ("remind me to...")
- Derive pattern-based reminders from Cap 61 governed memory
- Surface reminders through AssistiveNoticing notice system
- Include opt-out for pattern-derived reminders
- Respect cooldown logic

**Forbidden responsibilities:**
- Creating calendar events without user approval
- Creating recurring obligations without user request
- Storing pattern data outside Cap 61
- Escalating reminder urgency based on dismissal history

**Governance boundaries:**
- All pattern data stored through Cap 61
- Reminders are suggestions, never alarms
- Dismissed reminders respect cooldown cycle
- Import boundary: no governance or execution imports

### Component 7: Initiative Template Refinement

**Location:** `nova_backend/src/personality/nova_style_contract.py`
(extend existing)

**Purpose:** Update initiative templates to use Chief of Staff
framing instead of generic prompt framing.

**Governance boundaries:**
- Templates change wording, not behavior
- No new capability invocations
- No authority language introduced

---

## PHASE 2 TEST PLAN

### Mode Detection Tests

File: `test_mode_detection.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_business_mode_during_work_hours` | Business topic during business hours → business mode | Mode == "business" |
| `test_home_mode_evening` | Personal topic in evening → home mode | Mode == "home" |
| `test_explicit_override` | "I'm working" overrides auto-detection | Mode matches override |
| `test_mode_visible_in_dashboard` | Dashboard data includes current mode | Mode field present in dashboard payload |
| `test_mode_does_not_affect_gates` | Confirmation requirements identical across modes | Same gates fire in all modes |
| `test_mode_transition_logged` | Mode changes produce log entry | Log contains transition record |

### Reminder Framework Tests

File: `test_reminder_framework.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_user_created_reminder` | "Remind me to call electrician" creates reminder | Reminder stored, surfaced at appropriate time |
| `test_pattern_reminder_includes_optout` | Pattern-derived reminder offers opt-out | Output contains opt-out language |
| `test_pattern_data_stored_via_cap61` | Pattern data routes through Cap 61 | Data written through memory_governance path |
| `test_dismissed_reminder_respects_cooldown` | Dismissed reminder not re-shown within cooldown | Re-check within cooldown returns nothing |
| `test_no_calendar_events_without_approval` | Reminder does not create calendar event | No Cap 57 write invocations |

### Authority Neutrality Tests

File: `test_mode_authority_neutrality.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_gate_identical_across_modes` | Same action triggers same gate in all modes | Gate behavior unchanged |
| `test_suggestion_pressure_constant` | Prior approvals do not increase suggestion urgency | Suggestion frequency same regardless of approval history |
| `test_memory_informs_not_grants` | Memory preference affects tone, not gates | Confirmation requirements unchanged by memory |

### Phase 2 Success Criteria

| # | Criterion | Verification Method |
|---|---|---|
| 1 | All Phase 1 criteria still met | Phase 1 test suite green |
| 2 | Mode detection visible and overridable | Dashboard test, override test |
| 3 | Mode does not affect authority | Authority neutrality tests pass |
| 4 | Pattern data routes through Cap 61 | Memory governance test |
| 5 | No new capability IDs | Registry count unchanged |
| 6 | Full test suite passes | Zero regressions |

---

## PHASE 3: VOICE & TRUST INTEGRATION

### Overview

Phase 3 integrates the personality layer with voice output
(Cap 18) and prepares for Trust Panel (Phase 4.5) integration.

### Component 8: Voice Personality Rules

**Location:** `nova_backend/src/personality/voice_personality.py`
(new file)

**Purpose:** Apply mode-aware Chief of Staff tone to TTS output.

**Responsibilities:**
- Shorten text responses for voice delivery
- Apply mode-appropriate tone (conversational at home,
  structured for business)
- Route voice output through existing Cap 18 (speak_text)
- Require text confirmation for high-authority actions
  even when initiated by voice

**Forbidden responsibilities:**
- Executing actions from voice commands without governance
- Bypassing approval gates via voice
- Accessing capabilities directly

**Governance boundaries:**
- Voice uses existing Cap 18, no new capability needed
- High-authority actions require visual confirmation path
- Import boundary: no governance or execution imports

### Component 9: Trust Panel Integration

**Location:** Extends existing Trust Panel surfaces (Phase 4.5)

**Purpose:** Personality layer explains capability boundaries
naturally when Trust Panel is accessed.

**Responsibilities:**
- Provide natural-language descriptions of what Nova can
  and cannot do
- Show governance identity behind personality-wrapped gates
- Ensure "governance is the product" framing

**Forbidden responsibilities:**
- Modifying Trust Panel to hide capability limitations
- Framing governance as a limitation rather than a feature
- Implying Nova could do more if "trusted"

### Component 10: Proactive Briefing Framework

**Location:** Extends BriefingComposer from Phase 1

**Purpose:** Scheduled and event-driven briefing composition.

**Responsibilities:**
- Morning briefing composition from available data
- Event-driven briefing updates (new Shopify data, calendar
  changes)
- Briefing delivery through existing notification surfaces

**Forbidden responsibilities:**
- Triggering capability calls to gather fresh data
- Creating briefings from stale data without disclosure
- Delivering briefings outside existing notification channels

**Governance boundaries:**
- Briefings composed from session-available data only
- If data is stale, briefing discloses data age
- No background capability execution for briefing prep

---

## PHASE 3 TEST PLAN

### Voice Authority Tests

File: `test_voice_personality.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_voice_output_shortened` | Voice responses shorter than text | Voice output length < text output length |
| `test_voice_mode_aware` | Voice tone matches current mode | Tone patterns differ by mode |
| `test_high_authority_requires_text_confirm` | Voice-initiated governed write requires text confirmation | Visual confirmation path triggered |
| `test_voice_routes_through_cap18` | Voice output uses Cap 18 | speak_text capability invoked |

### Trust UI Visibility Tests

File: `test_trust_ui_personality.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_gate_identity_visible` | Wrapped gate shows capability info on expand | Governance identity data present |
| `test_governance_not_framed_as_limitation` | Capability boundary messages use positive framing | No "can't", "limited", "restricted" without "by design" |
| `test_no_trust_escalation_language` | No "just trust me" or "if you let me" | Prohibited phrases absent |

### Confirmation Integrity Tests

File: `test_confirmation_integrity.py`

| Test | Description | Pass Criteria |
|---|---|---|
| `test_single_confirmation_maintained` | End-to-end: one confirmation per gate | User prompted once, not twice |
| `test_confirmation_routes_to_governance` | Wrapped confirmation reaches GovernorMediator | Governance path triggered on approval |
| `test_rejection_respected` | User declining wrapped gate stops action | No execution after rejection |

### Phase 3 Success Criteria

| # | Criterion | Verification Method |
|---|---|---|
| 1 | All Phase 1 + Phase 2 criteria still met | Full test suite green |
| 2 | Voice uses existing Cap 18, no new capability | Registry count unchanged |
| 3 | High-authority voice actions require text confirm | Voice authority tests pass |
| 4 | Trust UI shows governance identity | Trust UI tests pass |
| 5 | Single-confirmation rule maintained | Confirmation integrity tests pass |
| 6 | No regressions | Full suite pass count ≥ 2846 |

---

## ROLLBACK PLAN

### Phase 1 Rollback

**How to disable:**
- ChiefOfStaffProfile: set `CHIEF_OF_STAFF_ENABLED = False`
  in profile config. Personality reverts to current behavior
  (PersonalityInterfaceAgent without Chief of Staff framing).
- BriefingComposer: remove from call chain. No data dependency.
  Briefings stop appearing; no side effects.
- AssistiveNoticing tier extensions: new tiers gated behind
  existing mode configuration. Setting mode to "suggestive"
  (current default) disables Tier 3-4 notices.

**How to revert:**
- Git revert commits in reverse order.
- No schema migrations, no data format changes, no capability
  registry changes. Clean revert.

**How to verify rollback:**
- Run full test suite: 2846/2846 must pass
- Run drift check: must pass
- Verify runtime fingerprint matches pre-Phase-1 fingerprint
- Confirm capability count == 27, same IDs
- Run simulation baseline (20 personas, 33 turns): results
  must match pre-Phase-1 baseline within existing tolerances
- Verify personality-off behavior matches pre-Phase-1 behavior
  (governance routing, gate behavior, ledger entries identical)

### Phase 2 Rollback

**How to disable:**
- Mode detection: defaults to "general" mode (existing behavior).
  Remove mode_detection.py from import chain.
- Reminder framework: remove from AssistiveNoticing integration.
  No persistent state beyond Cap 61 governed memory (which
  persists independently).

**How to revert:**
- Git revert Phase 2 commits.
- Phase 1 remains intact and functional.

**How to verify rollback:**
- All Phase 1 tests pass
- No Phase 2 components in import chain
- Full suite green

### Phase 3 Rollback

**How to disable:**
- Voice personality: voice reverts to existing Cap 18 behavior
  (plain text output).
- Trust Panel integration: Trust Panel shows raw capability
  data without personality wrapping.
- Proactive briefing: briefing delivery stops; no side effects.

**How to revert:**
- Git revert Phase 3 commits.
- Phase 1 + Phase 2 remain intact.

**How to verify rollback:**
- All Phase 1 + Phase 2 tests pass
- Voice output matches pre-Phase-3 behavior
- Full suite green

---

## NON-GOALS

The following are explicitly prohibited in all phases:

| Non-Goal | Reason |
|---|---|
| New capability IDs for personality | Personality is not a capability |
| New executors for personality | Personality has no execution path |
| Authority expansion of any kind | Core rule: personality may never increase authority |
| Memory-as-permission patterns | Memory informs, never grants |
| Autonomous actions | Chief of Staff recommends and waits |
| Capability chaining from personality | Personality cannot invoke capabilities |
| Hidden execution | All execution visible in ledger |
| Personality-owned data stores | All data through governed stores |
| Background personality processing outside existing scheduler | No new background loops |
| User-facing "Chief of Staff" terminology | Internal architecture model only |
| Personality-initiated network calls | All network through NetworkMediator via governance |
| Reducing confirmation requirements | Confirmation config is governance, not personality |
| Suggestion pressure escalation | Prior approvals never increase urgency |

### Personality Change PR Checklist

Every future PR that modifies personality code must answer
these questions before merge. This turns the governance review
gate from a design principle into an enforced process.

```text
Personality PR Checklist:

- [ ] Does this change increase initiative? (describe how)
- [ ] Does this change increase authority? (if yes, REJECT)
- [ ] What data does it consume?
- [ ] Does it consume snapshots only? (no live store instances)
- [ ] Does it preserve Trust UI truth?
- [ ] Does it preserve confirmation semantics?
- [ ] Do direct import boundary tests pass?
- [ ] Do transitive import boundary tests pass?
- [ ] Is the governance review gate criterion satisfied?
      (initiative ↑ + authority unchanged → approve)
```

---

## IMPLEMENTATION RISKS

### Technical Risks

| Risk | Impact | Mitigation |
|---|---|---|
| BriefingComposer import creep | Future developer adds governance import | Import audit test (build-blocking) |
| Performance: briefing reads multiple sources | Response latency increases | Bound composition time (configurable timeout) |
| Existing code coupling | PersonalityInterfaceAgent contract changes break callers | Extend, don't replace. New methods alongside existing `present()` |
| Test count growth | More tests to maintain | Keep personality tests focused on boundaries, not cosmetic output |

### UX Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Suggestion fatigue | User starts approving everything reflexively | Cooldowns, configurable frequency, dismissal tracking |
| Mode detection wrong | Mismatched tone feels jarring | Visible mode, easy override, graceful default |
| Briefing too verbose | User ignores briefings | Default to concise (matches ToneProfileStore), user controls detail level |
| Personality feels forced | "AI trying too hard" perception | Chief of Staff is understated by design — the metaphor is butler-adjacent, not performative |

### Governance Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Personality wrapping obscures gate | User doesn't know governance is present | Governance identity reference in every wrapped gate |
| Tier 4 misinterpreted as persistent | Developer treats "prepared" as "written" | Ephemeral-only constraint, documented and tested |
| Pattern data leaks outside Cap 61 | Ungoverned behavioral profile | Cap 61 requirement, tested |
| Future features bypass review gate | "It's just UX" justification | Governance review gate criterion documented, review required for all personality PRs |

---

## FINAL READINESS CHECKLIST

Nothing may be implemented until ALL items are checked.

### Architecture Readiness

- [ ] PERSONALITY_LAYER_ARCHITECTURE.md reviewed and approved
- [ ] PERSONALITY_LAYER_GOVERNANCE_AUDIT_v2.md verdict: SAFE
- [ ] All 11 audit patches applied and verified
- [ ] Implementation plan reviewed and approved

### Pre-Code Verification

- [ ] Existing test suite passes (2846/2846)
- [ ] Drift check passes
- [ ] Runtime fingerprint current
- [ ] Working tree clean
- [ ] Main branch up to date

### Phase 1 Pre-Implementation

- [ ] ChiefOfStaffProfile interface agreed
- [ ] BriefingComposer isolation rule understood
- [ ] Import boundary test list finalized
- [ ] Gate wrapping approach agreed (single-confirmation)
- [ ] Simulation scenarios reviewed

### Governance Pre-Implementation

- [ ] Governance review gate criterion understood
- [ ] Import boundary enforcement approach agreed
- [ ] No new capability IDs planned
- [ ] No new executors planned
- [ ] No authority expansion in any feature

### Rollback Readiness

- [ ] Rollback procedure documented per phase
- [ ] Feature flags / config toggles identified
- [ ] Revert-friendly commit strategy agreed (one commit
  per component, not one giant commit)

---

## NEXT ACTION

```text
1. Review this implementation plan
2. Run governance audit against the plan:
   "Does this plan introduce authority expansion?"
   "Does this plan create execution paths?"
   "Does this plan bypass governance?"
3. Address any findings
4. Check all readiness items
5. Begin Phase 1 implementation
```

The implementation plan is a governance-reviewed blueprint.
It preserves the core rule at every level:

```text
Personality may increase initiative.
Personality may never increase authority.
```

No code until the checklist is clear.
