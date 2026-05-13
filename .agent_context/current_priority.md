# Current Priority

Current active task:

```text
#141 — Search widget not surfacing in live WebSocket sessions.
```

Priority lock:

```text
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-12_SEARCH_WIDGET_WS.md
```

Status:

```text
Bug fully mapped. Two-part fix identified:
1. session_handler.py ~line 3619: add session_state["search_widget"] = widget and
   await send_widget_message(ws, "search", action_message, widget) after source extraction.
2. brain_server.py send_widget_message: add "search" case to send {type: "search", data: inner_data}
   before the generic fallthrough.
Frontend (dashboard-chat-news.js) and executor (web_search_executor.py) are both correct.
No changes needed there.
```

Scope:

```text
generated runtime docs / fingerprints / MOC artifacts only
no runtime code
no manual continuity-doc rewrite beyond status synchronization
no capability expansion
no authority expansion
```

## Recent merged truth

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
```

## Recent closed / not merged truth

```text
PR #151 — Everyday UX continuity sync closed unmerged.
PR #155 — Runtime docs regeneration closed unmerged.
```

Generated runtime docs are current as of 2026-05-12. No pending regeneration PR needed.

## Historical branch note

```text
audit/full-repo-doc-code-alignment
```

is historical/stale work. Do not reuse it as an active merge target.

## Current grounded repo summary

```text
Nova is a governance-first local AI/runtime platform with real bounded execution infrastructure, real OpenClaw runtime systems, real mediation layers, and active hardening against authority drift.

OpenClaw is implemented runtime code, not planning-only.

The PASS4 freeform-goal governance gap appears patched by PR #154 through a read-only allowlist, mutation-tool exclusion, MeteredNetworkProxy enforcement, explicit approve-action stub labeling, and regression tests.

This does not make OpenClaw broadly autonomous or fully certified.
```

## Phase Status Annotation (human layer)

`CURRENT_RUNTIME_STATE.md` is the authoritative machine-generated source. The following is
a human-layer interpretation annotation only:

```text
Phase 8 — PARTIAL. Broader envelope-governed execution remains deferred.
           CURRENT_RUNTIME_STATE.md lists this under Known Runtime Gaps.
Phase 9 — ACTIVE surfaces built on a partially incomplete Phase 8 foundation.
           Treat as IN PROGRESS until envelope execution is converged.
```

This does not override the generated runtime docs. It records the interpretation gap.

---

## Active / certified / locked discipline

```text
active != certified != locked
```

Current lock truth:

```text
Cap 16 — P1-P5 passed / locked.
Cap 64 — P1-P4 passed / P5 pending / not locked.
Cap 65 — P1-P4 passed / P5 pending / not locked.
Most other active capabilities — certification lock phases pending.
```

## Open carried-forward follow-ups

```text
#141 — Search widget not surfacing in live WebSocket sessions.
#142 — RS-2 capability list truncation needs reproduction.
#143 — "tell me more" with prior context needs session-state-aware test.
```

#141 is likely the first runtime fix after generated runtime docs are synchronized, but it is not authorized by this generated-doc task.

## Next correct sequence

```text
1. Second-pass review complete — docs/audits/SECOND_PASS_REVIEW_2026-05-12.md committed.
2. Select one scoped runtime follow-up, likely #141 (search widget WS).
3. Then: Trust Panel MVP or approval flow wiring per review priority order.
```

## Safety boundary

Do not start or include:

```text
runtime behavior changes
capability expansion
authority expansion
OpenClaw expansion
browser/computer-use expansion
external writes
Shopify writes
email sending
finance automation
social posting automation
ElevenLabs implementation
Google connector runtime implementation
UI simplification implementation
autonomous workflow execution
```

## Preserved boundary

```text
Intelligence is not authority.
```

This file is an agent continuity note. Runtime truth still comes from code and generated runtime docs.
