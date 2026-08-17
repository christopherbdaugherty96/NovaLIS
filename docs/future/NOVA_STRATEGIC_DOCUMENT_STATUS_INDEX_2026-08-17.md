# Nova Strategic Document Status Index — 2026-08-17

Status: documentation-governance reference; non-authorizing.

Purpose: reduce ambiguity among multiple generations of Nova strategy. This index does not change runtime truth, roadmap ordering, lane scope, or implementation authority. When a listed document has its own explicit status or a canonical roadmap/lock disagrees, the higher-authority source wins.

## Active truth hierarchy

Preferred interpretation order:

```text
1. Generated Runtime Truth — what exists now
2. Product Definition — what Nova is
3. Current State — where the project is now
4. Master Roadmap — what comes next
5. Lane Lock — exact authorized implementation scope
6. Evidence / Proof — why work is considered complete
7. Strategic/Future docs — non-authorizing direction/reference
```

Future docs should not be used to infer current capability or permission.

## Current strategic direction

### ACTIVE STRATEGY / NON-AUTHORIZING

- `docs/product/PRODUCT_DEFINITION.md`
  - Stable product identity and permanent architecture.
- `docs/future/NOVA_AUTHORITY_AND_DECISION_OS_DIRECTION_2026-07-28.md`
  - Long-term Awareness -> Decision -> Authority -> Execution -> Outcome direction and Continuity model.
- `docs/future/NOVA_PRODUCT_PLATFORM_DIRECTION_2026-08-17.md`
  - Single consolidated August 2026 Product/Platform strategy. Includes local-first personal operations positioning, platform/control-plane framing, frontier-model escalation, cost-aware local execution, provider neutrality, capability/authority boundaries, ApprovalGrant/outcome truth, routing pressure point, Continuity, Google evidence, deployment, competitive position, collaboration/investment gates, validation sequence, and implementation-discipline conclusions.
- `docs/future/NOVA_PRODUCT_VALIDATION_PROTOCOL_2026-08-17.md`
  - Defines the future 7–14 day owner proof and 3–10 user validation criteria once implementation prerequisites exist.

These docs guide interpretation but do not order or authorize implementation.

The former `NOVA_PRODUCT_PLATFORM_DIRECTION_2026-08-17_SECOND_PASS.md` was intentionally consolidated into the primary Product/Platform direction before merge to avoid competing strategic narratives. Git history preserves the prior addendum.

## ACTIVE ORDERING / SCOPE SOURCES

- `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`
  - Canonical ordering, subject to current truth-sync updates.
- current-state/status surfaces named by the roadmap and Issue #343
  - Operational position only; must be kept synchronized to current main.
- lane-specific priority/lock documents
  - Exact implementation scope when active.

## REFERENCE / DEFERRED CONCEPTS

The following concepts remain useful design/reference material but should not independently activate work or compete with the newer Product Platform + Continuity direction.

### Governed local memory workspace / Second Brain concepts

Representative source: Issue #71 — governed local memory workspace.

Status: `REFERENCE / DEFERRED`.

Useful ideas such as memory provenance, project capsules, candidate memory, contradiction/staleness checks, and reviewability may later support Continuity. The proposed large workspace hierarchy is not current implementation direction and should not be treated as a prerequisite to minimal Continuity.

### Governed learning layer

Representative source: Issue #73 — governed learning layer.

Status: `REFERENCE / DEFERRED`.

Learning may later improve recommendations and attention. It remains below explicit memory/Continuity proof and may never create authority. Predictive learning is not current priority.

### Brain / Daily Brief architecture generations

Representative source: Issue #74 — Brain matrix / Daily Brief boundary.

Status: `REFERENCE`.

The useful separation of reasoning, routines, memory, and Governor remains valid. Newer permanent product language takes precedence where terminology differs: Awareness, Decision, Authority, Execution, Outcome, with Continuity cross-cutting.

### Agent workspaces / broad agent coordination

Representative source: Issue #67 — agent workspaces and Google coordination.

Status: `DEFERRED / PARTIALLY SUPERSEDED BY CURRENT GOOGLE + CONTINUITY SEQUENCING`.

Read-first Google evidence and prepared/draft-only work remain useful. AgentRegistry/workspace/multi-agent expansion is not current product priority.

### Multi-model advisory layer

Representative source: Issue #189 — multi-model advisory and ecosystem proof planning.

Status: `REFERENCE / STRATEGICALLY ABSORBED`.

The core principle `Models advise. Nova governs.` remains active and is captured in the consolidated 2026-08-17 Product/Platform direction. Broad provider-routing implementation remains deferred behind stabilization, Google evidence, and minimal Continuity and should receive an implementation contract only when its lane activates.

### Economic-value / OpenClaw expansion

Representative source: Issue #326.

Status: `REFERENCE / GATED`.

Economic usefulness remains important, but broad OpenClaw execution remains gated. OpenClaw is a replaceable actuator and should not gain durable strategy, authority, budgets, or state ownership.

## Explicitly not current implementation priorities

Unless separately reactivated through the canonical roadmap and a reviewed lane lock:

```text
large graph/memory infrastructure
predictive learning
multi-agent orchestration
broad browser/computer-use
expanded OpenClaw autonomy
autonomous business operation
broad SaaS productization
provider marketplace / broad ModelRouter implementation
```

## Implementation-contract rule

Do not turn strategic future requirements into speculative implementation contracts prematurely.

When a lane actually activates:

1. ground against then-current runtime truth and external provider/API behavior;
2. define the exact interfaces, schemas, policy, tests, persistence, and UI required for that lane;
3. preserve permanent Nova boundaries such as authority separation, data minimization, provenance, and truthful outcomes;
4. do not treat earlier illustrative schemas or provider examples as binding implementation authority.

For example, multi-provider strategy may name future needs such as privacy classes, budget ceilings, provider fallback, context minimization, and a ModelProviderRegistry. The actual contract should be written only when multi-provider routing is authorized for implementation.

## Maintenance rule

When a new strategic document materially replaces an older concept:

1. preserve the old material through Git history or explicit reference when useful;
2. mark/index the concept as `SUPERSEDED`, `REFERENCE`, `DEFERRED`, `ACTIVE STRATEGY`, or `ACTIVE IMPLEMENTATION`;
3. link to the newer source;
4. do not duplicate large strategy blocks across multiple authoritative-looking files;
5. ensure AI coding agents can identify the current truth hierarchy without interpreting old planning as permission.

The objective is fewer competing narratives, not deletion of useful design history.