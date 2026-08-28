# Nova Canonical Truth — Index

Last reconciled: 2026-08-28.

This folder is a thin **navigation and reconciliation layer**. It does not create runtime facts. Each canonical file summarizes one kind of truth and points to the implementation, generated artifact, proof, or maintained status surface that supports it.

## Authority and evidence order

There is no single artifact that is automatically authoritative for every kind of claim.

Use the source appropriate to the claim:

1. **Implementation:** running code in `nova_backend/` determines what behavior is implemented.
2. **Automated/recorded evidence:** tests, proof packets, and live-verification artifacts are evidence for the revision, environment, and scope they actually exercised.
3. **Mechanically generated runtime claims:** `docs/current_runtime/` — authoritative only for the properties each generator actually measures.
4. **Current ordering / operational interpretation:** current canonical/status/priority documents and Issue #343.
5. **Design / strategy / future / archive:** intent, constraints, and history; never proof of current implementation or authority.

Generated documents can become incomplete or misleading when their generators have incomplete coverage. A generated PASS must not be expanded into a claim the generator did not test.

## Current development interpretation

The current post-#394 boundary supersedes older ordering language later in this file:

```text
#388 COMPLETE
#368 COMPLETE
#387 COMPLETE / DOCS-ONLY
#393 COMPLETE / EXACT-HEAD PROOF POLICY
#394 GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
main at reconciliation start: 691a397d14e93c1e0607a73de2ab54b9bbfc3cc2

PR #335: OPEN / DRAFT / UNMERGED / UNTOUCHED
PR #335 implementation path: SUPERSEDED BY MERGED PR #394

NEXT: Google identity-only live proof
LATER, SEPARATELY AUTHORIZED: Google Tasks READ -> minimal Continuity -> owner daily-use proof
```

This synchronization adds no capability or authority. The identity proof is provider-backed
verification of the merged foundation only. Issue #343 must use this same boundary; its older
#368/#387/#335 sequence is obsolete.

### Historical pre-#394 development interpretation

Wave A1 operational truth synchronization is complete and merged through PR #353:

```text
f25c798c7cb488495a343068463e9214cab0a763
```

Wave A2 strategy reconciliation is complete and merged through PR #355.

Wave B1 runtime-truth instrumentation is complete and merged through PR #356. Post-B1 operational truth sync #357 is also merged. Wave B2 capability narration is complete and merged through PR #358. Wave B3 memory governance is complete and merged through PR #360. Wave B4 reproducibility hygiene is complete and merged through PR #362. Post-B4 operational truth sync #363 established the Wave C initial candidate. Wave C then merged through PR #364 at reviewed head `786c048df6dc4ed8f3c8245c5b365d4296f342f4`; its squash merge established the immutable validated baseline:

```text
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
```

PR #365 then recorded the validated-baseline/evidence-waiver state in documentation without changing the validated runtime baseline:

```text
post_wave_c_sync_sha: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
```

`d5b0dc66...` is durable provenance for PR #365 and the PR #366 branch base, not a forever-current `main` claim. Current HEAD must be resolved from Git/repository state when needed.

POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE. PR #366 is merged truth-hygiene provenance and PR #378 is the merged/verified narration/front-door package:

```text
PR #366 squash merge: 4ddd46ad0c3e3c5db55e006680f4a426956581c1
PR #378 reviewed head: 84222288335c399c1ffa73186858e8ba84e9a64a
PR #378 squash merge: 67c3d8fd10e013eef466769cd4c8d96f75d27845
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
#368: COMPLETE
#387: COMPLETE / DOCS-ONLY
PR #335 implementation path: SUPERSEDED BY MERGED PR #394
PR #335 state: OPEN / DRAFT / UNMERGED
```

Neither PR #366 nor PR #378 establishes a new runtime validated baseline. Documentation closeout completion does not authorize #335 reconstruction, Google implementation, or any authority expansion.

Wave C is complete and merged. The complete non-hosted proof passed on exact validated baseline `ec20a714...`; GitHub-hosted jobs did not execute because of the external account-billing restriction recorded in Issue #354. The owner explicitly waived hosted execution as a Wave C exit requirement without classifying those jobs as PASS. The later documentation-only #365/#366/#378 commits do not extend that runtime proof to a new baseline.

B1 through B4 and Wave C are complete. Their proof packages remain evidence only for the revisions, environments, and mechanisms actually exercised.

Current order is summarized in `07_ROADMAP_TRUTH.md` and detailed in Issue #343:

```text
Wave A1 operational truth sync                 COMPLETE
-> Wave A2 strategy reconciliation             COMPLETE
-> B1 runtime-truth instrumentation             COMPLETE / MERGED
-> B2 capability narration                      COMPLETE / MERGED
-> B3 memory governance                         COMPLETE / MERGED
-> B4 reproducibility hygiene                   COMPLETE / MERGED
-> Wave C validated-baseline proof checkpoint   COMPLETE / MERGED / VALIDATED
-> post-Wave-C documentation closeout           COMPLETE
   truth-hygiene provenance: PR #366 MERGED
   narration/front-door package: PR #378 MERGED / VERIFIED
-> #388                                         COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
-> #368                                         COMPLETE
-> #387                                         COMPLETE / DOCS-ONLY
-> #393                                         COMPLETE / EXACT-HEAD PROOF POLICY
-> #394                                         GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
-> historical PR #335 implementation path       SUPERSEDED BY MERGED PR #394
-> Google identity proof
-> first Google READ/evidence vertical
-> evidence-based Continuity warrant
```

Issue #354 remains an external account/billing infrastructure issue. Its zero-step jobs are `NOT EXECUTED`, not behavioral PASS or FAIL. The owner waived that evidence source for the Wave C baseline; the issue remains separate from Nova runtime truth.

## The canonical truth files

| # | File | Question it answers |
| --- | --- | --- |
| 01 | [01_PROJECT_TRUTH.md](01_PROJECT_TRUTH.md) | What is Nova intended to be? |
| 02 | [02_RUNTIME_TRUTH.md](02_RUNTIME_TRUTH.md) | What runtime surfaces exist now? |
| 03 | [03_GOVERNANCE_TRUTH.md](03_GOVERNANCE_TRUTH.md) | What governance/control-plane boundaries exist and what is actually enforced? |
| 04 | [04_CAPABILITY_TRUTH.md](04_CAPABILITY_TRUTH.md) | Which capabilities exist, and what do their states mean? |
| 05 | [05_FRONTEND_BACKEND_TRUTH.md](05_FRONTEND_BACKEND_TRUTH.md) | How is the code laid out, front and back? |
| 06 | [06_TEST_AND_PROOF_TRUTH.md](06_TEST_AND_PROOF_TRUTH.md) | What evidence exists, what revision/environment does it cover, and how current is it? |
| 07 | [07_ROADMAP_TRUTH.md](07_ROADMAP_TRUTH.md) | What is next, and what gates it? |
| 08 | [08_ARCHIVE_POLICY.md](08_ARCHIVE_POLICY.md) | What counts as historical, and how is it treated? |

## Label vocabulary

- **runtime-backed** — supported by implementation and/or a mechanically relevant runtime check.
- **generated** — emitted by a script; scope is limited to what that script actually measures.
- **current** — hand-maintained and deliberately reconciled with current repository state.
- **live-proven** — observed against a specified running revision/environment.
- **historical proof** — valid evidence for an earlier revision/environment, not a claim about current HEAD.
- **unverified** — implemented or claimed but lacking the required proof for the statement being made.
- **superseded** — replaced as current guidance; retained only for history/reference.
- **historical** — a record of a past state; never a statement about today.

## Permanent truth distinctions

Keep these separate across all canonical files:

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
request acceptance != verified effect
memory != Operational Continuity
current HEAD != immutable validated baseline
```

## Relationship to other entry points

- [`../INDEX.md`](../INDEX.md) — goal-based router into the docs set.
- [`../../REPO_MAP.md`](../../REPO_MAP.md) — engineering navigation.
- [`../FULL_DOCUMENTATION_MAP.md`](../FULL_DOCUMENTATION_MAP.md) — deep discoverability map.
- [`../status/DAILY_COMMAND_CENTER.md`](../status/DAILY_COMMAND_CENTER.md) — current operational surface.
- [`../../AGENTS.md`](../../AGENTS.md) — agent entry point.
