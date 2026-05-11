# Current Priority

Current active task:

```text
Full repo/doc/code alignment audit — safety-bounded, audit-only.
```

Branch:

```text
audit/full-repo-doc-code-alignment
```

This is an audit-first priority. It does not authorize runtime implementation changes.

## Recent merged truth

```text
PR #134 — Cap 16 governed_web_search certification locked.
PR #144 — Everyday UX Friction workstream closed.
PR #145 — Work Style Enforcement Lock merged.
PR #146 — Creator-led Shopify/POD future direction merged.
PR #147 — Nova two-domain product direction merged.
PR #148 — Piper-first voice direction merged.
PR #149 — Current status / continuity synchronization merged.
```

## Audit scope

```text
1. Runtime/generated truth reconciliation
2. Capability registry ↔ docs alignment
3. Governance authority/bypass audit
4. UI/WebSocket/routing audit
5. Future docs/planning-only labeling audit
6. Proof/test/CI claims audit
7. Stale/duplicate docs cleanup map
8. Final patch roadmap
```

## Safety boundary

The audit may identify gaps and propose patches.

The audit must not directly implement runtime fixes unless a separate reviewed priority lock is created.

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

## Open carried-forward follow-ups

```text
#141 — Search widget not surfacing in live WebSocket sessions.
#142 — RS-2 capability list truncation needs reproduction.
#143 — "tell me more" with prior context needs session-state-aware test.
```

#141 is likely the first runtime fix after the audit, but it is not authorized by this audit lock.

## Preserved boundaries

```text
Intelligence is not authority.
```

Do not add capabilities, expand OpenClaw, add browser/computer-use, add external writes,
add autonomous workflows, or bypass GovernorMediator during the audit.

This file is an agent continuity note. Runtime truth still comes from code and generated runtime docs.
