# Phase 2 — Design Scope

Status: design (no code, no runtime changes)
Date: 2026-06-05
Prerequisite: Phase 1 complete (294cfa6)
Governing rule: initiative ↑, authority unchanged

---

## What Phase 2 Is

Phase 2 makes Nova context-aware. Phase 1 built the personality
layer (presentation, briefing, tiered notices). Phase 2 teaches
that layer to detect what mode the user is in and surface the
right initiative at the right time.

Three components:

```
Component 5: Mode Detection
Component 6: Reminder Framework
Component 7: Initiative Template Refinement
```

## What Phase 2 Is Not

- Not live automation wiring (that requires simulation first)
- Not voice integration (Phase 3)
- Not Trust Panel integration (Phase 3)
- Not new capabilities, executors, or authority paths

---

## Component 5: Mode Detection

**File:** `src/personality/mode_detection.py` (new)

**What it does:**

Detects whether the user is in home, business, or development
context. The detected mode flows into `present_with_mode()` and
the AssistiveNoticing tier system from Phase 1B.

**Detection signals (all read-only):**

| Signal | Source | Example |
|---|---|---|
| Time of day | `datetime.now()` | Before 9 AM or after 6 PM → home |
| Topic keywords | User input text | "shopify", "revenue" → business |
| Explicit override | User says "I'm working" | → business until cleared |
| Session history | Recent capability IDs | Cap 65 Shopify → business |

**Interface:**

```python
@dataclass(frozen=True)
class ModeDetectionResult:
    mode: str                    # "home" | "business" | "development"
    confidence: str              # "explicit" | "inferred" | "default"
    reason: str                  # Human-readable explanation
    override_active: bool        # True if user explicitly set mode

class ModeDetector:
    def detect(
        self,
        *,
        user_text: str = "",
        hour: int | None = None,
        recent_capabilities: list[int] | None = None,
        explicit_override: str | None = None,
    ) -> ModeDetectionResult: ...

    def clear_override(self) -> ModeDetectionResult: ...
```

**Governance boundaries:**

- No imports from `src.governor`, `src.executors`, `src.ledger`
- Mode changes tone and initiative ceiling only
- Approval gates identical across all modes
- Current mode visible in dashboard payload
- Mode transitions logged (not to ledger — to session state)
- Import boundary test required

**Integration point:**

ModeDetector is called by the session handler before personality
wrapping. It reads session state but does not write governance
state. The detected mode is passed to `present_with_mode()` and
to the assistive notices widget builder.

**Existing infrastructure:**

ConversationRouter already supports `session_mode_override` for
explicit mode changes ("I'm working" / "back to default"). Phase
2 extends this with automatic inference that can be overridden.

---

## Component 6: Reminder Framework

**File:** `src/personality/reminder_framework.py` (new)

**What it does:**

Manages user-created reminders ("remind me to call the
electrician") and pattern-derived reminders (Nova notices you
mentioned the electrician twice this week). Surfaces reminders
through the existing AssistiveNoticing system.

**Interface:**

```python
@dataclass(frozen=True)
class Reminder:
    id: str
    text: str
    source: str              # "user_created" | "pattern_derived"
    created_at: str          # ISO timestamp
    dismissed: bool
    opt_out: bool            # User said "stop mentioning this"

class ReminderFramework:
    def create_reminder(
        self,
        text: str,
        *,
        source: str = "user_created",
    ) -> Reminder: ...

    def derive_from_pattern(
        self,
        pattern_description: str,
        *,
        source_label: str,
    ) -> Reminder | None: ...

    def list_active(self) -> list[Reminder]: ...

    def dismiss(self, reminder_id: str) -> None: ...

    def opt_out(self, reminder_id: str) -> None: ...

    def to_notice(
        self,
        reminder: Reminder,
    ) -> dict[str, Any] | None: ...
```

**Governance boundaries:**

- No imports from `src.governor`, `src.executors`, `src.ledger`
- No calendar event creation (Cap 57 is read-only for reminders)
- No recurring obligations without explicit user request
- Pattern data stored as plain dicts, routed through Cap 61
  by the caller (not by ReminderFramework itself)
- Dismissed reminders respect cooldown from ChiefOfStaffProfile
- Pattern-derived reminders always include opt-out language
- Import boundary test required

**Key constraint — snapshot-only rule:**

ReminderFramework does not call Cap 61 directly. It produces
reminder dicts. The session handler (which already has Cap 61
access through the governed path) is responsible for persisting
them. This preserves the same structural isolation as
BriefingComposer.

```
ReminderFramework produces → plain dicts
Session handler persists  → through governed Cap 61
```

**Integration point:**

`to_notice()` converts a Reminder to the same dict format used
by `build_tier3_recommend_notice()`. This means reminders flow
through the existing AssistiveNoticing widget pipeline with no
new surfaces needed.

---

## Component 7: Initiative Template Refinement

**File:** `src/personality/nova_style_contract.py` (extend existing)

**What it does:**

Updates the `_INITIATIVE_TEMPLATES` and `_CHAT_MODE_GUIDANCE`
dictionaries to use Chief of Staff framing. Currently these use
generic prompt framing ("If useful, I can..."). Phase 2 aligns
them with `ChiefOfStaffProfile.permitted_suggestion_language`.

**Scope:**

- Replace initiative tail templates with language from
  `ChiefOfStaffProfile.permitted_suggestion_language`
- Add mode-aware guidance entries for "home", "business",
  "development" (mapping to existing casual/analytical/
  implementation styles)
- No new methods, no new classes

**Governance boundaries:**

- Templates change wording only
- No capability invocations
- No authority language introduced
- Verified by existing `test_existing_style_contract_*` tests
  plus new tests confirming no forbidden language

---

## Phase 2 Test Plan

### Tests first, then implementation

| File | Tests | What it covers |
|---|---|---|
| `test_mode_detection.py` | ~10 | Time signals, keyword signals, explicit override, default fallback, mode visibility, gates unchanged across modes |
| `test_reminder_framework.py` | ~10 | User-created, pattern-derived, opt-out, dismiss, cooldown, no calendar creation, notice format |
| `test_mode_authority_neutrality.py` | ~5 | Gate identical across modes, suggestion pressure constant, memory informs not grants |
| `test_initiative_template_refinement.py` | ~5 | No forbidden language in templates, permitted language used, existing templates unchanged |

### Phase 2 simulation (after implementation)

Extend the Phase 1 simulation with:

| Scenario | What it tests |
|---|---|
| Mode auto-detection | Business keywords → business mode; evening time → home mode |
| Mode explicit override | "I'm working" → business; "I'm done" → clears override |
| Reminder creation | "Remind me to..." → reminder created, surfaced as Tier 3 |
| Reminder opt-out | Pattern reminder dismissed → not re-shown within cooldown |
| Mode + personality off | Same routing across all modes with personality disabled |

---

## Phase 2 Success Criteria

| # | Criterion | Verification |
|---|---|---|
| 1 | All Phase 1 criteria still met | Phase 1 test suite green |
| 2 | Mode detection visible and overridable | Dashboard test, override test |
| 3 | Mode does not affect authority | Authority neutrality tests |
| 4 | Reminder data is plain dicts only | No store/client imports |
| 5 | Pattern reminders include opt-out | Opt-out test |
| 6 | No new capability IDs | Registry count == 27 |
| 7 | No new executors | Executor count == 22 |
| 8 | Full fast suite passes | Zero regressions |
| 9 | Phase 2 simulation passes | All scenarios green |

---

## Implementation Order

```
1. Write tests for ModeDetector         (test_mode_detection.py)
2. Write tests for ReminderFramework    (test_reminder_framework.py)
3. Write authority neutrality tests     (test_mode_authority_neutrality.py)
4. Write initiative template tests      (test_initiative_template_refinement.py)
5. Implement ModeDetector               (mode_detection.py)
6. Implement ReminderFramework          (reminder_framework.py)
7. Refine initiative templates          (nova_style_contract.py)
8. Import boundary tests                (extend test_personality_import_boundary.py)
9. Run fast suite — confirm green
10. Phase 2 simulation
11. Phase 2 completion report
```

No live routing changes until simulation validates behavior.

---

## Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| Mode detection wrong | Mismatched tone feels jarring | Default to "home", visible override, low confidence = default |
| Reminder spam | User ignores all notices | Cooldown from profile, max 2 active reminders, opt-out respected |
| Pattern derivation creepy | "How did Nova know?" | Always disclose source, always offer opt-out |
| Initiative templates feel robotic | Chief of Staff framing too stiff | Test with real conversation flows, not just unit tests |
| Import creep in new files | Governance violation | Import boundary tests block build |

---

## What Phase 2 Does Not Touch

- No voice integration (Phase 3)
- No Trust Panel integration (Phase 3)
- No proactive briefing delivery (Phase 3)
- No live routing changes
- No new capabilities
- No new executors
- No authority expansion
