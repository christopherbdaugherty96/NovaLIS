# Nova Capability Inventory

**Canonical human-maintained capability verification surface.**

Last reconciled: **2026-08-20**.

For exact capability existence/enabled-state at a revision, compare this file with the capability registry and generated runtime state. For live reliability claims, require observed evidence. Do not treat `exists`, `enabled`, `configured`, `live-proven`, `available_on_this_path`, and `authorized` as synonyms.

## Current repository checkpoint

Merged `main` when Wave A1 began:

```text
1a517d8832a2c834c80b10a7062bed878f6312cc
```

This is an A1 planning checkpoint, not an immutable validated baseline.

Generated runtime state at that checkpoint reports **27 active capabilities**.

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

These rows mean the named implementation defects are not current pending work. They do **not** mean every capability has been broadly re-live-verified after every later merge.

## Current high-level readiness

| Surface | Exists | Current truth |
| --- | :---: | --- |
| Governed execution / authority spine | ✅ | core architecture present and heavily tested; Wave B/C will improve truth instrumentation/proof semantics |
| Runtime truth / health surfaces | ✅ | generated surfaces exist; Wave B1 is required because some generator claims/coverage are broader than the mechanisms actually prove |
| Governed memory | ✅ | explicit memory capability exists; ordinary GeneralChat durable-persistence semantics require Wave B3 governance repair |
| Awareness brief | ✅ | grounded brief/category routing exists; broader semantic usefulness remains a product-quality concern |
| Weather | ✅ | configured/default path exists; explicit-location preservation repair is merged through #341/#344 |
| News | ✅ | sourced RSS/news surface exists; any remaining parameter/relevance defect must be reproduced before being treated as active |
| Calendar | ✅ | local `.ics` read surface exists; source-selection and tomorrow-scope repairs are merged through #349/#350 |
| Local reminder schedules | ✅ | persistent SCH records/retrieval exist; cancellation routing repair merged through #351; dependable background alert delivery is not established by this contract |
| Governed web search | ✅ | capability exists; live execution depends on configured provider/key/runtime availability |
| General chat / local inference | ✅ | exists; semantic quality, reference binding, and current local-model throughput remain validation targets |
| Google Workspace Foundation | ❌ on current main | PR #335 is draft/unmerged Foundation-only code; not current capability |
| Google Tasks | ❌ | not built |
| Gmail | ❌ | not built |
| Google Reminders | ❌ | not built |
| Traffic | ❌ | not built |

## Active capability registry

Generated runtime state currently reports these active capability IDs:

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

- merged routing repairs are not a substitute for one clean Wave C validated-baseline proof package;
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

After the Wave A/B/C stabilization gate and a separate #335 merge decision:

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

Wave B2 is the implementation lane for this narration repair.

## Verification discipline

Before any live verification:

1. confirm the running process corresponds to the intended revision;
2. restart if stale;
3. record exact revision/environment;
4. exercise only the behavior being claimed;
5. preserve accepted-vs-verified outcome distinctions;
6. do not generalize one passing phrase/location/source into universal natural-language support.

Historical proof remains useful for what it actually tested. It does not silently become current proof after later merges.

## Product criterion for new connectors

A new data source is not a Nova product feature merely because Nova can connect to it. It becomes product value when trustworthy source evidence can be connected to other relevant state and reduce a real uncertainty or improve a grounded decision.
