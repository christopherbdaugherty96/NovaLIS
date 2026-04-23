# Live News And Headlines Verification - 2026-04-23

## Scope

Live dashboard testing against the served app at `http://127.0.0.1:8000/`, using ordinary user-style prompts:

- `What are today's headlines?`
- `What's the latest on AI?`
- `Tell me more about the second story.`
- `Summarize that in 2 sentences.`
- `Where did you get that?`
- `What's going on right now?`

Focused verification also covered backend turn correlation for widget replies and governor parsing for natural-language headline requests.

## What Was Fixed

1. Widget replies now carry the active manual `turn_id`.
   - Before this pass, widget-based responses like `news`, `search`, `weather`, and `calendar` could finish on the backend without the dashboard recognizing that the active manual turn had actually received a reply.
   - Fix: `send_widget_message()` now echoes the current WebSocket `turn_id`.

2. Dashboard manual-turn completion now recognizes widget replies.
   - Before this pass, the dashboard only treated `chat` frames as proof that a manual turn had been answered.
   - Fix: dashboard chat/news surfaces now treat matching `news`, `news_summary`, `intelligence_brief`, `search`, `weather`, and `calendar` widget replies as valid turn output when the `turn_id` matches.

3. Question-form headline asks now route to the news capability.
   - `What are today's headlines?` previously missed the headline/news regex and could drift into slower or less coherent paths.
   - Fix: governor news parsing now includes question forms like `what are today's headlines`.

4. Ordinal story follow-ups now work.
   - `Tell me more about the second story.` now maps to the story-page summary path instead of falling through.

5. Natural source follow-up now works.
   - `Where did you get that?` now resolves like `show sources for your last response`.

## Focused Verification

Command:

```powershell
python -m pytest nova_backend\tests\test_governor_mediator_phase4_capabilities.py nova_backend\tests\phase45\test_brain_server_basic_conversation.py nova_backend\tests\phase45\test_dashboard_auto_widget_dispatch.py nova_backend\tests\conversation\test_conversation_router.py -q
```

Result:

```text
76 passed
```

Additional checks:

- `python -m py_compile nova_backend\src\brain_server.py nova_backend\src\governor\governor_mediator.py nova_backend\src\websocket\session_handler.py nova_backend\src\conversation\conversation_router.py`
- dashboard source parity kept in both:
  - `Nova-Frontend-Dashboard/dashboard-chat-news.js`
  - `nova_backend/static/dashboard-chat-news.js`

## Live Runtime Result

Status: PASS with two documented residual issues

Passing behaviors observed:

- `What are today's headlines?`
  - returned current headline coverage and follow-up guidance
  - emitted correlated `chat` and `chat_done` frames for the same manual turn
- `What's the latest on AI?`
  - returned a sourced multi-domain intelligence brief
- `Tell me more about the second story.`
  - correctly resolved to story 2 and produced a story-page summary
- `Summarize that in 2 sentences.`
  - produced a follow-up summary for the previously selected story
- `Where did you get that?`
  - returned the source list for the prior sourced answer instead of generic fallback

Observed frame examples from the passing pass:

```text
chat(turn_id=ui-turn-...-1) -> Loaded 5 sources. Theme: global security...
chat_done(turn_id=ui-turn-...-1)

chat(turn_id=ui-turn-...-3) -> STORY PAGE SUMMARY - Story 2...
chat_done(turn_id=ui-turn-...-3)

chat(turn_id=ui-turn-...-5) -> Sources for last response:
1. www.reuters.com
...
chat_done(turn_id=ui-turn-...-5)
```

## Remaining Issues

1. `What's going on right now?` still falls back too often.
   - This phrasing is broad enough that Nova should probably route it to live news/current-events clarification or a current-events summary instead of generic fallback.

2. Very early first-turn sends can still collide with startup WebSocket hydration.
   - In one rerun, a just-loaded dashboard showed the queueing message and startup greeting before the first headline response.
   - This is a startup readiness/polish issue, not a news-capability correctness issue, but it is still real first-user friction.

## Recommended Next Step

Continue with a short polish pass for live-information prompts:

- improve vague current-events routing for phrases like `what's going on right now?`
- tighten first-turn startup readiness so the first manual send does not compete with greeting/hydration traffic
