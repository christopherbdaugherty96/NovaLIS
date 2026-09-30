# NovaLIS

**Version 0.5 Alpha — Current State**

**Nova is a governance-first, local-first AI system that connects model intelligence to
bounded execution, explicit user authority, and inspectable outcomes.**

## A supported workflow today

On a configured development installation, ask:

> Draft an email to test@example.com about tomorrow's plans.

Confirm the governed draft action, then review the draft in your local mail client and inspect
the governed-action receipt. You review and send the message yourself: Nova does not send email.
A receipt records the governed action and available outcome evidence; opening a draft is not
proof that a message was sent.

This is one bounded workflow, not an autonomous assistant taking over your accounts.
[First 5 Minutes](docs/product/FIRST_5_MINUTES.md) describes more evaluation steps.

## Why use Nova alongside powerful models?

Models provide reasoning and language; Nova provides a governed local system around supported
tools, explicit memory, and action receipts. A recommendation is not permission, memory is not
authority, and an accepted request is not a verified outcome. Nova is not a replacement
foundation model or a universal interface to every model provider.

## Current maturity and limits

This alpha is preparing for private-beta validation, not an accepted or
distribution-ready beta. Usefulness and repeat use with outside users remain to be established.

- Local-first does not mean offline-only: configured search, data sources, and external
  reasoning paths may contact providers.
- Full Operational Continuity and broad autonomous execution are not implemented.
- Windows is the primary beta target; clean-machine acceptance remains outstanding.
- A known local-boundary P1 must be repaired and freshly proven before Windows acceptance.
  Do not expose the development server to a LAN or the internet.

## Evidence and current status

- [Daily Command Center](docs/status/DAILY_COMMAND_CENTER.md) — current gates and ordering.
- [Proof evidence index](docs/capability_verification/PROOF_EVIDENCE_INDEX_2026-09-28.md) —
  what the recorded evidence does and does not establish.
- [Canonical Truth Index](docs/CANONICAL/00_INDEX.md) — how to distinguish implementation,
  measured evidence, and future direction.
- [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md) — generated claims,
  limited to the properties its checks measure.
- [Detailed readiness sequence](#current-post-405-beta-readiness-order--2026-09-20) — preserved
  engineering gates and proof history below.

## Why Nova
Most assistants wait for a command. Nova is being built to establish what changed, what matters,
what remains uncertain, and which decision deserves attention before choosing whether a tool is
relevant.

Its permanent architectural model is:

```text
Awareness -> Decision -> Authority -> Execution -> Outcome
```

Capability is a property of the governed runtime: what Nova can technically do. It is not
permission. Authority decides whether an exact action may occur. In Nova’s target architecture,
Outcome is responsible for verifying what actually happened and reconciling it into future
awareness without expanding permission.

The intended operating loop is:

```text
Observe -> build awareness -> identify relevance -> expose uncertainty -> recommend
-> authorize -> execute -> evaluate outcome -> reconcile -> record
```

Intelligence proposes. Nova governs. You decide.

Canonical ordering authority for all future work:
- [Nova Master Roadmap 2026-07-05](docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md)

Canonical future-product summary:
- [Nova Authority and Decision OS Direction](docs/future/NOVA_AUTHORITY_AND_DECISION_OS_DIRECTION_2026-07-28.md)

See:
- [Product Definition](docs/product/PRODUCT_DEFINITION.md)
- [Nova Two-Domain Direction](docs/future/NOVA_TWO_DOMAIN_DIRECTION_2026-05-11.md)
- [Nova Creator-Led Shopify POD Model](docs/future/NOVA_CREATOR_LED_SHOPIFY_POD_MODEL_2026-05-11.md)
- [Five-Pass Stability And Operational Roadmap](docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md)
- [Repo Sync And Roadmap Update](docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md)

## Start Here

Current truth first (recommended reading order):

1. [Canonical Truth Index](docs/CANONICAL/00_INDEX.md) — how to read repo truth
2. [Daily Command Center](docs/status/DAILY_COMMAND_CENTER.md) — where the project is right now
3. [Capability Inventory](docs/capability_verification/CAPABILITY_INVENTORY.md) — what verifiably works
4. [Product Definition](docs/product/PRODUCT_DEFINITION.md) — identity, mission, phases
5. [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md) — generated runtime truth

For runtime-existence claims, generated runtime docs win; CANONICAL explains how to resolve conflicts.

Then the human onboarding path:

6. [Start Here](START_HERE.md)
7. [Quickstart](QUICKSTART.md)
8. [First 5 Minutes](docs/product/FIRST_5_MINUTES.md)
9. [What Works Today](docs/product/WHAT_WORKS_TODAY.md)
10. [Nova Operating Model](docs/product/NOVA_OPERATING_MODEL.md)
11. [Nova Brain](docs/brain.md)
12. [Conversation and Memory Model](docs/product/CONVERSATION_AND_MEMORY_MODEL.md)
13. [Known Limitations](docs/product/KNOWN_LIMITATIONS.md)
14. [Current Work Status](docs/status/CURRENT_WORK_STATUS.md)

## Proof Layer
- [Trust Proof Plan](docs/product/TRUST_PROOF_PLAN.md)
- [Trust Review Card Plan](docs/product/TRUST_REVIEW_CARD_PLAN.md)
- [See It Work](docs/product/SEE_IT_WORK.md)
- [Trust Model](docs/product/TRUST_MODEL.md)
- [Demo Script](docs/product/DEMO_SCRIPT.md)
- [Screenshot Asset Plan](docs/product/SCREENSHOT_ASSET_PLAN.md)
- [Trust UI Spec](docs/product/TRUST_UI_SPEC.md)
- [Capability Verification Status](docs/capability_verification/STATUS.md)
- [Capability Signoff Matrix](docs/product/CAPABILITY_SIGNOFF_MATRIX.md)
- [Proof Capture Checklist](docs/product/PROOF_CAPTURE_CHECKLIST.md)

## Selected Proof Packages
Selected historical and current proof records:

- [Seven-Morning Synthesis — 2026-07-22](docs/observation/SEVEN_MORNING_SYNTHESIS_2026-07-22.md)
- [Grounded Brief Routing Closeout — 2026-07-23](docs/status/GROUNDED_BRIEF_ROUTING_CLOSEOUT_2026-07-23.md)
- [Current Capability Inventory](docs/capability_verification/CAPABILITY_INVENTORY.md)

- [2026-04-29 Conversation + Search Proof](docs/demo_proof/2026-04-29_conversation_search_proof/CONVERSATION_SEARCH_REPORT.md)
- [Conversation + Search Proof Index](docs/demo_proof/2026-04-29_conversation_search_proof/PROOF_INDEX.md)
- [Brain Live Test Report](docs/demo_proof/brain_live_test/REPORT.md)
- [Brain Live Test Proof Index](docs/demo_proof/brain_live_test/PROOF_INDEX.md)
- [2026-04-28 User Test Report](docs/demo_proof/2026-04-28_user_test/USER_TEST_REPORT.md)
- [Proof Index](docs/demo_proof/2026-04-28_user_test/PROOF_INDEX.md)
- [Demo Script](docs/demo_proof/2026-04-28_user_test/DEMO_SCRIPT.md)
- [Friction Log](docs/demo_proof/2026-04-28_user_test/FRICTION_LOG.md)
- [Screenshot Checklist](docs/demo_proof/2026-04-28_user_test/SCREENSHOT_CHECKLIST.md)
- [Recorded Demo Flow](docs/demo_proof/2026-04-28_user_test/video/nova_user_test_demo_flow.webm)
- [Live User Simulation Results — 2026-05-19](docs/audits/LIVE_USER_SIMULATION_RESULTS_2026-05-19.md)

Historical visual proof captures — 2026-04-28:

These are authentic, dated local captures of the UI paths described in their checklist. They do
not identify the current source SHA and therefore are not proof of the current candidate,
installer, local-boundary security, or beta acceptance. See the
[proof evidence index](docs/capability_verification/PROOF_EVIDENCE_INDEX_2026-09-28.md) for
the scope and status of current evidence.

![Nova local-first dashboard](docs/demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level0_dashboard_connection_status.png)

![Nova Trust receipts](docs/demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level1_surface_trust.png)

![Nova memory authority boundary](docs/demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level2_memory_authority.png)

Current proof verdict:

```text
Governance paths are now strongly evidenced for the current confirmation-bound scope.
Everyday live-session reliability workstream closed 2026-05-19 (75% -> 97% pass, 0 timeouts).
Seven-morning observation and its rank-1 grounded-routing repair are complete.
Later current-state and acceptance-provenance details live in the Daily Command Center.
Nova is not yet a finished consumer product.
```

## Current Status
Version 0.5 Alpha is a technical-user / early-adopter state, not a finished mainstream release.

### Beta support boundary

Windows is Nova's primary beta-support target. The Windows installer path exists, but
clean-machine certification is still a later acceptance gate. macOS and Linux may be
used for source-based development only; they are not certified or supported beta
platforms.

Current grounded status:

```text
- local-first governed awareness and decision-support system
- bounded execution infrastructure exists
- generated runtime state reports 27 active capability surfaces
- active != certified != locked != configured != authorized
- Cap 16 web search is P1-P5 certification-locked
- Cap 22 file-folder access is P1-P5 certification-locked
- Cap 64 email draft is P1-P5 certification-locked and remains local mailto draft only
- Cap 65 Shopify intelligence is P1-P5 certification-locked, read-only, not Shopify writes
- OpenClaw exists as bounded/manual-first runtime infrastructure; presence does not imply broad autonomy
- Wave A1, A2, B1, B2, B3, B4, and Wave C stabilization are complete and merged
- immutable Wave C validated_baseline_sha:
  ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
- GitHub-hosted Wave C jobs remained NOT EXECUTED because of the external account/billing
  restriction tracked in Issue #354; the owner waived that source as mandatory exit evidence
  without classifying it as PASS
- POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE; truth/checker hardening is merged through PR #385
- PR #366 truth-hygiene provenance: MERGED
- PR #378 narration/front-door package: MERGED / VERIFIED
- #388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
- #368: COMPLETE
- #387: COMPLETE / DOCS-ONLY
- #394: GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
- historical PR #335 implementation path: SUPERSEDED BY MERGED PR #394;
  retain it as historical reference only, not a reconstruction or merge lane
- the Foundation is identity/auth infrastructure, not permission for Google domain-data access
- Google Tasks and Gmail are not built as current Nova capabilities
- Operational Continuity is strategically accepted but implementation-inactive and non-authorizing
- no broad browser/computer-use, financial-write, autonomous outreach, contracting,
  autonomous-business, broad provider-routing, or expanded OpenClaw authority lane is active
```

For exact generated runtime truth, use [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md).

For current human-readable work continuity, including the current gate, use [Current Work Status](docs/status/CURRENT_WORK_STATUS.md).

Historical sequencing references (May 2026; superseded by the master roadmap for ordering):
[Five-Pass Stability And Operational Roadmap](docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md),
[Repo Sync And Roadmap Update](docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md).

Historical pre-#394 decision sequence (superseded; not current work or authorization):

```text
1. Issue #388 is COMPLETE; its TRUTH-CHECKER PREREQUISITE is SATISFIED.
2. Issue #368 is the NEXT BOUNDED TECHNICAL LANE.
3. Issue #387 is AFTER #368 / DOCS-ONLY.
4. PR #335 reconstruction remains PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED.
5. The owner may later decide whether to authorize reconstruction/reconciliation of PR #335
   against exact validated baseline
   ec20a7146f7d6d55b8983cb7d6d3918d5fad9915.
6. If separately authorized, harden the bounded Google Foundation lifecycle/security defects
   identified during review, then rerun exact-head verification and independent security/architecture review.
7. Make the #335 merge decision separately.
8. Prove Google identity-only connection live without treating OAuth scope as Nova authority.
9. Add Google Tasks READ as the first provider-backed Google evidence vertical and prove
   provenance/freshness/evidence boundaries.
10. Only then evaluate an evidence-based Operational Continuity implementation warrant.

This summary authorizes nothing. The Daily Command Center, canonical roadmap truth, Issue #343,
and lane-specific locks hold current ordering and implementation scope.
```

## Current post-#405 beta-readiness order — 2026-09-20

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
verified main after Lane 5A rollback/restore proof: 868de9d92c701834f1c4fba422ab9c47a01ea33f
#397 through #405: COMPLETE / MERGED
COMPLETE: #406 governed-memory ID collision correctness (PR #411; main `ca66a06d`)
COMPLETE: #408 durability/state-ownership decision (PR #412; main `2592ad91`)
COMPLETE: durability implementation lane 1 - canonical state registry/migration detection (PR #413; main `e74fdca0`)
COMPLETE: durability implementation lane 2 - corruption-safe readers (PR #416; main `80e1c86f`)
COMPLETE: durability implementation lane 3 - maintenance locking + mutation quiescence (PR #419; main `2bfe202e`)
COMPLETE: durability implementation lane 4 - versioned snapshot + manifest (PR #421; main `4e32b501`)
FRESH-MAIN CLOSEOUT: PASS (314 focused durability/operational-truth tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: #409 release integrity / repository control (PR #423; main `aa39515f`)
COMPLETE: #410 private-beta freeze criteria (PR #410; main `3ad3f544`)
AUTHORIZED / ACTIVE: Lane 5A recovery construction (owner authorization; base main `3ad3f544`)
COMPLETE: Lane 5A step 1 - inactive recovery candidate migration (PR #424; main `298b7731`)
MIGRATION PROOF: PASS (173 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 2 - recovery candidate validation (PR #426; main `9de640cd`)
VALIDATION PROOF: PASS (184 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 3 - controlled recovery activation (PR #427; main `678dda6c`)
ACTIVATION PROOF: PASS (192 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A authority-foundation correction (PR #428; main `3a3e9d33`)
AUTHORITY FOUNDATION PROOF: PASS (201 durability tests passed; 1 expected Windows POSIX-FIFO skip)
RECOVERY AUTHORITY MODEL: dual-slot highest-valid-generation selection
COMPLETE: Lane 5A step 4 - rollback/restore proof (PR #430; main `868de9d9`)
ROLLBACK/RESTORE PROOF: PASS (208 durability tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: beta user-facing truth pass (PR #433; main `ad64048e`)
COMPLETE: rollback/restore operational-truth checker contract (PR #436; main `0003a2e`)
FRESH-MAIN PROOF: PASS (39 focused checker-contract tests; Ruff; operational-truth consistency; runtime structural smoke)
COMPLETE: first Synthetic Beta Cohort v1 (PR #438; test-only evidence, not product acceptance)
COMPLETE: connected-user cohort test-spec correction (PR #439; main `486ad3dddc3f75412085b968c28561ab57e25686`)
CONFIRMED P1 BEFORE BETA ACCEPTANCE: the local-only boundary is unsafe if `NOVA_HOST` accepts a non-loopback bind; repair and fresh proof are required before any Windows acceptance run.
NEXT REQUIRED ENGINEERING: bounded local-boundary P1 repair (no remote mode or authority expansion)
THEN: fresh-main security and truth proof
THEN: installer supply-chain and privacy/Data-Out/secrets audit
THEN: build a new exact Windows candidate artifact; the prior artifact is historical only
THEN: clean Windows operator proof against that exact artifact
THEN: freeze exact candidate identity
THEN: rerun #434 and remaining acceptance checks against that frozen candidate
THEN: owner acceptance/distribution decision
THEN: 3 real non-developer users
```

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. This current order supersedes older ordering language below and
grants no new capability or authority.

## Future Directions

Ordering authority: [Nova Master Roadmap 2026-07-05](docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md).
The documents below remain design references; the master roadmap decides sequence.

- [Nova Personal/Home/Business Operating System Summary](docs/future/NOVA_PERSONAL_HOME_BUSINESS_OS_SUMMARY.md)
- [Nova Two-Domain Direction](docs/future/NOVA_TWO_DOMAIN_DIRECTION_2026-05-11.md)
- [Nova Creator-Led Shopify POD Model](docs/future/NOVA_CREATOR_LED_SHOPIFY_POD_MODEL_2026-05-11.md)
- [Five-Pass Stability And Operational Roadmap](docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md)
- [Repo Sync And Roadmap Update](docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md)
- [Realistic Scope and Priorities](docs/future/REALISTIC_SCOPE_AND_PRIORITIES.md)
- [Google Connector Model](docs/future/NOVA_GOOGLE_CONNECTOR_MODEL.md)
- [Google Connector Implementation Roadmap](docs/future/GOOGLE_CONNECTOR_IMPLEMENTATION_ROADMAP.md)
- [Free-First Cost Governance First Steps](docs/design/Phase%206/FREE_FIRST_COST_GOVERNANCE_FIRST_STEPS_2026-04-30.md)
- [Governed Media and E-Commerce Engine](docs/future/NOVA_GOVERNED_MEDIA_AND_ECOMMERCE_ENGINE.md)
- [Media Engine Safe Implementation Roadmap](docs/future/NOVA_MEDIA_ENGINE_SAFE_IMPLEMENTATION_ROADMAP.md)
- [Nova x Auralis Digital Website Engine](docs/future/NOVA_AURALIS_DIGITAL_WEBSITE_ENGINE.md)
- [Auralis Website Coworker Workflow](docs/future/AURALIS_WEBSITE_COWORKER_WORKFLOW.md)
- [YouTubeLIS Tool Folder](docs/tools/youtubelis.md)

## Core Principles
**Intelligence is not authority.**

**Visibility is not authority.**

**Capability is not permission.**

**Outcome learning may improve recommendations, never authority.**

Nova may reason, summarize, search, draft, and recommend. Conversation context and memory can improve understanding, but they do not authorize execution. Real actions should remain bounded by capability checks, execution boundaries, confirmation where required, and visible receipts.

Visibility surfaces, dashboards, proofs, and status views do not grant execution authority. They exist to help the operator understand what is active, what is locked, what is pending, and what actually happened.

## AI Workflow Note
This project may use AI tools for planning, coding support, audits, review, and prototyping.

- GitHub remains the durable source of truth for code, docs, commits, and project status.
- Runtime truth should be grounded in implementation, tests, and generated runtime artifacts.
- Visual builders or prototype tools may help present ideas, but do not replace Nova's governed runtime.
- AI-generated work should be reviewed before being treated as final.

See:
- [AI Tooling Workflow](docs/WORKFLOW_AI_TOOLING.md)
- [AI Tooling Boundaries](docs/AI_TOOLING_BOUNDARIES.md)

## License
See [LICENSE].
