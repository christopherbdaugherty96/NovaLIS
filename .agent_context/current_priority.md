# Current Priority

## Wave B2 — Capability Narration Implementation — 2026-08-23

Current active lane:

```text
WAVE B2 — capability narration
STATUS: ACTIVE / IMPLEMENTATION AUTHORIZED
B3: BLOCKED
B4: BLOCKED
WAVE C: BLOCKED
```

Handoff anchors:

```text
current main: 864ceba9747384b3bdca4a693dca938b3899864e
B1 reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
B1 generated-artifact commit: e668ec0c09df6e0d304427431e95a26619a9f507
B1 PR #356: MERGED
```

B1 is complete and merged. Its proof, generated truth, operational synchronization, and final review are historical evidence for the merged B1 package. Post-B1 sync PR #357 is also merged. B2 capability narration is now active under a separate reviewed owner authorization.

## Completed gates

```text
Wave A1 — MERGED via PR #353
  f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — MERGED via PR #355
  060380f2e8c6437ff888773f0078647547ff4622

Wave B1 — MERGED via PR #356
  reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
  squash merge: 969c369b453fffca0eb2b8dad65ff3f285df8fbc
  proof / generated truth / operational truth / final review: COMPLETE
```

Issue #354 remains open as a separate zero-step hosted-Actions infrastructure issue. It is neither behavioral PASS nor behavioral FAIL evidence and does not silently authorize or block B2 implementation.

## B1 completed evidence

```text
Ruff: PASS
focused B1 tests: 13 PASS
auditor/governance tests: 29 PASS
operational consistency: PASS before/after generation
runtime-doc drift: PASS before/after generation
scope_version: behaviorally_active_v2
runtime_surface_file_count: 230 existing files
runtime_surface_hash: c5cadfeff5db3e22fea0f1c2efeb05016765c20bb7cd24e33ad758361fd9acd9
runtime_fingerprint_hash: 9c0d4ee90572e3356811436bc490de13fb82fc1393c63aa5774b36fd05154f34
generated-artifact commit: e668ec0c09df6e0d304427431e95a26619a9f507
_MOCs: excluded
exact A2-to-B1 diff: CLEAN
```

## Current action — implement bounded B2 capability narration truth

Preserve only the established B2 scope:

```text
exists
enabled
configured
verification_status
available_on_this_path
requires_approval
authority_class
```

`authorized` is request-specific, not static capability metadata. Connection, capability, OAuth scope, and Nova authority remain distinct. Do not modify runtime authority, registry membership, enablement, confirmation requirements, or execution behavior.

## Google Foundation / CI state

PR #335 remains:

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

Do not modify or merge #335 during B2.

Issue #354 remains:

```text
infrastructure/open
zero-step hosted Actions
not behavioral pass/fail evidence
required before Wave C relies on hosted CI
```

## Ordered sequence

```text
B1 COMPLETE / MERGED
-> B2 capability narration / active bounded implementation
-> B3 memory governance
-> B4 reproducibility hygiene
-> Wave C proof / semantic-contract stabilization / validated baseline
-> reconstruct #335 onto exact validated baseline
-> independent #335 review + separate merge decision
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> evidence-based Operational Continuity warrant
```

B2 is active and bounded. B3 and B4 remain blocked.

## Scope lock

Do not start or modify outside the active bounded B2 lane:

```text
GeneralChat durable-memory semantics (B3)
dependency-source truth (B4)
network behavior / NetworkMediator wiring
capability registry
OAuth / #335
Google domain-data access
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
README/front-door rewrite
_MOCs publication / Obsidian overlay refresh
```

## Permanent truth boundaries

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
request acceptance != verified effect
memory != Operational Continuity
current HEAD != immutable validated baseline
```

Generated evidence is authoritative only for what its generator mechanically measures. Tests prove only the revision/environment/scope actually exercised. A proof PASS on `f44cb8b8...` does not automatically prove a later corrective head.
