# Current Priority

Current active task:

```text
Post-PR #149 continuity closeout / current-priority cleanup.
```

PR #149 merged the status/continuity synchronization after PR #144-#148. This follow-up closes the stale wording left by that sync and restores the repo to a clear current-priority state.

No runtime implementation priority is currently selected.

## Runtime truth checked

Use these as higher authority than this continuity note when exact implementation status matters:

```text
docs/current_runtime/CURRENT_RUNTIME_STATE.md
nova_backend/src/config/registry.json
nova_backend/src/config/capability_locks.json
```

Current code/runtime truth to preserve:

```text
Runtime registry: 27 active capabilities in registry/runtime docs.
Capability locks: Cap 16 is locked; Cap 64 and Cap 65 are active but not locked.
Cap 64: confirmation-bound local mailto draft only; no SMTP, inbox access, or autonomous send.
Cap 65: read-only Shopify intelligence only; no Shopify writes.
```

## Recent merged truth

```text
PR #134 — Cap 16 governed_web_search certification locked.
PR #144 — Everyday UX Friction workstream closed.
PR #145 — Work Style Enforcement Lock merged.
PR #146 — Creator-led Shopify/POD future direction merged.
PR #147 — Nova two-domain product direction merged.
PR #148 — Piper-first voice direction merged.
PR #149 — Continuity/status sync after PR #144-#148 merged.
```

## Open carried-forward follow-ups

```text
#141 — Search widget not surfacing in live WebSocket sessions.
       Scope: live WS/front-end surfacing investigation only. Cap 16 remains locked;
       do not change Cap 16 authority, registry scope, or search executor behavior unless
       investigation shows the issue is below the WS/render layer.

#142 — RS-2 capability list truncation needs reproduction.
       Scope: reproduce first; do not patch without captured live-session evidence.

#143 — "tell me more" with prior context needs session-state-aware test.
       Scope: test-only unless the test disproves the expected behavior.
```

## Recommended next priority candidate

After this docs-only closeout lands, the highest-ROI runtime/proof candidate is:

```text
#141 — Search widget not surfacing in live WebSocket sessions.
```

This is not automatically selected as an implementation priority until a reviewed priority lock or explicit user instruction selects it.

## Queued / not active

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

## Preserved boundaries

Do not add capabilities, expand OpenClaw, add browser/computer-use, add external writes,
add autonomous workflows, or bypass GovernorMediator during this docs-only closeout.

This file is an agent continuity note. Runtime truth still comes from code and generated runtime docs.
