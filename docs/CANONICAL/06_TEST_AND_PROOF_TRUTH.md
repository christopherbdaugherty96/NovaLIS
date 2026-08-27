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

## Current validated-baseline proof posture — 2026-08-27

Wave A1/A2, Wave B1-B4, and Wave C are complete. Wave C established one immutable validated
runtime baseline after its required exact-revision non-hosted proof package:

```text
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
```

That SHA is evidence for the revision, environments, and proof package actually exercised. It is
not a permanent alias for current HEAD. Later documentation, truth-checker, terminology, and
roadmap merges do not create a new runtime-validated baseline.

GitHub-hosted Actions did not execute because of the external account/billing restriction tracked
in Issue #354. The owner waived hosted execution as mandatory Wave C exit evidence without
classifying those zero-step jobs as PASS. The complete required non-hosted package passed on the
exact baseline above.

```text
hosted proof: NOT EXECUTED
behavioral PASS from hosted jobs: NO
behavioral FAIL from hosted jobs: NO
repository workflow defect indicated: NO
Issue #354: OPEN / DEFERRED
```

The waiver is historical Wave C disposition, not a blanket waiver for future security-sensitive
work. PR #335 remains open/draft/unmerged and pending a separate owner decision; this proof posture
does not authorize its reconstruction, Google work, or any merge.

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

Wave B1 added the separate bounded operational-truth consistency check at
`python scripts/check_operational_truth_consistency.py`. Its PASS remains limited to the surfaces
and invariants the checker explicitly reports.

## Wave C proof shape — completed historical contract

Wave C used the following proof shape to establish the immutable baseline above:

1. freeze one exact candidate code commit;
2. regenerate repaired runtime truth against that exact candidate;
3. run the strongest supported proof matrix in each environment without inventing unsupported cross-platform evidence;
4. run semantic-contract regression across intent, reference binding, evidence relevance, execution truth, lifecycle state, capability narration, memory persistence/provenance, source scope, and temporal scope;
5. prioritize metamorphic/invariant tests, including paraphrase and scope-preservation cases;
6. re-evaluate Issue #227 against the actual current local inference stack;
7. fix only defects that reproduce;
8. record an immutable validated baseline only after the required package passes.

Future work may reuse this evidence discipline, but it must execute and record the checks required
for its own exact revision. It may not inherit behavioral PASS merely because it descends from the
Wave C baseline.

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

## Accepted non-hosted exact-head proof path

When hosted CI is unavailable for external infrastructure/account reasons, a bounded package may
use the following owner-accepted proof path. Every applicable item must refer to the same exact
candidate revision:

1. record the exact candidate SHA;
2. use a clean isolated worktree;
3. define and execute focused tests appropriate to the change;
4. define and execute broader regression tests where applicable;
5. run Ruff on the applicable source/test scope;
6. run structural/runtime proof where applicable;
7. run dependency consistency where applicable;
8. run operational-truth consistency;
9. run runtime-document drift;
10. run diff hygiene and review the exact changed-path scope;
11. retain recorded outputs tied to the same candidate SHA;
12. perform an independent exact-head review;
13. merge only with expected-head protection;
14. classify unavailable hosted CI explicitly as `NOT EXECUTED`, never PASS; and
15. require separate owner merge authorization.

Applicability must be stated rather than silently omitted. A docs-only package may have no focused
runtime tests; a security-sensitive runtime package requires stronger focused, broader, and live
evidence. Proof from different SHAs must not be assembled into one final-candidate claim.

Issue #354 remains open/deferred as external account/billing infrastructure debt. Current evidence
does not indicate a repository workflow defect, so this policy authorizes no workflow rewrite.
Required hosted checks must not be enabled while those jobs are guaranteed to execute zero steps;
that would create a permanently blocked gate rather than trustworthy proof. Revisit branch/review
protection and required checks when an actually executable hosted or self-hosted CI path exists.

This process policy does not authorize PR #335 reconstruction, Google/OAuth implementation,
Operational Continuity, capability or authority expansion, GitHub billing changes, branch-setting
changes, or any merge.

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
