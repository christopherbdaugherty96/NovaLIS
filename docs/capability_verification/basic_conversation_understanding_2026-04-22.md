# Basic Conversation and Understanding Verification - 2026-04-22

## Scope

This is a platform/runtime verification slice, not a numbered governed action capability. It covers:

- Warm startup and greeting behavior
- Casual chat routing
- Open-ended explanation/understanding
- Follow-up and rewrite handling
- Clarification prompts
- Safety gate handling
- Memory/context injection into general chat
- WebSocket chat path behavior

## Automated Result

Status: PASS

Command:

```powershell
python -m pytest nova_backend/tests/conversation nova_backend/tests/test_general_chat_behavior.py nova_backend/tests/phase45/test_brain_server_basic_conversation.py nova_backend/tests/test_llm_manager_version_lock.py -q
```

Result:

```text
341 passed in 56.02s
```

Coverage confirmed by automated tests:

- Conversation routing modes: casual, direct, action, analysis, brainstorm, follow-up
- Clarification for vague or referential requests
- Safety blocking for common unsafe first-user prompts
- General chat tone profiles and concise/detailed behavior
- Greeting path through personality model in unit tests
- Deterministic thanks/repeat/help/time responses without model calls
- Conversation context, option references, rewrite/clarification follow-ups
- Memory context injection into general chat runtime
- WebSocket startup greeting, help, repeat, voice-friendly response, repo-summary, and local project paths

## Live Runtime Result

Status: PASS - signed off

Backend was started with:

```powershell
python scripts/start_daemon.py --no-browser
```

Health check:

```text
/phase-status returned active Phase 8 runtime
```

Passing live WebSocket probes:

- `hello` returned a warm greeting.
- `what can you do?` returned the capability help surface with suggested actions.
- `what is a GPU?` returned a relevant explanation through the local model fallback path.
- `say that simpler` rewrote the previous explanation in simpler language.
- `how should I think about choosing between a GPU and CPU for local AI?` returned a coherent comparison.
- `open that file` returned the expected clarification prompt.
- `???` returned a spoken-style retry prompt.
- `thanks` returned `You're welcome.`

Observed behavior:

- Before the fix, startup reported local model inference locked pending explicit confirmation.
- After sending `confirm model update`, `/api/settings/model/status` reported `inference_blocked=false` and `ready=true`.
- The configured primary model `gemma4:e4b` returned HTTP 500 from Ollama on this machine because it required more memory than available.
- The previous configured fallback `gemma4:e2b` also required more memory than available.
- The verified installed fallback `gemma2:2b` can answer local chat requests.
- After the fallback fix, live WebSocket open-ended turns answer successfully instead of degrading to the generic fallback.

Relevant log evidence:

```text
Model network call failed: 500 Server Error: Internal Server Error for url: http://localhost:11434/api/chat
Primary model gemma4:e4b failed; retrying with fallback model gemma2:2b.
```

## Sign-Off Decision

Basic conversation and understanding is signed off for this machine.

The deterministic conversation shell is healthy, and open-ended understanding now succeeds through the local fallback model when the configured primary model is too large for available memory.

## Applied Fixes

1. Changed the default fallback model from `gemma4:e2b` to `gemma2:2b`.
2. Added immediate fallback retry when the primary Ollama chat call fails.
3. Scoped fallback generation to a smaller context/prediction budget.
4. Updated Quickstart to install both the primary model and fallback model.
5. Added unit coverage for immediate fallback retry and fallback context clamping.

## Remaining Follow-Up

The model status endpoint still says the primary model is "reachable" because it checks model presence, not whether `/api/chat` can fit in memory. A later diagnostics pass should distinguish installed from runnable.
