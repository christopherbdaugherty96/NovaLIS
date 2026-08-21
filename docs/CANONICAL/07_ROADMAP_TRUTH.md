# 07 — Roadmap Truth

**Status: current ordering summary.**

This file does not redesign Nova's roadmap. It reconciles the current stabilization gate around the existing roadmap and points to the master ordering document.

## Ordering authority

- [`../future/NOVA_MASTER_ROADMAP_2026-07-05.md`](../future/NOVA_MASTER_ROADMAP_2026-07-05.md) remains the long-lived ordering authority.
- Issue #343 is the current detailed stabilization checkpoint/order.
- Lane-specific lock/spec documents remain scope authority for their lane.
- Explicit reviewed owner authorization remains required to activate implementation where the governing lane requires it.

Ordering and scope are distinct:

```text
roadmap / Issue #343 -> what comes before what
lane contract         -> what the lane may change
implementation/proof  -> what actually changed and was verified
```

## Current checkpoint — 2026-08-20

Current active stabilization lane: B1

```text
A1 — COMPLETE / MERGED via #353
A2 — COMPLETE / MERGED via #355
B1 — ACTIVE; source/truth corrections complete; mechanical proof required
B2 — BLOCKED
B3 — BLOCKED
B4 — BLOCKED
C  — BLOCKED
```

Current merged `main` / A2 comparison base:

```text
060380f2e8c6437ff888773f0078647547ff4622
```

Accepted B1 implementation/truth-harness checkpoint after third-pass static review:

```text
b43a3989527e1c20892694b307351948a6129727
```

Handoff-only operational-document commits may advance the B1 branch after that implementation checkpoint. The mechanical proof pass must verify and record the actual branch HEAD used for execution.

Neither the current branch HEAD nor `b43a398...` is a `validated_baseline_sha`.

## Merged stabilization state

The following August truth/routing packages are already merged and are not pending roadmap items:

```text
#337 / #338  P1-A commitment/capability truth
#339         P1-B receipt-correlated session action/outcome history
#340         Cap 19 outcome truth
#341 / #344  explicit weather-location preservation / WebSocket repair
#345         brightness outcome truth
#346         turn-down-volume routing/wording
#347         current-information freshness/source-boundary routing
#348         broad awareness follow-up interpretation
#349         Calendar source-selection overmatch repair
#350         Calendar tomorrow-scope preservation
#351         local schedule-cancellation routing
#352         private Drive source-selection truth
#353         Wave A1 operational truth synchronization
#355         Wave A2 strategy reconciliation
```

Merged implementation is not identical to universal product readiness or unlimited live-proof scope. Capability verification must remain evidence-specific.

## Google Workspace Foundation state

PR #335 remains:

```text
OPEN
DRAFT
UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

It must not be merged in its historical branch state. It will be reconstructed/reconciled only after Wave C establishes an exact validated baseline, then undergo exact-head proof and independent review before a separate merge decision.

## Current stabilization gate

The roadmap itself remains intact. The current gate is:

```text
WAVE A — truth reconciliation
  A1 operational truth synchronization              COMPLETE
  A2 strategy reconciliation                        COMPLETE

WAVE B — truth-integrity repairs
  B1 runtime-truth instrumentation                  ACTIVE / PROOF GATE
  B2 capability narration                           BLOCKED
  B3 memory governance                              BLOCKED
  B4 reproducibility hygiene                        BLOCKED

WAVE C — proof and stabilization checkpoint         BLOCKED
  exact candidate baseline
  repaired runtime-truth regeneration
  supported proof matrix
  semantic-contract regression
  current local-inference benchmark / Issue #227
  reproduced-defect-only fixes
  immutable validated baseline
  reconstruct #335
  OAuth hardening cases
  exact-head #335 verification
  independent security/architecture review
  separate merge decision
```

After Wave C and only after a separate #335 merge decision:

```text
Google identity-only live proof
-> Google Tasks READ / first real provider-backed Google evidence vertical
-> evidence-based Operational Continuity warrant
```

## Wave A1 — completed gate

A1 synchronized active operational/canonical truth against the already-merged August stabilization work and corrected the three-control-plane/current-truth doctrine.

A1 changed documentation/current-truth surfaces only. It did not authorize later runtime lanes.

## Wave A2 — completed strategy reconciliation

A2 separately reconciled the consolidated August Product/Platform strategy against the truthful operational baseline while keeping strategy and current-state documentation distinct.

The durable strategy package is:

```text
NOVA_PRODUCT_PLATFORM_DIRECTION_2026-08-17.md
NOVA_PRODUCT_VALIDATION_PROTOCOL_2026-08-17.md
NOVA_STRATEGIC_DOCUMENT_STATUS_INDEX_2026-08-17.md
```

The governed-protection-wall concept remains long-term security/digital-sovereignty reference material. It does not silently become present roadmap authority or replace Nova's current product identity.

## Wave B — truth-integrity repairs

Wave B is intentionally split into focused PRs rather than one broad stabilization branch.

### B1 — runtime-truth instrumentation

**Current active lane; source changes frozen for mechanical proof unless execution reproduces a concrete defect.**

B1 source/truth-harness work now covers:

```text
requests-based network discrepancy visibility
connections_api.py explicit local_administrative_health_probe classification
Phase 9 live import/symbol evidence
behaviorally_active_v2 fingerprint coverage
exact hash/count path-set semantics
qualified generated invariants/network wording
operational-truth consistency checker
canonical-index lane checking + regression
generator-entrypoint integration regression
```

The remaining B1 work is not more static design. It is:

```text
verify exact checkout / HEAD
-> execute focused B1 + existing auditor/governance-doc tests
-> run operational consistency + runtime-doc drift checks
-> mechanically run scripts/generate_runtime_docs.py
-> inspect CURRENT_RUNTIME_STATE.md / BYPASS_SURFACES.md / RUNTIME_FINGERPRINT.md
-> exact A2-base -> final-B1 diff review
-> only then open a draft B1 PR
```

The checked-in generated runtime artifacts remain pre-B1 until that generator step actually executes. Manual edits are forbidden.

### B2 — capability narration

**Blocked until B1 completes its separate proof/review/merge decision.**

Separate:

```text
exists
enabled
configured
verification_status
available_on_this_path
requires_approval
authority_class
```

`authorized` is request-specific and must not be static capability metadata.

### B3 — memory governance

**Blocked until B1 completes.**

Define ordinary GeneralChat persistence boundaries and explicit-vs-observed precedence/provenance. This is a future runtime behavior repair, not B1 work.

### B4 — reproducibility hygiene

**Blocked until B1 completes.**

Make dependency source-of-truth unambiguous, including the current `python-multipart` declaration mismatch.

## Wave C — validated-baseline checkpoint

Wave C turns a candidate commit into a validated baseline only after the required proof completes.

Important distinction:

```text
current HEAD != candidate baseline != validated baseline
```

The validated baseline is immutable evidence for a verification package. It is not expected to remain current HEAD forever.

Wave C also re-evaluates Issue #227 using current model/context/hardware/latency evidence rather than May assumptions.

Only reproduced failures are repaired. Acceptance failure must be classified before root cause is assigned.

## Issue #354 — hosted CI infrastructure

Issue #354 remains:

```text
infrastructure/open
zero-step hosted GitHub Actions
not behavioral pass/fail evidence
```

This is separate from B1 content/runtime semantics. It must be resolved before Wave C depends on hosted CI for the validated-baseline proof package.

## Operational Continuity strategic ordering

Operational Continuity remains **strategically accepted / inactive / not implementation-authorized**.

It is the future product model for persistent reconciled state around Awareness, Decision, Authority, Execution, and Outcome. It is not a sixth authority system.

A future Continuity slice requires its own:

- evidence-based warrant;
- exact scope;
- persistence/provenance contract;
- authority/non-authority boundaries;
- tests;
- implementation authorization;
- fresh-main proof.

Continuity may never:

- authorize;
- execute;
- change permission;
- manufacture commitments;
- silently reopen decisions;
- convert learned behavior into authority.

## Google permanent boundary

```text
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
```

OAuth proves provider permission/technical eligibility, not Nova authorization for an exact action.

Google evidence/actions must reuse Nova's provenance, request-acceptance, effect-verification, and outcome distinctions rather than introduce a second success model.

## Deferred until Wave C exits

Do not begin:

```text
Google Tasks domain work
Gmail expansion
Google Calendar writes
Operational Continuity runtime
broad multi-provider routing
large graph/memory infrastructure
predictive learning
multi-agent orchestration
broad browser/computer-use
expanded OpenClaw autonomy
autonomous business operation
broad SaaS productization
Protection Wall runtime expansion
```

README/front-door sequencing cleanup is separate documentation debt and must not be folded into the B1 instrumentation branch.

## Historical context

The seven-morning observation threshold, grounded brief/category routing, Commitment Truth, Local Action Outcome Truth, Semantic Substrate Slice 1, and the August 12 acceptance-derived P1 repairs are historical inputs to the current state. Their old `current` or `next` wording is superseded by the stabilization gate above.

Historical records remain evidence of what was decided or proven at their date. Do not use their old current-main SHAs or pending-work language to select today's work.
