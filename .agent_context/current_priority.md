# Current Priority

Current active task:

```text
Generated runtime-doc regeneration after PR #152-#158 — generated-output only.
```

Branch:

```text
docs/regenerate-runtime-docs-post-openclaw-hardening
```

Status:

```text
TODO tracked by PR #158. Generator has not yet been run.
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

Generated runtime docs still need a fresh regeneration PR because PR #155 did not merge and PR #158 only tracked the TODO.

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
1. Run scripts/generate_runtime_docs.py on the runtime-doc regeneration branch in a real repo working tree.
2. Run scripts/check_runtime_doc_drift.py.
3. Inspect that changed files are generated runtime/MOC/fingerprint artifacts only.
4. Open/merge a generated-docs-only PR.
5. Run targeted OpenClaw freeform-goal governance regression tests.
6. Then select one scoped runtime follow-up, likely #141.
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
