# Personality Live Wiring — Design Scope

Status: design (no code, no runtime changes)
Date: 2026-06-05
Prerequisite: Phase 3 complete (1f267b0)
Governing rule: initiative ↑, authority unchanged

---

## 1. CURRENT TRUTH

### Personality Stack (Complete, Isolated)

| Phase | Components | Tests | Simulation |
|---|---|---|---|
| Phase 1 | ChiefOfStaffProfile, BriefingComposer, wrap_gate, humanize_failure, present_with_mode, tiers 2-4 | 57 | 28 |
| Phase 2 | ModeDetector, ReminderFramework, mode-aware templates | 59 | 38 |
| Phase 3 | VoicePersonality, TrustPresenter, ProactiveBriefing | 50 | 22 |
| **Total** | **10 components** | **187** | **88** |

### Live Session Integration Points (Current Code)

**Failure messages** — scattered "currently unavailable" strings:

```
session_handler.py:1089  "News is currently unavailable."
session_handler.py:1174  "Weather is currently unavailable."
session_handler.py:2265  "Phase 4.2 analysis is currently unavailable."
session_handler.py:2326  "Calendar is currently unavailable."
session_handler.py:2381  "System diagnostics are currently unavailable."
```

These are raw system messages. `humanize_failure()` exists but
is not called.

**Gate wrapping** — raw confirmation prompts:

```
session_handler.py:3608  "Open {resource}?\n"
                         "This action needs confirmation.\n"
                         "Reply 'yes' to proceed or 'no' to cancel."

session_handler.py:3628  "I'll draft this email and open it...\n"
                         "Reply 'yes' to proceed or 'no' to cancel."
```

These are hand-written. `wrap_gate()` exists but is not called.

**Trust center** — raw data rendering:

```
brain_server.py:1698  _render_trust_center_message()
```

Renders raw trust status data. `TrustPresenter` exists but is
not called.

### Runtime Baseline

```
Capabilities: 27
Executors: 22
Fast suite: 2983 passing
Working tree: clean (only _MOCs overlays)
origin/main: 1f267b0
```

---

## 2. WIRING GOALS

Connect three existing personality components to the live
session path:

```
A. Failure humanization → replace raw "unavailable" strings
B. Gate wrapping → replace hand-written confirmation prompts
C. TrustPresenter → accompany trust center rendering
```

### What Wiring Changes

- User sees personality-wrapped text instead of raw system text
- Governance identity visible in wrapped gates
- Trust descriptions accompany raw data

### What Wiring Does NOT Change

- Routing logic (same ConversationRouter decisions)
- Capability dispatch (same GovernorMediator paths)
- Approval requirements (same confirmation gates)
- Ledger entries (same events logged)
- Execution semantics (same executors called)
- Capability count (27)
- Executor count (22)

---

## 3. COMPONENT A — FAILURE HUMANIZATION WIRING

### Current State

Raw string literals scattered across `session_handler.py`:

```python
await send_chat_message(ws, "News is currently unavailable.")
await send_chat_message(ws, "Weather is currently unavailable.")
await send_chat_message(ws, "Calendar is currently unavailable.")
```

### Proposed Change

Create a helper function in the session handler that calls
`humanize_failure()`:

```python
def _personality_failure_message(
    raw_message: str,
    *,
    personality_agent: PersonalityInterfaceAgent,
    profile: ChiefOfStaffProfile,
) -> str:
    return personality_agent.humanize_failure(
        raw_message, profile=profile,
    )
```

Replace each raw string with a call to this helper. The helper
is a pure function — it takes a string, returns a string. No
routing change. No capability invocation.

### Integration Points

| Line | Current | After |
|---|---|---|
| ~1089 | `"News is currently unavailable."` | `_personality_failure_message("News capability unavailable", ...)` |
| ~1174 | `"Weather is currently unavailable."` | `_personality_failure_message("Weather capability unavailable", ...)` |
| ~2265 | `"Phase 4.2 analysis is currently unavailable."` | `_personality_failure_message("Analysis unavailable", ...)` |
| ~2326 | `"Calendar is currently unavailable."` | `_personality_failure_message("Calendar unavailable", ...)` |
| ~2381 | `"System diagnostics are currently unavailable."` | `_personality_failure_message("Diagnostics unavailable", ...)` |

### Governance Impact

- Routing: unchanged (failure message is post-routing)
- Capability dispatch: unchanged (failure is already a failed path)
- Approval: not applicable (failures don't require approval)
- Ledger: unchanged (failure events already logged before message)
- Execution: unchanged (nothing executes on failure path)

---

## 4. COMPONENT B — GATE WRAPPING WIRING

### Current State

Hand-written confirmation prompts in `session_handler.py`:

```python
# Cap 22
await send_chat_message(ws, (
    f"Open {resource}?\n"
    "This action needs confirmation.\n"
    "Reply 'yes' to proceed or 'no' to cancel."
))

# Cap 64
await send_chat_message(ws, (
    f"I'll draft this email...\n"
    "Reply 'yes' to proceed or 'no' to cancel."
))
```

### Proposed Change

Replace the hand-written text with `wrap_gate()`:

```python
# Cap 22
wrapped = personality_agent.wrap_gate(
    action_description=f"Open {resource}",
    cap_name="open_file_folder",
    cap_id=22,
    authority_class="local_write",
    profile=profile,
)
await send_chat_message(ws, wrapped)

# Cap 64
wrapped = personality_agent.wrap_gate(
    action_description=f"Draft email to {to} about {subject}",
    cap_name="send_email_draft",
    cap_id=64,
    authority_class="local_write",
    profile=profile,
)
await send_chat_message(ws, wrapped)
```

### Critical Constraint: Single-Confirmation Rule

`wrap_gate()` produces text ending with exactly one question.
The session handler's existing `pending_governed_confirm` state
machine is unchanged. The user replies "yes" or "no" as before.
The wrapped text replaces the prompt string — not the
confirmation logic.

### What Must Not Change

- `session_state["pending_governed_confirm"]` still set
- `pending_confirmation_resolution_action()` still works
- "yes" routes to `invoke_governed_capability()`
- "no" cancels the pending action
- Ledger events: `ACTION_ATTEMPTED`, `ACTION_COMPLETED` unchanged

### Governance Impact

- Routing: unchanged (gate is already triggered)
- Capability dispatch: unchanged (same cap ID, same params)
- Approval: unchanged (same yes/no → same governance path)
- Ledger: unchanged (same events logged on approve/cancel)
- Execution: unchanged (same executor called on approve)

---

## 5. COMPONENT C — TRUSTPRESENTER WIRING

### Current State

`_render_trust_center_message()` in `brain_server.py` renders
raw trust status data as formatted text.

### Proposed Change

Add TrustPresenter descriptions alongside existing raw data:

```python
def _render_trust_center_message(trust_status):
    # ... existing raw rendering unchanged ...

    # Add personality descriptions for blocked conditions
    from src.personality.trust_presenter import TrustPresenter
    presenter = TrustPresenter()
    for item in blocked:
        explanation = presenter.explain_boundary(
            action_description=item.get("label", ""),
            reason=item.get("reason", ""),
        )
        # Append explanation to the existing rendered line
```

### Critical Constraint: Accompany, Never Replace

The raw trust data (`mode`, `last_external_call`, `data_egress`,
`failure_state`, `recent_runtime_activity`, `blocked_conditions`)
must remain visible in the output. TrustPresenter adds a
natural-language line alongside each item — it does not
replace the structured data.

### Governance Impact

- Routing: not applicable (trust center is a read-only view)
- Capability dispatch: not applicable
- Approval: not applicable
- Ledger: not applicable (trust center reads ledger, never writes)
- Execution: not applicable
- Receipt data: unchanged (raw receipts from `/api/trust/receipts`
  are not touched by this wiring)

---

## 6. DATA FLOW DIAGRAMS

### Failure Humanization Flow

```
Capability fails
    ↓
session_handler catches failure
    ↓
session_handler builds raw failure string (unchanged)
    ↓
_personality_failure_message(raw_string)   ← NEW
    ↓
humanize_failure() returns calm text
    ↓
send_chat_message(ws, calm_text)
```

No new data enters the pipeline. The raw failure string is the
only input. The humanized string is the only output.

### Gate Wrapping Flow

```
GovernorMediator parses invocation (unchanged)
    ↓
session_handler detects confirmation-required cap (unchanged)
    ↓
session_handler sets pending_governed_confirm (unchanged)
    ↓
wrap_gate(action_desc, cap_name, cap_id, authority_class)  ← NEW
    ↓
send_chat_message(ws, wrapped_text)
    ↓
User replies yes/no (unchanged)
    ↓
invoke_governed_capability() or cancel (unchanged)
```

Gate wrapping replaces the prompt string. Nothing else changes.
The confirmation state machine is untouched.

### TrustPresenter Flow

```
User requests "trust center" (unchanged)
    ↓
_render_trust_center_message(trust_status) (unchanged)
    ↓
TrustPresenter.explain_boundary() for blocked items  ← NEW
    ↓
Explanation appended to existing rendered lines
    ↓
send_chat_message(ws, trust_text)
```

Raw data still rendered. Explanation added alongside.

---

## 7. GOVERNANCE BOUNDARIES

| Wiring | Touches session_handler.py | Touches brain_server.py | Touches governance | Touches routing | Touches ledger |
|---|---|---|---|---|---|
| Failure humanization | Yes (string replacement) | No | No | No | No |
| Gate wrapping | Yes (string replacement) | No | No | No | No |
| TrustPresenter | No | Yes (additive line) | No | No | No |

### Cross-Wiring Rules

1. No new imports of GovernorMediator, ExecuteBoundary,
   NetworkMediator, or LedgerWriter in personality code
2. Personality components receive strings, return strings
3. No capability invocations from personality wiring
4. No new `await` calls that contact external services
5. No modification of `session_state["pending_governed_confirm"]`
   structure
6. No modification of confirmation resolution logic
7. No modification of ledger event types or payloads
8. `wrap_gate()` output includes governance identity footer

---

## 8. IMPORT BOUNDARIES

### New Imports in session_handler.py

```python
from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
```

These are presentation-only components with verified import
isolation (12 boundary tests + transitive scans).

### New Import in brain_server.py

```python
from src.personality.trust_presenter import TrustPresenter
```

Presentation-only. Verified by import boundary tests.

### No New Imports

- No imports of GovernorMediator, ExecuteBoundary,
  NetworkMediator, or LedgerWriter added by wiring
- No imports of capability dispatch surfaces
- No imports of executor classes

---

## 9. TEST STRATEGY

### Wiring Tests (New)

File: `tests/personality/test_personality_wiring.py`

| Test | Pass Criteria |
|---|---|
| `test_failure_message_uses_humanize_failure` | "unavailable" string replaced by calm personality output |
| `test_failure_message_no_alarm_words` | No ERROR/CRITICAL/ALERT in failure output |
| `test_cap22_gate_uses_wrap_gate` | Cap 22 confirmation includes governance identity |
| `test_cap64_gate_uses_wrap_gate` | Cap 64 confirmation includes governance identity |
| `test_gate_still_single_confirmation` | Exactly one "?" in wrapped output |
| `test_gate_pending_state_unchanged` | `pending_governed_confirm` structure identical |
| `test_gate_yes_still_invokes_capability` | "yes" after wrapped gate → same `invoke_governed_capability()` |
| `test_gate_no_still_cancels` | "no" after wrapped gate → cancellation |
| `test_trust_center_includes_personality_description` | Trust message contains "by design" explanation |
| `test_trust_center_raw_data_preserved` | Mode, last_external_call, failure_state still in output |
| `test_trust_receipts_api_unchanged` | `/api/trust/receipts` returns same data |

### Regression Tests

- All 187 personality tests must still pass
- All 88 simulation tests must still pass
- Fast suite (2983+) must pass with zero regressions

### Personality-Off Baseline

| Test | Pass Criteria |
|---|---|
| `test_routing_identical_after_wiring` | Same capability sequences |
| `test_governor_decisions_identical_after_wiring` | Same decisions |
| `test_capability_count_still_27` | Registry unchanged |
| `test_executor_count_still_22` | Executor dir unchanged |
| `test_ledger_events_unchanged` | Same event types logged |

---

## 10. SIMULATION STRATEGY

### Simulation Scenarios

| # | Scenario | What It Tests |
|---|---|---|
| 1 | News unavailable | Failure message is calm, not raw |
| 2 | Weather unavailable | Same |
| 3 | Cap 22 gate prompt | Governance identity in wrapped gate |
| 4 | Cap 64 gate prompt | Same, with email context |
| 5 | Cap 22 yes → execution | Approval still routes to executor |
| 6 | Cap 22 no → cancellation | Rejection still cancels |
| 7 | Trust center with blocked condition | Explanation accompanies raw data |
| 8 | Personality-off baseline | Routing/governor/ledger identical |

---

## 11. NON-GOALS

| Non-Goal | Reason |
|---|---|
| Voice integration | Higher UX/authority risk; deferred |
| Proactive briefing integration | Requires session-event triggers; deferred |
| Reminder integration | Requires Cap 61 caller coordination; deferred |
| Mode-based routing | Mode affects presentation, not routing; deferred |
| ModeDetector wiring | Not needed for first three wiring components |
| New capabilities | Personality is not a capability |
| New executors | Personality has no execution path |
| Background loops | No background execution from personality |
| Shopify/calendar writes | Read-only personality layer |
| Confirmation semantics change | Existing yes/no logic untouched |
| Ledger event changes | Existing event types/payloads untouched |
| Session state structure changes | `pending_governed_confirm` structure untouched |

---

## 12. IMPLEMENTATION READINESS CHECKLIST

- [ ] Wiring design scope reviewed (this document)
- [ ] Governance audit complete
- [ ] All 187 personality tests green
- [ ] All 88 simulation tests green
- [ ] Fast suite green (2983+)
- [ ] Runtime fingerprint current
- [ ] Working tree clean
- [ ] Integration points in session_handler.py identified
- [ ] Integration point in brain_server.py identified
- [ ] Single-confirmation rule understood
- [ ] Accompany-not-replace rule understood for TrustPresenter
- [ ] No new capability IDs planned
- [ ] No new executors planned

---

## 13. RISKS

| Risk | Impact | Mitigation |
|---|---|---|
| Humanized failure loses context | User doesn't know which capability failed | Include capability name in humanized text |
| Gate wrapping changes prompt length | Existing "yes"/"no" parsing breaks | Parsing operates on user input, not prompt text |
| Wrapped gate confuses existing tests | Brain_server integration tests fail | Mark as slow; existing tests use raw endpoint |
| TrustPresenter explanation too verbose | Trust center becomes hard to scan | Keep explanations to one sentence per item |
| Import of personality in session_handler | Increases module load time | Lazy import inside function if needed |
| Regression in confirmation flow | User says "yes" but action doesn't execute | Test yes/no flow explicitly after wiring |

---

## 14. NEXT ACTION

```
1. Complete governance audit of this design scope
2. Address any findings
3. Check all readiness items
4. Write wiring tests (tests first)
5. Implement wiring (string replacements only)
6. Run personality tests
7. Run simulation tests
8. Run fast suite
9. Wiring completion report
```

The wiring phase is the smallest possible live integration:
replace three categories of raw strings with personality-wrapped
strings. Nothing else changes.

```
Personality may increase initiative.
Personality may never increase authority.
```

No code until the governance audit clears this document.
