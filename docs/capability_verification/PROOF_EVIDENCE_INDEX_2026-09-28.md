# Nova Proof Evidence Index

Last reviewed: 2026-09-28  
Repository reference for this review: `origin/main@486ad3dddc3f75412085b968c28561ab57e25686`

## Purpose

This index keeps screenshots, automated checks, repository inspection, and release acceptance
from being conflated. Evidence supports only the behavior, revision, environment, and claim it
actually exercised. Generated runtime documents remain authoritative only for the properties their
generators inspect.

## Current evidence posture

| Evidence | What it supports | What it does not support |
| --- | --- | --- |
| PR #438 first Synthetic Beta Cohort v1 | Test-only cohort evidence for the candidate it exercised | Product acceptance, a clean Windows install, or security certification |
| PR #439 connected-user cohort expectation correction | Correction of the cohort route expectation on current main | A rerun against a new accepted candidate |
| Generated runtime truth | Mechanically inspected registered runtime properties | Uninspected direct paths, user acceptance, or release readiness |
| `docs/demo_proof/2026-04-28_user_test/` | Historical visible UI states from that date | Current main, source provenance, installer integrity, local-boundary security, authority, or beta acceptance |

## Known pre-acceptance boundary

A confirmed P1 affects the local-only boundary: if `NOVA_HOST` accepts a non-loopback bind, the
HTTP/WebSocket locality checks can trust attacker-controlled `Host`/`Origin` values rather than
the peer address. This means Nova must remain on the default loopback-only configuration; LAN or
internet exposure is unsupported. The bounded repair and fresh security proof are required before
a Windows acceptance run or a new accepted candidate.

This index records the boundary; it does not claim the repair has landed.

## Evidence required for a new candidate

1. Record the exact source SHA and candidate artifact identifier/hash.
2. Run the focused local-boundary/security tests and current truth checks after the P1 repair.
3. Run installer, supply-chain, privacy/Data-Out, and secrets checks with their actual output.
4. Perform clean Windows operator proof against that exact artifact, with environment and
   operator recorded.
5. Re-run Issue #434's frozen cohort against the accepted candidate; retain failures and results.
6. Treat three non-developer users as a later acceptance input, not as a substitute for the
   technical/security evidence above.

## Screenshot standard

New captures must name the source SHA, artifact identifier/hash if applicable, environment, date,
operator, and narrow UI claim. Pair a visual action claim with its approval/blocked state and
receipt when available. Redact personal data and secrets. Never use a screenshot alone to claim
security, release provenance, authorization correctness, persistence behavior, or an external
outcome.

Related guidance:

- [`docs/product/PROOF_CAPTURE_CHECKLIST.md`](../product/PROOF_CAPTURE_CHECKLIST.md)
- [`docs/product/SCREENSHOT_ASSET_PLAN.md`](../product/SCREENSHOT_ASSET_PLAN.md)
- [`docs/current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md)
