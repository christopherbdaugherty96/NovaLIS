# SEQ2 Roadmap Reconciliation

Date: 2026-10-27  
Baseline: `main@9b04979944e82bcabaa1c4baf242b6275b138ba1`  
Status: accepted documentation reconciliation; no runtime or authority change

## Decision

T1 is complete. PR #475 was squash-merged into `main` at the baseline above after exact-head
independent review, successful required checks, and review-thread resolution.

The current work order is `OWNER_OPERATING_SEQUENCE_2026_10_27`:

```text
COMPLETE: D1
COMPLETE: F9b
COMPLETE: SEQ1
COMPLETE: T1
COMPLETE: SEQ2
NEXT: provider-neutral Data-Out
THEN: approved stronger-model access
THEN: Morning Brief + Topic/Story Watch
THEN: SF + NL1
THEN: owner-use acceptance
THEN: REL1 + installer + clean Windows proof + outside users
```

The fixed November 13 review date is removed from current planning. The October 23 sequence is
retained only as historical provenance. Every downstream implementation lane requires a separate
owner authorization; this reconciliation grants no new capability or execution authority.

Shopify, Auralis Digital, and persistent business assistance remain deferred product goals. They
are not activated lanes.

## Preserved product and branch inputs

- Issue #463's fixed three-person/four-week trial plan is superseded as current sequencing. Its
  product intent remains useful, including the Auralis Digital horizon; the issue is not edited by
  this reconciliation.
- PR #459's minimal Continuity acceptance language is a useful product contract, but PR #459 is
  open and unmerged. Preserve its requirements as future acceptance input without treating its
  branch or obsolete ordering as runtime truth.
- PR #432 is the highest-value targeted branch-recovery reference because it contains capability-
  truth test intent absent from current `main`. Any recovery requires a separate present-runtime
  review and a fresh branch from current `main`; do not merge its historical patch wholesale.
- PR #435 is a non-authorizing design reference for future Data-Out/Data-In receipts and a reusable
  credential/permission broker. It does not authorize implementation.
- PR #445 is separate dependency maintenance and is not part of SEQ2.

Historical branches remain untouched. No bulk merge, rebase, cherry-pick, deletion, or cleanup is
authorized by this decision. Any selective recovery must first demonstrate a current gap, account
for the repository's history-rewrite and source-hygiene risks, and receive separate authorization.

## Boundary

SEQ2 changes documentation, the operational-order consistency checker, and focused checker tests
only. It does not implement Data-Out, connect a stronger model, expand connectors, alter the
Governor or capability registry, start branch recovery, or authorize distribution.
