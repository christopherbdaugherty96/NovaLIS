# 06 — Test and Proof Truth

**Status: current evidence map.**

Tests, generated proof, proof packets, live verification, and validated baselines are different evidence classes. None should be silently substituted for another.

## Evidence genres

| Evidence | What it proves | Important limit |
| --- | --- | --- |
| Runtime/unit/integration tests | behavior covered by those tests on the tested revision/environment | passing tests do not prove untested semantics or live-provider behavior |
| Generated runtime truth | properties mechanically inspected by the generator | cannot prove properties the generator does not inspect |
| Structural runtime smoke | selected imports/routes/registry/governance structure | not comprehensive behavioral validation |
| Implementation proof packet | what a bounded package proved when recorded | dated evidence; not automatically current proof |
| Live verification / acceptance | observed behavior on a specified running build | limited to the exact cases/environment exercised |
| Candidate baseline | exact commit selected for final proof | not validated yet |
| Validated baseline | exact commit after the required proof package passes | immutable evidence record; not a permanent alias for current HEAD |

## Existing evidence folders

These remain intentionally separate:

| Folder | Genre |
| --- | --- |
| [`../PROOFS/`](../PROOFS/) | implementation proof packets |
| [`../demo_proof/`](../demo_proof/) | demo / walkthrough evidence |
| [`../capability_verification/`](../capability_verification/) | observed capability verification |

Do not merge these genres merely for tidiness; the distinction preserves epistemic meaning.

## Current stabilization proof posture — 2026-08-20

The August stabilization implementation packages through PR #352 have merged. Their PR bodies/tests provide bounded package-level evidence, including P1-A/P1-B truth repairs, local outcome-truth repairs, weather/location routing, current-information routing, Calendar scope/selection, schedule cancellation, and private Drive source selection.

That is **not yet one unified validated baseline**.

At the start of Wave A1, merged `main` was:

```text
1a517d8832a2c834c80b10a7062bed878f6312cc
```

This SHA is the A1 planning checkpoint only. It must not be labeled `validated_baseline_sha` merely because it is current or because individual PR checks passed.

Wave C will later choose an exact candidate commit and run the required proof matrix. Only after those checks complete may Nova record:

```text
validated_baseline_sha
validated_at
verification package
supported-environment scope
known exceptions
remaining defects
```

That record is immutable evidence for the tested baseline. Future HEAD may move beyond it.

## Historical full-suite evidence

A complete merged-main suite was recorded on 2026-07-27 after PRs #315/#316:

```text
3799 passed
exit code 0
6:46
```

That remains valid historical evidence for that revision. It is **not** proof that the current August 20 codebase has passed that same exact full-suite package.

Later PRs include their own focused/broader/full-suite results. Those totals are evidence for those PR heads/bases and must not be copied forward as proof of a future reconciled #335 or Wave C candidate.

## Structural runtime proof

`python scripts/prove_runtime_truth.py` is a structural smoke proof. A PASS does not by itself prove:

- semantic response correctness;
- evidence relevance;
- reference binding;
- temporal/source scope preservation;
- live-provider success;
- complete network mediation;
- durable-memory governance;
- exact authorization semantics across every path;
- effect verification;
- cross-platform equivalence.

Use the script for what it measures; do not inflate its meaning.

## Runtime-document drift proof

`python scripts/check_runtime_doc_drift.py` remains useful for the narrow document/runtime relationship it checks. It must not be represented as complete consistency across all operational/canonical instructions.

Wave B1 is expected to add a separate operational-truth consistency check.

## Wave C required proof shape

After A1, A2, and the Wave B repairs, Wave C should:

1. freeze one exact candidate code commit;
2. regenerate repaired runtime truth against that exact candidate;
3. run the strongest supported proof matrix in each environment without inventing unsupported cross-platform evidence;
4. run semantic-contract regression across intent, reference binding, evidence relevance, execution truth, lifecycle state, capability narration, memory persistence/provenance, source scope, and temporal scope;
5. prioritize metamorphic/invariant tests, including paraphrase and scope-preservation cases;
6. re-evaluate Issue #227 against the actual current local inference stack;
7. fix only defects that reproduce;
8. record an immutable validated baseline only after the required package passes.

## Failure classification rule

A failed acceptance scenario does not establish its own root cause.

Before choosing a repair, classify the failure. Possible classes include:

```text
evidence quality / normalization
semantic inference / intent resolution
reference binding
source or temporal scope
ranking / selection logic
UX framing / narration
runtime execution behavior
persistence/lifecycle behavior
product-hypothesis failure
```

This keeps the proof framework falsifiable. Do not infer a specific root cause from the scenario structure alone.

The separate August Product/Platform validation package is Wave A2 input. A1 does not import its scenario doctrine into canonical proof truth.

## Semantic-contract regression doctrine

High-value invariants include:

```text
paraphrase should preserve intent
temporal wording should preserve temporal scope
private-source wording must not upgrade to public web
narration must not upgrade accepted_unverified to verified
reference wording must not bind to an unrelated prior object
model narration must not manufacture capability availability
connection or OAuth scope must not become Nova authority
```

## Environment truth

Report the strongest evidence actually supported by each environment.

For example:

```text
primary/full-suite environment:
  required full suite

Windows:
  supported Windows certification/adversarial coverage
  + explicit remaining full-suite gap, if any

live local environment:
  fresh-main real-user proof where required
```

Do not label unexecuted/zero-step CI as passing or failing test evidence. Infrastructure status is a separate fact.

## Proof currency rule

When using any proof artifact, record or inspect:

- exact revision;
- date;
- environment;
- test/acceptance scope;
- known exclusions;
- whether the claim is structural, automated-behavioral, or live-observed.

A newer timestamp on a copied or regenerated document does not automatically make the underlying behavioral evidence newer.

## Naming reconciliation

`PROOFS/Trust-Panel/` and current runtime references to an incomplete fuller Trust Panel can coexist: the earlier trust-page MVP proof is historical evidence for that bounded surface, while the broader Trust Panel concept remains a different scope. Preserve the distinction rather than forcing one boolean status.
