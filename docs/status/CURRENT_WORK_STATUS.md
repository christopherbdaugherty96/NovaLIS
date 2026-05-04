# Nova Current Work Status

Last reviewed: 2026-05-04 (priority lock applied)

This is a human-maintained continuity note for the current development slice.

It is not generated runtime truth. For exact runtime fingerprint, capability count, active capabilities, and generated invariants, use [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

Generated runtime docs and actual code win if they conflict with this note.

---

## Priority Lock (2026-05-04)

Active development is restricted to:

```text
RequestUnderstanding review card
→ capability signoff matrix
→ OpenClawMediator skeleton
→ read-only workflow proof
```

All other workstreams are intentionally paused to prevent premature expansion before execution governance boundaries are proven.

---

## Implemented Runtime / Code Truth

(unchanged baseline retained below)

- Governance spine remains the strongest runtime truth: GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, and ledger discipline are still the authority path.
- Cap 16 governed web search remains the active current-information lane.
- Search Evidence Synthesis is implemented as a deterministic evidence-structuring module for Cap 16 search output. It does not add a new capability, does not authorize action, and does not bypass NetworkMediator.
- Daily Brief MVP is implemented as a deterministic, on-demand session brief (PR #68). It synthesizes session state, memory, receipts, weather (live via WeatherService), calendar (local ICS via CalendarSkill), and email placeholder into 11 sections. Non-authorizing frozen dataclass; `execution_performed=False` and `authorization_granted=False` are enforced by `__post_init__`. No new capability, no LLM calls, no Governor path.
- Stage 3 Memory Loop is implemented as an explicit user-initiated conversational memory skill.
- Stage 4 Context Pack is implemented and live-wired into general_chat_runtime.py.
- Cap 64 remains confirmation-bound local `mailto:` draft only.
- Cap 65 remains read-only Shopify intelligence.

---

## Planning-Only / Future Direction

All future direction remains valid but is currently paused under the priority lock.

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-04.md`
