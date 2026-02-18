# (Phase 4)# ⚙️ RUNTIME_TRUTH.md

**Nova — Mechanical Runtime Specification**
**Status:** CANONICAL (Phase-3.5 Sealed — Spine Installed, Execution Inert)
**Scope:** `nova_backend/src/` only
**Nature:** Implementation-binding, non-aspirational

Grounded in:
- `brain_server.py`
- `skill_registry.py`
- `confirmation_gate.py`
- `governor/` (Governor class, ExecuteBoundary)
- Skills (`system.py`, `weather.py`, `news.py`, `web_search_skill.py`, `general_chat.py`)
- `nova_config.py`
- **Nova Complete Constitutional Blueprint v1.8** (authoritative)

---

## 1. Runtime Entry Surface

### 1.1 Entrypoint

Primary runtime module:



------------------------------------------------
(phase 3)RUNTIME_TRUTH.md

---

# ⚙️ RUNTIME_TRUTH.md

**NovaLIS — Mechanical Runtime Specification**
**Status:** CANONICAL (Phase-3.5 Frozen)
**Scope:** `nova_backend/src/` only
**Nature:** Implementation-binding, non-aspirational

Grounded in:

* `brain_server.py` 
* `skill_registry.py` 
* `confirmation_gate.py` 
* `governor_mediator.py` 
* Skills (`system.py`, `weather.py`, `news.py`, `web_search_skill.py`, `general_chat.py`)
* `nova_config.py` 

---

# 1. Runtime Entry Surface

## 1.1 Entrypoint

Primary runtime module:

```
nova_backend/src/brain_server.py
```

Source: 

FastAPI application:

```python
app = FastAPI()
```

Inbound surfaces:

| Surface         | Type      | Purpose                           |
| --------------- | --------- | --------------------------------- |
| `/`             | HTTP GET  | Serve static dashboard            |
| `/phase-status` | HTTP GET  | Publish frozen runtime guarantees |
| `/ws`           | WebSocket | Primary interaction channel       |

STT router mounted:

```python
app.include_router(stt_router)
```

No additional routers registered.

---

# 2. Execution Authority — Structural Reality

## 2.1 Execution Flag

From configuration:

```
EXECUTION_ENABLED = False
```

Source: 

This is constant in Phase-3.5.

## 2.2 Import Surface Proof

Active runtime modules:

* `brain_server.py` 
* `skill_registry.py` 
* `confirmation_gate.py` 
* `governor_mediator.py` 
* All registered skills

None import:

* `archive_quarantine`
* `execution/*`
* `actions/*`
* `ActionRequest`
* `execute_action`

Therefore:

> No import path from any active runtime module leads to quarantine or execution code.

Execution code exists physically but is unreachable.

---

# 3. Governor Layer

Source: 

Properties:

* Stateless
* Pure function
* No imports
* No side effects
* No semantic analysis
* No routing
* No policy enforcement
* No execution hooks

Behavior:

```python
if not text or not text.strip():
    return "I'm not sure right now."
return text.strip()
```

GovernorMediator does not:

* Interpret intent
* Enforce permissions
* Trigger tools
* Modify state

It only strips whitespace or returns a fallback string.

---

# 4. Confirmation Gate

Source: 

## 4.1 Engagement

Gate consulted only if:

```python
confirmation_gate.has_pending_confirmation()
```

Source: 

If no pending context:

```
try_resolve() → GateResult(message=None)
```

Gate is silent when idle.

## 4.2 Vocabulary

Accepted:

* `"yes"`
* `"no"`

All other input:

* Silent (`message=None`)

## 4.3 No Initiation Path

There is **no code path** in Phase-3.5 that calls:

```
confirmation_gate.set_pending()
```

Therefore:

> Confirmation flows cannot begin in Phase-3.5 runtime.

---

# 5. Skill Dispatch — Deterministic Registry

Source: 

Registration order:

1. SystemSkill
2. WeatherSkill
3. NewsSkill
4. WebSearchSkill (if `ONLINE_ACCESS_ALLOWED`)
5. GeneralChatSkill

Single-pass selection:

* First `can_handle()` True wins.
* No chaining.
* No orchestration.

Exception handling:

* Any exception inside a skill is caught.
* Logged.
* Converted to:

```python
SkillResult(
    success=False,
    message="Something went wrong."
)
```

Registry never crashes runtime.

---

# 6. Configuration Surface

Source: 

Configuration values are read at import time.

No configuration is reloaded at runtime.

## 6.1 Web Search Governance

```
ONLINE_ACCESS_ALLOWED
WEB_SEARCH_TRIGGERS
WEB_SEARCH_MAX_RESULTS
```

Trigger phrases are defined in `nova_config.WEB_SEARCH_TRIGGERS`.

Max results defined in `nova_config.WEB_SEARCH_MAX_RESULTS`.

WebSearchSkill enforces word-boundary regex matching. 

## 6.2 Weather Configuration

```
DEFAULT_LOCATION
WEATHER_CACHE_SECONDS
```

WeatherSkill performs a single HTTP GET to a configured weather API via WeatherService. 

It is read-only and does not modify system state.

---

# 7. Skills — Mechanical Contracts

## 7.1 SystemSkill

Source: 

* Local time/date
* Uses `datetime`, `platform`, `time`
* No network
* No state mutation

---

## 7.2 WeatherSkill

Source: 

* Trigger: substring `"weather"`
* Calls `WeatherService.get_current_weather()`
* Performs single HTTP GET
* No write operations
* Returns canonical widget:

```
{
  "type": "weather",
  "data": {...}
}
```

---

## 7.3 NewsSkill

Source: 

* Fixed RSS feeds
* One headline per source
* Uses RSS primary
* Deterministic fallback (`fallback_headline`) when RSS fails
* Always returns canonical widget shape:

```
{
  "type": "news",
  "items": [...]
}
```

No summaries.
No synthesis.
No ranking.

---

## 7.4 WebSearchSkill (Conditional)

Source: 

Requirements:

* `ONLINE_ACCESS_ALLOWED == True`
* Explicit trigger phrase
* Word-boundary enforced

Behavior:

* Single fetch
* No retries
* No caching
* No synthesis
* Title + URL only
* Mandatory disclosure: `"I'm checking online."`

Widget shape:

```
{
  "type": "web_search_results",
  "items": [...]
}
```

---

## 7.5 GeneralChatSkill

Source: 

* Lazy import of `ollama`
* No crash if unavailable
* Blocks authoritative tokens:
  `{weather, forecast, news, headlines, time, date, system, status}`
* Advisory only
* No tools
* No memory writes
* No execution

---

# 8. Memory Surface

Quick corrections only.

Source: 

Trigger:

```
Correction: ...
```

Effect:

* Calls `record_correction()`
* Responds: `"Okay. Correction noted."`

Corrections are recorded but not applied to runtime behaviour in Phase-3.5.

---

# 9. Speech State

`speech_state`:

* Stores `last_spoken_text`
* Provides `stop()` method
* Used only for:

  * `"repeat"`
  * `"stop"`

No background audio processing initiated here.

---

# 10. WebSocket Protocol Details

Source: 

Greeting:

```
{"type":"chat","message":"Hello. How can I help?"}
{"type":"chat_done"}
```

`chat_done` payload schema:

```
{"type":"chat_done"}
```

No streaming.
No partial messages.

---

# 11. Background Activity Audit

Absent:

* `@app.on_event("startup")` loops
* `asyncio.create_task` background loops
* Schedulers
* Timers
* Periodic refresh
* Autonomous threads

All outbound calls occur only in response to inbound requests.

---

# 12. Mechanical Guarantees

1. No execution surface exists.
2. GovernorMediator cannot execute.
3. ConfirmationGate cannot initiate.
4. Skill dispatch is deterministic and single-pass.
5. No background polling.
6. **All skills are read-only.**

   * No disk writes
   * No OS command execution
   * No file modification
   * No system control

---

# 13. Explicit Exclusions

Not present:

* DeepSeek
* Multi-agent pools
* ExecutionGate enforcement engine
* Delegated autonomy
* Device control
* Reminder scheduling
* Automation engine

---

# 14. Runtime Identity (Mechanical Summary)

Phase-3.5 runtime is:

* Deterministic
* Single-pass routed
* Read-only
* Passive when idle
* Execution-disabled
* Authority-contained

No roadmap.
No expansion.
No inference.

Only current runtime fact.

---

# 15. AudioManager is a non-cognitive infrastructure loop.
It does not generate content, evaluate intent, or mutate state.
It exists solely to serialize TTS playback.
It is not considered background cognition under Phase 3.5.

---
