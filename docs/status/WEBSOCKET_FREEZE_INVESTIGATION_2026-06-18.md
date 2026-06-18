# WebSocket-Induced Server Freeze — Investigation Report

**Date:** 2026-06-18
**Status:** Root cause identified. No code changes made.
**Scope:** Investigation only — per user directive.

---

## 1. CURRENT TRUTH

Nova's uvicorn server stops responding to HTTP requests after a Chrome
browser connects via WebSocket. The server process remains alive but
CPU-saturated (97%) with runaway memory growth (63 MB → 1,378 MB in
~15 seconds). This is **not a deadlock** — the event loop thread is
busy, not blocked.

**Key discriminator:** Python WebSocket clients (7 test variants) do
NOT trigger the freeze. Only Chrome triggers it. The difference is
Chrome's dashboard JavaScript, which fires 16+ governed commands and
multiple HTTP API calls within seconds of connection.

---

## 2. REPRODUCTION RESULTS

| Test | Client | Result |
|------|--------|--------|
| v1: Single WS + HTTP | Python (websockets) | PASS — no freeze |
| v2-A: Normal single WS | Python | PASS |
| v2-B: Model blocked | Python | PASS |
| v2-C: 3 simultaneous WS | Python | PASS |
| v2-D: 3 reconnect cycles | Python | PASS |
| v2-E: Model blocked + 3 WS | Python | PASS |
| v2-F: WS + 10 concurrent HTTP | Python | PASS |
| v2-G: Model blocked + reconnects | Python | PASS |
| v3: Chrome connection test | Chrome | **FREEZE — deadlock confirmed** |
| v4: Chrome + PID/CPU analysis | Chrome | **FREEZE — CPU 97%, mem 1.4 GB** |

Scripts: `scripts/pids/reproduce_deadlock*.py`

---

## 3. RUNTIME FLOW MAP

When Chrome opens `http://127.0.0.1:{PORT}`:

```
Chrome loads HTML + 10 static assets (CSS/JS)          ~parallel HTTP
  → GET /api/settings/runtime                          HTTP (sync OSDiag calls)
  → GET /api/profile                                   HTTP
  → GET /api/settings/connections                      HTTP
  → WebSocket /ws opens                                connection accepted
    → Server: send_chat_message("Hey — what are you working on?")
    → Server: create_task(_send_initial_trust_status)
        → send_trust_status → _maybe_send_trust_review_snapshot
            → asyncio.to_thread(_build_trust_review_snapshot)
                → _model_status_details() → 5s Ollama HTTP
                → _ledger_status_details() → read ledger file
                → _recent_runtime_activity() → parse ledger JSON
                → 7 more OSDiag methods
  → GET /api/openclaw/agent/status                     HTTP (another _model_status_details)
  → probeRuntimeHealthOnce()                           HTTP → /api/settings/runtime
```

Then `scheduleStartupHydration()` fires these WebSocket messages:

```
  t=0.25s:  "weather"          → invoke_governed_text_command → thread
            "calendar"         → invoke_governed_text_command → thread
  t=0.80s:  "news"             → invoke_governed_text_command → thread
            loadConnectionsData()  → HTTP /api/settings/connections
  t=1.60s:  requestOpenClawAgentRefresh(true)  → HTTP → _model_status_details
            requestSettingsRuntimeRefresh(true) → HTTP → OSDiag methods
            refreshPrivacyPanel()
  t=2.60s:  "system status"    → invoke_governed_text_command → thread
            "workspace home"   → invoke_governed_text_command → thread
            "operational context" → invoke_governed_text_command → thread
  t=3.60s:  "assistive notices" → invoke_governed_text_command → thread
            "show structure map" → invoke_governed_text_command → thread
            "trust center"     → invoke_governed_text_command → thread
            "policy overview"  → invoke_governed_text_command → thread
            "tone status"      → invoke_governed_text_command → thread
            "notification status" → invoke_governed_text_command → thread
            "pattern status"   → invoke_governed_text_command → thread
```

Each `invoke_governed_text_command` runs in `asyncio.to_thread()`, spawning
a thread in the default `ThreadPoolExecutor`. Every thread runs
`governor.handle_governed_invocation()` which dispatches to an executor.

The WebSocket receive loop is **sequential**: it `await`s
`ws.receive_text()`, processes the full command (including the
`asyncio.to_thread` call and all subsequent `ws_send` calls), then
loops back. But Chrome sends all 16 messages before the server
finishes processing the first one, so they queue in the WebSocket
buffer and get processed back-to-back.

---

## 4. EVENT LOOP ANALYSIS

**Architecture:** Single uvicorn worker, single asyncio event loop
(ProactorEventLoop on Windows 11).

**The bottleneck is NOT the event loop itself.** The problem is the
thread pool explosion:

1. The initial `_build_trust_review_snapshot` spawns a thread that
   calls `_model_status_details()` → synchronous 5s-timeout HTTP to
   Ollama.

2. While that thread is blocked on Ollama, the main loop processes
   queued WebSocket messages. Each fires another
   `asyncio.to_thread()`.

3. Simultaneously, Chrome makes HTTP requests to `/api/settings/runtime`
   and `/api/openclaw/agent/status`. These are async FastAPI endpoints
   but they call OSDiagnosticsExecutor methods **synchronously on the
   event loop thread** — including `_model_status_details()` which
   blocks for up to 5 seconds.

4. **The critical path**: `/api/openclaw/agent/status` calls
   `_model_status_details()` directly in the async handler (not via
   `to_thread`). This blocks the event loop for up to 5 seconds,
   preventing ALL other async operations from progressing.

5. The "system status" command (from hydration) runs the full
   `OSDiagnosticsExecutor.execute()` in a thread. This calls:
   - `psutil.cpu_percent(interval=0.12)` — blocks 0.12s
   - `_model_status_details()` — blocks up to 5s (Ollama HTTP)
   - `_recent_runtime_activity()` — reads and parses entire ledger
   - `_capability_surface()` — iterates all capabilities
   - `_tone_status_details()` — file I/O
   - `_memory_status_details()` — file I/O
   - `_notification_schedule_details()` — file I/O
   - `_policy_status_details()` — file I/O
   - `_ledger_status_details()` — file I/O
   - Plus 5 more methods

6. The "system status" thread calls `_model_status_details()` which
   itself triggers another synchronous HTTP call to Ollama while the
   `_build_trust_review_snapshot` thread is already doing the same.

**Thread count explosion:** Within 3.6 seconds of Chrome connecting,
the server spawns threads for: weather, calendar, news, system status,
workspace home, operational context, assistive notices, structure map,
trust center, policy overview, tone status, notification status,
pattern status, plus the trust review snapshot. That's **14+ threads**
running heavy executor code simultaneously.

**Memory explosion:** Each thread instantiates executors, builds large
response dicts, reads files, parses JSON. The "system status" executor
alone builds a response with 50+ fields including full capability
surfaces, recent activity, ledger data, and policy state. Multiply by
14 concurrent threads.

---

## 5. EXTERNAL DEPENDENCY ANALYSIS

| Dependency | Call Site | Timeout | Blocking? |
|------------|-----------|---------|-----------|
| Ollama `/api/tags` | `_model_status_details()` | 5s | **Yes — synchronous HTTP** |
| Ollama `/api/tags` | Called from 4 code paths during startup | 5s each | **Yes** |
| Weather API | `WeatherSkill` via governed command | Network-dependent | In thread |
| News API | `NewsSkill` via governed command | Network-dependent | In thread |
| Calendar | `CalendarSkill` (local file) | None | In thread |
| Ledger file | `_recent_runtime_activity()`, `_ledger_status_details()` | None | File I/O in thread |

**Critical external dependency:** Ollama. If Ollama is slow or
unreachable, `_model_status_details()` blocks its thread for the full
5-second timeout. This happens at least 3-4 times during startup:
1. `_build_trust_review_snapshot` (thread)
2. `OSDiagnosticsExecutor.execute()` for "system status" (thread)
3. `/api/openclaw/agent/status` (**event loop thread**)
4. `_blocked_conditions()` in trust review snapshot (thread)

If Ollama responds slowly (e.g., 2-3 seconds), these pile up. If
Ollama is unreachable, each blocks for the full 5 seconds.

---

## 6. COMPETING PROCESS ANALYSIS

| Process | Impact |
|---------|--------|
| Codex (OpenAI) | Hijacks localhost:8000 with 6+ TCP connections; forces use of alternate ports. Auto-respawns when killed. Not directly related to the freeze but complicates testing. |
| Ollama | Must be running for `_model_status_details()` to return quickly. When not running or when the configured model (`gemma4:e4b`) isn't installed, each health check blocks for 5 seconds. |
| Chrome | Opens 10+ parallel HTTP connections for static assets, then opens WebSocket, then fires 16 governed commands + 3-4 HTTP API calls within 3.6 seconds. |

---

## 7. ROOT CAUSE CANDIDATES

### PRIMARY: Startup hydration stampede (HIGH CONFIDENCE)

Chrome's `scheduleStartupHydration()` fires 16 WebSocket commands
within 3.6 seconds of connection. Each spawns a thread via
`asyncio.to_thread(governor.handle_governed_invocation, ...)`. Combined
with the initial `_build_trust_review_snapshot` thread and 3-4 HTTP
endpoints that also call OSDiagnosticsExecutor methods, the server
executes **17-20 concurrent blocking operations** in the first 4
seconds after Chrome connects.

The single-worker uvicorn instance cannot service HTTP requests while:
- The event loop is blocked by sync calls in async handlers
  (`/api/openclaw/agent/status` calling `_model_status_details()`)
- The thread pool is saturated with 14+ executor threads
- Memory is growing as each thread builds large response payloads

**Why Python clients don't trigger it:** They connect via WebSocket
but send zero messages. The WebSocket receive loop just waits. No
hydration commands, no concurrent HTTP API calls, no thread pool
stampede.

### CONTRIBUTING: Synchronous Ollama calls on the event loop (HIGH CONFIDENCE)

`/api/openclaw/agent/status` at line 69 of `openclaw_agent_api.py`
calls `_model_status_details()` **synchronously** in an async handler.
This blocks the event loop for up to 5 seconds. During that time, no
HTTP requests or WebSocket messages can be processed.

### CONTRIBUTING: No deduplication of concurrent `_model_status_details()` calls (MEDIUM)

The same synchronous 5s Ollama HTTP call runs 3-4 times concurrently
during startup. There is no cache or deduplication — each call
independently hits `GET /api/tags` with a 5-second timeout.

Note: `_build_trust_review_snapshot` has a 15-second cache
(`_TRUST_REVIEW_CACHE`), but this only prevents repeated calls to the
full snapshot builder. The individual `_model_status_details()` calls
from other code paths are not covered.

### CONTRIBUTING: Sequential WebSocket message processing (MEDIUM)

The WebSocket receive loop processes messages one at a time. When
Chrome queues 16 messages, each must complete fully (including
`await asyncio.to_thread(...)` and response sends) before the next
begins. But the thread calls themselves overlap because the event loop
`await`s the `to_thread` future and yields control, allowing the next
iteration to start another thread. This is by design for asyncio, but
it means the thread pool fills up quickly.

### NOT A FACTOR: Event loop deadlock

No evidence of actual deadlock (mutual resource waiting). The
`_TRUST_REVIEW_CACHE_LOCK` is an asyncio.Lock that could cause
ordering issues but not deadlock — there's only one lock and no
nested acquisition.

### NOT A FACTOR: WebSocket protocol-level issue

The WebSocket connection itself works correctly. The server accepts
connections, sends the greeting, and begins processing messages
normally. The freeze is caused by the volume and cost of work
triggered after connection, not by the connection mechanism.

---

## 8. RECOMMENDED NEXT ACTION

**Do not implement yet.** These are investigation findings only.

When ready to fix, the recommended approach (ordered by impact):

1. **Move sync Ollama calls off the event loop.** The
   `/api/openclaw/agent/status` endpoint calls
   `_model_status_details()` synchronously in an async handler.
   Wrapping this in `asyncio.to_thread()` or using an async HTTP
   client prevents event loop starvation. Same applies to any async
   endpoint that calls OSDiagnosticsExecutor methods.

2. **Add a short-TTL cache for `_model_status_details()`.** The
   Ollama health check result doesn't change within 5-10 seconds.
   A module-level cache (similar to `_TRUST_REVIEW_CACHE`) would
   prevent 3-4 redundant 5-second HTTP calls during startup.

3. **Throttle startup hydration.** The client fires 16 commands in
   3.6 seconds. Options:
   - Server-side: debounce or queue governed commands, process at
     most N concurrently
   - Client-side: increase hydration delays, batch related commands,
     or implement a single "hydrate all" endpoint
   - Either: Add a startup hydration endpoint that returns all widget
     data in one response instead of 16 separate governed commands

4. **Cap thread pool size for governed commands.** The default
   `ThreadPoolExecutor` allows `min(32, cpu_count + 4)` threads.
   A dedicated, smaller executor (e.g., 4 workers) for governed
   commands would prevent the stampede while maintaining concurrency.

5. **Reduce `_model_status_details()` timeout.** The 5-second Ollama
   timeout is aggressive for a health check. 1-2 seconds would be
   sufficient — if Ollama doesn't respond in 1 second, it's slow
   enough to report as degraded.

**Verification approach:** After implementing fixes, run
`scripts/pids/reproduce_deadlock_v4.py` and confirm:
- CPU stays below 50% after Chrome connects
- Memory stays below 200 MB
- HTTP requests respond within 1 second post-Chrome
- All 16 hydration commands still complete (no data loss)

---

## Appendix: File References

| File | Lines | Relevance |
|------|-------|-----------|
| `nova_backend/src/brain_server.py` | 3455-3530 | `_build_trust_review_snapshot`, cache, lock |
| `nova_backend/src/brain_server.py` | 3665-3679 | `invoke_governed_capability` → `asyncio.to_thread` |
| `nova_backend/src/brain_server.py` | 3409-3419 | `send_trust_status` → triggers snapshot |
| `nova_backend/src/websocket/session_handler.py` | 914-943 | Sequential WS receive loop |
| `nova_backend/src/websocket/session_handler.py` | 619-626 | Initial trust status task |
| `nova_backend/src/executors/os_diagnostics_executor.py` | 556-608 | `_model_status_details` (5s Ollama) |
| `nova_backend/src/executors/os_diagnostics_executor.py` | 1371-1470 | `execute()` — full system diagnostics |
| `nova_backend/src/executors/os_diagnostics_executor.py` | 274-315 | `_recent_runtime_activity` — ledger parse |
| `nova_backend/src/api/openclaw_agent_api.py` | 63-69 | Sync `_model_status_details` in async handler |
| `nova_backend/src/api/settings_api.py` | 34-43 | `/api/settings/runtime` → sync OSDiag calls |
| `nova_backend/src/llm/llm_manager.py` | 492-505 | `health_check()` — sync HTTP to Ollama |
| `nova_backend/static/dashboard-chat-news.js` | 2460-2493 | `scheduleStartupHydration` — 16 commands |
| `nova_backend/static/dashboard-chat-news.js` | 2496-2518 | `hydrateDashboardWidgets` — 15 commands |
| `nova_backend/static/dashboard-chat-news.js` | 2520-2524 | `startWidgetAutoRefresh` — 5 min interval |
| `nova_backend/static/dashboard.js` | 131-132 | Health probe: 15s interval, 4s timeout |
| `scripts/pids/reproduce_deadlock_v4.py` | full | Reproduction with CPU/memory analysis |
