# Current Priority

## Wave B3 — Memory Governance Authorization Gate — 2026-08-23

Current planning lane:

```text
B2: COMPLETE / MERGED
B3: NEXT / NOT IMPLEMENTATION-AUTHORIZED
B4: BLOCKED
WAVE C: BLOCKED
```

Handoff anchors:

```text
current main: e84a9d55f8575c687765b1df19e8f794b180599b
B1 reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
B1 generated-artifact commit: e668ec0c09df6e0d304427431e95a26619a9f507
B1 PR #356: MERGED
B2 reviewed head: b95039c2dc483ad330205de5dac8e3b3f94d8836
B2 PR #358: MERGED
B2 squash merge: e84a9d55f8575c687765b1df19e8f794b180599b
```

B1 and B2 are complete and merged. Their proof, generated truth, operational synchronization, and review records are historical evidence for the revisions and environments actually exercised. B3 is next, but implementation has not been authorized.

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

Wave B2 — MERGED via PR #358
  reviewed head: b95039c2dc483ad330205de5dac8e3b3f94d8836
  squash merge: e84a9d55f8575c687765b1df19e8f794b180599b
  capability narration projection / consumer migration / review: COMPLETE
```

Issue #354 remains open as a separate zero-step hosted-Actions infrastructure issue. It is neither behavioral PASS nor behavioral FAIL evidence and does not authorize B3 implementation.

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

## Current action — stop at the B3 authorization gate

The merged B2 projection preserves these distinct fields:

```text
exists
enabled
configured
verification_status
available_on_this_path
requires_approval
authority_class
```

`authorized` remains request-specific, not static capability metadata. Connection, capability, OAuth scope, and Nova authority remain distinct.

B3 may be described only at its established high level until separately authorized: ordinary chat must not silently create authoritative durable personal memory; explicit and observed memory remain distinct; provenance, confidence, conflict, supersession, and promotion semantics must remain visible. Do not design or implement new schemas, stores, APIs, or memory behavior in this synchronization.

## Google Foundation / CI state

PR #335 remains:

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

Do not modify or merge #335 before the Wave C validated-baseline sequence.

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
-> B2 capability narration / COMPLETE / MERGED
-> B3 memory governance / NEXT / NOT IMPLEMENTATION-AUTHORIZED
-> B4 reproducibility hygiene
-> Wave C proof / semantic-contract stabilization / validated baseline
-> reconstruct #335 onto exact validated baseline
-> independent #335 review + separate merge decision
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> evidence-based Operational Continuity warrant
```

B2 is complete and merged. B3 is next but not implementation-authorized; B4 remains blocked.

## Scope lock

Do not start or modify outside the B3 authorization gate:

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
