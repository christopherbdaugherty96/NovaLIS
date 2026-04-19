# SKILL_SURFACE_MAP

Deterministic surface map for skills, conversation modules, and governor capability routes.

| skill_or_surface | module | surface_type | network_usage | model_usage | capability_id |
| --- | --- | --- | --- | --- | --- |
| deepseek_bridge | src/conversation/deepseek_bridge.py | conversation | no | llm_gateway |  |
| analysis_document | src/governor/governor_mediator.py | governor_capability | no | none | 54 |
| brightness | src/governor/governor_mediator.py | governor_capability | no | none | 21 |
| calendar_snapshot | src/governor/governor_mediator.py | governor_capability | no | none | 57 |
| diagnostics | src/governor/governor_mediator.py | governor_capability | no | none | 32 |
| explain_anything | src/governor/governor_mediator.py | governor_capability | no | none | 60 |
| external_reasoning_review | src/governor/governor_mediator.py | governor_capability | no | none | 62 |
| headline_summary | src/governor/governor_mediator.py | governor_capability | yes | none | 49 |
| intelligence_brief | src/governor/governor_mediator.py | governor_capability | yes | none | 50 |
| media | src/governor/governor_mediator.py | governor_capability | no | none | 20 |
| memory_governance | src/governor/governor_mediator.py | governor_capability | no | none | 61 |
| news_snapshot | src/governor/governor_mediator.py | governor_capability | yes | none | 56 |
| open_folder | src/governor/governor_mediator.py | governor_capability | no | none | 22 |
| open_website | src/governor/governor_mediator.py | governor_capability | no | none | 17 |
| openclaw_execute | src/governor/governor_mediator.py | governor_capability | no | none | 63 |
| report | src/governor/governor_mediator.py | governor_capability | yes | none | 49 |
| response_verification | src/governor/governor_mediator.py | governor_capability | no | none | 31 |
| screen_analysis | src/governor/governor_mediator.py | governor_capability | no | none | 59 |
| screen_capture | src/governor/governor_mediator.py | governor_capability | no | none | 58 |
| search | src/governor/governor_mediator.py | governor_capability | yes | none | 48 |
| send_email_draft | src/governor/governor_mediator.py | governor_capability | no | none | 64 |
| speak | src/governor/governor_mediator.py | governor_capability | no | none | 18 |
| story_tracker_update | src/governor/governor_mediator.py | governor_capability | no | none | 52 |
| story_tracker_view | src/governor/governor_mediator.py | governor_capability | no | none | 53 |
| topic_memory_map | src/governor/governor_mediator.py | governor_capability | yes | none | 51 |
| volume | src/governor/governor_mediator.py | governor_capability | no | none | 19 |
| weather_snapshot | src/governor/governor_mediator.py | governor_capability | yes | none | 55 |
| calendar | src/skills/calendar.py | skill | no | none |  |
| general_chat | src/skills/general_chat.py | skill | yes | llm_gateway |  |
| news | src/skills/news.py | skill | yes | none |  |
| system | src/skills/system.py | skill | no | none |  |
| weather | src/skills/weather.py | skill | yes | none |  |

## OpenClaw Tool Registry (Phase 9 Intelligence Layer)

The OpenClaw agent intelligence layer has its own tool registry (`src/openclaw/tool_registry.py`) that exposes tools to the thinking loop for goal-based execution. These tools are discoverable at runtime by tag and category.

| tool_name | module | category | network | capability_id |
| --- | --- | --- | --- | --- |
| weather | src/skills/weather.py | collection | yes | — |
| calendar | src/skills/calendar.py | collection | no | — |
| news | src/skills/news.py | collection | yes | — |
| system | src/skills/system.py | control | no | — |
| web_search | src/skills/web_search.py | collection | yes | — |
| volume | src/skills/executor_adapter.py → VolumeExecutor | mutation | no | 19 |
| brightness | src/skills/executor_adapter.py → BrightnessExecutor | mutation | no | 21 |
| media | src/skills/executor_adapter.py → MediaExecutor | mutation | no | 20 |
| open_webpage | src/skills/executor_adapter.py → WebpageLaunchExecutor | mutation | no | 17 |
| screen_capture | src/skills/executor_adapter.py → ScreenCaptureExecutor | collection | no | 58 |

## Self-Awareness (Phase 9)

Nova has a dynamic self-awareness context block (`src/identity/nova_self_awareness.py`) injected into every system prompt. It reports:
- Identity and personality
- Active Governor capabilities (grouped by function)
- OpenClaw tool registry contents
- Connected/disconnected external services
- Runtime status (platform, uptime, model health, home agent, scheduler)

Cached for 60 seconds. Approximately 866 tokens (2.7% of 32K context window).

## Escalation vs governed execution

- `ALLOW_ANALYSIS_ONLY` is represented in `src/conversation/escalation_policy.py` and used by `GeneralChatSkill` as analysis-only output path.
- Governed capabilities are routed by `GovernorMediator.parse_governed_invocation(...)` and executed via `Governor.handle_governed_invocation(...)`.
- Legacy sealed skill shims that are not registered in `src/skill_registry.py` are intentionally omitted from this live runtime map.
