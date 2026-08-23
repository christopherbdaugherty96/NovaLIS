# AGENTS.md

Guidance for AI agents working on NovaLIS.

Start here before editing the repository.

## Core Rule

**Intelligence is not authority.**

Reasoning may clarify, plan, search, summarize, compare, and propose. Governed capability execution remains subject to Nova's authority and execution boundaries.

## Project Positioning

Nova is a governance-first local AI system that separates intelligence from execution authority.

Nova prioritizes visible authority boundaries, inspectable execution, and user-controlled AI operation.

Operational Continuity is strategic direction, not current runtime authority.

The consolidated August Product/Platform strategy is merged as strategy-only guidance through PR #355. Strategy does not override current runtime truth, operational ordering, lane scope, or authority.

## Read Order

Before selecting work, read:

1. `docs/CANONICAL/00_INDEX.md`
2. `docs/status/DAILY_COMMAND_CENTER.md`
3. `.agent_context/current_priority.md`
4. `docs/status/CURRENT_WORK_STATUS.md`
5. `docs/todo/ACTIVE_TODO.md`
6. `docs/capability_verification/CAPABILITY_INVENTORY.md`
7. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
8. `docs/CANONICAL/07_ROADMAP_TRUTH.md`

For exact runtime-existence claims, inspect code and the generated runtime surfaces that mechanically measure the relevant claim. Generated documents are authoritative only for the properties their generators actually inspect.

## Wave B1 Current Development State — 2026-08-23

Wave A1 and A2 are complete:

```text
#353  Wave A1 operational truth synchronization — MERGED
       merge: f25c798c7cb488495a343068463e9214cab0a763

#355  Wave A2 strategy reconciliation — MERGED
       merge/current main: 060380f2e8c6437ff888773f0078647547ff4622
```

Current active lane:

```text
Wave B1 — runtime-truth instrumentation
branch: codex/b1-runtime-truth-instrumentation-20260820
base: 060380f2e8c6437ff888773f0078647547ff4622
first published/proven candidate: f44cb8b856345ddc573fe0cb56037104350ffeb4
source/test correction checkpoint: ecd4033928990c68663f2ef81b46236686043765
PR #356: OPEN / DRAFT
substate: bounded final-review corrections applied; corrected exact-head proof/regeneration required
merge: NOT AUTHORIZED
```

The base SHA is a planning/comparison checkpoint, not a validated baseline. `f44cb8b8...` completed the first exact-head local proof, generated-artifact publication, final remote scope review, and draft PR #356 opening. Final release review then found two bounded truth-integrity defects: active B1 handoff surfaces still described the pre-generation/no-PR state, and `runtime_surface_file_count` included one nonexistent `ALLOWED_READ_PATHS` entry.

The fingerprint source/test correction is now applied. Later operational-document commits may advance branch HEAD beyond `ecd403...`; verify and record the actual corrected HEAD used for proof.

### Immediate worker instruction

Do **not** redesign or extend B1 instrumentation.

The final review reproduced concrete B1 truth-contract defects, so bounded correction is authorized only for those defects. The next step is corrective execution/proof, mechanical regeneration, final-state checks, exact diff review, and PR #356 reassessment.

The three generated runtime artifacts committed at `f44cb8b8...` were valid for that candidate but are now stale relative to the fingerprint correction. Regenerate them mechanically on the corrected head; manual edits are forbidden.

Merged stabilization work already includes:

```text
#337 / #338  P1-A commitment/capability truth
#339         P1-B receipt-correlated session activity/outcome history
#340         Cap 19 outcome truth
#341 / #344  explicit weather-location repair / WebSocket preservation
#345         brightness outcome truth
#346         volume command wording/routing
#347         current-information freshness/source-boundary routing
#348         broad awareness follow-up interpretation
#349         Calendar source-selection overmatch repair
#350         Calendar tomorrow-scope preservation
#351         local schedule-cancellation routing
#352         private Drive source-selection truth
```

Do **not** select any of those as if they are still unimplemented.

PR #335 remains:

```text
OPEN
DRAFT
UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

Do not merge or extend PR #335 in its historical state. It is deferred until the Wave C validated-baseline checkpoint.

## Current Ordered Gate

```text
Wave B1 — bounded correction / corrected exact-head proof / regeneration / final PR #356 review / separate merge decision
-> Wave B2 — capability narration
-> Wave B3 — memory governance
-> Wave B4 — reproducibility hygiene
-> Wave C — proof / validated-baseline checkpoint
-> reconstruct/reconcile #335 onto the exact validated baseline
-> separate #335 review/merge decision
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> evidence-based Continuity warrant
```

Issue #343 remains the detailed stabilization ordering record.

Issue #354 separately tracks the zero-step GitHub Actions infrastructure failure. That infrastructure state is not behavioral test evidence and must be resolved before Wave C certification evidence is relied on.

## Wave B1 Lock

B1 may change only what is required to make generated/runtime truth instrumentation accurately describe what it measures:

- runtime-auditor instrumentation;
- requests-based network discrepancy/classification reporting;
- Phase 9 implementation evidence checks;
- runtime fingerprint scope;
- generated runtime truth outputs required by those changes;
- focused tests;
- a separate operational-truth consistency checker;
- minimal current-status synchronization needed to name B1 and its proof/review substate accurately.

The first B1 publication pass is complete. Final release review reproduced one P1 operational-truth defect and one P2 fingerprint-count defect. Do not add implementation work beyond those bounded corrections.

B1 does **not** authorize:

```text
network behavior changes
moving connections_api.py behind NetworkMediator
capability narration repair (B2)
GeneralChat memory/persistence repair (B3)
dependency-source cleanup (B4)
capability registry or authority changes
OAuth or PR #335 implementation
Google domain-data access
Operational Continuity runtime
OpenClaw authority expansion
provider routing
external-write behavior
README/front-door rewrite
```

The known requests-based network checkpoint finding remains:

```text
nova_backend/src/api/connections_api.py
classification: local_administrative_health_probe
status: detected outside NetworkMediator; explicitly reported pending disposition
```

B1 makes that fact visible in discrepancy/runtime truth. It does not silently treat the path as mediated and does not fix the network path itself. The scanner is requests-based and does not prove absence of every possible network mechanism.

## Corrective Proof Gate

PR #356 already exists and must remain draft while the corrected head is proved. Verify the exact branch/HEAD:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
```

Then run:

```bash
export PYTHONPATH=nova_backend
python -m ruff check nova_backend/src/audit/runtime_truth_instrumentation.py nova_backend/tests/test_runtime_truth_b1.py scripts/check_operational_truth_consistency.py
python -m pytest nova_backend/tests/test_runtime_truth_b1.py
python -m pytest nova_backend/tests/test_runtime_auditor.py nova_backend/tests/test_runtime_governance_docs.py
python scripts/check_operational_truth_consistency.py
python scripts/check_runtime_doc_drift.py
python scripts/generate_runtime_docs.py
```

After generation inspect:

```text
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/BYPASS_SURFACES.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
```

The fingerprint acceptance contract now additionally requires that `runtime_surface_file_count` equal the exact **existing-file** set consumed by the runtime-surface hash. Missing allowlist paths must not be counted as files.

The generator also refreshes `_MOCs/*`; those side effects remain outside B1. Stage only the three runtime artifacts and do not use broad staging.

After regeneration, rerun operational consistency and runtime-doc drift, review the exact A2-base → corrected final-B1 diff, then reassess PR #356. A clean result supports a **merge decision** only; it does not authorize merge.

## Permanent Control-Plane Distinction

Nova has three distinct control planes.

### 1. Governed capability plane

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

This is the authority path for governed capabilities.

### 2. Local operator / administrative plane

Settings, credentials, connections, provider/runtime configuration, and other local operator controls are not automatically governed capabilities. They must remain explicitly classified and must not silently increase capability authority.

### 3. Bounded agent / routine plane

OpenClaw/routine/scheduler envelopes may have constrained enforcement of their own. They must not silently inherit or increase Nova capability authority.

Permanent invariant:

> No control plane may silently increase the authority available to another control plane.

Permanent distinctions:

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
request acceptance != verified effect
memory != Operational Continuity
current HEAD != immutable validated baseline
```

## Evidence Discipline

Do not collapse these evidence levels:

```text
exists
enabled
configured
available_on_this_path
request_accepted
effect_verified
verification_status
authority_class
```

`authorized` is not static capability metadata. Approval/authority is request-specific.

Do not infer that a generated PASS proves behavior the generator does not measure. Do not infer that a historical proof packet is current proof. Do not mark unexecuted test definitions as passing evidence. Do not call a candidate baseline validated until the required Wave C proof package has completed. Do not treat the PASS on `f44cb8b8...` as proof of a later corrected branch head.

## Continuity Boundary

Operational Continuity remains strategically accepted but implementation-inactive.

Continuity may preserve/reconcile/project state, but it may never:

- authorize;
- execute;
- change permission;
- manufacture commitments;
- silently reopen decisions;
- convert learned behavior into authority.

## Required Context Before Brain/Governance Changes

Read:

- `docs/brain.md`
- `docs/brain/README.md`
- `.agent_context/brain_loop.md`
- `.agent_context/environments.md`
- `.agent_context/governance.md`
- `.agent_context/current_priority.md`

## Do Not

- bypass `GovernorMediator` for governed capability execution;
- treat memory, conversation context, recommendations, model confidence, OAuth scopes, or repeated success as permission;
- claim conceptual/strategy docs are implemented behavior;
- infer broad autonomy from OpenClaw runtime presence;
- expand Google domain-data access before the ordered gate permits it;
- use old PR test totals as proof of a reconciled branch;
- start B2, B3, B4, Wave C, #335 reconstruction, Google domain work, or Continuity runtime inside B1;
- manually edit generated runtime artifacts;
- publish `_MOCs/*` as part of B1 without separate review/authorization;
- direct work from a stale `current`, `next`, or `active` statement without checking the current truth surfaces first.

## Repo Truth Rule

Code is authoritative for implemented behavior. Tests and proof artifacts are evidence for the revisions/environments/scopes they actually cover. Generated runtime surfaces are authoritative for the exact mechanically measured claims they report. Hand-maintained operational docs establish current ordering and interpretation, but may go stale and must be reconciled when the repository changes.
