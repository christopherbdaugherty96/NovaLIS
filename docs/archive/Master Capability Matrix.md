# Nova Master Capability Matrix
Updated: 2026-03-13
Status: Active
Purpose: Compact operator-facing matrix of the live capability surface

Primary references:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## How To Use This File
- Use this file for a quick map of what is live.
- Use `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md` for plain-English explanations.
- Use `docs/design/` only for planned behavior, not runtime truth.

## Active Governed Capability Matrix

| ID | Name | Category | Phase | Status | Short explanation |
| --- | --- | --- | --- | --- | --- |
| 16 | `governed_web_search` | Research | 4 | Active | Governed web search with result widget and follow-up prompts |
| 17 | `open_website` | Navigation | 4 | Active | Opens or previews websites and source/article URLs |
| 18 | `speak_text` | Voice output | 4 | Active | Speaks sanitized text aloud through local offline TTS |
| 19 | `volume_up_down` | Local control | 4 | Active | Adjusts system volume or mute state |
| 20 | `media_play_pause` | Local control | 4 | Active | Controls play, pause, and resume for local media |
| 21 | `brightness_control` | Local control | 4 | Active | Adjusts screen brightness |
| 22 | `open_file_folder` | Local navigation | 4 | Active | Opens approved folders or explicit file/folder paths |
| 31 | `response_verification` | Analysis safety | 4.2 | Active | Verifies claims or responses and suggests corrections |
| 32 | `os_diagnostics` | System insight | 4 | Active | Reports health, resources, network status, and model readiness |
| 48 | `multi_source_reporting` | Intelligence | 4.2 | Active | Builds structured multi-source intelligence reports |
| 49 | `headline_summary` | News intelligence | 4.2 | Active | Summarizes headlines and can summarize linked story pages |
| 50 | `intelligence_brief` | News intelligence | 4.2 | Active | Creates clustered daily/intelligence news briefs |
| 51 | `topic_memory_map` | News intelligence | 4.2 | Active | Shows recurring topic clusters from current headlines |
| 52 | `story_tracker_update` | Ongoing research | 4.2 | Active | Tracks, updates, and links stories over time |
| 53 | `story_tracker_view` | Ongoing research | 4.2 | Active | Views tracked story timelines and comparisons |
| 54 | `analysis_document` | Long-form analysis | 4.2 | Active | Creates and explains session-scoped analysis documents |
| 55 | `weather_snapshot` | Snapshot widget | 4.5 | Active | Loads weather summary and widget |
| 56 | `news_snapshot` | Snapshot widget | 4.5 | Active | Loads current news summary and headline widget |
| 57 | `calendar_snapshot` | Snapshot widget | 4.5 | Active | Loads calendar summary and agenda widget |
| 58 | `screen_capture` | Perception | 4.5 | Active | Captures a bounded screen region on request |
| 59 | `screen_analysis` | Perception | 4.5 | Active | Runs OCR and visual analysis on the captured region |
| 60 | `explain_anything` | Perception | 4.5 | Active | Explains the current screen, page, or selected file |
| 61 | `memory_governance` | Governed persistence | 5 | Active | Explicit save/list/show/lock/defer/unlock/delete/supersede memory |

## Active Runtime Surfaces Without Separate Capability IDs

| Surface | Status | Role |
| --- | --- | --- |
| STT transcription | Active | Voice ingress through local speech-to-text |
| Interface personality agent | Active | Presentation-only formatting and tone boundary layer |
| Working Context Engine | Active | Session-scoped task/context coherence |
| Project continuity threads | Active | Ongoing work tracking with blocker/health/decision context |
| Thread-memory bridge | Active | Explicit thread-linked saves into governed memory |
| Dashboard widgets and thread detail panel | Active | Primary user-facing display layer for snapshots and continuity |
| Orb presence layer | Active | Calm, non-semantic visual presence only |
| Context snapshot service | Active | Read-only request-time environment snapshot for perception flows |

## Documented But Not Active Runtime

| Surface | Status | Note |
| --- | --- | --- |
| Wake word listener (`Hey Nova`) | Design-stage | Documented in Phase 4.5 design docs but not a live runtime capability or active voice module today |

## Change Control
When runtime capabilities change:
1. Update code and tests first.
2. Regenerate runtime truth artifacts if needed.
3. Update this matrix and `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md` in the same pass.
