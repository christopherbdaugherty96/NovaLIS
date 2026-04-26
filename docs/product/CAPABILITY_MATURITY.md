# Capability Maturity Model

Use this model to describe capabilities more honestly than a simple enabled/disabled state.

## Labels
- **Stable**: Repeatedly tested, expected to work in common environments.
- **Tested**: Implemented and covered by tests, but may have environment caveats.
- **Experimental**: Works in some paths, subject to change.
- **Internal**: Primarily for development, audits, or internal operators.
- **Requires Key**: Needs external credentials.
- **Requires Local Dependency**: Needs local model, binary, or OS integration.
- **Confirmation Required**: Should require explicit user approval before action.
- **Not User-Ready**: Exists technically but should not be relied on by normal users.

## Recommended Next Step
Apply one or more labels to every capability in the registry and surface them in docs/UI.

---

## Applied Labels — All 27 Active Capabilities

Multiple labels may apply. Listed in registry ID order.

| ID | Capability | Labels | Notes |
|---|---|---|---|
| 16 | governed_web_search | Tested | May require search API key depending on provider config |
| 17 | open_website | Tested | Opens system default browser |
| 18 | speak_text | Tested · Requires Local Dependency | Needs Vosk + sounddevice; TTS path requires local audio |
| 19 | volume_up_down | Tested · Requires Local Dependency | OS-level media control; Windows primary target |
| 20 | media_play_pause | Tested · Requires Local Dependency | Platform-specific media control |
| 21 | brightness_control | Tested · Requires Local Dependency | Windows display control; may not work on all hardware |
| 22 | open_file_folder | Tested · Confirmation Required | Requires explicit user approval; opens within approved path roots only |
| 31 | response_verification | Stable | Read-only; no external dependencies |
| 32 | os_diagnostics | Stable | Read-only; no external dependencies |
| 48 | multi_source_reporting | Tested | Outbound read via NetworkMediator |
| 49 | headline_summary | Tested | Outbound read via NetworkMediator |
| 50 | intelligence_brief | Tested | Outbound read via NetworkMediator |
| 51 | topic_memory_map | Tested | Local read; no external dependencies |
| 52 | story_tracker_update | Tested | Local persistent write; reversible |
| 53 | story_tracker_view | Tested | Local read only |
| 54 | analysis_document | Tested | Session-scoped local write |
| 55 | weather_snapshot | Tested | May require location or weather service config |
| 56 | news_snapshot | Tested | RSS-based; no key required for default sources |
| 57 | calendar_snapshot | Tested · Requires Local Dependency | Reads local ICS calendar file; requires calendar connector setup |
| 58 | screen_capture | Experimental | Persistent local write; platform-specific capture path |
| 59 | screen_analysis | Experimental | Depends on screen_capture; OCR path may vary by environment |
| 60 | explain_anything | Tested | Routes to best available read path; output quality varies by context |
| 61 | memory_governance | Tested | Local persistent write; all operations reversible or exportable |
| 62 | external_reasoning_review | Stable | Read-only; no execution authority |
| 63 | openclaw_execute | Experimental | Agentic runtime surface; feature-flagged envelope hardening in progress |
| 64 | send_email_draft | Tested · Confirmation Required | P1–P4 certified; P5 live sign-off pending; requires configured mail client |
| 65 | shopify_intelligence_report | Tested · Requires Key | P1–P4 certified; P5 live sign-off pending; requires `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN` |

### Label key for this table

- **Stable** — read-only, no external dependencies, works in any standard Nova environment
- **Tested** — implementation and automated tests confirmed; may have environment or setup requirements
- **Experimental** — works in some paths; subject to change; not recommended for primary workflows
- **Confirmation Required** — requires explicit user approval before the action runs
- **Requires Local Dependency** — needs local binary, OS integration, or hardware support beyond a base Nova install
- **Requires Key** — needs external API credentials set via environment variables
