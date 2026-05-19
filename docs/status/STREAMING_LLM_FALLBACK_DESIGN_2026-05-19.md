# Streaming LLM Fallback Design -- 2026-05-19

Status:

```text
design proposal only -- no runtime changes yet
```

---

## Problem

Ollama serializes inference requests at the model level. Under
concurrent WebSocket sessions, LLM-dependent turns queue behind
each other, causing 30-45s timeouts. PR #207 reduced Nova-side
serialization but did not fix the model-level bottleneck.

Post-PR #207 simulation results:

```text
Timeouts:     5/32 turns (down from 7, but still significant)
p95 latency:  10053ms
Max latency:  41209ms
Connection errors: 2 (new failure mode under saturation)
```

The UX impact: users see a frozen interface for 30-45 seconds
with no feedback, then either get a response or a timeout.

---

## Proposed Mitigation

Change the Ollama `/api/chat` call from `stream: false` to
`stream: true` for the advisory general-chat LLM fallback path
only. Forward early tokens to the WebSocket client as they arrive.

This does not fix Ollama's serialization. It mitigates the
perceived impact by:

1. Delivering the first visible token within 2-5 seconds even
   under load (Ollama starts streaming as soon as inference
   begins for that request, even if queued).
2. Giving the user continuous feedback that Nova is working.
3. Eliminating most 45-second timeouts (partial responses
   arrive before the timeout fires).

---

## Scope Constraints

```text
Streaming applies ONLY to:
  - advisory general-chat LLM fallback path
  - the "Bounded advisory general-chat fallback" section
    in session_handler.py (around line 4000)

Streaming does NOT apply to:
  - governed action execution (Cap 22, Cap 64, etc.)
  - confirmation gate prompts
  - capability routing decisions
  - governed search
  - OpenClaw execution
  - any path that modifies state or triggers external effects

Governance gates remain unchanged.
Confirmation behavior remains unchanged.
Ledger sequence remains unchanged.
```

---

## Technical Design

### 1. ModelNetworkMediator: add streaming method

Current code (`model_network_mediator.py`):

```text
Uses requests.Session().request() with json payload
Returns ModelResponse(status_code, data) after full completion
```

New method: `request_stream()`

```text
Same validation (URL allowlist, rate limit, ledger)
Uses requests.Session().post(url, json=payload, stream=True)
Returns an iterator of text chunks
Logs MODEL_NETWORK_CALL on completion (not per-chunk)
Falls back to non-streaming on error
```

### 2. LLMManager: add streaming chat method

Current code (`llm_manager.py`, line ~324):

```text
Sends {"stream": false} to /api/chat
Waits for complete response
Returns full text or None
```

New method: `chat_stream()`

```text
Sends {"stream": true} to /api/chat
Yields text chunks as they arrive from Ollama
Assembles final complete text for return
Preserves fallback model logic
Preserves failure counting / circuit breaker
```

### 3. Session handler: stream advisory fallback

Current code (`session_handler.py`, line ~4012):

```text
skill_result = await run_general_chat_fallback(...)
# waits for complete LLM response
await send_chat_message(ws, message)
await send_chat_done(ws)
```

New behavior:

```text
# Send thinking status (already exists from PR #207)
await ws_send(ws, {"type": "status", "status": "thinking", ...})

# Stream chunks to client
assembled_text = ""
async for chunk in stream_general_chat_fallback(...):
    assembled_text += chunk
    await ws_send(ws, {
        "type": "chat_stream",
        "text": chunk,
        "turn_id": incoming_turn_id,
    })

# Send final assembled message (for logs/context/personality)
await send_chat_message(ws, assembled_text)
await send_chat_done(ws)
```

### 4. WebSocket frame contract changes

New frame type:

```json
{
    "type": "chat_stream",
    "text": "<partial token(s)>",
    "turn_id": "<turn identifier>"
}
```

Client behavior:

```text
- Accumulate chat_stream frames into a growing response bubble
- Replace accumulated text with the final chat message when it
  arrives (handles personality/formatting applied server-side)
- chat_done still signals end of turn (no change)
- If client does not recognize chat_stream, it ignores them
  and only renders the final chat message (backward compatible)
```

---

## What This Changes

```text
- LLM fallback response delivery: blocking -> streaming
- User-visible latency: 30-45s wait -> 2-5s first token
- WebSocket frame types: adds chat_stream (additive)
- ModelNetworkMediator: adds request_stream() method
- LLMManager: adds chat_stream() method
```

## What This Does NOT Change

```text
- Governance gates
- Confirmation behavior (Cap 22, Cap 64)
- Capability routing
- Governed search
- OpenClaw execution
- Ledger event sequence
- capability_locks.json
- Registry truth
- Approval-gate certification
- Any governed action path
```

---

## Files To Change

```text
nova_backend/src/llm/model_network_mediator.py
  - Add request_stream() method

nova_backend/src/llm/llm_manager.py
  - Add chat_stream() generator method
  - Keep existing chat() method unchanged for non-streaming paths

nova_backend/src/websocket/session_handler.py
  - Modify the "Bounded advisory general-chat fallback" section
    to use streaming when available
  - Preserve non-streaming path as fallback

nova_backend/tests/ (new)
  - Test streaming frame delivery
  - Test fallback to non-streaming on error
  - Test governance paths remain non-streaming
```

---

## Risk Assessment

```text
Low risk:
  - Additive frame type (backward compatible)
  - Streaming only applies to advisory fallback
  - Non-streaming paths remain unchanged
  - Governance paths untouched

Medium risk:
  - Partial responses may contain incomplete sentences
  - Client must handle accumulation correctly
  - Error mid-stream requires cleanup

Mitigated by:
  - Final chat message replaces accumulated stream
  - chat_done still required to close turn
  - Non-streaming fallback on any stream error
```

---

## Verification Plan

```text
1. Run the exact same 20-persona simulation after implementation
2. Compare timeout count, p95, max latency against post-PR #207
3. Verify governance turns (Morgan, Casey, Riley, Taylor, Frankie,
   Gale, Kai, Noor) remain non-streaming and unchanged
4. Verify streaming only occurs for advisory LLM fallback turns
5. Verify chat_done still signals end of turn
```

---

## Preserved Boundaries

```text
Intelligence is not authority.
```

This design does not authorize:

- Capability expansion
- Authority expansion
- Governed action streaming
- Confirmation gate changes
- OpenClaw expansion
- Browser/computer-use expansion
- Shopify writes
- Autonomous execution
