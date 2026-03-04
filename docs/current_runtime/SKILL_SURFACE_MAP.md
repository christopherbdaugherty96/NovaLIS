# SKILL_SURFACE_MAP

Deterministic surface map for skills, conversation modules, and governor capability routes.

| skill_or_surface | module | surface_type | network_usage | model_usage | capability_id |
| --- | --- | --- | --- | --- | --- |
| deepseek_bridge | src/conversation/deepseek_bridge.py | conversation | unknown | ollama_direct |  |
| brightness | src/governor/governor_mediator.py | governor_capability | unknown | none | 21 |
| diagnostics | src/governor/governor_mediator.py | governor_capability | unknown | none | 32 |
| media | src/governor/governor_mediator.py | governor_capability | unknown | none | 20 |
| open_folder | src/governor/governor_mediator.py | governor_capability | unknown | none | 22 |
| open_website | src/governor/governor_mediator.py | governor_capability | unknown | none | 17 |
| report | src/governor/governor_mediator.py | governor_capability | unknown | none | 48 |
| search | src/governor/governor_mediator.py | governor_capability | unknown | none | 16 |
| speak | src/governor/governor_mediator.py | governor_capability | unknown | none | 18 |
| volume | src/governor/governor_mediator.py | governor_capability | unknown | none | 19 |
| general_chat | src/skills/general_chat.py | skill | yes | ollama_direct |  |
| news | src/skills/news.py | skill | yes | none |  |
| news | src/skills/web_search.py | skill | no | none |  |
| system | src/skills/system.py | skill | no | none |  |
| weather | src/skills/weather.py | skill | yes | none |  |
| web_search | src/skills/web_search_skill.py | skill | no | none |  |

## Escalation vs governed execution

- `ALLOW_ANALYSIS_ONLY` is represented in `src/conversation/escalation_policy.py` and used by `GeneralChatSkill` as analysis-only output path.
- Governed capabilities are routed by `GovernorMediator.parse_governed_invocation(...)` and executed via `Governor.handle_governed_invocation(...)`.
