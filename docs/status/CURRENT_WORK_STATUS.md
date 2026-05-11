# Nova Current Work Status

Last reviewed: 2026-05-11

This is a human-maintained continuity note for the current development slice.

It is not generated runtime truth. For exact runtime fingerprint, capability count, active capabilities, and generated invariants, use [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

Generated runtime docs and actual code win if they conflict with this note.

---

## Current Active Task

```text
Post-PR #149 continuity closeout / current-priority cleanup.
```

PR #149 merged the status/continuity synchronization after PR #144-#148.

This follow-up branch exists to:

```text
remove stale “until this sync lands” wording
synchronize current-priority files with merged PR truth
preserve runtime/code-grounded capability status wording
carry forward scoped follow-up issues without expanding authority
```

No runtime implementation priority is currently selected.

---

## Most Recent Completed Workstreams / Direction Records

### Cap 16 governed_web_search certification

Status:

```text
LOCKED — P1-P5 passed / 60 tests / locked_date 2026-05-10
```

Sources:

```text
PR #134
docs/capability_verification/cap_16_governed_web_search_certification_2026-05-10.md
nova_backend/src/config/capability_locks.json
```

Cap 16 remains locked.

Issue #141 currently indicates a possible live WebSocket/front-end widget surfacing issue.
This does not currently invalidate Cap 16 certification or lock status.

### Everyday UX Friction

Status:

```text
closed — PR #144
```

Closeout:

```text
docs/PROOFS/Everyday-UX/EVERYDAY_UX_FRICTION_CLOSEOUT_2026-05-11.md
```

The workstream fixed routing and response-shape friction, added full-pipeline session tests, and carried forward three scoped follow-ups as issues.

### Work Style Enforcement Lock

Status:

```text
merged — PR #145
```

Source:

```text
docs/status/WORK_STYLE_ENFORCEMENT_LOCK_2026-05-11.md
```

This governs AI-assisted repo work style only.
It does not add runtime authority.

### Creator-led Shopify/POD future model

Status:

```text
merged — PR #146 / future planning only
```

Source:

```text
docs/future/NOVA_CREATOR_LED_SHOPIFY_POD_MODEL_2026-05-11.md
```

This records Shopify/POD business-intelligence direction only.
Cap 65 remains read-only; Shopify writes are not approved.

### Nova two-domain product direction

Status:

```text
merged — PR #147 / future planning only
```

Source:

```text
docs/future/NOVA_TWO_DOMAIN_DIRECTION_2026-05-11.md
```

This records Nova as a governed local-first operational intelligence platform for everyday life and creator-business operations.
It does not add runtime authority.

### Piper-first voice direction

Status:

```text
merged — PR #148 / future planning only
```

Source:

```text
docs/future/NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md
```

Piper is the current/default local TTS direction.
ElevenLabs remains future optional cloud voice only.

### PR #149 continuity synchronization

Status:

```text
merged — continuity sync completed
```

PR #149 synchronized status files after PR #144-#148.
This branch closes the stale continuity wording left after that merge.

---

## Open Carried-Forward Follow-Ups

```text
#141 — Search widget not surfacing in live WebSocket sessions.
       Scope: WS/front-end surfacing investigation only.
       Cap 16 remains locked unless investigation shows a lower-layer issue.

#142 — RS-2 capability list truncation needs reproduction.
       Scope: capture reproducible live-session evidence before patching.

#143 — "tell me more" with prior context needs session-state-aware test.
       Scope: test-only unless evidence disproves expected behavior.
```

These do not authorize capability expansion, authority expansion, browser/computer-use, external writes, or autonomous workflows.

---

## Queued / Not Active Without Separate Reviewed Priority Lock

```text
UI simplification
Cap 64 P5
Google connector runtime implementation
Shopify writes
ElevenLabs implementation
OpenClaw expansion
browser/computer-use expansion
external writes
finance automation
social posting automation
autonomous workflow execution
branch deletion / cleanup
CI baseline cleanup
```

---

## Implemented Runtime / Code Truth Snapshot

Runtime/code-grounded truth checked against:

```text
nova_backend/src/config/registry.json
nova_backend/src/config/capability_locks.json
nova_backend/src/governor/capability_registry.py
docs/current_runtime/CURRENT_RUNTIME_STATE.md
```

Current runtime/code truth:

- Governance spine remains the strongest runtime truth: GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, and ledger discipline are still the authority path.
- Runtime registry/runtime truth currently list 27 active capabilities.
- Cap 16 governed web search is certified and locked.
- Cap 64 remains confirmation-bound local `mailto:` draft only. No SMTP, inbox access, or autonomous send.
- Cap 65 remains read-only Shopify intelligence. No Shopify writes.
- Trust Review Card remains display-only and non-authorizing.
- OpenClaw proof/mediator work remains bounded, non-authorizing, and not an approval for broad automation.
- Browser Use visual proof remains blocked/setup-required and is not Nova runtime browser/computer-use authority.

---

## Preserved Boundaries

```text
Intelligence is not authority.
```

No recent docs merge authorizes:

- autonomous execution
- hidden background work
- browser/computer-use expansion
- external writes
- direct Shopify writes
- autonomous finance operations
- autonomous social posting
- OpenClaw authority expansion
- direct Cap 63 shortcut use

---

## Next Correct Step

Finish this docs-only continuity closeout before selecting a new runtime implementation priority.

Recommended next candidate after this branch lands:

```text
#141 — Search widget not surfacing in live WebSocket sessions.
```

This is a recommendation only, not an automatically selected implementation priority.
