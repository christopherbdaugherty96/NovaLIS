# NovaLIS

**Version 0.5 Alpha — Current State**

NovaLIS is a governance-first local AI platform designed to separate intelligence from execution.

Nova focuses on what the system is allowed to do, how actions are routed, and how real execution stays visible, bounded, reviewable, and auditable.

## Why Nova
Most AI tools optimize for capability expansion. Nova emphasizes bounded execution, reviewable actions, local ownership, visible trust boundaries, and user-visible control.

Nova is intended to evolve into:

```text
A governed operational coordination platform.
```

The long-term direction has two connected domains:

```text
1. Everyday home / voice / local assistant platform
2. Creator-business operational coordination platform
```

Canonical future-product summary:
- [Nova Personal/Home/Business Operating System Summary](docs/future/NOVA_PERSONAL_HOME_BUSINESS_OS_SUMMARY.md)

See:
- [Nova Two-Domain Direction](docs/future/NOVA_TWO_DOMAIN_DIRECTION_2026-05-11.md)
- [Nova Creator-Led Shopify POD Model](docs/future/NOVA_CREATOR_LED_SHOPIFY_POD_MODEL_2026-05-11.md)
- [Five-Pass Stability And Operational Roadmap](docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md)
- [Repo Sync And Roadmap Update](docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md)

## Start Here
1. [Start Here](START_HERE.md)
2. [Quickstart](QUICKSTART.md)
3. [First 5 Minutes](docs/product/FIRST_5_MINUTES.md)
4. [What Works Today](docs/product/WHAT_WORKS_TODAY.md)
5. [Nova Operating Model](docs/product/NOVA_OPERATING_MODEL.md)
6. [Nova Brain](docs/brain.md)
7. [Brain Architecture Package](docs/brain/README.md)
8. [Conversation and Memory Model](docs/product/CONVERSATION_AND_MEMORY_MODEL.md)
9. [Known Limitations](docs/product/KNOWN_LIMITATIONS.md)
10. [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md)
11. [Current Work Status](docs/status/CURRENT_WORK_STATUS.md)
12. [Five-Pass Stability And Operational Roadmap](docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md)
13. [Repo Sync And Roadmap Update](docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md)

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

## Current Demo Proof
Latest proof package:

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

Recent local-first proof captures:

![Nova local-first dashboard](docs/demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level0_dashboard_connection_status.png)

![Nova Trust receipts](docs/demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level1_surface_trust.png)

![Nova memory authority boundary](docs/demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level2_memory_authority.png)

Current proof verdict:

```text
Governance paths are now strongly evidenced for the current confirmation-bound scope.
Everyday live-session reliability under concurrent load remains the active workstream.
Nova is not yet a finished consumer product.
```

## Current Status
Version 0.5 Alpha is a technical-user / early-adopter state, not a finished mainstream release.

Current grounded status:

```text
- governance-first local AI/runtime platform
- bounded execution infrastructure exists
- active runtime capabilities exist
- active != certified != locked
- Cap 16 web search is certification-locked
- Cap 22 open_file_folder is approval-gate certified for current scope, not P1-P5 locked
- Cap 64 send_email_draft is approval-gate certified for current scope and remains local mailto draft only
- Cap 65 Shopify intelligence remains read-only, not Shopify writes
- OpenClaw exists as runtime code with bounded/manual-first execution surfaces
- PR #154 narrowed the OpenClaw freeform-goal path to read-only allowlisted tools and metered network access
- PR #206 merged a real live-user simulation baseline
- PR #207 merged the first Ollama wait-serialization mitigation
- generated runtime docs are current as of the latest recorded drift check
```

For exact generated runtime truth, use [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md).

For current human-readable work continuity, including the current active task, use [Current Work Status](docs/status/CURRENT_WORK_STATUS.md).

For the post-audit stabilization/productization sequence, use [Five-Pass Stability And Operational Roadmap](docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md).

For the consolidated roadmap and positioning update, use [Repo Sync And Roadmap Update](docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md).

Current active task:

```text
Approval-gate certification lane — COMPLETE / closed (2026-05-19).

Current active workstream:
Everyday live-session reliability hardening.

Next:
Rerun the exact same 20-persona live-user simulation after PR #207 and compare exact metrics against the PR #206 baseline.

Do not expand capabilities or start Shopify/website workflows yet.
```

## Future Directions
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

Nova may reason, summarize, search, draft, and recommend. Conversation context and memory can improve understanding, but they do not authorize execution. Real actions should remain bounded by capability checks, execution boundaries, confirmation where required, and visible receipts.

Visibility surfaces, dashboards, proofs, and status views do not grant execution authority. They exist to help the operator understand what is active, what is locked, what is pending, and what actually happened.

## AI Workflow Note
This project may use AI tools for planning, coding support, audits, review, and prototyping.

- GitHub remains the durable source of truth for code, docs, commits, and project status.
- Runtime truth should be grounded in implementation, tests, and generated runtime artifacts.