# Conversation + Search Proof Pass

Date: 2026-04-29

## Verdict

Conversation/search path mostly works with important P1/P2 friction.

Nova can now answer the memory-vs-intelligence baseline locally, route current/current-evidence questions to governed Cap 16 web search, show source URLs directly in chat, include confidence plus known/unclear sections, ask clarification for `search`, and avoid overclaiming when search results are weak or mismatched.

## Live Evidence Files

- `live_test_raw.json` - baseline failures before this pass
- `live_test_after_fixes.json` - full live run after routing/source/fallback fixes
- `live_smoke_after_meta_fix.json` - memory/intelligence local answer smoke
- `live_smoke_after_final_fixes.json` - final smoke for local answer and weak-search handling
- `live_smoke_after_final_fixes.json` is the best evidence for the normal no-web and fake-company tests.

## Results

- Normal no-web question: pass after meta/local fallback.
- Current AI model releases: partial; one live run returned sourced results, another hit `Execution exceeded allowed CPU budget`.
- Explicit EV sales source request: pass with visible URLs.
- Coffee/Alzheimer's uncertainty prompt: pass with visible sources; wording should still become more medically cautious.
- Shopify follow-up: partial; explanation and safe-use boundary improved, one avoid-doing follow-up drifted.
- Topic shift to electric bikes: mostly pass.
- Fake-company search: pass after low-relevance handling; Nova now says little reliable evidence was found.
- `search`: pass; asks what to search for.

## Remaining Friction

- P1: current-search CPU budget can still block a live answer.
- P2: local model latency and generic fallback still affect some open-ended turns.
- P2: connector/governance follow-up tracking needs more consistency.
- P2: proof harnesses must drain the WebSocket startup greeting before measuring the first prompt.

## Recommendation

Do not resume Cap 64 yet. Next step is fixing remaining Cap 16 search/runtime friction and follow-up coherence.
