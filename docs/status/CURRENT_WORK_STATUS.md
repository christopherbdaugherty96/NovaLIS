# Nova Current Work Status

Last reviewed: 2026-05-11

This is a human-maintained continuity note for the current development slice.

It is not generated runtime truth. For exact runtime fingerprint, capability count, active capabilities, and generated invariants, use [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

Generated runtime docs and actual code win if they conflict with this note.

---

## Current Active Task

```text
Status / continuity synchronization after PR #144-#148.
```

No runtime implementation priority is selected until this continuity synchronization lands.

This sync exists because the repo moved beyond older priority notes:

```text
PR #134 — Cap 16 governed_web_search certification locked.
PR #144 — Everyday UX Friction workstream closed.
PR #145 — Work Style Enforcement Lock merged.
PR #146 — Creator-led Shopify/POD future model merged.
PR #147 — Nova two-domain product direction merged.
PR #148 — Piper-first voice direction merged.
```

---

## Most Recent Completed Workstreams / Direction Records

### Cap 16 governed_web_search certification

Status:

```text
LOCKED — P1-P5 passed / 60 tests / locked_date 2026-05-10
```

Source: PR #134.

### Everyday UX Friction

Status:

```text
closed — PR #144
```

Closeout: `docs/PROOFS/Everyday-UX/EVERYDAY_UX_FRICTION_CLOSEOUT_2026-05-11.md`

The workstream fixed routing and response-shape friction, added full-pipeline session tests, and carried forward three scoped follow-ups as issues.

### Work Style Enforcement Lock

Status:

```text
merged — PR #145
```

Source: `docs/status/WORK_STYLE_ENFORCEMENT_LOCK_2026-05-11.md`

This governs AI-assisted repo work style only. It does not add runtime authority.

### Creator-led Shopify/POD future model

Status:

```text
merged — PR #146 / future planning only
```

Source: `docs/future/NOVA_CREATOR_LED_SHOPIFY_POD_MODEL_2026-05-11.md`

This records Shopify/POD business-intelligence direction only. Cap 65 remains read-only; Shopify writes are not approved.

### Nova two-domain product direction

Status:

```text
merged — PR #147 / future planning only
```

Source: `docs/future/NOVA_TWO_DOMAIN_DIRECTION_2026-05-11.md`

This records Nova as a governed local-first operational intelligence platform for everyday life and creator-business operations. It does not add runtime authority.

### Piper-first voice direction

Status:

```text
merged — PR #148 / future planning only
```

Source: `docs/future/NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md`

Piper is the current/default local TTS direction. ElevenLabs remains future optional cloud voice only.

---

## Open Carried-Forward Follow-Ups

```text
#141 — Search widget not surfacing in live WebSocket sessions.
#142 — RS-2 capability list truncation needs reproduction.
#143 — "tell me more" with prior context needs session-state-aware test.
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
```

---

## Implemented Runtime / Code Truth Snapshot

- Governance spine remains the strongest runtime truth: GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, and ledger discipline are still the authority path.
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

Finish and review this continuity sync branch before any new implementation branch.
