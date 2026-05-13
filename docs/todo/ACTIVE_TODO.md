# Active TODO - Nova

Last reviewed: 2026-05-13

---

## Current Active Task

```text
#141 — Search widget not surfacing in live WebSocket sessions.
```

Status:

```text
Runtime-doc regeneration is COMPLETE as of 2026-05-12.
CURRENT_RUNTIME_STATE.md was confirmed current; generator output produced no runtime-state drift.
MOC artifacts were refreshed.
No dedicated runtime-doc regeneration PR is pending.
```

Current scoped implementation target:

```text
Fix the live WebSocket/search-widget surfacing path for Cap 16 without changing
capability authority, search behavior, or runtime governance.
```

Known mapped fix from `.agent_context/current_priority.md`:

```text
1. session_handler.py: preserve the search widget in session_state and send it
   through send_widget_message(ws, "search", action_message, widget) after source extraction.
2. brain_server.py send_widget_message: add a "search" case that sends
   {type: "search", data: inner_data} before generic fallthrough.
```

---

## Recently Completed / Merged

```text
PR #134 — Cap 16 governed_web_search certification locked.
PR #144 — Everyday UX Friction workstream closed.
PR #145 — Work Style Enforcement Lock merged.
PR #146 — Creator-led Shopify/POD future direction merged.
PR #147 — Nova two-domain product direction merged.
PR #148 — Piper-first voice direction merged.
PR #149 — Current status / continuity synchronization merged.
PR #150 — Audit-first safety boundary merged.
PR #152 — Full repo/doc/code alignment audit artifacts merged.
PR #153 — PASS4 OpenClaw freeform goal inspection merged.
PR #154 — OpenClaw PATCH A-D hardening merged.
PR #156 — Search stopword cleanup merged.
PR #157 — Post-audit continuity/status synchronization merged.
PR #158 — Runtime-doc regeneration TODO tracking merged.
PR #159 — Current priority/status synchronization merged.
PR #164 — Runtime-doc regeneration task closed; current docs confirmed, MOCs refreshed.
```

---

## Closed / Not Merged

```text
PR #151 — continuity sync branch closed unmerged.
PR #155 — runtime docs regeneration closed unmerged.
```

These are historical and should not be reused as active merge targets.

---

## Current Open Follow-Ups

### #141 — Search widget not surfacing in live WebSocket sessions

Scope:

```text
WS transport / response serialization / frontend render surfacing only.
No capability changes.
No authority changes.
No search behavior expansion.
```

Priority:

```text
current scoped runtime follow-up
```

### #142 — RS-2 capability list truncation

Status:

```text
needs reproduction / not yet confirmed
```

First step:

```text
capture reproducible live-session evidence
```

### #143 — "tell me more" with prior context

Status:

```text
expected behavior likely correct / missing session-state-aware integration test
```

Scope:

```text
test-only change unless reproduction proves runtime drift
```

### #165 — Patch Shopify future design doc truth header

Status:

```text
open docs-truth cleanup
```

Current truth to preserve:

```text
Cap 65 shopify_intelligence_report is active and implemented as Tier 1 read-only Shopify intelligence.
Cap 65 has P1-P4 automated verification passing.
Cap 65 P5 live signoff is blocked until Shopify development-store credentials are configured and the live checklist passes.
Cap 65 is not locked.
Caps 66-76 are future design only and are not implemented runtime authority.
```

Required boundary:

```text
Do not describe Cap 65 as complete, live-signed, certified, locked, or operator-ready.
Do not imply Shopify writes, store mutation, publishing, customer messaging, pricing changes,
ad spend, refunds, or autonomous store management are current runtime authority.
```

---

## Shopify / Creator-Business Direction Truth

```text
Creator-led Shopify/POD business intelligence is a future product direction, not current execution authority.
```

Current runtime Shopify surface:

```text
Cap 65 — shopify_intelligence_report
authority_class: read_only_network
external_effect: true
requires_confirmation: false
status: active
lock state: P1-P4 pass / P5 pending / not locked
```

Allowed current/framed responsibilities:

```text
store intelligence reports
sales summaries
product catalog summaries
inventory visibility
marketing/finance visibility as reporting or drafting surfaces
recommendations requiring Christopher approval before action
```

Not authorized:

```text
Shopify writes
product publishing
price changes
refunds
customer messaging
ad spend
social posting
financial transactions
inventory ordering
autonomous store operation
```

---

## Current Governance Truth Notes

```text
OpenClaw is implemented runtime code, not planning-only.
```

PR #154 narrowed the freeform-goal execution surface through:

```text
read-only tool allowlist
mutation-tool exclusion
MeteredNetworkProxy enforcement
conservative network-call budgeting
governance regression tests
```

This does not authorize:

```text
broad autonomy
browser/computer-use expansion
external writes
OpenClaw authority expansion
```

---

## Active / Certified / Locked Discipline

```text
active != certified != locked
```

Current lock truth:

```text
Cap 16 — P1-P5 passed / locked.
Cap 64 — P1-P4 passed / P5 pending / not locked.
Cap 65 — P1-P4 passed / P5 pending / not locked.
Most active capabilities — certification phases pending.
```

---

## Queued / Not Active Without Separate Reviewed Priority Lock

```text
UI simplification
Cap 64 P5
Cap 65 P5
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

## Preserved Boundaries

```text
Intelligence is not authority.
Visibility is not authority.
Memory is not permission.
```

The recent audit, hardening, and Shopify direction merges do not approve:

- Shopify writes
- autonomous execution
- browser/computer-use expansion
- external writes
- autonomous finance operations
- autonomous social posting
- OpenClaw authority expansion
- direct Cap 63 shortcut use
- hidden background work

---

## Next Correct Step

```text
1. Complete the #141 search-widget live WebSocket patch under the current priority lock.
2. Separately patch #165 as a docs-only truth-header cleanup.
3. Do not merge stale Shopify/direction branches directly into main.
```
