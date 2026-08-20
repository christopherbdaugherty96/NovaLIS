# Current Priority

## Wave B1 — Runtime Truth Instrumentation — 2026-08-20

Current active lane:

```text
WAVE B1 — runtime-truth instrumentation only
```

Current B1 planning base:

```text
060380f2e8c6437ff888773f0078647547ff4622
```

This SHA is an observed post-A2 checkpoint, not a permanent current-main alias and not a validated baseline. Verify current GitHub head before later work.

## Completed gates

```text
Wave A1 — operational truth synchronization
  MERGED via PR #353
  merge: f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — strategy reconciliation
  MERGED via PR #355
  merge: 060380f2e8c6437ff888773f0078647547ff4622
```

Do not reopen A1/A2 unless a new material defect is reproduced.

## Why B1 exists

The generated runtime truth currently has measurement inconsistencies:

- direct `requests` usage can be detected in `BYPASS_SURFACES.md` while the main discrepancy set still says none;
- the known `nova_backend/src/api/connections_api.py` path outside NetworkMediator is documented manually but not represented in generated discrepancy state;
- Phase 9 status relies on retired placeholder-file existence rather than live implementation/import/symbol evidence;
- the runtime fingerprint does not cover all behaviorally active source families that generated truth depends on;
- generated invariants overstate whole-repository guarantees beyond what the auditor mechanically proves;
- `check_runtime_doc_drift.py` is intentionally narrow and does not check agreement among active operational truth surfaces.

## B1 target package

B1 is limited to:

```text
runtime-truth instrumentation
network-exception/discrepancy representation
Phase 9 live implementation evidence
fingerprint coverage
qualified generated invariants
focused regression tests
separate operational-truth consistency checker
required generated runtime outputs
minimal current-status sync
```

The known direct-network finding remains:

```text
path: nova_backend/src/api/connections_api.py
classification: local administrative health probe
status: detected outside NetworkMediator; pending explicit disposition
```

B1 must make that finding visible. B1 does not reroute or otherwise change the network behavior.

## Google Foundation state

PR #335 remains:

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
scope: Google identity/auth foundation only
```

It must not be merged from its historical branch state. Reconstruction/reconciliation waits for Wave C to establish an exact validated baseline.

## Current ordered sequence

```text
B1  runtime-truth instrumentation
B2  capability narration
B3  memory governance
B4  reproducibility hygiene
C   proof / semantic-contract stabilization / validated baseline
-> reconstruct #335 onto exact validated baseline
-> separate #335 review/merge decision
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> separately warranted Continuity slice
```

Issue #343 is the detailed ordering record.

Issue #354 separately tracks zero-step GitHub Actions infrastructure failures. Those failures are not behavioral test evidence, but trustworthy hosted CI evidence is required before Wave C certification.

## B1 scope lock

B1 may change only the instrumentation/proof surfaces listed above.

B1 does **not** change:

```text
network behavior or NetworkMediator wiring
capability narration semantics (B2)
GeneralChat durable-memory semantics (B3)
dependency-source truth (B4)
capability registry
OAuth
Google #335 implementation
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
```

## Permanent architecture boundary

Three distinct control planes exist:

1. governed capability plane;
2. local operator / administrative plane;
3. bounded agent / routine plane.

No plane may silently increase authority available to another.

Keep these distinctions explicit:

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
execution != verified outcome
memory != Operational Continuity
```

## Evidence discipline

Do not equate:

```text
exists
enabled
configured
available_on_this_path
authorized
request_accepted
effect_verified
```

Authorization is request-specific. Generated evidence is authoritative only for what its generator mechanically measures. Historical test/proof totals remain historical until reproduced against the exact candidate being certified.

## What agents should do now

```text
1. Read AGENTS.md and docs/CANONICAL/00_INDEX.md.
2. Treat Wave B1 as the only active implementation lane.
3. Repair the auditor's measurement/reporting semantics only.
4. Keep #335 untouched.
5. Do not start B2, B3, B4, Google domain work, or Continuity runtime work.
6. Keep Issue #354 separate from B1 behavior/content unless diagnosing hosted Actions is explicitly selected.
7. Do not call a baseline validated until Wave C proof completes.
```

## Strategic direction

The consolidated August Product/Platform strategy is merged through PR #355 and remains non-authorizing. Operational Continuity remains strategically accepted and implementation-inactive; it must remain non-authorizing and non-executing.
