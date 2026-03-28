# Phase 7 Report Surfaces, Chat Summary Card, and Voice Refinement
Updated: 2026-03-28
Status: Complete runtime slice

## Purpose
This packet records the refinement pass that made Nova's long-form reporting surfaces easier to scan in chat and calmer to hear in voice output.

## What changed
- long-form report builders now lead more consistently with an explicit `Bottom line:` line
- analysis documents now surface a clearer lead takeaway for:
  - document creation
  - document summary
  - section explanation
- story tracker views now surface a lead takeaway before the detailed timeline
- assistant chat messages now render a reusable summary card when a message contains:
  - `Bottom line`
  - `Main gap`
  - `Best correction`
- the chat report parser now also recognizes `INTELLIGENCE BRIEF` and `DETAILED STORY ANALYSIS`
- voice presentation now summarizes structured reports through the same lead-takeaway path instead of reading a long report body verbatim

## Files changed
- `nova_backend/src/rendering/intelligence_brief_renderer.py`
- `nova_backend/src/executors/analysis_document_executor.py`
- `nova_backend/src/executors/story_tracker_executor.py`
- `nova_backend/src/voice/voice_agent.py`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`
- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/style.phase1.css`

## Why this matters
Phase 7 is already a bounded reasoning and review layer.
This slice improves how those review/reporting results land for users:
- the useful takeaway appears first
- spoken output stays shorter and more natural
- chat cards make structured review signals easier to notice without opening Trust first

## Verification
Run from `nova_backend/` unless noted.

- `python -m pytest tests\conversation\test_voice_agent.py tests\executors\test_analysis_document_executor.py tests\executors\test_multi_source_reporting_executor.py tests\executors\test_story_tracker_executor.py -q`
- `python -m py_compile src\rendering\intelligence_brief_renderer.py src\executors\analysis_document_executor.py src\executors\story_tracker_executor.py src\voice\voice_agent.py`
- from repo root: `node --check nova_backend/static/dashboard.js`
- from repo root: `node --check Nova-Frontend-Dashboard/dashboard.js`
- from repo root: `python scripts/check_frontend_mirror_sync.py`
- from repo root: `python scripts/check_runtime_doc_drift.py`

## Verification snapshot
- focused voice/report bundle: passed
- python compile check: passed
- frontend syntax checks: passed
- frontend mirror parity check: passed
- runtime documentation drift check: passed

## Boundary
This slice improves presentation only.
It does not widen the advisory-only authority boundary of Phase 7 reasoning or review.
