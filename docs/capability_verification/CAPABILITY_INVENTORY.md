# Nova Capability Inventory

**Canonical human-maintained capability verification surface.**

Last reconciled: **2026-08-25**.

For exact capability existence/enabled-state at a revision, compare this file with the capability registry and generated runtime state. For live reliability claims, require observed evidence. Do not treat `exists`, `enabled`, `configured`, `live-proven`, `available_on_this_path`, and `authorized` as synonyms.

## Current repository checkpoint

The immutable Wave C validated runtime baseline is:

```text
ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
```

The later PR #365 documentation sync merged at `d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c` and is the base of draft PR #366. That later documentation commit did not establish a new runtime validated baseline.

At the Wave C validated baseline, generated runtime state reports **27 active capabilities**. Current HEAD must be resolved from Git/repository state rather than inferred from this evidence SHA.

## August stabilization update

The following previously observed truth/routing defects now have merged repairs:

| Area | Merged repair | Current inventory interpretation |
| --- | --- | --- |
| Commitment/capability truth | #337 / #338 | implementation repair merged; no longer a pending P1 item |
| Session action/outcome recap | #339 | receipt-correlated repair merged |
| Volume outcome truth | #340 | accepted-vs-verified wording/receipt repair merged |
| Explicit-location weather | #341 / #344 | mediator/executor + WebSocket location-preservation repairs merged |
| Brightness outcome truth | #345 | accepted-vs-verified repair merged |
| `turn down volume` wording | #346 | deterministic routing repair merged |
| Current-information source/freshness routing | #347 | routing/source-boundary repair merged |
| Broad awareness follow-up | #348 | interpretation repair merged |
| Calendar source-selection overmatch | #349 | repair merged |
| Calendar `tomorrow` scope | #350 | temporal-scope preservation repair merged |
| Local schedule cancellation | #351 | cancellation routing repair merged |
| Private Drive source selection | #352 | private-source/public-web separation repair merged |
| Runtime-truth instrumentation | #356 | B1 repair and generated-truth instrumentation merged |
| Capability narration | #358 | B2 shared non-authorizing projection merged |
| Memory governance | #360 | B3 ordinary-chat persistence/provenance repair merged |
| Reproducibility hygiene | #362 | B4 canonical dependency truth merged |
| Validated-baseline proof | #364 | Wave C complete; exact-baseline non-hosted proof passed under explicit hosted-evidence waiver |

These rows mean the named implementation defects are not current pending work. They do **not** mean every capability has been broadly re-live-verified after every later merge. PR #365/#366 documentation work does not extend Wave C runtime proof to later repository revisions.

## Current high-level readiness

| Surface | Exists | Current truth |
| --- | :---: | --- |
| Governed execution / authority spine | ✅ | core architecture present and heavily tested; Wave C validated-baseline proof is complete for the exercised revision/environment |
| Runtime truth / health surfaces | ✅ | B1 truth-instrumentation repair is complete; generated claims remain limited to what their mechanisms mechanically inspect |
| Governed memory | ✅ | explicit memory capability exists; B3 ordinary-GeneralChat durable-persistence/provenance repair is complete and merged |
| Awareness brief | ✅ | grounded brief/category routing exists; broader semantic usefulness remains a product-quality concern |
| Weather | ✅ | configured/default path exists; explicit-location preservation repair is merged through #341/#344 |
| News | ✅ | sourced RSS/news surface exists; any remaining parameter/relevance defect must be reproduced before being treated as active |
| Calendar | ✅ | local `.ics` read surface exists; source-selection and tomorrow-scope repairs are merged through #349/#350 |
| Local reminder schedules | ✅ | persistent SCH records/retrieval exist; cancellation routing repair merged through #351; dependable background alert delivery is not established by this contract |
| Governed web search | ✅ | capability exists; live execution depends on configured provider/key/runtime availability |
| General chat / local inference | ✅ | exists; Wave C covered semantic-contract regression, but semantic quality and local-model throughput remain environment/evidence-specific concerns |
| Google Workspace Foundation | ❌ on current main | PR #335 remains draft/unmerged Foundation-only code; reconstruction is next but separately authorization-gated |
| Google Tasks | ❌ | not built |
| Gmail | ❌ | not built |
| Google Reminders | ❌ | not built |
| Traffic | ❌ | not built |

## Active capability registry

At the Wave C validated baseline, generated runtime state reports these active capability IDs:

```text
16 governed_web_search
17 open_website
18 speak_text
19 volume_up_down
20 media_play_pause
21 brightness_control
22 open_file_folder
31 response_verification
32 os_diagnostics
48 multi_source_reporting
49 headline_summary
50 intelligence_brief
51 topic_memory_map
52 story_tracker_update
53 story_tracker_view
54 analysis_document
55 weather_snapshot
56 news_snapshot
57 calendar_snapshot
58 screen_capture
59 screen_analysis
60 explain_anything
61 memory_governance
62 external_reasoning_review
63 openclaw_execute
64 send_email_draft
65 shopify_intelligence_report
```

Capability existence does not imply configuration, path availability, live proof, approval, or exact-request authority.

## Certification-lock truth

Mechanical certification state should be checked with:

```text
python scripts/certify_capability.py status
```

The long-standing locked set is:

```text
Cap 16  governed_web_search
Cap 22  open_file_folder
Cap 64  send_email_draft
Cap 65  shopify_intelligence_report
```

A lock means the bounded certified scope is locked. It does not authorize expansion.

## What can be relied on vs what merely exists

### Stronger current surfaces

- governed capability routing/execution boundaries;
- explicit approval/receipt architecture for the paths that use it;
- local `.ics` Calendar reads;
- sourced News and Weather surfaces with graceful degradation;
- persistent local reminder schedule records and retrieval;
- bounded local device/navigation actions, with outcome wording constrained by available effect evidence;
- awareness/brief routing over loaded structured state.

### Important qualifications

- Wave C provides one clean validated-baseline proof package for `ec20a714...`; later commits do not silently inherit that proof;
- successful OS-command dispatch may remain `accepted_unverified` if no trusted observer establishes the final physical state;
- GeneralChat remains a semantic-quality risk surface and must not manufacture capability or execution truth;
- private-source requests must not silently upgrade to public web search;
- live web/provider capability depends on actual configuration and provider availability;
- local schedules are not equivalent to dependable closed-app/background notifications;
- OpenClaw runtime presence is not broad autonomy or blanket tool availability.

## Current missing personal evidence surfaces

These remain genuinely absent rather than merely misrouted:

```text
Google Tasks
Gmail
Google Reminders
Traffic
```

PR #335 does not change that because it remains draft/unmerged and is Foundation/auth/identity only.

## Google evidence order

After PR #366 truth hygiene is reviewed, #335 reconstruction receives separate authorization/review, and a separate #335 merge decision is made:

```text
Google identity-only live proof
-> Google Tasks READ
-> prove provider-backed evidence/provenance/freshness
-> use that evidence in Nova Awareness/Decision
-> only then consider later Google families one at a time
```

Permanent boundary:

```text
connection != capability
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
```

## Capability narration doctrine

User/model-facing capability copy must distinguish, where relevant:

```text
exists
enabled
configured
verification_status
available_on_this_path
requires_approval
authority_class
```

Do not say a capability is simply "real and working" when the relevant truth is only that it exists/enabled in the registry.

Do not model `authorized` as static capability metadata. Exact-request authority/approval is contextual and consumable.

Wave B2 implemented and merged this shared non-authorizing narration projection through PR #358. Do not reopen or redesign it without concrete new evidence.

## Verification discipline

Before any live verification:

1. confirm the running process corresponds to the intended revision;
2. restart if stale;
3. record exact revision/environment;
4. exercise only the behavior being claimed;
5. preserve accepted-vs-verified outcome distinctions;
6. do not generalize one passing phrase/location/source into universal natural-language support.

Historical proof remains useful for what it actually tested. It does not silently become current proof after later merges.
