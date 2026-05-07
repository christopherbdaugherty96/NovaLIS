# UI / Commands Blockers - 2026-05-06

Status: draft / review required

## Blocking / High Priority

1. **Browser/computer-use evidence capture unavailable**
   - Attempted in-app browser runtime failed before page interaction with `failed to write kernel assets: The system cannot find the path specified`.
   - Impact: no direct UI screenshots or click-path evidence captured in this pass.
   - Evidence: `evidence/2026-05-06/raw/browser_use_failure.txt`

2. **Invalid URL prompt remains too permissive**
   - `open website notaurl` prompted `Open notaurl? URL: https://notaurl`.
   - Confirmation prevented immediate open, but malformed/low-confidence URL input still looks more valid than it should.
   - Evidence: `evidence/2026-05-06/raw/websocket_command_probe_corrected.json`

3. **Prompt-injection text handling is safe but noisy**
   - The injected command was not executed, which is the important boundary pass.
   - The text was routed into search rather than summarized as quoted/untrusted article content.
   - Evidence: `evidence/2026-05-06/raw/websocket_command_probe_corrected.json`

## Resolved In 2026-05-07 Fix Pass

1. **Pending website confirmation monopolized subsequent command flow**
   - Fix validation: after `open website example.com`, the unrelated `weather` command canceled the stale pending open request and then returned weather in the same turn.
   - Evidence: `evidence/2026-05-07/raw/ui_blocker_fix_probe.json`
   - Regression: `nova_backend/tests/websocket/test_session_handler_proof_blockers.py`

2. **Blocked action coercion was too generic**
   - Fix validation: OpenClaw automation/browser, external write, GovernorMediator bypass, and direct Cap 63 shortcut prompts now return boundary-specific refusals.
   - Evidence: `evidence/2026-05-07/raw/ui_blocker_fix_probe.json`
   - Regression: `nova_backend/tests/websocket/test_session_handler_proof_blockers.py`

3. **Nonsense/empty-result search returned high confidence on irrelevant results**
   - Fix validation: the nonsense query now reports `Confidence: Low` and says results may be weak or unrelated.
   - Evidence: `../Web-News-Reporting/evidence/2026-05-07/raw/web_news_blocker_fix_probe.json`
   - Regression: `nova_backend/tests/brain/test_search_synthesis.py`

## Non-Blocking But Important

1. **Headline summary command drift is resolved for loaded headline state**
   - Fix validation is recorded in the Web/News proof package.
   - Keep a regression fixture because the UI button text naturally depends on session state.
