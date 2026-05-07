# Web / News / Reporting Blockers - 2026-05-06

Status: draft / review required

## Blocking / High Priority

1. **Computer-use screenshot capture unavailable**
   - Prevented direct visual proof of news/article buttons in this pass.
   - UI screenshots should be captured once browser runtime is working.
   - Evidence: `../UI-Commands/evidence/2026-05-06/raw/browser_use_failure.txt`, `../UI-Commands/evidence/2026-05-07/raw/browser_screenshot_followup_attempt.txt`

## Resolved In 2026-05-07 Fix Pass

1. **Nonsense search relevance/confidence failure**
   - Query: `search qzxqzxqzx nonexistent topic with 1000 sources`
   - Fix validation: result now reports `Confidence: Low` and says results may be weak or unrelated.
   - Evidence: `evidence/2026-05-07/raw/web_news_blocker_fix_probe.json`
   - Regression: `nova_backend/tests/brain/test_search_synthesis.py`

2. **Headline summary command did not reliably summarize loaded headline state**
   - Query: `news`, then `summarize all headlines in plain language`
   - Fix validation: response summarized the loaded headlines and stated no web search or external action was performed.
   - Evidence: `evidence/2026-05-07/raw/web_news_blocker_fix_probe.json`
   - Regression: `nova_backend/tests/websocket/test_session_handler_proof_blockers.py`

3. **Topic map and story tracker lacked live proof**
   - Fix validation: `show topic map`, `track story global security`, and `show story tracker` now have direct proof evidence.
   - Evidence: `evidence/2026-05-07/raw/web_news_blocker_fix_probe.json`

4. **Prompt-injection content was safe but noisy**
   - Fix validation: quoted prompt-injection/article text is now handled as untrusted local content and does not route into search.
   - Evidence: `../UI-Commands/evidence/2026-05-07/raw/ui_followup_probe.json`
   - Regression: `nova_backend/tests/websocket/test_session_handler_proof_blockers.py`

5. **Story tracker proof dirtied local workspace state**
   - Fix validation: story tracker proof can use a temp-store executor path; no default `nova_workspace/story_tracker/story_proof_only.json` was created.
   - Evidence: `evidence/2026-05-07/raw/story_tracker_temp_store_proof.json`
   - Regression: `nova_backend/tests/executors/test_story_tracker_executor.py`

## Non-Blocking But Important

1. **Invalid URL confirmation is resolved for single-label malformed input**
   - `open website notaurl` became `https://notaurl` and asked for confirmation.
   - Follow-up validation now rejects it before confirmation.
   - Evidence: `../UI-Commands/evidence/2026-05-07/raw/ui_followup_probe.json`

2. **Open website/article visual proof remains blocked by browser-use runtime**
   - Article/open behavior remains proven through WebSocket confirmation evidence, not screenshots.
