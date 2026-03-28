# Phase 7 Reasoning Surface And Long-Form Presentation Refinement
Updated: 2026-03-28
Status: Runtime refinement on top of the already-complete bounded reasoning lane

## Purpose
This packet records a presentation-quality refinement across the live Phase-7 reasoning and answer-delivery surfaces.

The governance boundary did not change.
The goal was to make long-form outputs easier to scan, easier to speak, and easier to review in Trust and Settings.

## What Changed
- `ResponseFormatter` now recognizes stronger summary anchors instead of blindly prepending `Summary:` to every long structured response
- explicit lines like `Bottom line:` now survive as the lead summary when they already exist
- long-form content with sections like `Top Headlines` now gets a cleaner executive summary line based on the first real item rather than the heading itself
- `GeneralChatSkill` now routes local-model chat replies through `format_payload`, so the shared executive-summary behavior applies there too
- `OSDiagnosticsExecutor` now carries the latest second-opinion:
  - bottom line
  - main gap
  - best correction
- Trust and Settings reasoning panels now show those three fields directly instead of only provider, route, authority, and budget
- `WebSearchExecutor` now leads long-form search answers with a bottom-line sentence before the supporting details
- `NewsIntelligenceExecutor` now leads the main long-form report variants with a bottom-line sentence before the fuller body:
  - headline-by-headline summary
  - category summary
  - story-page summary
  - daily intelligence brief
  - expanded brief story view

## Why This Matters
This does not widen authority.

It improves the actual product experience in three ways:
- Nova leads with the useful thing faster in long answers
- the review lane summary now stays visible outside the chat transcript
- chat, voice, and Trust surfaces are better aligned around the same review signals

## Verification
Run these commands from `nova_backend/`.

Passed:
- `python -m pytest tests\conversation\test_response_formatter.py tests\conversation\test_general_chat_tone.py tests\executors\test_web_search_executor.py tests\executors\test_news_intelligence_executor.py tests\executors\test_os_diagnostics_openclaw_agent.py tests\phase45\test_dashboard_trust_center_widget.py -q`
- `python -m pytest tests\conversation\test_general_chat_runtime.py tests\conversation\test_voice_agent.py tests\executors\test_external_reasoning_executor.py tests\executors\test_response_verification_executor.py tests\phase45\test_dashboard_phase7_chat_controls.py -q`
- `python -m py_compile src\conversation\response_formatter.py src\skills\general_chat.py src\executors\os_diagnostics_executor.py src\executors\web_search_executor.py src\executors\news_intelligence_executor.py`
- `node --check static\dashboard.js`
- `python ..\scripts\check_runtime_doc_drift.py`
- `python ..\scripts\check_frontend_mirror_sync.py`

## Bottom Line
Phase 7 remains advisory-only and bounded.

This refinement makes the reasoning lane easier to read in Trust and Settings, and it makes Nova’s longer search, news, and general-chat answers lead with the answer more consistently.
