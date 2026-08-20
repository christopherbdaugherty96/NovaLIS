# 03 — Governance Truth

**Status: current / runtime-backed where explicitly stated.**

This file describes Nova's governance/control-plane boundaries without pretending that every adjacent administrative, network, persistence, or agent surface is enforced by one identical path.

## Primary sources

- [`../current_runtime/GOVERNANCE_MATRIX.md`](../current_runtime/GOVERNANCE_MATRIX.md)
- [`../current_runtime/GOVERNANCE_MATRIX_TREE.md`](../current_runtime/GOVERNANCE_MATRIX_TREE.md)
- [`../current_runtime/ROUTE_PROTECTION_COVERAGE.md`](../current_runtime/ROUTE_PROTECTION_COVERAGE.md)
- [`../current_runtime/BYPASS_SURFACES.md`](../current_runtime/BYPASS_SURFACES.md)
- [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md)
- implementation under `nova_backend/src/governor/`, `nova_backend/src/openclaw/`, `nova_backend/src/api/`, `nova_backend/src/config/`, and related execution/persistence modules.

Generated governance documents are authoritative for the structures they mechanically inspect. They are not evidence that every network call, persistence path, administrative mutation, or agent tool has been exhaustively measured unless the generator explicitly proves that claim.

## Three control planes

Nova currently has three distinct control planes.

### 1. Governed capability plane

The canonical governed capability execution spine is:

```text
User
-> GovernorMediator
-> Governor
-> CapabilityRegistry
-> SingleActionQueue
-> LedgerWriter
-> ExecuteBoundary
-> Executor
```

This is the authority path for registered governed capabilities.

| Component | Role | Location |
| --- | --- | --- |
| GovernorMediator | invocation routing / policy mediation | `nova_backend/src/governor/governor_mediator.py` |
| Governor | authority decision | `nova_backend/src/governor/` |
| CapabilityRegistry | capability existence/enabled-state control | `nova_backend/src/governor/capability_registry.py` |
| SingleActionQueue | serialized governed action dispatch | runtime queue layer |
| LedgerWriter | durable action/receipt evidence | `nova_backend/src/ledger/writer.py` |
| ExecuteBoundary | final governed execution boundary | `nova_backend/src/governor/execute_boundary/execute_boundary.py` |
| Executor | capability-specific execution | executor modules |

### 2. Local operator / administrative plane

Nova also contains local configuration and operator surfaces such as:

- settings;
- credentials;
- connection management;
- provider/runtime configuration;
- local administrative controls.

These surfaces are not automatically the same thing as registered governed capabilities. They must remain explicitly classified and protected according to their own risk and route contracts.

An administrative setting, credential, or connection may change technical availability. It must not silently create Nova action authority.

### 3. Bounded agent / routine plane

Nova contains bounded OpenClaw/routine/scheduler execution envelopes and related operator surfaces.

These may use constrained enforcement models appropriate to their path. Their existence does not grant them the entire governed capability surface, and they may not silently inherit, synthesize, or expand capability authority.

## Permanent cross-plane invariant

> **No control plane may silently increase the authority available to another control plane.**

Keep these distinctions explicit:

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
request acceptance != verified effect
memory != Operational Continuity
```

## Network governance truth

`NetworkMediator` is Nova's primary governed outbound-network control for the paths wired through it. Generated route/governance surfaces and tests should identify which paths are mediated and which explicit exceptions/bypass surfaces exist.

Do **not** state the stronger invariant that every outbound HTTP call in the entire repository necessarily passes `NetworkMediator` unless the runtime auditor mechanically demonstrates that property for the exact revision.

The correct requirement is:

```text
known governed network paths -> mediated according to their contract
known exceptions -> mechanically visible and explicitly justified
new direct-network paths -> treated as governance discrepancies until reviewed
```

A generated report must not simultaneously detect a relevant direct-network exception and summarize the relevant discrepancy set as empty.

## Execution and outcome truth

For governed execution, authority, dispatch, and outcome are separate facts.

```text
capability exists
!= capability enabled
!= path available
!= exact request authorized
!= request accepted
!= effect verified
```

Receipts and user-facing narration must preserve those distinctions. Successful dispatch is not automatically evidence that the intended external or physical effect occurred.

## Approval truth

Approval is request-specific, not static capability metadata.

An approval lifecycle may include states such as:

```text
none
pending
granted_for_exact_request
consumed
expired
```

A capability may require approval without being currently authorized for a particular request.

## Persistence truth

Nova contains intentional persistence surfaces, including governed memory and other explicit stores. Therefore an absolute repository-level rule of "no persistence" or "no silent persistence anywhere" is too broad unless scoped to a specific contract.

The active stabilization doctrine is narrower and testable:

- persistence must be explicit in the behavior contract;
- provenance/authority status must survive persistence where relevant;
- ordinary GeneralChat must not silently create durable personal memory once the Wave B3 contract is implemented;
- persisted state never becomes action authority merely because it exists.

Memory governance repair is a future Wave B3 implementation lane, not a Wave A1 behavior change.

## Local and remote route protection

Route protection is separately represented by `ROUTE_PROTECTION_COVERAGE.md`.

Current generated state at the Wave A1 planning checkpoint reports:

```text
47 local-only routes
1 token-gated remote route
2 public routes
0 unclassified routes
```

These counts are generated evidence for route classification at that revision. They do not prove every semantic authorization property of each route.

## OpenClaw boundary

OpenClaw is implemented runtime code and is not merely a planning concept. It remains a bounded actuator/agent surface, not an authority source.

Its tool registry, routines, scheduling, and local/operator surfaces must not be described as inheriting every capability or permission that exists elsewhere in Nova.

## Operational Continuity boundary

Operational Continuity is strategic direction, not current execution authority.

Continuity may eventually preserve, reconcile, and project state, but it may never:

- authorize actions;
- execute actions;
- alter permission;
- manufacture commitments;
- silently reopen decisions;
- convert learned behavior into authority.

Existing runtime/session continuity or memory functionality must not be mislabeled as the full future Operational Continuity product model.

## Review guardrails

Changes touching authority, execution, network access, credentials, persistence, agent tools, or control-plane boundaries should be reviewed against the exact path they modify rather than an assumed one-plane model.

In particular, no change may silently:

- bypass the authority contract for a governed capability;
- convert connection or OAuth scope into Nova authority;
- upgrade recommendation/inference into permission;
- upgrade accepted execution into verified outcome;
- let one control plane increase another plane's authority;
- let persistent memory or learned state become authority.

## Cost posture

Capability `cost_posture` remains metadata/visibility unless runtime enforcement is separately proven. It must not be described as quota, billing, or spend enforcement merely because the field exists.
