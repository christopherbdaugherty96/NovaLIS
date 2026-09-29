# Nova Beta Freeze Criteria

Date: 2026-09-03  
Reconciled: 2026-09-18 against `main@aa39515fbcf0e961fb71e2ff468d97145435dadd` (post-#423)  
Status: Product decision / non-authorizing until merged

## Decision

Preserve these distinctions:

```text
architecture truth != product value
product promise != product proof
product proof != platform
```

Nova's engineering doctrine remains binding internally, but outside-user evidence becomes the priority once Nova is safe enough to test as a product.

## User-facing promise

> **Nova helps keep track of what matters, tells you what’s next, acts only within the authority you give it, and shows you what happened.**

`Authority you give it` includes standing bounded authority under Nova's governed model. Nova does not require a new prompt for every operation already within that authorization; it asks when additional approval is required.

Full long-horizon Operational Continuity is not implemented, so do not claim Nova remembers everything.

## Hard blockers

These block candidate freeze or outside-user distribution regardless of P-level label:

- unauthorized external effect;
- false execution/success claim;
- silent loss or corruption of authoritative user state;
- silent failed restore presented as success;
- secret exposure;
- materially false authority/capability wording that can mislead a user about what Nova can do.

A hard blocker is never averaged away by otherwise successful tests or positive feedback.

## Freeze condition

Freeze an exact private-beta candidate SHA only when:

```text
#406 governed-memory correctness resolved
+
#408 durability/state-ownership decision accepted
+
minimum durability/recovery implementation passes the accepted #408 contract
+
clean supported-Windows install/upgrade/startup proof passes on the candidate revision
+
no known hard trust/state blocker
+
no known P0/P1 beta blocker of any category
=
FREEZE EXACT BETA CANDIDATE SHA
```

Once this condition is met, stop adding capabilities, architecture, or stabilization work unless the candidate fails a required acceptance test.

Freeze is a stop condition, not a claim of beta success.

## Exact frozen-SHA gate

### Controlled technical-validation exception

Once the [technical-alpha protocol](2026-09-29-technical-alpha-protocol.md) is reviewed and
merged, its designated external technical operators may receive an exact experimental artifact
to obtain clean-Windows evidence before this frozen-candidate gate. This requires the protocol's
security, distribution-permission, reporting, and artifact-specific owner authorization gates.
Hard blockers remain binding. Technical operators are not product-cohort participants for this
evidence, and their reports do not establish product acceptance. Before acceptance, artifact
delivery remains private and access-controlled to the protocol's named technical operators.
Public artifact listings/downloads require clean-Windows proof, normal frozen-candidate acceptance,
and the owner acceptance/distribution decision. Ordinary product users remain gated below.

### Product distribution

Before any ordinary product tester receives the candidate (outside the controlled technical-validation exception above), rerun acceptance against the **exact frozen SHA and intended distribution artifact** without changing code:

- full hero loop from startup through awareness, recommendation, governed action/outcome, and end-of-day use;
- relevant degraded/failure behavior;
- restart/recovery behavior;
- #408-required durability/recovery checks;
- secret/privacy/support-artifact review;
- version/build identity and supported-platform truth;
- clean Windows install/startup from the intended beta distribution path;
- confirmation that no hard blocker or P0/P1 beta blocker remains open.

If a hard acceptance check fails:

```text
DO NOT DISTRIBUTE
-> reopen only the failed lane
-> correct it
-> create a new candidate SHA
-> rerun exact-SHA acceptance
```

Never silently patch a frozen candidate artifact.

## Minimum durability meaning

The exact implementation is selected by #408. The beta contract must cover the user state people are asked to depend on, including as applicable:

- canonical durable-state ownership/location;
- backup/recovery and truthful partial-restore behavior;
- migration/recovery for persisted-state changes;
- machine-bound secret handling;
- privacy boundaries for backup/support artifacts;
- no silent authoritative-state loss or corruption.

This decision does not mandate SQLite or another storage technology.

## First outside-user proof

Use one frozen, accepted candidate.

```text
3 non-developer users first
-> if no hard blocker, expand to 5 total
-> evaluate the provisional gate after 5 completed journeys
```

After five completed journeys, provisional signals are:

- at least 4/5 install without direct developer intervention;
- at least 4/5 complete the hero workflow;
- at least 4/5 can correctly explain what Nova did and did not do;
- at least 3/5 voluntarily use Nova again within several days;
- setup time, time to first useful answer, rephrase rate, confusion points, and missing-evidence expectations are recorded.

If fewer than five journeys are complete, report only preliminary observations; do not claim the 4/5 or 3/5 gates were evaluated.

Do not add silent telemetry for this cohort. Manual/local evidence is sufficient.

## Tester questions

Record:

1. Did they install Nova without developer intervention?
2. Did they understand what Nova is for?
3. Did they know what to ask without coaching?
4. Did the hero flow provide real value?
5. Did they understand what Nova did, did not do, and was not allowed to do?
6. Did Nova retain enough relevant state to stay useful?
7. What did they expect Nova to know that it did not know?
8. What forced rephrasing, setup help, or developer intervention?
9. Did they return on another day without prompting?
10. What caused them to stop using Nova or distrust an answer?

## Evidence selects the next lane

```text
Missing real-day evidence repeats
-> consider one separately reviewed read-only provider lane.

Ongoing context/open-loop failures repeat
-> consider the smallest evidence-warranted Continuity slice.

Install/recovery failures repeat
-> continue release/durability work.

Users install but do not return
-> treat as a product-value/workflow failure, not an architecture deficit.

Users return and depend on the hero loop
-> expand the cohort before expanding architecture.
```

Do not add capabilities because they are merely technically possible.

## Current execution order

```text
COMPLETE: #407 operational-truth sync
COMPLETE: #406 governed-memory correctness
COMPLETE: #408 durability/state-ownership decision
COMPLETE: durability implementation lanes 1-4 through trustworthy versioned snapshot capture
COMPLETE: #409 release-integrity / repository-control lane (PR #423; main `aa39515fbcf0e961fb71e2ff468d97145435dadd`)
CURRENT: merge this decision note after current-main rebase and exact-head review
THEN: separate owner authorization decision for recovery construction (Lane 5A)
THEN: separately authorized recovery proof: inactive candidate migration -> candidate validation -> activation -> rollback/restore semantics
THEN: one bounded beta product-translation/readiness pass over existing user-facing surfaces
THEN: clean Windows operator proof against the actual user-facing build
THEN: freeze exact beta candidate
THEN: exact frozen-SHA acceptance
THEN: 3-user initial rollout
THEN: expand to 5 if no hard blocker
THEN: evidence-selected next development
```

Recovery remains separately owner-gated. This decision note does not authorize Lane 5A or any later implementation lane.

## Beta product-translation/readiness boundary

Before clean-Windows certification, run one bounded readiness pass over existing user-facing surfaces so the machine proof exercises the same onboarding, claims, defaults, and UI that outside users will receive. Ground that pass in accepted #408/runtime truth and limit it to existing surfaces such as `PRODUCT_DEFINITION.md`, README, `FIRST_RUN.md`, `FIRST_5_MINUTES.md`, active runtime/landing/onboarding language, minimum visible trust/failure wording, local-data/privacy wording, and removal of creator-specific runtime assumptions that remain in user-facing defaults.

This is not a new strategy document, architecture initiative, capability lane, provider expansion, or authorization for broader product work.

## Non-goals

This decision does not authorize new capabilities, broad provider work, Operational Continuity without evidence, full SQLite migration, broad OpenClaw/computer-use expansion, voice expansion, telemetry, public-beta publication, repository-visibility changes, or platform/ecosystem work.

## Permanent rule

> **Once Nova is safe enough to test as a product, outside-user evidence outranks additional internal architectural refinement.**
