# Capability Gap Map - 2026-04-23

## Current Truth Sources

- Local branch: `main`
- GitHub branch: `origin/main`
- Current synced commit at start of pass: `d51dcfa`
- Formal certification source: `python scripts/certify_capability.py status`
- Human simulation reports: `docs/capability_verification/*simulation*.md`

## Summary

Formal capability locking is still mostly incomplete. Product-level live simulations have started, but most capabilities have not yet gone through the full P1-P6 certification pipeline.

Current formal status:

- 27 governed capabilities tracked.
- 0 capabilities locked.
- 64 has P1-P4 passing, P5 live signoff pending.
- 65 has P1-P2 passing, P3-P5 pending.
- 16-63 are formally pending across P1-P5, even when they have older automated tests outside `tests/certification/`.

Current live simulation coverage:

- Basic conversation and understanding: signed off as a platform/runtime slice.
- Basic user commands: passed after confirmation correction.
- News/headlines: passed after routing and RSS title cleanup corrections.
- Governed web search: passed after pending-search query cleanup correction.

## Formal Capability Gaps

| ID | Capability | Formal status | Simulation status | Next action |
|---:|---|---|---|---|
| 16 | governed_web_search | P1-P5 pending | PASS after correction | Convert existing executor/routing/API tests into certification P1-P4, then P5 signoff |
| 17 | open_website | P1-P5 pending | Not yet separately simulated | Simulate preview/open/cancel/confirm |
| 18 | speak_text | P1-P5 pending | Not yet simulated | Simulate speak last answer/read custom text |
| 19 | volume_up_down | P1-P5 pending | Basic pass in user-command sweep | Convert to cap-specific checklist and certification |
| 20 | media_play_pause | P1-P5 pending | Not yet simulated in this pass | Simulate play/pause/resume on Windows |
| 21 | brightness_control | P1-P5 pending | Basic pass in user-command sweep | Convert to cap-specific checklist and certification |
| 22 | open_file_folder | P1-P5 pending | PASS after confirmation correction | Convert to cap-specific checklist and certification |
| 31 | response_verification | P1-P5 pending | Not yet simulated | Simulate verify/fact-check answer |
| 32 | os_diagnostics | P1-P5 pending | Not yet simulated | Simulate system status/model status |
| 48 | multi_source_reporting | P1-P5 pending | Not yet simulated | Simulate research/report with current sources |
| 49 | headline_summary | P1-P5 pending | PASS in news/headlines sweep | Convert to certification |
| 50 | intelligence_brief | P1-P5 pending | PASS in news/headlines sweep | Convert to certification |
| 51 | topic_memory_map | P1-P5 pending | Not yet simulated | Simulate topic map after news fetch |
| 52 | story_tracker_update | P1-P5 pending | Not yet simulated | Simulate track/update story; verify local write |
| 53 | story_tracker_view | P1-P5 pending | Not yet simulated | Simulate show/compare tracked story |
| 54 | analysis_document | P1-P5 pending | Not yet simulated | Simulate create/list/summarize/explain doc |
| 55 | weather_snapshot | P1-P5 pending | Not yet simulated | Simulate weather and forecast |
| 56 | news_snapshot | P1-P5 pending | PASS in news/headlines sweep | Convert to certification |
| 57 | calendar_snapshot | P1-P5 pending | Not yet simulated | Simulate agenda/calendar with available connectors |
| 58 | screen_capture | P1-P5 pending | Not yet simulated | Simulate screenshot/capture with user-visible output |
| 59 | screen_analysis | P1-P5 pending | Not yet simulated | Simulate analyze current screen |
| 60 | explain_anything | P1-P5 pending | Not yet simulated | Simulate explain this/current context |
| 61 | memory_governance | P1-P5 pending | Basic pass in user-command sweep | Convert to cap-specific checklist and certification |
| 62 | external_reasoning_review | P1-P5 pending | Not yet simulated | Simulate second opinion/review answer |
| 63 | openclaw_execute | P1-P5 pending | Not yet simulated | Simulate run template and verify run history/status |
| 64 | send_email_draft | P1-P4 pass, P5 pending | Not yet live-signed in this pass | Run live checklist, then `live-signoff 64` |
| 65 | shopify_intelligence_report | P1-P2 pass, P3-P5 pending | Not simulated; needs connector env | Fix current review findings, then test with configured env or mock live harness |

## Prioritized Workdown

1. Finish live simulations by user-facing clusters:
   - Search/research: 16, 48, 62
   - Local controls/navigation: 17-22
   - News/story intelligence: 49-53, 56
   - System/weather/calendar/perception: 32, 55, 57-60
   - Memory/persistence: 54, 61
   - Automation/external integrations: 63-65

2. For every capability with a passing live simulation, backfill certification:
   - P1 unit
   - P2 routing
   - P3 governor integration
   - P4 API/WebSocket
   - P5 live signoff
   - P6 lock

3. Keep simulation docs separate from formal certification state until `certify_capability.py` records the phase advances.

## Open Review Findings To Fold Into Workdown

- Trial loop roadmap references an ignored local report.
- Served static dashboard needs run-status parity with source dashboard.
- Shopify connector needs configurable supported API version.
- OpenClaw goal runs need completed run history recording.
- `docs/product/visual_proof.md` has a whitespace hygiene issue in the committed range.
