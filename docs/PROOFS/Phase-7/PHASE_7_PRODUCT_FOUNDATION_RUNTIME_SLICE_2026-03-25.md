# Phase 7 Product Foundation Runtime Slice
Date: 2026-03-25
Status: Verified on current branch and ready to land
Scope: Ship the highest-value bounded Phase-7 user-facing improvements without widening authority

## What this slice implements
This runtime slice improves the product where users feel Phase 7 most directly:

- web search now answers first and keeps sources behind an explicit reveal
- the News page now supports inline summaries inside the page instead of bouncing the user back to chat
- user-facing news categories are simplified to:
  - Politics news
  - Global news
  - Local news
  - Tech news
  - Crypto news
- the chat bar now exposes a `DeepSeek` one-shot second-opinion control
- TTS capability 18 now prefers the stronger local Piper-backed renderer before falling back to `pyttsx3`

## Product effect
The product now feels less like:
- a visible tooling breakdown
- a launcher that pushes users between pages
- a hidden second-opinion pipeline

and more like:
- answer-first search
- in-place news work
- a bounded same-thread second opinion
- a cleaner speech-output path

## Boundaries preserved
This slice does not:
- widen execution authority
- add autonomous behavior
- turn DeepSeek into a second assistant persona
- add hidden memory creation
- make the governor less strict for real-world actions

## Key files
- `nova_backend/src/executors/web_search_executor.py`
- `nova_backend/src/executors/news_intelligence_executor.py`
- `nova_backend/src/executors/response_verification_executor.py`
- `nova_backend/src/executors/tts_executor.py`
- `nova_backend/src/voice/tts_engine.py`
- `nova_backend/src/skills/news.py`
- `nova_backend/src/governor/governor_mediator.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/index.html`
- `nova_backend/static/style.phase1.css`

## Verification completed
Focused product bundles:
- `38 passed`
- `15 passed`
- `99 passed`

Broader regression bundle:
- `215 passed`

Additional checks:
- `node --check nova_backend/static/dashboard.js` passed
- `python scripts/check_frontend_mirror_sync.py` passed

## Important caveat
The TTS code path is stronger now, but real-device spoken-output validation is still a live product concern.

Truthful current state:
- Nova now prefers the stronger local renderer
- fallback still exists
- hardware/audio-path confirmation still matters on real machines

## Next strongest product moves after this slice
- project/workspace home foundations
- unified trust-center surface
- onboarding / first-run guidance
- live TTS device restore validation and polish
